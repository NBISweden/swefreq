USE swefreq;

RENAME TABLE users TO users_old;
RENAME TABLE user_log TO user_log_old;
-- leaves tables users_old and user_log_old as is when done

source swefreq.sql

INSERT INTO user
    (name, email, affiliation, country,
        create_date, is_full_user, download_count)
    SELECT username, email, affiliation, country,
           create_date, full_user, download_count
    FROM users_old;

-- since table dataset is empty, insert 1 for dataset_pk (will point to
-- SweGen dataset later).
INSERT INTO user_log
    (user_pk, dataset_pk, action, ts)
    SELECT user_pk, 1, action, ts
    FROM user JOIN user_log_old ON (user.email = user_log_old.email);

