#!/usr/bin/env perl

use strict;
use warnings;

use Carp;
use DBD::Pg qw( :pg_types );
use DBI;
use File::Basename;
use Getopt::Long;
use IO::File;
use JSON;
use MIME::Types;

my $opt_config  = 'settings.json';
my $opt_file    = 'metadata-example.json';
my $opt_dry_run = 0;
my $opt_update  = 0;
my $opt_help    = 0;

# Everything the metadata file would change about a row that is already
# loaded.  Without --update these are collected and reported instead of
# being applied.
my @conflicts;

sub usage {
    print("Usage:\n");
    print("\t$0 [-c config-file] [-f data-file] [-u] [-n]\n");
    print("\t$0 -h\n");
    print("\n");
    print("\t-c, --config\tJSON file with database settings; the same\n");
    print("\t\t\tsettings.json the backend uses, read for its\n");
    print("\t\t\tpostgresHost/Port/User/Pass/Name keys\n");
    print("\t-f, --file\tJSON file with study metadata\n");
    print("\t-u, --update\tOverwrite rows that are already loaded\n");
    print("\t-n, --dry-run\tRun everything, then roll back\n");
    print("\t-h, --help\tThis message\n");
    print("\n");
    print("New rows are always loaded.  A row that is already loaded and\n");
    print("still matches the file is left alone.  One that no longer\n");
    print("matches is a conflict: by default the run reports every such\n");
    print("row and writes nothing, and only --update overwrites them.\n");
    print("\n");
    print("Rows are matched on their stable identifiers (dataset\n");
    print("short-name, version, collection name); every other field is\n");
    print("taken from the file, and a field dropped from the file is set\n");
    print("back to NULL.  Nothing is ever deleted: dropping a dataset\n");
    print("version, sample set, logotype or released file from the\n");
    print("metadata leaves what is already loaded in place.\n");
}

sub get_file {
    my ( $fname, $binary ) = @_;

    local $/;
    my $fh = IO::File->new( $fname, "r" ) or croak("$!");
    if ($binary) { binmode($fh) }
    my $text = <$fh>;
    $fh->close();

    return $text;
}

sub has_data {
    my ( $hash, $key ) = @_;

    return exists( $hash->{$key} ) && $hash->{$key} =~ /\S/;
}

# A value is only a candidate filename if it is short enough to be a path
# and holds no newline.  Without this, -f on a multi-kilobyte document
# (a description or terms-of-use pasted straight into the JSON) is at best
# wasted work and at worst a warning.
sub looks_like_filename {
    my ($value) = @_;

    return defined($value)
      && length($value) < 256
      && $value !~ /\n/;
}

# Read a value that may be either inline text or the name of a file
# holding that text.
sub text_or_file {
    my ($value) = @_;

    if ( looks_like_filename($value) && -f $value ) {
        return get_file($value);
    }

    return $value;
}

sub validate_required {
    my ( $variable, $name, @keys ) = @_;

    my $error = 0;
    foreach my $key (@keys) {
        if ( !has_data( $variable, $key ) ) {
            ++$error;
            printf( STDERR "%s is missing required key %s\n",
                    $name, $key );
        }
    }

    return $error;
}

