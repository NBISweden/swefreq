#!/bin/sh

# This script is running hourly on Hertz to backup the user database.
# The cronjob belongs to user "andkaha" and is simply
#   @hourly /data/SweFreq/userdb-backup.sh >/dev/null 2>&1

PATH="/bin:/usr/bin:$PATH"
export PATH

backup_base="/data/SweFreq/userdb-backup"
backup_dir="$backup_base/$( date '+%Y-%m' )"
backup_file="$backup_dir/tornado-userdb.$( date '+%Y%m%d-%H%M%S' ).dump"

test -d "$backup_base" || exit 1

tmpbackup="$backup_base/in_progress.dump"

# Dump database, and remove the "Dump completed" comment at the end to
# be able to compare with previous dump.
lxc exec swefreq-web -- mysqldump -u swefreq swefreq |
sed '/^-- Dump completed on/d' >"$tmpbackup"

gzip --best "$tmpbackup"

if [ ! -d "$backup_dir" ] ||
   [ ! -e "$backup_base/latest.dump.gz" ] ||
   ! zcmp -s "$tmpbackup.gz" "$backup_base/latest.dump.gz"
then
    mkdir -p "$backup_dir"
    mv "$tmpbackup.gz" "$backup_file.gz"

    # Create a symbolic link to the latest backup
    ln -sf "$backup_file.gz" "$backup_base/latest.dump.gz"

    echo 'New backup made'
else
    rm -f "$tmpbackup.gz"
    echo 'No new backup needed'
fi
