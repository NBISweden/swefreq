USE swefreq;

RENAME TABLE users TO users_old;
RENAME TABLE user_log TO user_log_old;
-- leaves tables users_old and user_log_old as is when done

source swefreq.sql

INSERT INTO user
    (name, email, affiliation, country, create_date)
    SELECT username, email, affiliation, country, create_date
    FROM users_old;

-- Insert "fake" SweFreq dataset into 'dataset' table to be able
-- to refer to it with the next INSERT.  We need to fill in
-- 'dataset_access', 'dataset_file' and 'dataset_version' for this
-- dataset later.
INSERT INTO dataset (dataset_pk) VALUES (1);

INSERT INTO user_log
    (user_pk, dataset_pk, action, ts)
    SELECT user_pk, 1, action, ts
    FROM user JOIN user_log_old ON (user.email = user_log_old.email);
