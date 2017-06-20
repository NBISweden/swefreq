-- Script for creating the swefreq tables. To run this file use:
-- mysql < swefreq.sql
-- Possibly with mysql credentials


CREATE TABLE IF NOT EXISTS user (
    user_pk             INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name                VARCHAR(100)    DEFAULT NULL,
    email               VARCHAR(100)    NOT NULL,
    affiliation         VARCHAR(100)    DEFAULT NULL,
    country             VARCHAR(100)    DEFAULT NULL,
    CONSTRAINT UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS dataset (
    dataset_pk          INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    short_name          VARCHAR(50)     NOT NULL,
    full_name           VARCHAR(100)    NOT NULL,
    browser_uri         VARCHAR(200)    DEFAULT NULL,
    beacon_uri          VARCHAR(200)    DEFAULT NULL,
    CONSTRAINT UNIQUE (short_name)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS user_log (
    user_log_pk         INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_pk             INTEGER         NOT NULL,
    dataset_pk          INTEGER         NOT NULL,
    action  ENUM ('consent','download',
                  'access_requested','access_granted','access_revoked')
                                        DEFAULT NULL,
    ts                  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FOREIGN KEY (user_pk)    REFERENCES user(user_pk),
    CONSTRAINT FOREIGN KEY (dataset_pk) REFERENCES dataset(dataset_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS dataset_access (
    dataset_access_pk   INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    dataset_pk          INTEGER         NOT NULL,
    user_pk             INTEGER         NOT NULL,
    wants_newsletter    BOOLEAN         DEFAULT false,
    is_admin            BOOLEAN         DEFAULT false,
    has_consented       BOOLEAN         DEFAULT false,
    has_access          BOOLEAN         DEFAULT false,
    CONSTRAINT UNIQUE (dataset_pk, user_pk),
    CONSTRAINT FOREIGN KEY (dataset_pk) REFERENCES dataset(dataset_pk),
    CONSTRAINT FOREIGN KEY (user_pk)    REFERENCES user(user_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS dataset_version (
    dataset_version_pk  INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    dataset_pk          INTEGER         NOT NULL,
    version             VARCHAR(20)     NOT NULL,
    ts                  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    is_current          BOOLEAN         DEFAULT true,
    description         TEXT            NOT NULL,
    terms               TEXT            NOT NULL,
    CONSTRAINT FOREIGN KEY (dataset_pk) REFERENCES dataset(dataset_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS dataset_file (
    dataset_file_pk     INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    dataset_version_pk  INTEGER         NOT NULL,
    name                VARCHAR(100)    NOT NULL,
    uri                 VARCHAR(200)    NOT NULL,
    CONSTRAINT FOREIGN KEY (dataset_version_pk)
        REFERENCES dataset_version(dataset_version_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS dataset_logo (
    dataset_logo_pk     INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    dataset_pk          INTEGER         NOT NULL,
    mimetype            VARCHAR(50),
    data                BLOB,
    CONSTRAINT FOREIGN KEY (dataset_pk) REFERENCES dataset(dataset_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
