/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Beams`
--

DROP TABLE IF EXISTS `Targets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Targets` (
  `target_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "unqiue ID of target",
  `project_id` int(11) unsigned NOT NULL COMMENT "unique project name identifer",
  `subarray_id` int(11) unsigned NOT NULL,
  `source_name` text DEFAULT NULL COMMENT "Name of source",
  `ra` float(10) DEFAULT NULL COMMENT "Right Ascension hhmmss- need not be too accurate",
  `dec` float(10) DEFAULT NULL COMMENT "Declination ddmmss - need not be too accurate",  
  `region` text NOT NULL COMMENT "Name of specific region of sky (if valid) e.g. globular cluster",
  `semi_major_axis` float NOT NULL COMMENT "length of semi major axis of elliptic target region",
  `semi_minor_axis` float NOT NULL COMMENT "length of semi minor axis of elliptic target region",
  `position_angle` float  NOT NULL COMMENT "angle of source system with respect to plane of sky; edge on is 90 deg",
  `metadata` text DEFAULT NULL COMMENT "some extra parameters if any",  
  `notes` text NOT NULL COMMENT "useful points to be noted",
  INDEX(`ra`,`dec`,`target_id`), 
  PRIMARY KEY (`target_id`)
  
) ENGINE=InnoDB AUTO_INCREMENT=752653 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Processings`
--

DROP TABLE IF EXISTS `Subarray`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Subarray` (
  `subarray_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "Sub array id",
  `centre_frequency(MHz)` float(10) DEFAULT NULL,
  `bandwidth(MHz)` float(10) DEFAULT NULL,
   INDEX (`subarray_id`),
  PRIMARY KEY (`subarray_id`)
) ENGINE=InnoDB AUTO_INCREMENT=752653 DEFAULT CHARSET=latin1;
 


DROP TABLE IF EXISTS `Projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Projects`(
  `project_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "Project ID",
  `Name` text DEFAULT NULL,
  `notes` text NOT NULL COMMENT "useful points to be noted",
   INDEX (`project_id`),
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=752653 DEFAULT CHARSET=latin1;



DROP TABLE IF EXISTS `Processings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Processings` (
  `processing_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "unique ID of processing",
  `observation_id` int(11) NOT NULL COMMENT "unique observation identifier",
  `pipeline_id` int(11) unsigned NOT NULL COMMENT "unique ID of pipeline through which data is running",
  `hardware_id` int(11) unsigned DEFAULT NULL COMMENT "unqiue hardware iderntifier ",
  `dp_id` int(11) unsigned NOT NULL COMMENT "unique derivative products ID",
  `submit_time` datetime NOT NULL COMMENT "time stamp of submitting job" ,
  `start_time` datetime DEFAULT NULL COMMENT "start time of process",
  `end_time` datetime DEFAULT NULL COMMENT "End time of process",
  `process_status` tinyint(1) DEFAULT NULL COMMENT "status of the process - done , in progress, intermediate values produced.. i.e. multiple states",
  `metadata` text DEFAULT NULL COMMENT "some extra parameters if any",  
  `notes` text NOT NULL COMMENT "useful points to be noted",
   INDEX (`processing_id`),
  PRIMARY KEY (`processing_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1702925 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


DROP TABLE IF EXISTS `Pipelines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Pipelines`(
  `pipeline_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "Pipeline ID",
  `hash` text NOT NULL,
  `name` text DEFAULT NULL,
  `notes` text NOT NULL COMMENT "useful points to be noted",
   INDEX (`pipeline_id`),
  PRIMARY KEY (`pipeline_id`)
) ENGINE=InnoDB AUTO_INCREMENT=752653 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Hardwares`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Hardwares`(
  `hardware_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "Hardware ID",
  `name` text DEFAULT NULL,
  `notes` text NOT NULL COMMENT "useful points to be noted",
   INDEX (`hardware_id`),
  PRIMARY KEY (`hardware_id`)
) ENGINE=InnoDB AUTO_INCREMENT=752653 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Observations`;

--
-- Table structure for table `Observations`
--

CREATE TABLE `Observations` (
  `observation_id` int(11) NOT NULL AUTO_INCREMENT COMMENT "unique observation identifier",
  `target_id` int(11) unsigned NOT NULL COMMENT "pointing identifier",
  `project_id` int(11) unsigned NOT NULL COMMENT "unique project name identifer",
  `subarray_id` int(11) unsigned NOT NULL COMMENT "Sub array used" ,
  `filename` char(20) NOT NULL COMMENT "name of data file written",
  `filetype` char(20) NOT NULL COMMENT "Type of data file", 
  `ra` float(10) DEFAULT NULL COMMENT "Right Ascension hhmmss of individual beam",
  `dec` float(10) DEFAULT NULL COMMENT "Declination ddmmss of individual beam",  
  `tobs` float NOT NULL COMMENT "Observation time (s)",
  `utc_start` float NOT NULL COMMENT "MJD of start of observation",
  `sb_id` text NOT NULL COMMENT "scheduling block ID",
  `metadata` text NOT NULL COMMENT "other important details described",
  `notes` text NOT NULL COMMENT "useful points to be noted",
  INDEX (`ra`,`dec`,`observation_id`),
  PRIMARY KEY (`observation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `DataProducts`;

--
-- Table structure for table `Derivative Products`
--
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

CREATE TABLE `Data_Products` (
  `dp_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "unique derivative products ID",
  `observation_id` int(11) NOT NULL COMMENT "observation identifier",
  `parent_id` int(11) NOT NULL COMMENT "observation identifier",
  `processing_id` int(11) unsigned NULL COMMENT "unique ID of processing it created",
  `file_status` tinyint(11) unsigned NOT NULL COMMENT "check if file exists or not",
  `filepath` char(20) NOT NULL COMMENT  "path to file",
  `file_type` char(20) NOT NULL COMMENT "type of file",
  `metadata` text NOT NULL COMMENT "important points described",
  `notes` text NOT NULL COMMENT "useful points to be noted",  
   PRIMARY KEY (`dp_id`),
   INDEX (`dp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1; 
/*!40101 SET character_set_client = @saved_cs_client */;


