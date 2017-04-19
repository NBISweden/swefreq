-- Script for creating swefreq-database and swefreq-user
-- as well as the tables. To run this file use:
-- mysql -u root -p < swefreq.sql

CREATE DATABASE IF NOT EXISTS swefreq /*!40100 DEFAULT CHARACTER SET latin1 */;
CREATE USER IF NOT EXISTS swefreq@localhost IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON swefreq.* TO swefreq@localhost;
FLUSH PRIVILEGES;
USE swefreq;

CREATE TABLE IF NOT EXISTS users (
  pk                INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  username          VARCHAR(100) DEFAULT NULL,
  email             VARCHAR(100) NOT NULL,
  download_count    INTEGER DEFAULT 0,
  swefreq_admin     BOOLEAN DEFAULT false,
  affiliation       VARCHAR(100) DEFAULT NULL,
  full_user         BOOLEAN DEFAULT false,
  create_date       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  country           VARCHAR(100) DEFAULT NULL,
  newsletter        TINYINT DEFAULT 0,
  UNIQUE KEY email_idx (email)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS user_log (
  pk                INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  email             VARCHAR(100) DEFAULT NULL,
  action            VARCHAR(45) DEFAULT NULL,
  ts                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
