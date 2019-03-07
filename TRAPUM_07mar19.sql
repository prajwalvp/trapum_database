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
DROP TABLE IF EXISTS `Pointings`;
DROP TABLE IF EXISTS `Beamformer_Configuration`;
DROP TABLE IF EXISTS `Projects`;
DROP TABLE IF EXISTS `Processings`;
DROP TABLE IF EXISTS `Pipelines`;
DROP TABLE IF EXISTS `Data_Products`;
DROP TABLE IF EXISTS `Beams`;
DROP TABLE IF EXISTS `Processing_Pivot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Targets` (
  `target_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "unqiue ID of target",
  `project_id` int(11) unsigned NOT NULL COMMENT "unique project name identifer",
  `source_name` text DEFAULT NULL COMMENT "Name of source",
  `ra` float(10) NOT NULL COMMENT "Right Ascension hhmmss- need not be too accurate",
  `dec` float(10) NOT NULL COMMENT "Declination ddmmss - need not be too accurate",  
  `region` text NOT NULL COMMENT "Name of specific region of sky (if valid) e.g. globular cluster",
  `semi_major_axis` float NOT NULL COMMENT "length of semi major axis of elliptic target region",
  `semi_minor_axis` float NOT NULL COMMENT "length of semi minor axis of elliptic target region",
  `position_angle` float  NOT NULL COMMENT "angle of source system with respect to plane of sky; edge on is 90 deg",
  `metadata` text DEFAULT NULL COMMENT "some extra parameters if any",  
  `notes` text NOT NULL COMMENT "useful points to be noted",
--  INDEX(`ra`,`dec`,`target_id`), 
  PRIMARY KEY (`target_id`),
  FOREIGN KEY (`project_id`) REFERENCES Projects(`project_id`) ON UPDATE CASCADE 
  
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Beamformer_Configuration`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Beamformer_Configuration`(
  `bf_config_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "beamformer configuration id",
  `centre_frequency` float(10) DEFAULT NULL,
  `bandwidth` float(10) DEFAULT NULL,
  `nchans` int(10) DEFAULT NULL,
  `tsamp` float(10) DEFAULT NULL COMMENT "",
  `receiver` text DEFAULT NULL COMMENT "Receiver used",
  `metadata` text DEFAULT NULL COMMENT "info about coherent and incoherent config",
--   INDEX (`bf_config_id`),
  PRIMARY KEY (`bf_config_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;



 
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Projects`(
  `project_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "Project ID",
  `Name` text DEFAULT NULL,
  `notes` text NOT NULL COMMENT "useful points to be noted",
--   INDEX (`project_id`),
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;



/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Processings` (
  `processing_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "unique ID of processing",
  `pipeline_id` int(11) unsigned NOT NULL COMMENT "unique ID of pipeline through which data is running",
  `hardware_id` int(11) unsigned DEFAULT NULL COMMENT "unique hardware iderntifier",
  `submit_time` float(10) NOT NULL COMMENT "time stamp of submitting job",
  `start_time` float(10) DEFAULT NULL COMMENT "start time of process",
  `end_time` float(10) DEFAULT NULL COMMENT "End time of process",
  `process_status` tinyint(1) DEFAULT NULL COMMENT "status of the process - done , in progress, intermediate values produced.. i.e. multiple states",
  `metadata` text DEFAULT NULL COMMENT "some extra parameters if any",  
  `notes` text NOT NULL COMMENT "useful points to be noted",
  PRIMARY KEY(`processing_id`),
  FOREIGN KEY (`pipeline_id`) REFERENCES Pipelines(`pipeline_id`) ON UPDATE CASCADE,
  FOREIGN KEY (`hardware_id`) REFERENCES Hardwares(`hardware_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Pipelines`(
  `pipeline_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "Pipeline ID",
  `hash` text NOT NULL,
  `name` text DEFAULT NULL,
  `notes` text NOT NULL COMMENT "useful points to be noted",
--   INDEX (`pipeline_id`),
  PRIMARY KEY (`pipeline_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Hardwares`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Hardwares`(
  `hardware_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "Hardware ID",
  `name` text DEFAULT NULL,
  `metadata` text DEFAULT NULL,
  `notes` text NOT NULL,
--   INDEX (`hardware_id`),
  PRIMARY KEY (`hardware_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;



--
-- Table structure for table `Beams`
--

CREATE TABLE `Beams` (
  `beam_id` int(11) NOT NULL AUTO_INCREMENT COMMENT "unique beam identifier",
  `pointing_id` int(11) unsigned NOT NULL,
  `on_target` tinyint(1) unsigned NOT NULL COMMENT "Indicate on and off axis beams: 1 yes , 0 no" ,
  `ra` float(10) DEFAULT NULL COMMENT "Right Ascension hhmmss of individual beam",
  `dec` float(10) DEFAULT NULL COMMENT "Declination ddmmss of individual beam", 
  `coherent` tinyint(1) DEFAULT NULL COMMENT " Coherent or incoherent beam", 
--  INDEX (`ra`,`dec`,`beam_id`),
  PRIMARY KEY (`beam_id`),
  FOREIGN KEY (`pointing_id`) REFERENCES Pointings(`pointing_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



--
-- Table structure for table `Derivative Products`
--
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

CREATE TABLE `Data_Products` (
  `dp_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "unique derivative products ID",
  `pointing_id` int(11) unsigned NOT NULL,
  `beam_id` int(11) NOT NULL COMMENT "beam identifer",
  `processing_id` int(11) DEFAULT NULL COMMENT "unique ID of processing it created",
  `file_status` tinyint(11) unsigned NOT NULL COMMENT "check if file exists or not",
  `filepath` char(20) NOT NULL COMMENT  "path to file",
  `file_type` char(20) NOT NULL COMMENT "type of file",
  `metadata` text NOT NULL COMMENT "important points described",
  `notes` text NOT NULL COMMENT "useful points to be noted",  
   PRIMARY KEY (`dp_id`),
   FOREIGN KEY (`pointing_id`) REFERENCES Pointings(`pointing_id`) ON UPDATE CASCADE,
   FOREIGN KEY (`beam_id`) REFERENCES Beams(`beam_id`) ON UPDATE CASCADE,
--   FOREIGN KEY (`processing_id`) REFERENCES Processings(`processing_id`),    
   INDEX (`dp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1; 




--
-- Table structure for table `Pointings`
--
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

CREATE TABLE `Pointings` (
  `pointing_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "unique pointing id", 
  `target_id` int(11) unsigned NOT NULL COMMENT "pointing identifier",
  `bf_config_id` int(11) unsigned NOT NULL COMMENT "subarray identifier",
  `tobs` float DEFAULT NULL COMMENT "Observation time (s)",
  `utc_start` float NOT NULL COMMENT "MJD of start of observation",
  `sb_id` text NOT NULL COMMENT "scheduling block ID",
  `metadata` text NOT NULL COMMENT "other important details described",
  `notes` text NOT NULL COMMENT "useful points to be noted",
  PRIMARY KEY (`pointing_id`),
  FOREIGN KEY (`target_id`) REFERENCES Targets(`target_id`) ON UPDATE CASCADE,
  FOREIGN KEY (`bf_config_id`) REFERENCES Beamformer_Configuration(`bf_config_id`) ON UPDATE CASCADE
--  INDEX (`pointing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;



-- Table structure for table `Pivot`
--
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

CREATE TABLE `Processing_Pivot` (
  `processing_pivot_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT "unique pivot id",
  `dp_id` int(11) unsigned NOT NULL COMMENT "dataproduct_id",
  `processing_id` int(11) unsigned NOT NULL COMMENT "processing identifier",
--  INDEX (`processing_pivot_id`),
  PRIMARY KEY (`processing_pivot_id`),
  FOREIGN KEY (`dp_id`) REFERENCES Data_Products(`dp_id`) ON UPDATE CASCADE, 
  FOREIGN KEY (`processing_id`) REFERENCES Processings(`processing_id`) ON UPDATE CASCADE 
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

 