# Build the statements an upsert needs for one table, so that a single
# list of columns drives all of them and they cannot drift apart.
#
# Columns are [ name, value ] pairs, where value is the SQL written in
# place of the column's parameter -- normally '?', but carrying a cast or
# a wrapping expression where one is needed.  A third element gives a
# different expression to use on insert, for the cases where the update
# form refers to the column's own stored value.
#
# Identity columns are matched on and never overwritten; content columns
# are taken from the file every time; literals are written only on insert.
# The parameters of every statement are the identity values followed by
# the content values, in the order listed here.
sub make_statements {
    my ( $table, $identity, $content, $literals ) = @_;

    my ( @where, @set, @differs, @columns, @values );

    foreach my $column ( @{$identity} ) {
        my ( $name, $value ) = @{$column};

        push( @where,   sprintf( '%s = %s', $name, $value ) );
        push( @columns, $name );
        push( @values,  $value );
    }

    foreach my $column ( @{$content} ) {
        my ( $name, $value, $insert_value ) = @{$column};

        push( @set, sprintf( '%s = %s', $name, $value ) );
        push( @differs,
              sprintf( "CASE WHEN %s IS DISTINCT FROM %s THEN '%s' END",
                       $name, $value, $name ) );
        push( @columns, $name );
        push( @values, defined($insert_value) ? $insert_value : $value );
    }

    foreach my $column ( @{ $literals || [] } ) {
        my ( $name, $value ) = @{$column};

        push( @columns, $name );
        push( @values,  $value );
    }

    my %statement = (

        # Names the columns whose stored value differs from the file, so
        # that a conflict can say what it would change.  Empty when the
        # row still matches.
        'differs' => sprintf(
                 "SELECT array_to_string(ARRAY[%s], ', ') " .
                   'FROM %s WHERE id = ?',
                 join( ', ', @differs ), $table ),

        'update' => sprintf( 'UPDATE %s SET %s WHERE id = ?',
                             $table, join( ', ', @set ) ),

        'insert' => sprintf( 'INSERT INTO %s (%s) VALUES (%s) RETURNING id',
                             $table,
                             join( ',', @columns ),
                             join( ',', @values ) ) );

    if ( scalar(@where) ) {
        $statement{'find'} = sprintf( 'SELECT id FROM %s WHERE %s',
                                      $table, join( ' AND ', @where ) );
    }

    return \%statement;
}

# Overwrite an already-loaded row, or record what overwriting it would
# change.  $what names the row for the conflict report.
sub update_or_conflict {
    my ( $dbh, $what, $statement, $id, $content_args ) = @_;

    my ($differs) =
      $dbh->selectrow_array( $statement->{'differs'}, undef,
                             @{$content_args}, $id );

    return if !( defined($differs) && length($differs) );

    if ($opt_update) {
        $dbh->do( $statement->{'update'}, undef, @{$content_args}, $id );
    }
    else {
        push( @conflicts, sprintf( '%s: would change %s', $what, $differs ) );
    }

    return;
}

# Insert the row if it is not loaded yet, otherwise update it or record
# the conflict.  Returns its id either way.
sub upsert {
    my ( $dbh, $what, $statement, $identity_args, $content_args ) = @_;

    my ($id) = $dbh->selectrow_array( $statement->{'find'}, undef,
                                      @{$identity_args} );

    if ( !defined($id) ) {
        ($id) =
          $dbh->selectrow_array( $statement->{'insert'}, undef,
                                 @{$identity_args}, @{$content_args} );
        return $id;
    }

    update_or_conflict( $dbh, $what, $statement, $id, $content_args );

    return $id;
}

if ( !GetOptions( 'help|h'     => \$opt_help,
                  'config|c=s' => \$opt_config,
                  'file|f=s'   => \$opt_file,
                  'update|u'   => \$opt_update,
                  'dry-run|n'  => \$opt_dry_run ) )
{
    usage();
    die('Failed to parse command line options');
}
if ($opt_help) { usage(); exit 0; }

my $settings = decode_json( get_file($opt_config) );
my $study    = decode_json( get_file($opt_file) );

my $dbh = DBI->connect(sprintf( "DBI:Pg:dbname=%s;host=%s;port=%s",
				$settings->{'postgresName'},
				$settings->{'postgresHost'},
				$settings->{'postgresPort'} ),
			$settings->{'postgresUser'},
			$settings->{'postgresPass'},
			{ 'RaiseError' => 1, 'AutoCommit' => 0 } );

$dbh->do("SET search_path TO data, public");

