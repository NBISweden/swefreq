-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.

-- Rename user_log to user_access_log

RENAME TABLE user_log TO user_access_log;
ALTER TABLE user_access_log
    CHANGE user_log_pk
    user_access_log_pk  INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT;

DROP VIEW _user_log_summary;
CREATE OR REPLACE VIEW _user_access_log_summary AS
    SELECT MAX(user_access_log_pk) AS user_access_log_pk, user_pk,
        dataset_pk, action, MAX(ts) AS ts
    FROM user_access_log
    GROUP BY user_pk, dataset_pk, action;

CREATE OR REPLACE VIEW dataset_access_current AS
    SELECT DISTINCT
        access.*,
        TRUE AS has_access,
        request.ts AS access_requested
    FROM dataset_access AS access
    JOIN ( SELECT user_pk, dataset_pk, MAX(ts) AS ts
           FROM user_access_log WHERE action = "access_requested"
           GROUP BY user_pk, dataset_pk ) AS request
        ON access.user_pk = request.user_pk AND
           access.dataset_pk = request.dataset_pk
    WHERE (access.user_pk, access.dataset_pk) IN (
        -- gets user_pk for all users with current access
        -- from https://stackoverflow.com/a/39190423/4941495
        SELECT granted.user_pk, granted.dataset_pk
        FROM _user_access_log_summary AS granted
        LEFT JOIN _user_access_log_summary AS revoked
                ON granted.user_pk = revoked.user_pk AND
                   granted.dataset_pk = revoked.dataset_pk AND
                   revoked.action  = 'access_revoked'
        WHERE granted.action = 'access_granted' AND
            (revoked.user_pk IS NULL OR granted.ts > revoked.ts)
        GROUP BY granted.user_pk, granted.dataset_pk, granted.action
    );

CREATE OR REPLACE VIEW dataset_access_pending AS
    SELECT DISTINCT
        access.*,
        FALSE AS has_access,
        request.ts AS access_requested
    FROM dataset_access AS access
    JOIN ( SELECT user_pk, dataset_pk, MAX(ts) AS ts
           FROM user_access_log WHERE action = "access_requested"
           GROUP BY user_pk, dataset_pk ) AS request
        ON access.user_pk = request.user_pk AND
           access.dataset_pk = request.dataset_pk
    WHERE (access.user_pk, access.dataset_pk) IN (
        -- get user_pk for all users that have pending access requests
        SELECT requested.user_pk, requested.dataset_pk
        FROM _user_access_log_summary AS requested
        LEFT JOIN _user_access_log_summary AS granted
                ON requested.user_pk = granted.user_pk AND
                   requested.dataset_pk = granted.dataset_pk AND
                   granted.action  = 'access_granted'
        LEFT JOIN _user_access_log_summary AS revoked
                ON requested.user_pk = revoked.user_pk AND
                   requested.dataset_pk = revoked.dataset_pk AND
                   revoked.action  = 'access_revoked'
        WHERE requested.action = 'access_requested' AND
                (granted.user_pk IS NULL OR requested.ts > granted.ts) AND
                (revoked.user_pk IS NULL OR requested.ts > revoked.ts)
        GROUP BY requested.user_pk, requested.dataset_pk, requested.action
    );

-- TODO: Create user_consent_log
-- TODO: Create user_download_log
-- TODO: Add unique constraint on linkhash.hash
-- TODO: Remove "consent" and "download" enums from dataset_access_log
-- TODO: Remove has_concented from views
