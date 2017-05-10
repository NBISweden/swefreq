The following refers to what's present in "/data/SweFreq" on Hertz:

------------------------------------------------------------------------

    The "userdb-backup" directory contains the gzip compressed database
    dumps from the "swefreq" MySQL database running in the "swefreq-web"
    container.  The directory is divided into sub-directories by month.

    The dumps are made once every hour through a cronjob belonging to
    user "andkaha".  The cronjob runs the script "backup.sh" which is
    present in this directory.  The script takes no arguments.

    No cleanup of old backups is currently performed.

    If no changes to the database are detected, no backup will be
    stored.  At least one backup will be stored every month regardless
    of whether the database has been modified or not.

    There is a symbolic link from "userdb-backup/latest.dump.gz" to the
    most recently stored backup.

------------------------------------------------------------------------

    The "data-backup/release" is a mirror of the
    "/opt/swefreq/tornado/release" directory from the live "swefreq-web"
    container.  It contains all publically available datasets (past
    and present) as tar archives (this is how they are distributed to
    users).

    Thes same "backup.sh" script as above will ensure that this data is
    kept up to date.

------------------------------------------------------------------------

    The other directories in "data-backup" contains manually saved files
    that are needed in case the MongDB database needs to be re-populated
    from scratch.

/Andreas, 2017-05-09