eval {
    load_study( $dbh, $study );

    # Reported together rather than one at a time, so that a single run
    # shows everything the file would change.
    if ( scalar(@conflicts) ) {
        die( sprintf( "%d row(s) already loaded no longer match the " .
                        "metadata file:\n%s\n\nRe-run with -u/--update " .
                        "to overwrite them.\n",
                      scalar(@conflicts),
                      join( "\n", map { "    $_" } @conflicts ) ) );
    }

    if ($opt_dry_run) {
        $dbh->rollback();
        print("Dry run: everything rolled back\n");
    }
    else {
        $dbh->commit();
    }

    1;
} or do {
    my $error = $@ || 'Unknown error';
    eval { $dbh->rollback() };
    $dbh->disconnect();
    die("Load failed, nothing was written: $error");
};

$dbh->disconnect();

# Work out which study row this file describes.
#
# The study is anchored by its datasets' short-names rather than by its
# own title: a short-name is a stable slug, while the title is editable
# content.  So any dataset already in the database points us at the study
# row to update, which is what makes renaming a study just another edit.
sub resolve_study {
    my ( $dbh, $study ) = @_;

    my %seen;
    foreach my $dataset ( @{ $study->{'datasets'} } ) {
        my ($study_id) =
          $dbh->selectrow_array(
                         'SELECT study FROM datasets WHERE short_name = ?',
                         undef, $dataset->{'short-name'} );

        if ( defined($study_id) ) {
            push( @{ $seen{$study_id} }, $dataset->{'short-name'} );
        }
    }

    if ( scalar( keys(%seen) ) > 1 ) {
        die( sprintf(
                 "The datasets in this file already belong to %d " .
                   "different studies (%s); refusing to guess which " .
                   "one to update\n",
                 scalar( keys(%seen) ),
                 join( '; ',
                       map {
                           sprintf( 'study %s holds %s',
                                    $_, join( ', ', @{ $seen{$_} } ) )
                         } sort( keys(%seen) ) ) ) );
    }

    my ($study_id) = keys(%seen);
    return $study_id if defined($study_id);

    # Nothing from this file is loaded yet, so fall back to the study's
    # own natural key.  Returns undef for a genuinely new study.
    ($study_id) =
      $dbh->selectrow_array(
                  'SELECT id FROM studies WHERE title = ? AND pi_email = ?',
                  undef, @{$study}{ 'title', 'pi-email' } );

    return $study_id;
}

sub load_study {
    my ( $dbh, $study ) = @_;

    die
      if validate_required(
        $study,
        'study',
        qw( title publication-date pi-name pi-email contact-name contact-email datasets )
      );

    if ( has_data( $study, 'description' ) ) {
        $study->{'description'} = text_or_file( $study->{'description'} );
    }
    else { delete( $study->{'description'} ); }

    if ( !has_data( $study, 'ref-doi' ) ) {
        delete( $study->{'ref-doi'} );
    }

    # The study has no identity columns of its own here: it is found
    # through its datasets, so even the title is content.
    my $statement = make_statements(
        'studies',
        [],
        [ [ 'pi_name',          '?' ],
          [ 'pi_email',         '?' ],
          [ 'contact_name',     '?' ],
          [ 'contact_email',    '?' ],
          [ 'title',            '?' ],
          [ 'study_description', '?' ],
          [ 'publication_date', '?::timestamp' ],
          [ 'ref_doi',          '?' ] ] );

    # Deleted keys read back as undef, which binds as NULL -- that is what
    # makes dropping an optional field from the file clear the column.
    my @content = @{$study}{
        'pi-name',          'pi-email',
        'contact-name',     'contact-email',
        'title',            'description',
        'publication-date', 'ref-doi' };

    my $study_id = resolve_study( $dbh, $study );

    if ( defined($study_id) ) {
        update_or_conflict( $dbh,
                            sprintf( 'study "%s"', $study->{'title'} ),
                            $statement, $study_id, \@content );
    }
    else {
        ($study_id) = $dbh->selectrow_array( $statement->{'insert'},
                                             undef, @content );
    }

    foreach my $dataset ( @{ $study->{'datasets'} } ) {
        load_dataset( $dbh, $study_id, $dataset );
    }

    return;
}

