# ************************************************************
# Sequel Pro SQL dump
# Version 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: 127.0.0.1 (MySQL 5.6.27)
# Database: vista_tv_bbc
# Generation Time: 2017-02-26 12:23:13 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table categories
# ------------------------------------------------------------

CREATE TABLE `categories` (
  `cat_id` varchar(255) CHARACTER SET latin1 NOT NULL,
  `cat_type` text CHARACTER SET latin1,
  `cat_name` text CHARACTER SET latin1,
  `cat_broader` text CHARACTER SET latin1,
  PRIMARY KEY (`cat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table categories_annotations
# ------------------------------------------------------------

CREATE TABLE `categories_annotations` (
  `cat_id` varchar(255) CHARACTER SET latin1 NOT NULL,
  `annotation_name` text CHARACTER SET latin1,
  `annotation_value` text CHARACTER SET latin1,
  `annotation_URIs` text CHARACTER SET latin1,
  PRIMARY KEY (`cat_id`),
  KEY `cat_id` (`cat_id`),
  CONSTRAINT `categories_annotations_ibfk_1` FOREIGN KEY (`cat_id`) REFERENCES `categories` (`cat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table channels
# ------------------------------------------------------------

CREATE TABLE `channels` (
  `channel_id` varchar(100) CHARACTER SET latin1 NOT NULL,
  `channel_name` text CHARACTER SET latin1,
  `channel_image` text CHARACTER SET latin1,
  `channel_common_name` text CHARACTER SET latin1,
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table credits
# ------------------------------------------------------------

CREATE TABLE `credits` (
  `credit_id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `credit_name` text CHARACTER SET latin1,
  `gender` text,
  `birthdate` text,
  PRIMARY KEY (`credit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table credits_annotations
# ------------------------------------------------------------

CREATE TABLE `credits_annotations` (
  `credit_id` mediumint(9) NOT NULL,
  `annotation_name` varchar(255) NOT NULL DEFAULT '',
  `annotation_value` varchar(255) NOT NULL DEFAULT '',
  `annotation_URIs` text,
  PRIMARY KEY (`credit_id`,`annotation_name`,`annotation_value`),
  CONSTRAINT `credits_annotations_ibfk_1` FOREIGN KEY (`credit_id`) REFERENCES `credits` (`credit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table epg
# ------------------------------------------------------------

CREATE TABLE `epg` (
  `pid` varchar(100) CHARACTER SET latin1 NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `end_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `channel_id` varchar(100) CHARACTER SET latin1 NOT NULL DEFAULT '',
  PRIMARY KEY (`pid`,`start_time`,`channel_id`),
  KEY `epg2_ibfk_1` (`channel_id`),
  KEY `end_time` (`end_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table epg_status
# ------------------------------------------------------------

CREATE TABLE `epg_status` (
  `day` date NOT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`day`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table programme_annotations
# ------------------------------------------------------------

CREATE TABLE `programme_annotations` (
  `pid` varchar(100) CHARACTER SET latin1 NOT NULL,
  `annotation_name` varchar(255) CHARACTER SET latin1 NOT NULL DEFAULT '',
  `annotation_value` varchar(255) CHARACTER SET latin1 NOT NULL DEFAULT '',
  `annotation_URIs` text CHARACTER SET latin1,
  `annotation_analysis` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`pid`,`annotation_name`,`annotation_value`),
  KEY `pid` (`pid`),
  CONSTRAINT `programme_annotations_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `programme_info` (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table programme_categories
# ------------------------------------------------------------

CREATE TABLE `programme_categories` (
  `pid` varchar(100) CHARACTER SET latin1 NOT NULL,
  `cat_id` varchar(255) CHARACTER SET latin1 NOT NULL,
  PRIMARY KEY (`pid`,`cat_id`),
  KEY `cat_id` (`cat_id`),
  CONSTRAINT `programme_categories_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `programme_info` (`pid`),
  CONSTRAINT `programme_categories_ibfk_2` FOREIGN KEY (`cat_id`) REFERENCES `categories` (`cat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table programme_credits
# ------------------------------------------------------------

CREATE TABLE `programme_credits` (
  `pid` varchar(100) CHARACTER SET latin1 NOT NULL,
  `credit_id` mediumint(9) NOT NULL,
  `role` text CHARACTER SET latin1,
  PRIMARY KEY (`pid`,`credit_id`),
  KEY `credit_id` (`credit_id`),
  CONSTRAINT `programme_credits_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `programme_info` (`pid`),
  CONSTRAINT `programme_credits_ibfk_2` FOREIGN KEY (`credit_id`) REFERENCES `credits` (`credit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table programme_info
# ------------------------------------------------------------

CREATE TABLE `programme_info` (
  `pid` varchar(100) CHARACTER SET latin1 NOT NULL,
  `title` text CHARACTER SET latin1,
  `episode_title` text CHARACTER SET latin1,
  `short_synopsis` text CHARACTER SET latin1,
  `medium_synopsis` text CHARACTER SET latin1,
  `long_synopsis` text CHARACTER SET latin1,
  `main_programme_pid` varchar(100) CHARACTER SET latin1 DEFAULT NULL,
  `language` text,
  `Release_Date` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
