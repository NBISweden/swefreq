USE swefreq;

RENAME TABLE users TO users_old;
RENAME TABLE user_log TO user_log_old;

source swefreq.sql

INSERT INTO user
    (name, email, affiliation, country,
        create_date, is_full_user, download_count)
    SELECT username, email, affiliation, country,
           create_date, full_user, download_count
    FROM users_old;

INSERT INTO user_log
    (user_pk, dataset_pk, action, ts)
    SELECT user_pk, 1, action, ts
    FROM user JOIN user_log_old ON (user.email = user_log_old.email);

-- leaves tables users_old and user_log_old as is
