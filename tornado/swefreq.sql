-- Script for creating swefreq-database and swefreq-user
-- as well as the tables. To run this file use:
-- mysql -u root -p < swefreq.sql

CREATE DATABASE `swefreq` /*!40100 DEFAULT CHARACTER SET latin1 */;
CREATE USER swefreq@localhost IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON swefreq.* TO swefreq@localhost;
FLUSH PRIVILEGES;
USE swefreq;

CREATE TABLE swefreq.users (
  `pk` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `download_count` int(11) DEFAULT '0',
  `swefreq_admin` boolean DEFAULT '0',
  `affiliation` varchar(100) DEFAULT NULL,
  `full_user` boolean DEFAULT '0',
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `country` varchar(100) DEFAULT NULL,
  `newsletter` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`pk`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE swefreq.user_log (
  `pk` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(100) DEFAULT NULL,
  `action` varchar(45) DEFAULT NULL,
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`pk`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