sub load_dataset {
    my ( $dbh, $study_id, $dataset ) = @_;

    die
      if validate_required( $dataset, 'dataset',
          qw( short-name full-name dataset-size version sample-sets ) );

    foreach
      my $opt_key (qw( avg-seq-depth seq-type seq-tech seq-center ))
    {
        if ( !has_data( $dataset, $opt_key ) ) {
            delete( $dataset->{$opt_key} );
        }
    }

    my $statement = make_statements(
        'datasets',
        [ [ 'short_name', '?' ] ],
        [ [ 'study',         '?' ],
          [ 'full_name',     '?' ],
          [ 'avg_seq_depth', '?' ],
          [ 'seq_type',      '?' ],
          [ 'seq_tech',      '?' ],
          [ 'seq_center',    '?' ],
          [ 'dataset_size',  '?' ] ] );

    my $dataset_id =
      upsert( $dbh,
              sprintf( 'dataset %s', $dataset->{'short-name'} ),
              $statement,
              [ $dataset->{'short-name'} ],
              [ $study_id,
                @{$dataset}{
                    'full-name', 'avg-seq-depth',
                    'seq-type',  'seq-tech',
                    'seq-center', 'dataset-size' } ] );

    load_dataset_version( $dbh, $dataset, $dataset_id,
                          $dataset->{'version'} );

    foreach my $sample_set ( @{ $dataset->{'sample-sets'} } ) {
        load_sample_set( $dbh, $dataset, $dataset_id, $sample_set );
    }

    load_logotype( $dbh, $dataset, $dataset_id );

    return;
}

# dataset_versions.reference_set is a NOT NULL reference into
# data.reference_sets, which this loader never populates -- reference sets
# are loaded separately and are shared between datasets.  Resolve the
# free-text var-call-ref against the ones that exist.
sub get_reference_set {
    my ( $dbh, $var_call_ref ) = @_;

    my $rows = $dbh->selectcol_arrayref(
        'SELECT id FROM reference_sets ' .
          'WHERE reference_build = ? OR reference_name = ?',
        undef, $var_call_ref, $var_call_ref );

    if ( scalar( @{$rows} ) == 0 ) {
        die( sprintf( "No reference set matches var-call-ref '%s'; " .
                        "expected it to match reference_build or " .
                        "reference_name in data.reference_sets\n",
                      $var_call_ref ) );
    }
    if ( scalar( @{$rows} ) > 1 ) {
        die( sprintf( "var-call-ref '%s' matches %d rows in " .
                        "data.reference_sets, cannot pick one\n",
                      $var_call_ref, scalar( @{$rows} ) ) );
    }

    return $rows->[0];
}

sub load_dataset_version {
    my ( $dbh, $dataset, $dataset_id, $version ) = @_;

    die
      if validate_required( $version, 'version',
                            qw( version description terms var-call-ref ) );

    foreach my $opt_key (qw( ref-doi available-from )) {
        if ( !has_data( $version, $opt_key ) ) {
            delete( $version->{$opt_key} );
        }
    }

    $version->{'description'} = text_or_file( $version->{'description'} );
    $version->{'terms'}       = text_or_file( $version->{'terms'} );

    my $reference_set =
      get_reference_set( $dbh, $version->{'var-call-ref'} );

    # available_from is the one field an omission does not clear.  On
    # insert it falls back to the schema default of now(); on update it
    # keeps whatever is already stored, because re-running the loader must
    # not keep moving the date a dataset became available.  Comparing
    # against that same expression also keeps an omission from ever
    # counting as a conflict.
    #
    # portal_avail, file_access and beacon_access are all NOT NULL with no
    # default, and none of them has a counterpart in the metadata file, so
    # the loader supplies them.  A dataset being loaded is one meant to
    # appear, hence portal_avail; access starts restricted everywhere, and
    # opening a version up afterwards is a deliberate decision.
    #
    # All three are written on insert only.  Leaving them out of the
    # content list is what keeps a re-run from slamming a version that has
    # since been opened up back shut.
    my $statement = make_statements(
        'dataset_versions',
        [ [ 'dataset',         '?' ],
          [ 'dataset_version', '?' ] ],
        [ [ 'reference_set',       '?' ],
          [ 'dataset_description', '?' ],
          [ 'terms',               '?' ],
          [ 'available_from',
            'COALESCE(?::timestamp, available_from)',
            'COALESCE(?::timestamp, CURRENT_TIMESTAMP)' ],
          [ 'ref_doi', '?' ] ],
        [ [ 'portal_avail',  'true' ],
          [ 'file_access',   "'CONTROLLED'" ],
          [ 'beacon_access', "'CONTROLLED'" ] ] );

    my $version_id =
      upsert( $dbh,
              sprintf( 'dataset %s version %s',
                       $dataset->{'short-name'}, $version->{'version'} ),
              $statement,
              [ $dataset_id, $version->{'version'} ],
              [ $reference_set,
                @{$version}{ 'description', 'terms',
                             'available-from', 'ref-doi' } ] );

    load_dataset_files( $dbh, $dataset, $version, $version_id );

    return $version_id;
}

