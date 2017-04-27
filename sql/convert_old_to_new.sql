USE swefreq;

RENAME TABLE users TO users_old;
RENAME TABLE user_log TO user_log_old;
-- leaves tables users_old and user_log_old as is when done

source swefreq.sql

INSERT INTO user (name, email, affiliation, country, create_date)
SELECT username, email, affiliation, country, create_date
    FROM users_old;

-- Insert "fake" SweFreq dataset into 'dataset' table to be able
-- to refer to it with the next INSERT.  We need to fill in
-- 'dataset_access', 'dataset_file' and 'dataset_version' for this
-- dataset later.
INSERT INTO dataset (dataset_pk, name) VALUES (1, "SweGen");

INSERT INTO user_log (user_pk, dataset_pk, action, ts)
SELECT user_pk, 1, action, ts
    FROM user JOIN user_log_old ON (user.email = user_log_old.email);

INSERT INTO dataset_access (dataset_pk, user_pk)
SELECT DISTINCT dataset_pk, user_pk
    FROM user_log;

-- Fix dataset_access.wants_newsletter
UPDATE dataset_access
SET wants_newsletter = true
    WHERE user_pk IN
        ( SELECT DISTINCT user_pk
            FROM user JOIN users_old ON (user.email = users_old.email)
            WHERE users_old.newsletter = 1 );

-- Fix dataset_access.has_consented
UPDATE dataset_access
SET has_consented = true
    WHERE user_pk IN
        ( SELECT DISTINCT user_pk FROM user_log WHERE action = 'consent' );

-- Fix dataset_access.has_access
UPDATE dataset_access
SET has_access = true
    WHERE user_pk IN
        ( SELECT DISTINCT user_pk
            FROM user JOIN users_old ON (user.email = users_old.email)
            WHERE users_old.full_user = 1 );

-- Fix dataset_access.is_admin
UPDATE dataset_access
SET is_admin = true
    WHERE user_pk IN
        ( SELECT DISTINCT user_pk
            FROM user JOIN users_old ON (user.email = users_old.email)
            WHERE users_old.swefreq_admin = 1 );
