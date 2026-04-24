-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: 127.0.0.1    Database: chit_fund_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_adminprofile`
--

DROP TABLE IF EXISTS `accounts_adminprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_adminprofile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `employee_id` varchar(20) DEFAULT NULL,
  `department` varchar(100) NOT NULL,
  `branch_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  KEY `accounts_adminprofile_branch_id_988f9e61_fk_branches_branch_id` (`branch_id`),
  CONSTRAINT `accounts_adminprofile_branch_id_988f9e61_fk_branches_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `branches_branch` (`id`),
  CONSTRAINT `accounts_adminprofile_user_id_bb9bff2e_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_adminprofile`
--

LOCK TABLES `accounts_adminprofile` WRITE;
/*!40000 ALTER TABLE `accounts_adminprofile` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_adminprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_newslettersubscription`
--

DROP TABLE IF EXISTS `accounts_newslettersubscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_newslettersubscription` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_newslettersubscription`
--

LOCK TABLES `accounts_newslettersubscription` WRITE;
/*!40000 ALTER TABLE `accounts_newslettersubscription` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_newslettersubscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_staffprofile`
--

DROP TABLE IF EXISTS `accounts_staffprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_staffprofile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `employee_id` varchar(20) DEFAULT NULL,
  `shift_timing` varchar(50) NOT NULL,
  `branch_id` bigint(20) DEFAULT NULL,
  `reporting_to_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  KEY `accounts_staffprofile_branch_id_a89d7765_fk_branches_branch_id` (`branch_id`),
  KEY `accounts_staffprofil_reporting_to_id_aac58aa7_fk_accounts_` (`reporting_to_id`),
  CONSTRAINT `accounts_staffprofil_reporting_to_id_aac58aa7_fk_accounts_` FOREIGN KEY (`reporting_to_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `accounts_staffprofile_branch_id_a89d7765_fk_branches_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `branches_branch` (`id`),
  CONSTRAINT `accounts_staffprofile_user_id_1ed1af60_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_staffprofile`
--

LOCK TABLES `accounts_staffprofile` WRITE;
/*!40000 ALTER TABLE `accounts_staffprofile` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_staffprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_superadminprofile`
--

DROP TABLE IF EXISTS `accounts_superadminprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_superadminprofile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `designation` varchar(100) NOT NULL,
  `last_login_ip` char(39) DEFAULT NULL,
  `access_level` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `accounts_superadminprofile_user_id_17db1475_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_superadminprofile`
--

LOCK TABLES `accounts_superadminprofile` WRITE;
/*!40000 ALTER TABLE `accounts_superadminprofile` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_superadminprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user`
--

DROP TABLE IF EXISTS `accounts_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) NOT NULL,
  `profile_picture` varchar(100) DEFAULT NULL,
  `auction_alerts` tinyint(1) NOT NULL,
  `email_notifications` tinyint(1) NOT NULL,
  `language` varchar(50) NOT NULL,
  `payment_reminders` tinyint(1) NOT NULL,
  `otp` varchar(6) DEFAULT NULL,
  `otp_created_at` datetime(6) DEFAULT NULL,
  `two_factor_enabled` tinyint(1) NOT NULL,
  `two_factor_secret` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user`
--

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` VALUES (1,'admin123','2026-04-22 09:58:05.364464',1,'admin','CF','Admin','admin@gmail.com',1,1,'2026-04-08 10:46:08.743249','SUPERADMIN','profiles/3d6a6444-d6b4-46b9-943d-ef404c361e21-1_all_1030.jpg',1,1,'English',1,NULL,NULL,0,'UHZRQQWGKOO4XIVKD3OBDFHR534EJXU5'),(2,'123456','2026-04-22 05:23:24.400147',0,'roki','','','',0,1,'2026-04-08 11:46:59.751913','CUSTOMER','',1,1,'English',1,NULL,NULL,0,NULL),(3,'chitfund123','2026-04-17 12:43:13.174081',0,'mani','Mani','Mani','mani@gmail.com',0,1,'2026-04-08 11:54:33.679691','STAFF','',1,1,'English',1,NULL,NULL,0,NULL),(4,'123456','2026-04-10 05:19:01.680636',0,'jessica','','','',0,1,'2026-04-09 10:47:39.580034','CUSTOMER','',1,1,'English',1,NULL,NULL,0,NULL),(5,'123456','2026-04-21 06:07:37.586252',0,'anantha','Anantha','Kumar G','anantha@gmail.com',0,1,'2026-04-10 05:42:52.159633','ADMIN','',1,1,'English',1,NULL,NULL,0,'TXIEC6RJUUPRTNPMKFCHKFXIDCB5GY57'),(6,'9876543210','2026-04-16 07:27:21.138731',0,'9876543210','vicky','','',0,1,'2026-04-15 10:11:26.456568','CUSTOMER','',1,1,'English',1,NULL,NULL,0,NULL),(7,'Varshini87','2026-04-20 05:19:43.538399',0,'varshini','Varshini','Varshini','krishnanibm05@gmail.com',0,1,'2026-04-15 12:27:20.250195','CUSTOMER','',1,1,'English',1,NULL,NULL,0,NULL),(8,'vicky@123','2026-04-20 12:54:28.833732',0,'vicky','','','',0,1,'2026-04-20 12:53:45.791053','CUSTOMER','',1,1,'English',1,NULL,NULL,0,NULL);
/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_groups`
--

DROP TABLE IF EXISTS `accounts_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_groups`
--

LOCK TABLES `accounts_user_groups` WRITE;
/*!40000 ALTER TABLE `accounts_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_user_permissions`
--

DROP TABLE IF EXISTS `accounts_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_user_permissions`
--

LOCK TABLES `accounts_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auctions_auction`
--

DROP TABLE IF EXISTS `auctions_auction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auctions_auction` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `month_number` int(11) NOT NULL,
  `auction_date` date NOT NULL,
  `bid_amount` decimal(12,2) NOT NULL,
  `payout_amount` decimal(12,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `chit_group_id` bigint(20) NOT NULL,
  `winner_id` bigint(20) NOT NULL,
  `dividend_per_member` decimal(12,2) NOT NULL,
  `foreman_commission` decimal(12,2) NOT NULL,
  `total_dividend` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auctions_auction_chit_group_id_month_number_4b601b5f_uniq` (`chit_group_id`,`month_number`),
  KEY `auctions_auction_winner_id_7ff56637_fk_members_member_id` (`winner_id`),
  CONSTRAINT `auctions_auction_chit_group_id_f4551abd_fk_chits_chitgroup_id` FOREIGN KEY (`chit_group_id`) REFERENCES `chits_chitgroup` (`id`),
  CONSTRAINT `auctions_auction_winner_id_7ff56637_fk_members_member_id` FOREIGN KEY (`winner_id`) REFERENCES `members_member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auctions_auction`
--

LOCK TABLES `auctions_auction` WRITE;
/*!40000 ALTER TABLE `auctions_auction` DISABLE KEYS */;
INSERT INTO `auctions_auction` VALUES (1,1,'2026-04-10',5000.00,18750.00,'2026-04-10 06:05:20.843470',1,1,2500.00,1250.00,5000.00);
/*!40000 ALTER TABLE `auctions_auction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auctions_guarantor`
--

DROP TABLE IF EXISTS `auctions_guarantor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auctions_guarantor` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `relationship` varchar(100) NOT NULL,
  `id_proof_type` varchar(50) NOT NULL,
  `id_proof_number` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `auction_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auctions_guarantor_auction_id_d1f65065_fk_auctions_auction_id` (`auction_id`),
  CONSTRAINT `auctions_guarantor_auction_id_d1f65065_fk_auctions_auction_id` FOREIGN KEY (`auction_id`) REFERENCES `auctions_auction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auctions_guarantor`
--

LOCK TABLES `auctions_guarantor` WRITE;
/*!40000 ALTER TABLE `auctions_guarantor` DISABLE KEYS */;
/*!40000 ALTER TABLE `auctions_guarantor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',3,'add_permission'),(6,'Can change permission',3,'change_permission'),(7,'Can delete permission',3,'delete_permission'),(8,'Can view permission',3,'view_permission'),(9,'Can add group',2,'add_group'),(10,'Can change group',2,'change_group'),(11,'Can delete group',2,'delete_group'),(12,'Can view group',2,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',7,'add_user'),(22,'Can change user',7,'change_user'),(23,'Can delete user',7,'delete_user'),(24,'Can view user',7,'view_user'),(25,'Can add newsletter subscription',6,'add_newslettersubscription'),(26,'Can change newsletter subscription',6,'change_newslettersubscription'),(27,'Can delete newsletter subscription',6,'delete_newslettersubscription'),(28,'Can view newsletter subscription',6,'view_newslettersubscription'),(29,'Can add member',8,'add_member'),(30,'Can change member',8,'change_member'),(31,'Can delete member',8,'delete_member'),(32,'Can view member',8,'view_member'),(33,'Can add member document',9,'add_memberdocument'),(34,'Can change member document',9,'change_memberdocument'),(35,'Can delete member document',9,'delete_memberdocument'),(36,'Can view member document',9,'view_memberdocument'),(37,'Can add chit group',10,'add_chitgroup'),(38,'Can change chit group',10,'change_chitgroup'),(39,'Can delete chit group',10,'delete_chitgroup'),(40,'Can view chit group',10,'view_chitgroup'),(41,'Can add chit member',11,'add_chitmember'),(42,'Can change chit member',11,'change_chitmember'),(43,'Can delete chit member',11,'delete_chitmember'),(44,'Can view chit member',11,'view_chitmember'),(45,'Can add payment',12,'add_payment'),(46,'Can change payment',12,'change_payment'),(47,'Can delete payment',12,'delete_payment'),(48,'Can view payment',12,'view_payment'),(49,'Can add auction',13,'add_auction'),(50,'Can change auction',13,'change_auction'),(51,'Can delete auction',13,'delete_auction'),(52,'Can view auction',13,'view_auction'),(53,'Can add guarantor',14,'add_guarantor'),(54,'Can change guarantor',14,'change_guarantor'),(55,'Can delete guarantor',14,'delete_guarantor'),(56,'Can view guarantor',14,'view_guarantor'),(57,'Can add settlement',15,'add_settlement'),(58,'Can change settlement',15,'change_settlement'),(59,'Can delete settlement',15,'delete_settlement'),(60,'Can view settlement',15,'view_settlement'),(61,'Can add branch',16,'add_branch'),(62,'Can change branch',16,'change_branch'),(63,'Can delete branch',16,'delete_branch'),(64,'Can view branch',16,'view_branch'),(65,'Can add system setting',17,'add_systemsetting'),(66,'Can change system setting',17,'change_systemsetting'),(67,'Can delete system setting',17,'delete_systemsetting'),(68,'Can view system setting',17,'view_systemsetting'),(69,'Can add log entry',18,'add_logentry'),(70,'Can change log entry',18,'change_logentry'),(71,'Can delete log entry',18,'delete_logentry'),(72,'Can view log entry',18,'view_logentry'),(73,'Can add notification',19,'add_notification'),(74,'Can change notification',19,'change_notification'),(75,'Can delete notification',19,'delete_notification'),(76,'Can view notification',19,'view_notification'),(77,'Can add cash handover',20,'add_cashhandover'),(78,'Can change cash handover',20,'change_cashhandover'),(79,'Can delete cash handover',20,'delete_cashhandover'),(80,'Can view cash handover',20,'view_cashhandover'),(81,'Can add follow up',21,'add_followup'),(82,'Can change follow up',21,'change_followup'),(83,'Can delete follow up',21,'delete_followup'),(84,'Can view follow up',21,'view_followup'),(85,'Can add payment proof',22,'add_paymentproof'),(86,'Can change payment proof',22,'change_paymentproof'),(87,'Can delete payment proof',22,'delete_paymentproof'),(88,'Can view payment proof',22,'view_paymentproof'),(89,'Can add payment qr',23,'add_paymentqr'),(90,'Can change payment qr',23,'change_paymentqr'),(91,'Can delete payment qr',23,'delete_paymentqr'),(92,'Can view payment qr',23,'view_paymentqr'),(93,'Can add Loan Agent',24,'add_loanagent'),(94,'Can change Loan Agent',24,'change_loanagent'),(95,'Can delete Loan Agent',24,'delete_loanagent'),(96,'Can view Loan Agent',24,'view_loanagent'),(97,'Can add Loan Customer',25,'add_loancustomer'),(98,'Can change Loan Customer',25,'change_loancustomer'),(99,'Can delete Loan Customer',25,'delete_loancustomer'),(100,'Can view Loan Customer',25,'view_loancustomer'),(101,'Can add emi schedule',26,'add_emischedule'),(102,'Can change emi schedule',26,'change_emischedule'),(103,'Can delete emi schedule',26,'delete_emischedule'),(104,'Can view emi schedule',26,'view_emischedule'),(105,'Can add Loan',27,'add_loan'),(106,'Can change Loan',27,'change_loan'),(107,'Can delete Loan',27,'delete_loan'),(108,'Can view Loan',27,'view_loan'),(109,'Can add loan transaction',29,'add_loantransaction'),(110,'Can change loan transaction',29,'change_loantransaction'),(111,'Can delete loan transaction',29,'delete_loantransaction'),(112,'Can view loan transaction',29,'view_loantransaction'),(113,'Can add Loan Payment',28,'add_loanpayment'),(114,'Can change Loan Payment',28,'change_loanpayment'),(115,'Can delete Loan Payment',28,'delete_loanpayment'),(116,'Can view Loan Payment',28,'view_loanpayment'),(117,'Can add loan payment proof',30,'add_loanpaymentproof'),(118,'Can change loan payment proof',30,'change_loanpaymentproof'),(119,'Can delete loan payment proof',30,'delete_loanpaymentproof'),(120,'Can view loan payment proof',30,'view_loanpaymentproof'),(121,'Can add staff profile',32,'add_staffprofile'),(122,'Can change staff profile',32,'change_staffprofile'),(123,'Can delete staff profile',32,'delete_staffprofile'),(124,'Can view staff profile',32,'view_staffprofile'),(125,'Can add super admin profile',33,'add_superadminprofile'),(126,'Can change super admin profile',33,'change_superadminprofile'),(127,'Can delete super admin profile',33,'delete_superadminprofile'),(128,'Can view super admin profile',33,'view_superadminprofile'),(129,'Can add admin profile',31,'add_adminprofile'),(130,'Can change admin profile',31,'change_adminprofile'),(131,'Can delete admin profile',31,'delete_adminprofile'),(132,'Can view admin profile',31,'view_adminprofile');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `branches_branch`
--

DROP TABLE IF EXISTS `branches_branch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `branches_branch` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(20) DEFAULT NULL,
  `address` longtext NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `gstin` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `branches_branch`
--

LOCK TABLES `branches_branch` WRITE;
/*!40000 ALTER TABLE `branches_branch` DISABLE KEYS */;
INSERT INTO `branches_branch` VALUES (1,'Main Office',NULL,'Near Matha Kovil, Thoothukudi','9876543210','anantha130404@gmail.com',1,'2026-04-08 11:43:10.237709','33ABCDEF12Z53'),(2,'Teacher\'s Colony Branch',NULL,'2G/1, Rajiv Nagar, Main Road, Thoothukudi','9876543210','anantha130404@gmail.com',1,'2026-04-08 11:45:28.652454','33ABCDEF12Z53');
/*!40000 ALTER TABLE `branches_branch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chits_chitgroup`
--

DROP TABLE IF EXISTS `chits_chitgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chits_chitgroup` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `duration_months` int(11) NOT NULL,
  `installment_amount` decimal(10,2) NOT NULL,
  `start_date` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `commission_percentage` decimal(5,2) NOT NULL,
  `branch_id` bigint(20) DEFAULT NULL,
  `due_day` int(11) NOT NULL,
  `penalty_per_day` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `chits_chitgroup_branch_id_6ff6867a_fk_branches_branch_id` (`branch_id`),
  CONSTRAINT `chits_chitgroup_branch_id_6ff6867a_fk_branches_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `branches_branch` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chits_chitgroup`
--

LOCK TABLES `chits_chitgroup` WRITE;
/*!40000 ALTER TABLE `chits_chitgroup` DISABLE KEYS */;
INSERT INTO `chits_chitgroup` VALUES (1,'Gold',25000.00,25,1000.00,'2026-04-10','ACTIVE','2026-04-08 11:41:06.775442',5.00,NULL,8,50.00),(2,'Silver',25000.00,25,1000.00,'2026-04-20','ACTIVE','2026-04-15 11:52:16.658964',5.00,NULL,18,0.00);
/*!40000 ALTER TABLE `chits_chitgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chits_chitmember`
--

DROP TABLE IF EXISTS `chits_chitmember`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chits_chitmember` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `joined_date` date NOT NULL,
  `chit_group_id` bigint(20) NOT NULL,
  `member_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chits_chitmember_chit_group_id_member_id_9e853bd1_uniq` (`chit_group_id`,`member_id`),
  KEY `chits_chitmember_member_id_589a519f_fk_members_member_id` (`member_id`),
  CONSTRAINT `chits_chitmember_chit_group_id_f1eb1fd8_fk_chits_chitgroup_id` FOREIGN KEY (`chit_group_id`) REFERENCES `chits_chitgroup` (`id`),
  CONSTRAINT `chits_chitmember_member_id_589a519f_fk_members_member_id` FOREIGN KEY (`member_id`) REFERENCES `members_member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chits_chitmember`
--

LOCK TABLES `chits_chitmember` WRITE;
/*!40000 ALTER TABLE `chits_chitmember` DISABLE KEYS */;
INSERT INTO `chits_chitmember` VALUES (1,'2026-04-08',1,1),(2,'2026-04-09',1,2),(3,'2026-04-15',2,3),(4,'2026-04-20',2,4);
/*!40000 ALTER TABLE `chits_chitmember` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (31,'accounts','adminprofile'),(6,'accounts','newslettersubscription'),(32,'accounts','staffprofile'),(33,'accounts','superadminprofile'),(7,'accounts','user'),(1,'admin','logentry'),(13,'auctions','auction'),(14,'auctions','guarantor'),(2,'auth','group'),(3,'auth','permission'),(16,'branches','branch'),(10,'chits','chitgroup'),(11,'chits','chitmember'),(4,'contenttypes','contenttype'),(26,'loans','emischedule'),(27,'loans','loan'),(24,'loan_customers','loanagent'),(25,'loan_customers','loancustomer'),(28,'loan_payments','loanpayment'),(30,'loan_payments','loanpaymentproof'),(29,'loan_payments','loantransaction'),(18,'logs','logentry'),(8,'members','member'),(9,'members','memberdocument'),(19,'notifications','notification'),(20,'payments','cashhandover'),(21,'payments','followup'),(12,'payments','payment'),(22,'payments','paymentproof'),(23,'payments','paymentqr'),(5,'sessions','session'),(15,'settlements','settlement'),(17,'system_settings','systemsetting');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-04-08 10:34:54.602551'),(2,'contenttypes','0002_remove_content_type_name','2026-04-08 10:34:54.804073'),(3,'auth','0001_initial','2026-04-08 10:34:55.479496'),(4,'auth','0002_alter_permission_name_max_length','2026-04-08 10:34:55.777960'),(5,'auth','0003_alter_user_email_max_length','2026-04-08 10:34:55.797841'),(6,'auth','0004_alter_user_username_opts','2026-04-08 10:34:55.817606'),(7,'auth','0005_alter_user_last_login_null','2026-04-08 10:34:55.840008'),(8,'auth','0006_require_contenttypes_0002','2026-04-08 10:34:55.847934'),(9,'auth','0007_alter_validators_add_error_messages','2026-04-08 10:34:55.877468'),(10,'auth','0008_alter_user_username_max_length','2026-04-08 10:34:55.899482'),(11,'auth','0009_alter_user_last_name_max_length','2026-04-08 10:34:55.937042'),(12,'auth','0010_alter_group_name_max_length','2026-04-08 10:34:56.047909'),(13,'auth','0011_update_proxy_permissions','2026-04-08 10:34:56.082750'),(14,'auth','0012_alter_user_first_name_max_length','2026-04-08 10:34:56.112329'),(15,'accounts','0001_initial','2026-04-08 10:34:56.940122'),(16,'accounts','0002_user_profile_picture','2026-04-08 10:34:56.993254'),(17,'accounts','0003_user_auction_alerts_user_email_notifications_and_more','2026-04-08 10:34:57.190858'),(18,'accounts','0004_newslettersubscription','2026-04-08 10:34:57.289347'),(19,'accounts','0005_user_otp_user_otp_created_at','2026-04-08 10:34:57.404191'),(20,'accounts','0006_user_two_factor_enabled_user_two_factor_secret','2026-04-08 10:34:57.576599'),(21,'accounts','0007_user_address_user_phone_number','2026-04-08 10:34:57.715299'),(22,'accounts','0008_remove_user_address_remove_user_phone_number','2026-04-08 10:34:57.826713'),(23,'admin','0001_initial','2026-04-08 10:34:58.322012'),(24,'admin','0002_logentry_remove_auto_add','2026-04-08 10:34:58.361778'),(25,'admin','0003_logentry_add_action_flag_choices','2026-04-08 10:34:58.433012'),(26,'members','0001_initial','2026-04-08 10:34:58.839486'),(27,'chits','0001_initial','2026-04-08 10:34:59.517567'),(28,'auctions','0001_initial','2026-04-08 10:35:00.199041'),(29,'auctions','0002_auction_dividend_per_member_and_more','2026-04-08 10:35:09.403645'),(30,'branches','0001_initial','2026-04-08 10:35:09.558080'),(31,'branches','0002_branch_gstin_alter_branch_code','2026-04-08 10:35:09.819492'),(32,'chits','0002_chitgroup_commission_percentage','2026-04-08 10:35:09.928237'),(33,'chits','0003_chitgroup_branch','2026-04-08 10:35:10.372158'),(34,'chits','0004_penalty_fields','2026-04-08 10:35:10.526475'),(35,'logs','0001_initial','2026-04-08 10:35:10.900115'),(36,'members','0002_member_account_number_member_bank_name_and_more','2026-04-08 10:35:11.879904'),(37,'members','0003_memberdocument_admin_notes_memberdocument_status_and_more','2026-04-08 10:35:12.126754'),(38,'members','0004_member_branch_and_nominee','2026-04-08 10:35:12.646686'),(39,'notifications','0001_initial','2026-04-08 10:35:12.935487'),(40,'payments','0001_initial','2026-04-08 10:35:13.848523'),(41,'payments','0002_payment_dividend_amount_payment_due_date_and_more','2026-04-08 10:35:14.074137'),(42,'payments','0003_payment_collected_by','2026-04-08 10:35:14.372330'),(43,'sessions','0001_initial','2026-04-08 10:35:14.491918'),(44,'settlements','0001_initial','2026-04-08 10:35:15.078566'),(45,'system_settings','0001_initial','2026-04-08 10:35:15.194620'),(46,'system_settings','0002_seed_settings','2026-04-08 10:35:15.351098'),(47,'accounts','0009_alter_user_managers','2026-04-09 05:30:33.431674'),(48,'chits','0005_alter_chitgroup_members','2026-04-09 05:30:33.590858'),(49,'payments','0004_cashhandover','2026-04-09 08:11:23.298567'),(50,'payments','0005_followup','2026-04-09 09:46:15.304968'),(51,'payments','0006_alter_payment_status_paymentproof','2026-04-09 11:25:36.422034'),(52,'payments','0007_paymentqr','2026-04-09 11:50:46.526179'),(53,'loan_customers','0001_initial','2026-04-15 07:00:21.738363'),(54,'loans','0001_initial','2026-04-15 07:00:23.453698'),(55,'loan_payments','0001_initial','2026-04-15 07:00:23.818272'),(56,'loan_payments','0002_initial','2026-04-15 07:00:25.015358'),(57,'loan_customers','0002_remove_loancustomer_agent_remove_loancustomer_branch_and_more','2026-04-15 11:26:56.635964'),(58,'members','0005_rename_address_member_blacklist_reason_and_more','2026-04-15 11:30:59.251616'),(59,'loans','0002_alter_loan_customer','2026-04-15 11:31:00.641136'),(60,'loan_customers','0003_delete_loancustomer','2026-04-15 11:31:00.727679'),(61,'loans','0003_loan_loan_type','2026-04-17 07:30:28.318800'),(62,'loan_payments','0003_loanpaymentproof','2026-04-17 07:53:27.987396'),(63,'loan_payments','0004_loanpaymentproof_member_name_and_more','2026-04-17 10:07:43.557199'),(64,'accounts','0010_adminprofile_staffprofile_superadminprofile','2026-04-22 10:03:44.639368');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('2mkx5i4pmqjmytsg0dussx8fs6kemtl6','.eJxVi0sKwjAQQO8yaykT87VLTyBeIExmJkSEFpqWLsS7i9CFbt_nBZm2teWt65IfAiNEOP2yQvzU6SuIed6mtQ8H6sOd9hv1vs-LXI_s723UG4xQsHrEc0jk2KgjDhq9shFLxlZTREK1iiFESqY6pAtX6wWLJqseHbw_4ZM2xw:1wCzMQ:svAwLswTOfRkKsmk6rKn8UoGnOgS01ps4sXoXGVx2C8','2026-04-29 12:28:50.994736'),('2oti0plvf3nwhnheentonjb3mf89cetj','.eJxVi0sKwjAQQO8yaykxzuTTpScQLxAmkwwRoYWmpQvx7iJ0odv3eUHibW1p63VJjwIjBDj9sszyrNNXsMi8TWsfDtSHO-837n2fl3I9sr-3cW8wgmJkNaaoLYhIUSuJOh8sYWDO1nvKhh2eq1dTbHUhCpG5OOJYxAZ4fwDXVjY0:1wEo8y:YYpYkRvyu776QEfB4Rp4Ma_c149vHB6hP2GKQ_AyN5Q','2026-05-04 12:54:28.845117'),('3kjteg44jresr5tnq65bxytmuvkzf3yq','.eJxVjEEKwyAQRe_iugRHM1q77AlCLyDjOGIpJBAjWZTevQSyaLfvv__eKlLfauxN1vjM6qaMuvyyRPyS-RiIeenz1oYTteFB-0St7cua76f2963U6lGEYp1AyFdEBmR0DsRzAS4aAyeLSdCR0zaP7EdByikYySZoS-CD-nwBygk2Tg:1wFQ3Y:KaWGC82bUxVmYDm_wgJBn-JoC75WYG2czv4g13-8rEc','2026-05-06 05:23:24.978488'),('fqv2jezq2ijfpfovblujc1v0fplo3to4','.eJxVi0sKwjAQQO8yaylJk-bTpScQLxAmMxMiQgtNQxfi3UXoQrfv84KEfa-pN9nSg2EGDZdflpGesnwFEq192dtwojbc8bhha8e68fXM_t6KrcIM3mmnSaGyViIWYzyRzcFiIS1TKTJ5lbnIKCo4jy7QaKOJno0izZ7h_QHXNDav:1wFULN:vfMthEKLb2GQ2UhIIoS_eX1Msafj9c1L-nisU70L74k','2026-05-06 09:58:05.393780'),('gd83euruih5d9n6blo117eq9hgzgqxwg','.eJxVi0sKwjAQQO8yaylJk-bTpScQLxAmMxMiQgtNQxfi3UXoQrfv84KEfa-pN9nSg2EGDZdflpGesnwFEq192dtwojbc8bhha8e68fXM_t6KrcIM3mmnSaGyViIWYzyRzcFiIS1TKTJ5lbnIKCo4jy7QaKOJno0izZ7h_QHXNDav:1wB5WI:bzfiokgXxV8U8m6JmFQeDzdcNBL7unWjcOLDCkGVtck','2026-04-24 06:39:10.734277'),('q2s3a69xmfo5old3wlyyn530irmh3mjd','.eJxVjEEKwyAQRe_iugRHM1q77AlCLyDjOGIpJBAjWZTevQSyaLfvv__eKlLfauxN1vjM6qaMuvyyRPyS-RiIeenz1oYTteFB-0St7cua76f2963U6lGEYp1AyFdEBmR0DsRzAS4aAyeLSdCR0zaP7EdByikYySZoS-CD-nwBygk2Tg:1wDej2:NDrVt_QUhPj3dAx5Sej5GSHo8Az3Wjvr-jUhUQkRhk4','2026-05-01 08:38:56.701121');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loan_customers_loanagent`
--

DROP TABLE IF EXISTS `loan_customers_loanagent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loan_customers_loanagent` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `employee_code` varchar(20) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `joined_on` date DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `branch_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_code` (`employee_code`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `loan_customers_loana_branch_id_d05de92b_fk_branches_` (`branch_id`),
  CONSTRAINT `loan_customers_loana_branch_id_d05de92b_fk_branches_` FOREIGN KEY (`branch_id`) REFERENCES `branches_branch` (`id`),
  CONSTRAINT `loan_customers_loanagent_user_id_c35d420b_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan_customers_loanagent`
--

LOCK TABLES `loan_customers_loanagent` WRITE;
/*!40000 ALTER TABLE `loan_customers_loanagent` DISABLE KEYS */;
/*!40000 ALTER TABLE `loan_customers_loanagent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loan_payments_loanpayment`
--

DROP TABLE IF EXISTS `loan_payments_loanpayment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loan_payments_loanpayment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `amount_paid` decimal(12,2) NOT NULL,
  `payment_date` date NOT NULL,
  `payment_mode` varchar(10) NOT NULL,
  `transaction_reference` varchar(100) NOT NULL,
  `receipt_number` varchar(30) NOT NULL,
  `penalty_waived` tinyint(1) NOT NULL,
  `penalty_paid` decimal(10,2) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `collected_by_id` bigint(20) DEFAULT NULL,
  `emi_installment_id` bigint(20) DEFAULT NULL,
  `loan_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `receipt_number` (`receipt_number`),
  KEY `loan_payments_loanpa_collected_by_id_d2bf582c_fk_accounts_` (`collected_by_id`),
  KEY `loan_payments_loanpa_emi_installment_id_27f524e9_fk_loans_emi` (`emi_installment_id`),
  KEY `loan_payments_loanpayment_loan_id_71def5f3_fk_loans_loan_id` (`loan_id`),
  CONSTRAINT `loan_payments_loanpa_collected_by_id_d2bf582c_fk_accounts_` FOREIGN KEY (`collected_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `loan_payments_loanpa_emi_installment_id_27f524e9_fk_loans_emi` FOREIGN KEY (`emi_installment_id`) REFERENCES `loans_emischedule` (`id`),
  CONSTRAINT `loan_payments_loanpayment_loan_id_71def5f3_fk_loans_loan_id` FOREIGN KEY (`loan_id`) REFERENCES `loans_loan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan_payments_loanpayment`
--

LOCK TABLES `loan_payments_loanpayment` WRITE;
/*!40000 ALTER TABLE `loan_payments_loanpayment` DISABLE KEYS */;
/*!40000 ALTER TABLE `loan_payments_loanpayment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loan_payments_loanpaymentproof`
--

DROP TABLE IF EXISTS `loan_payments_loanpaymentproof`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loan_payments_loanpaymentproof` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `transaction_id` varchar(100) NOT NULL,
  `screenshot` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL,
  `admin_notes` longtext DEFAULT NULL,
  `member_notes` longtext DEFAULT NULL,
  `submitted_at` datetime(6) NOT NULL,
  `processed_at` datetime(6) DEFAULT NULL,
  `emi_installment_id` bigint(20) NOT NULL,
  `processed_by_id` bigint(20) DEFAULT NULL,
  `member_name` varchar(255) DEFAULT NULL,
  `phone_no` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`),
  UNIQUE KEY `emi_installment_id` (`emi_installment_id`),
  KEY `loan_payments_loanpa_processed_by_id_bdd86ade_fk_accounts_` (`processed_by_id`),
  CONSTRAINT `loan_payments_loanpa_emi_installment_id_e939be6a_fk_loans_emi` FOREIGN KEY (`emi_installment_id`) REFERENCES `loans_emischedule` (`id`),
  CONSTRAINT `loan_payments_loanpa_processed_by_id_bdd86ade_fk_accounts_` FOREIGN KEY (`processed_by_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan_payments_loanpaymentproof`
--

LOCK TABLES `loan_payments_loanpaymentproof` WRITE;
/*!40000 ALTER TABLE `loan_payments_loanpaymentproof` DISABLE KEYS */;
INSERT INTO `loan_payments_loanpaymentproof` VALUES (1,'409823126781','loan_payment_proofs/jayalalitha.png','REJECTED','to update the wrong photo','','2026-04-17 10:08:22.881435','2026-04-17 10:32:36.614173',19,1,'Roki','9786204074');
/*!40000 ALTER TABLE `loan_payments_loanpaymentproof` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loan_payments_loantransaction`
--

DROP TABLE IF EXISTS `loan_payments_loantransaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loan_payments_loantransaction` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `txn_type` varchar(20) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `balance_after` decimal(12,2) NOT NULL,
  `description` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` bigint(20) DEFAULT NULL,
  `loan_id` bigint(20) NOT NULL,
  `payment_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `loan_payments_loantr_created_by_id_89e2d51c_fk_accounts_` (`created_by_id`),
  KEY `loan_payments_loantransaction_loan_id_1969662c_fk_loans_loan_id` (`loan_id`),
  KEY `loan_payments_loantr_payment_id_cfdb3d58_fk_loan_paym` (`payment_id`),
  CONSTRAINT `loan_payments_loantr_created_by_id_89e2d51c_fk_accounts_` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `loan_payments_loantr_payment_id_cfdb3d58_fk_loan_paym` FOREIGN KEY (`payment_id`) REFERENCES `loan_payments_loanpayment` (`id`),
  CONSTRAINT `loan_payments_loantransaction_loan_id_1969662c_fk_loans_loan_id` FOREIGN KEY (`loan_id`) REFERENCES `loans_loan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan_payments_loantransaction`
--

LOCK TABLES `loan_payments_loantransaction` WRITE;
/*!40000 ALTER TABLE `loan_payments_loantransaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `loan_payments_loantransaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loans_emischedule`
--

DROP TABLE IF EXISTS `loans_emischedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loans_emischedule` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `installment_number` int(10) unsigned NOT NULL CHECK (`installment_number` >= 0),
  `due_date` date NOT NULL,
  `emi_amount` decimal(12,2) NOT NULL,
  `principal_component` decimal(12,2) NOT NULL,
  `interest_component` decimal(12,2) NOT NULL,
  `opening_balance` decimal(12,2) NOT NULL,
  `closing_balance` decimal(12,2) NOT NULL,
  `paid_amount` decimal(12,2) NOT NULL,
  `paid_date` date DEFAULT NULL,
  `penalty_amount` decimal(12,2) NOT NULL,
  `status` varchar(10) NOT NULL,
  `loan_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `loans_emischedule_loan_id_installment_number_f116f0a2_uniq` (`loan_id`,`installment_number`),
  CONSTRAINT `loans_emischedule_loan_id_fc28a89c_fk_loans_loan_id` FOREIGN KEY (`loan_id`) REFERENCES `loans_loan` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loans_emischedule`
--

LOCK TABLES `loans_emischedule` WRITE;
/*!40000 ALTER TABLE `loans_emischedule` DISABLE KEYS */;
INSERT INTO `loans_emischedule` VALUES (1,1,'2026-05-10',2889.03,2680.70,208.33,50000.00,47319.30,0.00,NULL,0.00,'pending',2),(2,2,'2026-06-10',2889.03,2691.87,197.16,47319.30,44627.44,0.00,NULL,0.00,'pending',2),(3,3,'2026-07-10',2889.03,2703.08,185.95,44627.44,41924.35,0.00,NULL,0.00,'pending',2),(4,4,'2026-08-10',2889.03,2714.35,174.68,41924.35,39210.01,0.00,NULL,0.00,'pending',2),(5,5,'2026-09-10',2889.03,2725.65,163.38,39210.01,36484.35,0.00,NULL,0.00,'pending',2),(6,6,'2026-10-10',2889.03,2737.01,152.02,36484.35,33747.34,0.00,NULL,0.00,'pending',2),(7,7,'2026-11-10',2889.03,2748.42,140.61,33747.34,30998.93,0.00,NULL,0.00,'pending',2),(8,8,'2026-12-10',2889.03,2759.87,129.16,30998.93,28239.06,0.00,NULL,0.00,'pending',2),(9,9,'2027-01-10',2889.03,2771.37,117.66,28239.06,25467.69,0.00,NULL,0.00,'pending',2),(10,10,'2027-02-10',2889.03,2782.91,106.12,25467.69,22684.78,0.00,NULL,0.00,'pending',2),(11,11,'2027-03-10',2889.03,2794.51,94.52,22684.78,19890.27,0.00,NULL,0.00,'pending',2),(12,12,'2027-04-10',2889.03,2806.15,82.88,19890.27,17084.11,0.00,NULL,0.00,'pending',2),(13,13,'2027-05-10',2889.03,2817.85,71.18,17084.11,14266.27,0.00,NULL,0.00,'pending',2),(14,14,'2027-06-10',2889.03,2829.59,59.44,14266.27,11436.68,0.00,NULL,0.00,'pending',2),(15,15,'2027-07-10',2889.03,2841.38,47.65,11436.68,8595.30,0.00,NULL,0.00,'pending',2),(16,16,'2027-08-10',2889.03,2853.22,35.81,8595.30,5742.09,0.00,NULL,0.00,'pending',2),(17,17,'2027-09-10',2889.03,2865.10,23.93,5742.09,2876.98,0.00,NULL,0.00,'pending',2),(18,18,'2027-10-10',2889.03,2877.04,11.99,2876.98,0.00,0.00,NULL,0.00,'pending',2),(19,1,'2026-05-15',2043.62,1960.29,83.33,50000.00,48039.71,0.00,NULL,0.00,'pending',1),(20,2,'2026-06-15',2043.62,1963.55,80.07,48039.71,46076.16,0.00,NULL,0.00,'pending',1),(21,3,'2026-07-15',2043.62,1966.83,76.79,46076.16,44109.33,0.00,NULL,0.00,'pending',1),(22,4,'2026-08-15',2043.62,1970.10,73.52,44109.33,42139.23,0.00,NULL,0.00,'pending',1),(23,5,'2026-09-15',2043.62,1973.39,70.23,42139.23,40165.84,0.00,NULL,0.00,'pending',1),(24,6,'2026-10-15',2043.62,1976.68,66.94,40165.84,38189.16,0.00,NULL,0.00,'pending',1),(25,7,'2026-11-15',2043.62,1979.97,63.65,38189.16,36209.19,0.00,NULL,0.00,'pending',1),(26,8,'2026-12-15',2043.62,1983.27,60.35,36209.19,34225.92,0.00,NULL,0.00,'pending',1),(27,9,'2027-01-15',2043.62,1986.58,57.04,34225.92,32239.34,0.00,NULL,0.00,'pending',1),(28,10,'2027-02-15',2043.62,1989.89,53.73,32239.34,30249.46,0.00,NULL,0.00,'pending',1),(29,11,'2027-03-15',2043.62,1993.20,50.42,30249.46,28256.25,0.00,NULL,0.00,'pending',1),(30,12,'2027-04-15',2043.62,1996.53,47.09,28256.25,26259.73,0.00,NULL,0.00,'pending',1),(31,13,'2027-05-15',2043.62,1999.85,43.77,26259.73,24259.87,0.00,NULL,0.00,'pending',1),(32,14,'2027-06-15',2043.62,2003.19,40.43,24259.87,22256.69,0.00,NULL,0.00,'pending',1),(33,15,'2027-07-15',2043.62,2006.53,37.09,22256.69,20250.16,0.00,NULL,0.00,'pending',1),(34,16,'2027-08-15',2043.62,2009.87,33.75,20250.16,18240.29,0.00,NULL,0.00,'pending',1),(35,17,'2027-09-15',2043.62,2013.22,30.40,18240.29,16227.07,0.00,NULL,0.00,'pending',1),(36,18,'2027-10-15',2043.62,2016.57,27.05,16227.07,14210.50,0.00,NULL,0.00,'pending',1),(37,19,'2027-11-15',2043.62,2019.94,23.68,14210.50,12190.56,0.00,NULL,0.00,'pending',1),(38,20,'2027-12-15',2043.62,2023.30,20.32,12190.56,10167.26,0.00,NULL,0.00,'pending',1),(39,21,'2028-01-15',2043.62,2026.67,16.95,10167.26,8140.58,0.00,NULL,0.00,'pending',1),(40,22,'2028-02-15',2043.62,2030.05,13.57,8140.58,6110.53,0.00,NULL,0.00,'pending',1),(41,23,'2028-03-15',2043.62,2033.44,10.18,6110.53,4077.09,0.00,NULL,0.00,'pending',1),(42,24,'2028-04-15',2043.62,2036.82,6.80,4077.09,2040.27,0.00,NULL,0.00,'pending',1),(43,25,'2028-05-15',2043.62,2040.22,3.40,2040.27,0.05,0.00,NULL,0.00,'pending',1);
/*!40000 ALTER TABLE `loans_emischedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loans_loan`
--

DROP TABLE IF EXISTS `loans_loan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `loans_loan` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `loan_number` varchar(20) NOT NULL,
  `loan_amount` decimal(12,2) NOT NULL,
  `interest_rate` decimal(5,2) NOT NULL,
  `interest_type` varchar(10) NOT NULL,
  `tenure_months` int(10) unsigned NOT NULL CHECK (`tenure_months` >= 0),
  `start_date` date NOT NULL,
  `emi_amount` decimal(12,2) DEFAULT NULL,
  `total_interest` decimal(12,2) DEFAULT NULL,
  `total_payable` decimal(12,2) DEFAULT NULL,
  `outstanding_balance` decimal(12,2) DEFAULT NULL,
  `status` varchar(15) NOT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `rejection_reason` longtext NOT NULL,
  `disbursed_at` datetime(6) DEFAULT NULL,
  `disbursement_mode` varchar(20) NOT NULL,
  `disbursement_reference` varchar(100) NOT NULL,
  `penalty_rate` decimal(5,2) NOT NULL,
  `grace_period_days` int(10) unsigned NOT NULL CHECK (`grace_period_days` >= 0),
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `approved_by_id` bigint(20) DEFAULT NULL,
  `branch_id` bigint(20) NOT NULL,
  `created_by_id` bigint(20) DEFAULT NULL,
  `customer_id` bigint(20) NOT NULL,
  `parent_loan_id` bigint(20) DEFAULT NULL,
  `loan_type` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `loan_number` (`loan_number`),
  KEY `loans_loan_approved_by_id_5432836a_fk_accounts_user_id` (`approved_by_id`),
  KEY `loans_loan_branch_id_e92809a2_fk_branches_branch_id` (`branch_id`),
  KEY `loans_loan_created_by_id_cbe2b2ae_fk_accounts_user_id` (`created_by_id`),
  KEY `loans_loan_parent_loan_id_7fc68d4e_fk_loans_loan_id` (`parent_loan_id`),
  KEY `loans_loan_customer_id_19daeada_fk_members_member_id` (`customer_id`),
  CONSTRAINT `loans_loan_approved_by_id_5432836a_fk_accounts_user_id` FOREIGN KEY (`approved_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `loans_loan_branch_id_e92809a2_fk_branches_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `branches_branch` (`id`),
  CONSTRAINT `loans_loan_created_by_id_cbe2b2ae_fk_accounts_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `loans_loan_customer_id_19daeada_fk_members_member_id` FOREIGN KEY (`customer_id`) REFERENCES `members_member` (`id`),
  CONSTRAINT `loans_loan_parent_loan_id_7fc68d4e_fk_loans_loan_id` FOREIGN KEY (`parent_loan_id`) REFERENCES `loans_loan` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loans_loan`
--

LOCK TABLES `loans_loan` WRITE;
/*!40000 ALTER TABLE `loans_loan` DISABLE KEYS */;
INSERT INTO `loans_loan` VALUES (1,'LN-2026-0001',50000.00,2.00,'reducing',25,'2026-04-15',2043.62,1090.55,51090.55,51090.55,'approved','2026-04-15 07:41:47.606924','',NULL,'cash','',1.00,10,'','2026-04-15 07:09:06.748062','2026-04-15 07:41:47.644447',1,1,1,1,NULL,'personal'),(2,'LN-2026-0002',50000.00,5.00,'reducing',18,'2026-04-10',2889.03,2002.48,52002.48,52002.48,'approved','2026-04-17 07:37:45.504178','',NULL,'cash','',2.00,5,'','2026-04-17 07:36:18.994641','2026-04-17 07:37:45.520088',1,2,1,3,NULL,'personal');
/*!40000 ALTER TABLE `loans_loan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs_logentry`
--

DROP TABLE IF EXISTS `logs_logentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logs_logentry` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `action` varchar(20) NOT NULL,
  `module` varchar(50) NOT NULL,
  `details` longtext NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `timestamp` datetime(6) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `logs_logentry_user_id_b342b1ab_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `logs_logentry_user_id_b342b1ab_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=183 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs_logentry`
--

LOCK TABLES `logs_logentry` WRITE;
/*!40000 ALTER TABLE `logs_logentry` DISABLE KEYS */;
INSERT INTO `logs_logentry` VALUES (137,'LOGOUT','Authentication','User varshini logged out of the session.',NULL,'2026-04-17 08:38:54.255045',7),(138,'LOGIN','Authentication','User roki successfully logged into the system.','192.168.1.2','2026-04-17 08:38:56.695364',2),(139,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-17 09:42:10.884139',1),(140,'LOGIN','Authentication','User varshini successfully logged into the system.','127.0.0.1','2026-04-17 09:42:21.091163',7),(141,'LOGOUT','Authentication','User varshini logged out of the session.',NULL,'2026-04-17 09:50:10.228695',7),(142,'LOGIN','Authentication','User roki successfully logged into the system.','127.0.0.1','2026-04-17 09:50:15.774936',2),(143,'LOGOUT','Authentication','User roki logged out of the session.',NULL,'2026-04-17 10:08:30.966096',2),(144,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-17 10:08:36.179026',1),(145,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-17 12:43:02.578902',1),(146,'LOGIN','Authentication','User mani successfully logged into the system.','127.0.0.1','2026-04-17 12:43:13.261139',3),(147,'LOGOUT','Authentication','User mani logged out of the session.',NULL,'2026-04-17 12:48:33.374969',3),(148,'LOGIN','Authentication','User anantha successfully logged into the system.','127.0.0.1','2026-04-17 12:48:44.729082',5),(149,'LOGOUT','Authentication','User anantha logged out of the session.',NULL,'2026-04-17 12:51:01.178537',5),(150,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-18 06:55:01.420677',1),(151,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-18 07:03:43.344767',1),(152,'LOGIN','Authentication','User anantha successfully logged into the system.','127.0.0.1','2026-04-18 07:03:58.427662',5),(153,'LOGOUT','Authentication','User anantha logged out of the session.',NULL,'2026-04-18 07:04:14.053110',5),(154,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-20 04:59:19.053262',1),(155,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-20 05:11:12.334298',1),(156,'LOGIN','Authentication','User varshini successfully logged into the system.','192.168.1.2','2026-04-20 05:11:56.986195',7),(157,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-20 05:12:09.542597',1),(158,'LOGOUT','Authentication','User varshini logged out of the session.',NULL,'2026-04-20 05:17:27.280444',7),(159,'LOGIN','Authentication','User varshini successfully logged into the system.','192.168.1.2','2026-04-20 05:19:43.612484',7),(160,'LOGOUT','Authentication','User varshini logged out of the session.',NULL,'2026-04-20 07:00:01.742801',7),(161,'LOGIN','Authentication','User admin successfully logged into the system.','192.168.1.2','2026-04-20 07:02:33.061009',1),(162,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-20 07:11:13.327484',1),(163,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-20 08:12:31.855247',1),(164,'LOGIN','Authentication','User roki successfully logged into the system.','127.0.0.1','2026-04-20 08:12:50.566568',2),(165,'LOGOUT','Authentication','User roki logged out of the session.',NULL,'2026-04-20 10:28:48.435602',2),(166,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-20 10:28:54.789550',1),(167,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-20 11:15:04.966709',1),(168,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-20 11:15:26.794926',1),(169,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-20 11:20:30.287351',1),(170,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-20 11:20:59.155633',1),(171,'LOGIN','Authentication','User admin successfully logged into the system.','192.168.1.2','2026-04-20 12:43:19.254296',1),(172,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-20 12:54:02.044162',1),(173,'LOGIN','Authentication','User vicky successfully logged into the system.','192.168.1.2','2026-04-20 12:54:28.838783',8),(174,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-21 06:07:25.516308',1),(175,'LOGIN','Authentication','User anantha successfully logged into the system.','127.0.0.1','2026-04-21 06:07:37.624290',5),(176,'LOGOUT','Authentication','User anantha logged out of the session.',NULL,'2026-04-21 06:08:26.295505',5),(177,'LOGIN','Authentication','User admin successfully logged into the system.','192.168.1.6','2026-04-21 06:16:08.730286',1),(178,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-21 06:18:49.293779',1),(179,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-22 05:13:20.227412',1),(180,'LOGOUT','Authentication','User admin logged out of the session.',NULL,'2026-04-22 05:23:05.648081',1),(181,'LOGIN','Authentication','User roki successfully logged into the system.','127.0.0.1','2026-04-22 05:23:24.820952',2),(182,'LOGIN','Authentication','User admin successfully logged into the system.','127.0.0.1','2026-04-22 09:58:05.384366',1);
/*!40000 ALTER TABLE `logs_logentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members_member`
--

DROP TABLE IF EXISTS `members_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `members_member` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `account_number` varchar(50) NOT NULL,
  `bank_name` varchar(150) NOT NULL,
  `id_number` varchar(50) NOT NULL,
  `ifsc_code` varchar(20) NOT NULL,
  `photo` varchar(100) DEFAULT NULL,
  `branch_id` bigint(20) DEFAULT NULL,
  `nominee_id_number` varchar(50) DEFAULT NULL,
  `nominee_name` varchar(150) DEFAULT NULL,
  `nominee_phone` varchar(20) DEFAULT NULL,
  `nominee_relationship` varchar(100) DEFAULT NULL,
  `blacklist_reason` longtext NOT NULL,
  `address_line1` varchar(200) NOT NULL,
  `address_line2` varchar(200) NOT NULL,
  `alternate_phone` varchar(20) DEFAULT NULL,
  `blacklisted` tinyint(1) NOT NULL,
  `city` varchar(100) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `gender` varchar(10) NOT NULL,
  `id_card_type` varchar(50) DEFAULT NULL,
  `id_proof_document` varchar(100) DEFAULT NULL,
  `loan_agent_id` bigint(20) DEFAULT NULL,
  `pincode` varchar(10) NOT NULL,
  `state` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `members_member_id_number_67abc8ba_uniq` (`id_number`),
  UNIQUE KEY `members_member_phone_2f3e23db_uniq` (`phone`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `members_member_branch_id_7b3cf145_fk_branches_branch_id` (`branch_id`),
  KEY `members_member_loan_agent_id_110c1c62_fk_loan_cust` (`loan_agent_id`),
  CONSTRAINT `members_member_branch_id_7b3cf145_fk_branches_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `branches_branch` (`id`),
  CONSTRAINT `members_member_loan_agent_id_110c1c62_fk_loan_cust` FOREIGN KEY (`loan_agent_id`) REFERENCES `loan_customers_loanagent` (`id`),
  CONSTRAINT `members_member_user_id_5b73e2f8_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members_member`
--

LOCK TABLES `members_member` WRITE;
/*!40000 ALTER TABLE `members_member` DISABLE KEYS */;
INSERT INTO `members_member` VALUES (1,'Roki','9786204074','ACTIVE','2026-04-08 11:46:59.722202',2,'1234567890123456','SBI','123456789012','SBIN1234556','members/photos/3d6a6444-d6b4-46b9-943d-ef404c361e21-1_all_845.jpg',2,'123456789012','Rajendran','6574839201','Brother','','','',NULL,0,'',NULL,NULL,'',NULL,NULL,NULL,'','Tamil Nadu'),(2,'Jessica','9512364870','ACTIVE','2026-04-09 10:47:39.518354',4,'','','','','',1,NULL,NULL,NULL,NULL,'','','',NULL,0,'',NULL,NULL,'',NULL,NULL,NULL,'','Tamil Nadu'),(3,'Varshini','7685940321','ACTIVE','2026-04-15 12:27:20.199534',7,'1234567890123456','State Bank Of India','987654321098','SBIN1234556','',2,NULL,NULL,NULL,NULL,'','256,T.Nagar flat 3rd floor','','6574832901',0,'Chennai',NULL,'varshini@gmail.com','','Aadhar','',NULL,'600028','Tamil Nadu'),(4,'Vicky','9123456780','ACTIVE','2026-04-20 12:53:45.761930',8,'159260371482','State Bank of India','1592 6037 1482','SBIN0001234','',NULL,'2345 6789 0123','Ravi Kumar','9090909090','Brother','','12/7, Gandhi Street','Near Bus Stand','9123456780',0,'Erode',NULL,'vicky@gmail.com','','Aadhaar','',NULL,'638001','Tamil Nadu');
/*!40000 ALTER TABLE `members_member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members_memberdocument`
--

DROP TABLE IF EXISTS `members_memberdocument`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `members_memberdocument` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `document_type` varchar(20) NOT NULL,
  `document_file` varchar(100) NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `member_id` bigint(20) NOT NULL,
  `admin_notes` longtext DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `members_memberdocument_member_id_5e914cf4_fk_members_member_id` (`member_id`),
  CONSTRAINT `members_memberdocument_member_id_5e914cf4_fk_members_member_id` FOREIGN KEY (`member_id`) REFERENCES `members_member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members_memberdocument`
--

LOCK TABLES `members_memberdocument` WRITE;
/*!40000 ALTER TABLE `members_memberdocument` DISABLE KEYS */;
/*!40000 ALTER TABLE `members_memberdocument` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications_notification`
--

DROP TABLE IF EXISTS `notifications_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications_notification` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `message` longtext NOT NULL,
  `priority` varchar(20) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_notification_user_id_b5e8c0ff_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `notifications_notification_user_id_b5e8c0ff_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications_notification`
--

LOCK TABLES `notifications_notification` WRITE;
/*!40000 ALTER TABLE `notifications_notification` DISABLE KEYS */;
INSERT INTO `notifications_notification` VALUES (2,'Pending Cash Handover','Staff \'Mani Mani\' requested handover for ₹1000.00. Please review Branch Handovers panel.','warning',1,'2026-04-09 08:12:53.677769',1),(3,'Handover Approved','Your cash handover of ₹1000.00 on Apr 09 has been verified & approved by admin.','success',1,'2026-04-09 08:13:36.049931',3),(4,'New Payment Evidence','Proof submitted for Roki (₹1000.00). Review required.','info',1,'2026-04-09 12:11:47.986520',1),(5,'Payment Rejected','Your payment proof was rejected. Reason: Invalid transaction details or screenshot.. Please contact support.','danger',1,'2026-04-09 12:12:13.103874',2),(8,'New Payment Evidence','Proof submitted for Roki (₹1000.00). Review required.','info',1,'2026-04-09 12:48:30.835241',1),(9,'Payment Verified','Good news! Your payment of ₹1000.00 for Gold has been verified and approved.','success',1,'2026-04-09 12:49:04.722629',2),(10,'Test 50%Off','Welcome to Smart Chit Fund ','info',1,'2026-04-10 05:04:15.933414',1),(12,'Test 50%Off','Welcome to Smart Chit Fund ','info',1,'2026-04-10 05:04:15.967222',3),(14,'New Payment Evidence','Proof submitted for Jessica (₹1000.00). Review required.','info',1,'2026-04-10 05:22:39.534270',1),(15,'Payment Rejected','Your payment proof was rejected. Reason: Invalid transaction details or screenshot.. Please contact support.','danger',0,'2026-04-10 05:26:58.676126',4),(16,'Offer for EducationLoan','75%Off for EducationLoan','info',1,'2026-04-18 07:01:58.344231',1),(18,'Offer for EducationLoan','75%Off for EducationLoan','info',0,'2026-04-18 07:01:58.683773',3),(19,'Offer for EducationLoan','75%Off for EducationLoan','info',0,'2026-04-18 07:01:58.756351',4),(21,'Offer for EducationLoan','75%Off for EducationLoan','info',0,'2026-04-18 07:01:58.987773',6),(22,'Offer for EducationLoan','75%Off for EducationLoan','info',1,'2026-04-18 07:01:59.055727',7);
/*!40000 ALTER TABLE `notifications_notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments_cashhandover`
--

DROP TABLE IF EXISTS `payments_cashhandover`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payments_cashhandover` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `amount` decimal(12,2) NOT NULL,
  `date` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `staff_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `payments_cashhandover_staff_id_5803307a_fk_accounts_user_id` (`staff_id`),
  CONSTRAINT `payments_cashhandover_staff_id_5803307a_fk_accounts_user_id` FOREIGN KEY (`staff_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments_cashhandover`
--

LOCK TABLES `payments_cashhandover` WRITE;
/*!40000 ALTER TABLE `payments_cashhandover` DISABLE KEYS */;
INSERT INTO `payments_cashhandover` VALUES (1,1000.00,'2026-04-09','APPROVED','2026-04-09 08:12:53.660047','2026-04-09 08:13:36.026961',3);
/*!40000 ALTER TABLE `payments_cashhandover` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments_followup`
--

DROP TABLE IF EXISTS `payments_followup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payments_followup` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `note` longtext NOT NULL,
  `reminder_date` date NOT NULL,
  `is_completed` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `member_id` bigint(20) NOT NULL,
  `staff_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `payments_followup_member_id_c4fa8987_fk_members_member_id` (`member_id`),
  KEY `payments_followup_staff_id_5bfff3ec_fk_accounts_user_id` (`staff_id`),
  CONSTRAINT `payments_followup_member_id_c4fa8987_fk_members_member_id` FOREIGN KEY (`member_id`) REFERENCES `members_member` (`id`),
  CONSTRAINT `payments_followup_staff_id_5bfff3ec_fk_accounts_user_id` FOREIGN KEY (`staff_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments_followup`
--

LOCK TABLES `payments_followup` WRITE;
/*!40000 ALTER TABLE `payments_followup` DISABLE KEYS */;
INSERT INTO `payments_followup` VALUES (1,'Tomorrow is a last Date','2026-04-10',1,'2026-04-09 09:50:24.238609',1,1);
/*!40000 ALTER TABLE `payments_followup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments_payment`
--

DROP TABLE IF EXISTS `payments_payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payments_payment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `installment_number` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` date DEFAULT NULL,
  `status` varchar(25) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `chit_group_id` bigint(20) NOT NULL,
  `member_id` bigint(20) NOT NULL,
  `dividend_amount` decimal(10,2) NOT NULL,
  `due_date` date DEFAULT NULL,
  `penalty_amount` decimal(10,2) NOT NULL,
  `collected_by_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `payments_payment_chit_group_id_member_id__be9cc769_uniq` (`chit_group_id`,`member_id`,`installment_number`),
  KEY `payments_payment_member_id_2ea62bf9_fk_members_member_id` (`member_id`),
  KEY `payments_payment_collected_by_id_5729f0ec_fk_accounts_user_id` (`collected_by_id`),
  CONSTRAINT `payments_payment_chit_group_id_9e7305b7_fk_chits_chitgroup_id` FOREIGN KEY (`chit_group_id`) REFERENCES `chits_chitgroup` (`id`),
  CONSTRAINT `payments_payment_collected_by_id_5729f0ec_fk_accounts_user_id` FOREIGN KEY (`collected_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `payments_payment_member_id_2ea62bf9_fk_members_member_id` FOREIGN KEY (`member_id`) REFERENCES `members_member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments_payment`
--

LOCK TABLES `payments_payment` WRITE;
/*!40000 ALTER TABLE `payments_payment` DISABLE KEYS */;
INSERT INTO `payments_payment` VALUES (1,1,1000.00,'2026-04-09','PAID','2026-04-08 12:11:33.929615',1,1,0.00,NULL,0.00,NULL),(2,2,1000.00,'2026-04-09','PAID','2026-04-09 07:42:34.853465',1,1,2500.00,NULL,0.00,3),(3,3,1000.00,'2026-04-09','PAID','2026-04-09 07:45:14.977902',1,1,0.00,NULL,0.00,1),(4,4,1000.00,'2026-04-10','PAID','2026-04-09 07:45:34.229837',1,1,0.00,NULL,0.00,1),(5,1,1000.00,'2026-04-10','PAID','2026-04-10 05:18:50.987795',1,2,0.00,NULL,0.00,3),(6,2,1000.00,'2026-04-15','PAID','2026-04-10 06:05:20.948542',1,2,2500.00,'2026-05-08',0.00,1),(7,1,1000.00,'2026-04-20','PAID','2026-04-20 05:22:29.299500',2,3,0.00,NULL,0.00,NULL),(8,1,1000.00,'2026-04-20','PAID','2026-04-20 05:31:52.895572',2,1,0.00,NULL,0.00,NULL);
/*!40000 ALTER TABLE `payments_payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments_paymentproof`
--

DROP TABLE IF EXISTS `payments_paymentproof`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payments_paymentproof` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `member_name` varchar(255) NOT NULL,
  `phone_no` varchar(15) NOT NULL,
  `transaction_id` varchar(100) NOT NULL,
  `screenshot` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL,
  `admin_notes` longtext DEFAULT NULL,
  `submitted_at` datetime(6) NOT NULL,
  `processed_at` datetime(6) DEFAULT NULL,
  `payment_id` bigint(20) NOT NULL,
  `processed_by_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`),
  UNIQUE KEY `payment_id` (`payment_id`),
  KEY `payments_paymentproo_processed_by_id_b350ba1e_fk_accounts_` (`processed_by_id`),
  CONSTRAINT `payments_paymentproo_processed_by_id_b350ba1e_fk_accounts_` FOREIGN KEY (`processed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `payments_paymentproof_payment_id_bf3d30b1_fk_payments_payment_id` FOREIGN KEY (`payment_id`) REFERENCES `payments_payment` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments_paymentproof`
--

LOCK TABLES `payments_paymentproof` WRITE;
/*!40000 ALTER TABLE `payments_paymentproof` DISABLE KEYS */;
INSERT INTO `payments_paymentproof` VALUES (1,'Roki','9786204074','409823126781','payment_proofs/Copy_of_Maple_Wood_Logo.png','APPROVED','Invalid transaction details or screenshot.','2026-04-09 12:11:47.968397','2026-04-09 12:49:04.692576',3,1),(3,'Jessica','9512364870','409823126785','payment_proofs/Anantha_Kumar_G_Payment_QR.jpeg','REJECTED','Invalid transaction details or screenshot.','2026-04-10 05:22:39.429848','2026-04-10 05:26:58.628458',5,1);
/*!40000 ALTER TABLE `payments_paymentproof` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments_paymentqr`
--

DROP TABLE IF EXISTS `payments_paymentqr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payments_paymentqr` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `qr_code` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments_paymentqr`
--

LOCK TABLES `payments_paymentqr` WRITE;
/*!40000 ALTER TABLE `payments_paymentqr` DISABLE KEYS */;
INSERT INTO `payments_paymentqr` VALUES (4,'Primary QR Code','system/qr_codes/Anantha_Kumar_G_Payment_QR.jpeg',1,'2026-04-10 05:18:28.299272');
/*!40000 ALTER TABLE `payments_paymentqr` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settlements_settlement`
--

DROP TABLE IF EXISTS `settlements_settlement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settlements_settlement` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `total_paid` decimal(12,2) NOT NULL,
  `total_received` decimal(12,2) NOT NULL,
  `dividend` decimal(12,2) NOT NULL,
  `penalty` decimal(12,2) NOT NULL,
  `net_amount` decimal(12,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `closed_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `chit_group_id` bigint(20) NOT NULL,
  `member_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `settlements_settlement_member_id_chit_group_id_7b74395c_uniq` (`member_id`,`chit_group_id`),
  KEY `settlements_settleme_chit_group_id_c0ea071d_fk_chits_chi` (`chit_group_id`),
  CONSTRAINT `settlements_settleme_chit_group_id_c0ea071d_fk_chits_chi` FOREIGN KEY (`chit_group_id`) REFERENCES `chits_chitgroup` (`id`),
  CONSTRAINT `settlements_settlement_member_id_7f747182_fk_members_member_id` FOREIGN KEY (`member_id`) REFERENCES `members_member` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settlements_settlement`
--

LOCK TABLES `settlements_settlement` WRITE;
/*!40000 ALTER TABLE `settlements_settlement` DISABLE KEYS */;
/*!40000 ALTER TABLE `settlements_settlement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_settings_systemsetting`
--

DROP TABLE IF EXISTS `system_settings_systemsetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `system_settings_systemsetting` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `key` varchar(50) NOT NULL,
  `value` longtext NOT NULL,
  `description` varchar(255) NOT NULL,
  `is_editable` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_settings_systemsetting`
--

LOCK TABLES `system_settings_systemsetting` WRITE;
/*!40000 ALTER TABLE `system_settings_systemsetting` DISABLE KEYS */;
INSERT INTO `system_settings_systemsetting` VALUES (1,'CHIT_INTEREST_RATE','0','Default monthly interest rate percentage for late payments.',1,'2026-04-08 10:35:15.316936'),(2,'BID_INCREMENT_STEP','0','Minimum amount a bid must increase in an auction (₹).',1,'2026-04-08 10:35:15.323087'),(3,'PENALTY_GRACE_PERIOD','0','Number of days allowed after due date before late fee applies.',1,'2026-04-08 10:35:15.329330'),(4,'SYSTEM_CURRENCY','INR','Base currency for all financial calculations.',0,'2026-04-08 10:35:15.334410'),(5,'ADMIN_CONTACT_EMAIL','admin@chitfund.com','System-wide contact email for user notifications.',1,'2026-04-08 10:35:15.340576'),(6,'MAX_MEMBERS_PER_CHIT','50','Standard restriction for the number of participants in new groups.',1,'2026-04-08 10:35:15.345787'),(7,'Company_Name','SmartChit Management','The official name of the company',1,'2026-04-08 11:51:44.294955'),(8,'Register_Number','REG-10293847','Legal registration number of the entity',1,'2026-04-08 11:51:44.307752'),(9,'Company_City','Chennai','City where the head office is located',1,'2026-04-08 11:51:44.318872'),(10,'Company_State','Tamil Nadu','State where the head office is located',1,'2026-04-08 11:51:44.323354'),(11,'GST_Number','33AAACM1234F1Z1','GSTIN for tax purposes',1,'2026-04-08 11:51:44.328730');
/*!40000 ALTER TABLE `system_settings_systemsetting` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-22 16:43:39