# Register the files released with a dataset version, so that they can be
# downloaded through the site.  Serving them is nginx's job: the backend
# only checks that the user is allowed the file and then hands over with
# X-Accel-Redirect, so all that is stored here is the name, the size and
# the URL the download button points at.
#
# Access follows the dataset version, which this loader creates with
# file_access CONTROLLED, so a newly registered file sits behind both the
# login and the access application until someone opens the version up.
#
# Files are named by their path in the metadata file and the rest is
# derived, which means the loader has to run somewhere the released files
# are readable -- the same assumption logotype already makes.
sub load_dataset_files {
    my ( $dbh, $dataset, $version, $version_id ) = @_;

    return if !exists( $version->{'files'} );

    if ( ref( $version->{'files'} ) ne 'ARRAY' ) {
        die( sprintf( "Dataset %s version %s: files must be a list of " .
                        "paths\n",
                      $dataset->{'short-name'}, $version->{'version'} ) );
    }

    # uri is the href the download button uses, and the last part of it is
    # what the download handler matches against basename.  It is also the
    # one column of this table the schema makes UNIQUE, so it serves as
    # the identity here.
    my $statement =
      make_statements( 'dataset_files',
                       [ [ 'dataset_version', '?' ],
                         [ 'uri',             '?' ] ],
                       [ [ 'basename',  '?' ],
                         [ 'file_size', '?' ] ] );

    foreach my $path ( @{ $version->{'files'} } ) {
        if ( !( looks_like_filename($path) && -f $path ) ) {
            die( sprintf( "Dataset %s version %s lists a file that is " .
                            "not readable: '%s'\n",
                          $dataset->{'short-name'},
                          $version->{'version'}, $path ) );
        }

        my $basename  = basename($path);
        my $file_size = -s $path;
        my $uri       = sprintf( '/release/%s/versions/%s/%s',
                                 $dataset->{'short-name'},
                                 $version->{'version'}, $basename );

        upsert( $dbh,
                sprintf( 'dataset %s version %s file %s',
                         $dataset->{'short-name'},
                         $version->{'version'}, $basename ),
                $statement,
                [ $version_id, $uri ],
                [ $basename, $file_size ] );
    }

    return;
}

sub load_sample_set {
    my ( $dbh, $dataset, $dataset_id, $sample_set ) = @_;

    die
      if validate_required( $sample_set, 'sample-set',
                           qw( collection sample-size phenotype ) );

    if ( !has_data( $sample_set, 'ethnicity' ) ) {
        delete( $sample_set->{'ethnicity'} );
    }

    # Collections are keyed on their name alone and are shared between
    # datasets, so correcting an ethnicity here corrects it everywhere
    # that collection is used.
    my $collection_statement =
      make_statements( 'collections',
                       [ [ 'study_name', '?' ] ],
                       [ [ 'ethnicity',  '?' ] ] );

    my $collection_id =
      upsert( $dbh,
              sprintf( 'collection %s', $sample_set->{'collection'} ),
              $collection_statement,
              [ $sample_set->{'collection'} ],
              [ $sample_set->{'ethnicity'} ] );

    my $statement =
      make_statements( 'sample_sets',
                       [ [ 'dataset',    '?' ],
                         [ 'collection', '?' ] ],
                       [ [ 'sample_size', '?' ],
                         [ 'phenotype',   '?' ] ] );

    return upsert(
             $dbh,
             sprintf( 'dataset %s sample set %s',
                      $dataset->{'short-name'},
                      $sample_set->{'collection'} ),
             $statement,
             [ $dataset_id, $collection_id ],
             [ @{$sample_set}{ 'sample-size', 'phenotype' } ] );
}

