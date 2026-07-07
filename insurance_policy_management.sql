-- MySQL dump 10.13  Distrib 8.4.10, for Linux (x86_64)
--
-- Host: localhost    Database: insurance_policy_management
-- ------------------------------------------------------
-- Server version	8.4.10-0ubuntu0.26.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,'System Admin','admin','admin123','9999990001',NULL,1);
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `agents`
--

DROP TABLE IF EXISTS `agents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `commission_rate` decimal(5,2) NOT NULL DEFAULT '5.00',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `picture` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agents`
--

LOCK TABLES `agents` WRITE;
/*!40000 ALTER TABLE `agents` DISABLE KEYS */;
INSERT INTO `agents` VALUES (1,'Rajesh Agent','ragent','agent123','9999990002',NULL,5.00,1,'2026-07-01 13:18:58',NULL);
/*!40000 ALTER TABLE `agents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `claim_documents`
--

DROP TABLE IF EXISTS `claim_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `claim_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `claim_id` int NOT NULL,
  `document_type` varchar(80) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `uploaded_by` int NOT NULL,
  `uploaded_role` enum('admin','agent','policyholder') NOT NULL DEFAULT 'policyholder',
  `uploaded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_claim_doc_claim` (`claim_id`),
  CONSTRAINT `fk_claim_doc_claim` FOREIGN KEY (`claim_id`) REFERENCES `claims` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `claim_documents`
--

LOCK TABLES `claim_documents` WRITE;
/*!40000 ALTER TABLE `claim_documents` DISABLE KEYS */;
/*!40000 ALTER TABLE `claim_documents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `claim_events`
--

DROP TABLE IF EXISTS `claim_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `claim_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `claim_id` int NOT NULL,
  `event_type` varchar(40) NOT NULL,
  `from_status` varchar(20) DEFAULT NULL,
  `to_status` varchar(20) DEFAULT NULL,
  `note` text,
  `actor_id` int NOT NULL,
  `actor_role` enum('admin','agent','policyholder') NOT NULL DEFAULT 'admin',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `actor_id` (`actor_id`),
  KEY `idx_claim_event_claim` (`claim_id`),
  CONSTRAINT `claim_events_ibfk_1` FOREIGN KEY (`claim_id`) REFERENCES `claims` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `claim_events`
--

LOCK TABLES `claim_events` WRITE;
/*!40000 ALTER TABLE `claim_events` DISABLE KEYS */;
INSERT INTO `claim_events` VALUES (1,1,'status_change',NULL,'submitted','Claim submitted by policyholder',1,'policyholder','2026-06-18 12:56:27'),(2,2,'status_change',NULL,'submitted','Claim submitted',2,'policyholder','2026-06-18 12:56:27'),(3,2,'status_change','submitted','under_review','Review started by admin',1,'admin','2026-06-18 12:56:27'),(4,3,'status_change',NULL,'submitted','Claim submitted',1,'policyholder','2026-06-18 12:56:27'),(5,3,'status_change','under_review','approved','Approved after verification',1,'admin','2026-06-18 12:56:27');
/*!40000 ALTER TABLE `claim_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `claims`
--

DROP TABLE IF EXISTS `claims`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `claims` (
  `id` int NOT NULL AUTO_INCREMENT,
  `claim_number` varchar(30) NOT NULL,
  `policy_id` int NOT NULL,
  `submitted_by` int NOT NULL,
  `incident_date` date NOT NULL,
  `description` text NOT NULL,
  `amount_requested` decimal(10,2) NOT NULL,
  `approved_amount` decimal(10,2) DEFAULT NULL,
  `status` enum('submitted','under_review','approved','rejected','paid') DEFAULT 'submitted',
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `closed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `claim_number` (`claim_number`),
  KEY `idx_claim_policy` (`policy_id`),
  KEY `idx_claim_status` (`status`),
  KEY `fk_claims_submitted_by` (`submitted_by`),
  CONSTRAINT `claims_ibfk_1` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`),
  CONSTRAINT `fk_claims_submitted_by` FOREIGN KEY (`submitted_by`) REFERENCES `policy_holders` (`id`),
  CONSTRAINT `claims_chk_1` CHECK ((`amount_requested` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `claims`
--

LOCK TABLES `claims` WRITE;
/*!40000 ALTER TABLE `claims` DISABLE KEYS */;
INSERT INTO `claims` VALUES (1,'CLM-2026-0001',1,1,'2026-05-10','Minor hospitalization claim',25000.00,NULL,'submitted','2026-06-18 12:56:05',NULL),(2,'CLM-2026-0002',2,2,'2026-05-15','Surgery reimbursement claim',50000.00,NULL,'under_review','2026-06-18 12:56:05',NULL),(3,'CLM-2026-0003',1,1,'2026-04-05','Accidental injury claim',30000.00,25000.00,'approved','2026-06-18 12:56:05',NULL);
/*!40000 ALTER TABLE `claims` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nominations`
--

DROP TABLE IF EXISTS `nominations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nominations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `policy_id` int NOT NULL,
  `nominee_name` varchar(150) NOT NULL,
  `relationship` varchar(50) NOT NULL,
  `share_percent` decimal(5,2) NOT NULL DEFAULT '100.00',
  `contact_phone` varchar(15) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_nomination_policy` (`policy_id`),
  CONSTRAINT `fk_nominations_policy` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_share_percent` CHECK (((`share_percent` > 0) and (`share_percent` <= 100)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nominations`
--

LOCK TABLES `nominations` WRITE;
/*!40000 ALTER TABLE `nominations` DISABLE KEYS */;
/*!40000 ALTER TABLE `nominations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payouts`
--

DROP TABLE IF EXISTS `payouts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payouts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `claim_id` int NOT NULL,
  `amount_approved` decimal(10,2) NOT NULL,
  `payout_method` varchar(30) DEFAULT NULL,
  `payout_reference` varchar(100) DEFAULT NULL,
  `payout_date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `claim_id` (`claim_id`),
  CONSTRAINT `payouts_ibfk_1` FOREIGN KEY (`claim_id`) REFERENCES `claims` (`id`) ON DELETE CASCADE,
  CONSTRAINT `payouts_chk_1` CHECK ((`amount_approved` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payouts`
--

LOCK TABLES `payouts` WRITE;
/*!40000 ALTER TABLE `payouts` DISABLE KEYS */;
INSERT INTO `payouts` VALUES (1,3,25000.00,'NEFT','NEFT20260001','2026-05-01','2026-06-18 12:56:38');
/*!40000 ALTER TABLE `payouts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policies`
--

DROP TABLE IF EXISTS `policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `policy_number` varchar(30) NOT NULL,
  `policy_type_id` int NOT NULL,
  `policyholder_id` int NOT NULL,
  `agent_id` int DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `annual_premium` decimal(10,2) NOT NULL,
  `sum_assured` decimal(12,2) NOT NULL DEFAULT '0.00',
  `term_years` tinyint NOT NULL DEFAULT '1',
  `grace_period_days` tinyint NOT NULL DEFAULT '30',
  `status` enum('active','lapsed','expired','cancelled') DEFAULT 'active',
  `issued_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `closed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `policy_number` (`policy_number`),
  KEY `policy_type_id` (`policy_type_id`),
  KEY `idx_policyholder` (`policyholder_id`),
  KEY `idx_policy_agent` (`agent_id`),
  CONSTRAINT `fk_policies_agent` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`),
  CONSTRAINT `fk_policies_policyholder` FOREIGN KEY (`policyholder_id`) REFERENCES `policy_holders` (`id`),
  CONSTRAINT `policies_ibfk_1` FOREIGN KEY (`policy_type_id`) REFERENCES `policy_types` (`id`),
  CONSTRAINT `policies_chk_1` CHECK ((`annual_premium` > 0)),
  CONSTRAINT `policies_chk_2` CHECK ((`end_date` > `start_date`))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policies`
--

LOCK TABLES `policies` WRITE;
/*!40000 ALTER TABLE `policies` DISABLE KEYS */;
INSERT INTO `policies` VALUES (1,'POL-2026-0001',1,1,1,'2026-01-01','2027-01-01',12000.00,120000.00,1,30,'active','2026-06-18 12:54:52',NULL),(2,'POL-2026-0002',2,2,1,'2026-02-01','2027-02-01',18000.00,90000.00,1,30,'active','2026-06-18 12:54:52',NULL),(3,'POL-2026-0003',3,3,1,'2026-03-01','2027-03-01',15000.00,45000.00,1,30,'active','2026-06-18 12:54:52',NULL),(4,'POL-2026-0004',1,4,1,'2025-01-01','2026-01-01',12000.00,120000.00,1,30,'lapsed','2026-06-18 12:54:52','2026-01-01 00:00:00');
/*!40000 ALTER TABLE `policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policy_holders`
--

DROP TABLE IF EXISTS `policy_holders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policy_holders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `address` text,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `picture` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policy_holders`
--

LOCK TABLES `policy_holders` WRITE;
/*!40000 ALTER TABLE `policy_holders` DISABLE KEYS */;
INSERT INTO `policy_holders` VALUES (1,'Rahul Sharma','rahul','rahul123','9999990003',NULL,NULL,NULL,1,NULL),(2,'Priya Singh','priya','priya123','9999990004',NULL,NULL,NULL,1,NULL),(3,'Amit Verma','amit','amit123','9999990005',NULL,NULL,NULL,1,NULL),(4,'Neha Gupta','neha','neha123','9999990006',NULL,NULL,NULL,1,NULL);
/*!40000 ALTER TABLE `policy_holders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policy_types`
--

DROP TABLE IF EXISTS `policy_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policy_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `coverage_category` varchar(80) NOT NULL,
  `base_annual_premium` decimal(10,2) NOT NULL,
  `max_coverage_amount` decimal(12,2) NOT NULL DEFAULT '500000.00',
  `min_term_years` tinyint NOT NULL DEFAULT '1',
  `max_term_years` tinyint NOT NULL DEFAULT '30',
  `grace_period_days` tinyint NOT NULL DEFAULT '30',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `chk_policy_type_coverage` CHECK ((`max_coverage_amount` > 0)),
  CONSTRAINT `policy_types_chk_1` CHECK ((`base_annual_premium` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policy_types`
--

LOCK TABLES `policy_types` WRITE;
/*!40000 ALTER TABLE `policy_types` DISABLE KEYS */;
INSERT INTO `policy_types` VALUES (1,'Term Life','Life',12000.00,5000000.00,10,30,30,1,'Life insurance policy'),(2,'Health Plus','Health',18000.00,1000000.00,1,5,30,1,'Comprehensive health insurance'),(3,'Motor Secure','Motor',15000.00,1500000.00,1,3,15,1,'Vehicle insurance coverage');
/*!40000 ALTER TABLE `policy_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `premium_schedule`
--

DROP TABLE IF EXISTS `premium_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `premium_schedule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `policy_id` int NOT NULL,
  `installment_number` int NOT NULL,
  `due_date` date NOT NULL,
  `amount` decimal(8,2) NOT NULL,
  `status` enum('pending','paid','overdue','waived') DEFAULT 'pending',
  `paid_at` timestamp NULL DEFAULT NULL,
  `payment_method` varchar(30) DEFAULT NULL,
  `transaction_ref` varchar(100) DEFAULT NULL,
  `penalty_amount` decimal(8,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `policy_id` (`policy_id`,`installment_number`),
  KEY `idx_premium_policy` (`policy_id`),
  KEY `idx_premium_status` (`status`),
  CONSTRAINT `premium_schedule_ibfk_1` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
  CONSTRAINT `premium_schedule_chk_1` CHECK ((`installment_number` > 0)),
  CONSTRAINT `premium_schedule_chk_2` CHECK ((`amount` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `premium_schedule`
--

LOCK TABLES `premium_schedule` WRITE;
/*!40000 ALTER TABLE `premium_schedule` DISABLE KEYS */;
INSERT INTO `premium_schedule` VALUES (1,1,1,'2026-02-01',1000.00,'paid',NULL,NULL,NULL,0.00),(2,1,2,'2026-03-01',1000.00,'paid',NULL,NULL,NULL,0.00),(3,1,3,'2026-04-01',1000.00,'paid',NULL,NULL,NULL,0.00),(4,1,4,'2026-05-01',1000.00,'paid','2026-07-03 03:44:05',NULL,NULL,0.00),(5,1,5,'2026-06-01',1000.00,'pending',NULL,NULL,NULL,0.00),(6,1,6,'2026-07-01',1000.00,'pending',NULL,NULL,NULL,0.00),(7,2,1,'2026-03-01',1500.00,'paid',NULL,NULL,NULL,0.00),(8,2,2,'2026-04-01',1500.00,'paid',NULL,NULL,NULL,0.00),(9,2,3,'2026-05-01',1500.00,'paid','2026-07-01 13:53:54',NULL,NULL,0.00),(10,2,4,'2026-06-01',1500.00,'pending',NULL,NULL,NULL,0.00),(11,2,5,'2026-07-01',1500.00,'pending',NULL,NULL,NULL,0.00),(12,2,6,'2026-08-01',1500.00,'paid','2026-07-01 13:53:41',NULL,NULL,0.00),(13,3,1,'2026-04-01',1250.00,'paid',NULL,NULL,NULL,0.00),(14,3,2,'2026-05-01',1250.00,'paid','2026-07-07 04:30:44',NULL,NULL,0.00),(15,3,3,'2026-06-01',1250.00,'pending',NULL,NULL,NULL,0.00),(16,3,4,'2026-07-01',1250.00,'pending',NULL,NULL,NULL,0.00),(17,3,5,'2026-08-01',1250.00,'pending',NULL,NULL,NULL,0.00),(18,3,6,'2026-09-01',1250.00,'pending',NULL,NULL,NULL,0.00),(19,4,1,'2025-02-01',1000.00,'paid',NULL,NULL,NULL,0.00),(20,4,2,'2025-03-01',1000.00,'paid',NULL,NULL,NULL,0.00),(21,4,3,'2025-04-01',1000.00,'paid',NULL,NULL,NULL,0.00),(22,4,4,'2025-05-01',1000.00,'paid','2026-07-01 13:54:12',NULL,NULL,0.00),(23,4,5,'2025-06-01',1000.00,'overdue',NULL,NULL,NULL,0.00),(24,4,6,'2025-07-01',1000.00,'overdue',NULL,NULL,NULL,0.00);
/*!40000 ALTER TABLE `premium_schedule` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-07  4:34:18
