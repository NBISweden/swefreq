The following refers to what's present in "/data/SweFreq" on Hertz:

    The "userdb-backup" directory contains the gzip compressed database
    dumps from the "swefreq" MySQL database running in the "swefreq-web"
    container.  The directory is divided into sub-directories by month.

    The dumps are made once every hour through a cronjob belonging to
    user "andkaha".  The cronjob runs the script "userdb-backup.sh"
    which is present in this directory.  The script takes no arguments.

    No cleanup of old backups is currently performed.

    If no changes to the database are detected, no backup will be
    stored.  At least one backup will be stored every month regardless
    of whether the database has been modified or not.

    There is a symbolic link from "userdb-backup/latest.dump.gz" to the
    most recently stored backup.

    /Andreas, 2017-04-28