# Logos go their own way rather than through make_statements: bytes is
# bytea, so every statement touching it needs an explicit parameter type.
# Bound as an ordinary placeholder the image would be sent as text and
# mangled.
sub load_logotype {
    my ( $dbh, $dataset, $dataset_id ) = @_;

    # Dropping logotype from the file leaves the stored logo alone; it is
    # a row rather than a column, and the loader never deletes rows.
    return if !has_data( $dataset, 'logotype' );

    # Naming a logo that is not there is a mistake, not a way of skipping
    # one.  These paths are relative, so without this the usual symptom is
    # running from the wrong directory and having every logo silently not
    # load while the run still reports success.
    my $logotype = $dataset->{'logotype'};
    if ( !( looks_like_filename($logotype) && -f $logotype ) ) {
        die( sprintf( "Dataset %s gives a logotype that is not a " .
                        "readable file: '%s'\n",
                      $dataset->{'short-name'}, $logotype ) );
    }

    my $mt   = MIME::Types->new();
    my $type = $mt->mimeTypeOf($logotype);
    if ( !defined($type) ) {
        die( sprintf( "Cannot work out the media type of the logotype " .
                        "for dataset %s from its name: '%s'\n",
                      $dataset->{'short-name'}, $logotype ) );
    }

    my $mimetype = $type->type();
    my $bytes    = get_file( $logotype, 1 );

    my ($logo_id) =
      $dbh->selectrow_array( 'SELECT id FROM dataset_logos ' .
                               'WHERE dataset = ?',
                             undef, $dataset_id );

    if ( !defined($logo_id) ) {
        my $sth = $dbh->prepare( 'INSERT INTO dataset_logos ' .
                                   '(dataset,mimetype,bytes) ' .
                                   'VALUES (?,?,?)' );
        $sth->bind_param( 1, $dataset_id );
        $sth->bind_param( 2, $mimetype );
        $sth->bind_param( 3, $bytes, { 'pg_type' => PG_BYTEA } );
        $sth->execute();

        return;
    }

    my $sth = $dbh->prepare(
        "SELECT array_to_string(ARRAY[" .
          "CASE WHEN mimetype IS DISTINCT FROM ? THEN 'mimetype' END, " .
          "CASE WHEN bytes IS DISTINCT FROM ? THEN 'bytes' END], ', ') " .
          'FROM dataset_logos WHERE id = ?' );
    $sth->bind_param( 1, $mimetype );
    $sth->bind_param( 2, $bytes, { 'pg_type' => PG_BYTEA } );
    $sth->bind_param( 3, $logo_id );
    $sth->execute();

    my ($differs) = $sth->fetchrow_array();
    return if !( defined($differs) && length($differs) );

    if ( !$opt_update ) {
        push( @conflicts,
              sprintf( 'dataset %s logotype: would change %s',
                       $dataset->{'short-name'}, $differs ) );
        return;
    }

    $sth = $dbh->prepare( 'UPDATE dataset_logos ' .
                            'SET mimetype = ?, bytes = ? WHERE id = ?' );
    $sth->bind_param( 1, $mimetype );
    $sth->bind_param( 2, $bytes, { 'pg_type' => PG_BYTEA } );
    $sth->bind_param( 3, $logo_id );
    $sth->execute();

    return;
}
