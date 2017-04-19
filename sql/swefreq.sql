-- Script for creating swefreq-database and swefreq-user
-- as well as the tables. To run this file use:
-- mysql -u root -p < swefreq.sql

CREATE DATABASE IF NOT EXISTS swefreq /*!40100 DEFAULT CHARACTER SET latin1 */;
CREATE USER IF NOT EXISTS swefreq@localhost IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON swefreq.* TO swefreq@localhost;
FLUSH PRIVILEGES;
USE swefreq;

CREATE TABLE IF NOT EXISTS user (
    user_pk         INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username        VARCHAR(100)    DEFAULT NULL,
    email           VARCHAR(100)    NOT NULL,
    download_count  INTEGER         DEFAULT 0,
    affiliation     VARCHAR(100)    DEFAULT NULL,
    full_user       BOOLEAN         DEFAULT false,
    create_date     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    country         VARCHAR(100)    DEFAULT NULL,
    UNIQUE KEY email_idx (email)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS dataset (
    dataset_pk      INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    browser_uri     VARCHAR(200)    NOT NULL,
    beacon_uri      VARCHAR(200)    NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS user_log (
    user_log_pk     INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_pk         INTEGER         NOT NULL,
    dataset_pk      INTEGER         NOT NULL,
    action          VARCHAR(45)     DEFAULT NULL,
    ts              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS dataset_access (
    dataset_access_pk   INTEGER     NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_pk             INTEGER     NOT NULL,
    newsletter          BOOLEAN     DEFAULT false,
    admin               BOOLEAN     DEFAULT false,
    consented           BOOLEAN     DEFAULT false
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
