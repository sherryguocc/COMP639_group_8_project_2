CREATE DATABASE  IF NOT EXISTS `pirdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `pirdb`;
-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: pirdb
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `adminID` int NOT NULL AUTO_INCREMENT,
  `userNo` varchar(25) NOT NULL,
  `title` varchar(10) NOT NULL,
  `firstName` varchar(50) NOT NULL,
  `lastName` varchar(50) NOT NULL,
  `position` varchar(50) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`adminID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'admin1234567890','Mr','Kevin','Feige','Admin','32345678901','kevin@email.com','$2b$12$/uXx3cpwmnqGqyurJxGoY.Ki82ZgqctKrNmsVy.h0qBeE6GwGDfTi');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking` (
  `bookingID` int NOT NULL AUTO_INCREMENT,
  `customerID` int NOT NULL,
  `plannerID` int DEFAULT NULL,
  `venueOrderID` int DEFAULT NULL,
  `foodOrderID` int DEFAULT NULL,
  `decorOrderID` int DEFAULT NULL,
  `startDate` date NOT NULL,
  `startTime` time NOT NULL,
  `endDate` date NOT NULL,
  `endTime` time NOT NULL,
  `guestsNumber` int DEFAULT NULL,
  `comments` text,
  `status` enum('Pending','Processing','Waiting for Payment','Paid','Completed','Cancelled') DEFAULT NULL,
  `ref_num` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`bookingID`),
  KEY `customerID` (`customerID`),
  KEY `plannerID` (`plannerID`),
  KEY `venueOrderID` (`venueOrderID`),
  KEY `foodOrderID` (`foodOrderID`),
  KEY `decorOrderID` (`decorOrderID`),
  CONSTRAINT `Bookings_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `customer` (`customerID`),
  CONSTRAINT `Bookings_ibfk_2` FOREIGN KEY (`plannerID`) REFERENCES `planner` (`plannerID`),
  CONSTRAINT `Bookings_ibfk_3` FOREIGN KEY (`venueOrderID`) REFERENCES `venueorder` (`venueOrderID`),
  CONSTRAINT `Bookings_ibfk_4` FOREIGN KEY (`foodOrderID`) REFERENCES `menuorder` (`foodOrderID`),
  CONSTRAINT `Bookings_ibfk_5` FOREIGN KEY (`decorOrderID`) REFERENCES `decororder` (`decorOrderID`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking`
--

LOCK TABLES `booking` WRITE;
/*!40000 ALTER TABLE `booking` DISABLE KEYS */;
INSERT INTO `booking` VALUES (18,1001,100,4,4,4,'2023-10-11','10:30:00','2023-10-12','22:30:00',60,NULL,'Completed','a5b640d1-6300-49ac-adb3-e3a946717d4e'),(26,1001,100,12,NULL,NULL,'2023-10-18','08:00:00','2023-10-18','10:00:00',200,NULL,'Completed','d0507d87-a7d3-4985-8a61-557e49333f30'),(29,1001,NULL,15,NULL,7,'2023-10-06','07:30:00','2023-10-09','22:30:00',800,NULL,'Completed','bcce3a0a-42f1-4513-8941-972875d48b69'),(31,1001,100,17,NULL,8,'2023-10-25','08:00:00','2023-10-27','08:00:00',80,'666','Cancelled','8b16e8de-2893-4a35-9b0b-f38ede7532b4'),(32,1001,100,18,5,12,'2023-10-24','07:00:00','2023-11-02','21:00:00',60,'Market Fair','Cancelled','35990733-e349-4d3f-8567-40e6c058e37f'),(33,1001,100,19,NULL,NULL,'2023-11-14','19:00:00','2023-11-19','21:00:00',300,NULL,'Cancelled','92e9cd81-bcbc-4923-8c52-4c67d3368eb2'),(34,1001,100,20,NULL,NULL,'2023-11-27','16:10:00','2023-11-30','00:15:00',500,NULL,'Processing','7fbe6de9-d218-4410-871a-c0aefb450343'),(35,1003,NULL,21,6,13,'2023-11-14','08:00:00','2023-11-15','20:00:00',88,NULL,'Pending','93aef0ef-b7f4-445c-8795-0b10b7d528b2'),(36,1001,NULL,22,NULL,NULL,'2023-11-20','10:00:00','2023-11-26','22:00:00',300,NULL,'Pending','b00120fc-818e-4f48-a530-2ad6c38b5787'),(53,1001,NULL,39,NULL,NULL,'2024-03-08','17:40:00','2024-03-10','16:38:00',200,'None','Pending','2dba4a19-b5e8-4001-a91a-301566b3e197'),(54,1003,NULL,40,NULL,NULL,'2024-02-19','16:49:00','2024-02-25','16:49:00',200,'','Cancelled','eccb418f-d823-4e1e-bd11-757f78aa57d9');
/*!40000 ALTER TABLE `booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calendar`
--

DROP TABLE IF EXISTS `calendar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `calendar` (
  `calendarID` int NOT NULL AUTO_INCREMENT,
  `venueID` int DEFAULT NULL,
  `startDate` date DEFAULT NULL,
  `startTime` time DEFAULT NULL,
  `endDate` date DEFAULT NULL,
  `endTime` time DEFAULT NULL,
  `status` enum('Booked','Unavailable','Available','Maintenance','Holiday','Closed') DEFAULT NULL,
  `bookingID` int DEFAULT NULL,
  PRIMARY KEY (`calendarID`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calendar`
--

LOCK TABLES `calendar` WRITE;
/*!40000 ALTER TABLE `calendar` DISABLE KEYS */;
INSERT INTO `calendar` VALUES (1,1,'2023-11-09','08:00:00','2023-11-09','20:00:00','Holiday',NULL),(4,1,'2023-10-31','08:15:00','2023-10-31','16:15:00','Closed',NULL),(5,1,'2023-10-30','06:00:00','2023-10-30','22:00:00','Maintenance',NULL),(7,1,'2023-10-24','04:00:00','2023-10-24','08:00:00','Closed',NULL),(8,1,'2023-10-27','20:00:00','2023-10-28','21:00:00','Maintenance',NULL),(9,1,'2023-11-04','10:00:00','2023-11-05','12:00:00','Maintenance',NULL),(10,1,'2023-11-01','22:00:00','2023-11-02','08:00:00','Holiday',NULL),(11,1,'2023-10-26','18:00:00','2023-10-26','20:00:00','Available',NULL),(12,4,'2023-10-26','20:00:00','2023-10-26','21:00:00','Closed',NULL),(13,1,'2024-02-08','05:00:00','2024-02-08','07:00:00','Closed',NULL),(14,1,'2023-10-20','08:00:00','2023-10-20','10:00:00','Maintenance',NULL),(15,1,'2023-10-29','03:00:00','2023-10-29','05:00:00','Closed',NULL),(16,1,'2023-10-11','10:30:00','2023-10-12','22:30:00','Booked',18),(17,3,'2023-10-18','08:00:00','2023-10-18','10:00:00','Booked',26),(18,8,'2023-10-06','07:30:00','2023-10-09','22:30:00','Booked',29),(19,6,'2023-10-25','08:00:00','2023-10-27','08:00:00','Booked',31),(20,1,'2023-11-10','17:16:00','2023-11-10','16:16:00','Booked',32),(21,2,'2023-12-09','16:18:00','2023-12-09','17:20:00','Booked',33),(22,4,'2023-10-22','17:20:00','2023-10-22','18:20:00','Booked',34),(23,9,'2023-10-18','16:00:00','2023-10-18','23:30:00','Booked',35),(36,1,'2024-03-08','17:40:00','2024-03-10','16:38:00','Booked',53);
/*!40000 ALTER TABLE `calendar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `customerID` int NOT NULL AUTO_INCREMENT,
  `userNo` varchar(25) NOT NULL,
  `title` varchar(10) DEFAULT NULL,
  `firstName` varchar(50) NOT NULL,
  `lastName` varchar(50) NOT NULL,
  `position` varchar(50) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `DOB` date DEFAULT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `VIP` tinyint DEFAULT '0',
  PRIMARY KEY (`customerID`)
) ENGINE=InnoDB AUTO_INCREMENT=1006 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES (1001,'c36434','Miss','Naomi','Chen','customer','02040804383','naomichen@example.com','666 Dufek Crescent Christchurch',NULL,'$2b$12$YFHraZo.goZqVz7gEsuWhO0UrbHWqOKJ6BeeurcC69p1pclHxWfMK',0),(1003,'c57604','Dr','Jondy','Zhen','customer','02123456789','jondyzhen@example.com','123 Six Six Street,  Auckland','2001-08-08','$2b$12$NtuB8CvH69.JT9HQJqLgA.gbip4V9g3XNLF91nK/z0ysboYrSCcDu',0);
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `decoration`
--

DROP TABLE IF EXISTS `decoration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `decoration` (
  `decorationID` int NOT NULL AUTO_INCREMENT,
  `decorationType` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`decorationID`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `decoration`
--

LOCK TABLES `decoration` WRITE;
/*!40000 ALTER TABLE `decoration` DISABLE KEYS */;
INSERT INTO `decoration` VALUES (1,'Western Wedding Decor',600.00,NULL,'Elegant and romantic decor inspired by Western wedding traditions.'),(2,'Indian Wedding Decor',800.00,NULL,'Vibrant and colorful decor inspired by Indian wedding themes.'),(3,'Chinese Wedding Decor',700.00,NULL,'Traditional and culturally rich decor for Chinese weddings.'),(4,'Party Balloon Decor',80.00,NULL,'Colorful balloon decorations to create a festive party atmosphere.'),(5,'Party Lighting Package',200.00,NULL,'Customized lighting packages to set the mood for your party.'),(6,'Professional Meeting Setup',150.00,NULL,'Sleek and professional setup for corporate meetings.'),(7,'Team Building Props',150.00,NULL,'Engaging props and equipment for team building activities.'),(8,'Exhibition Booth Design',500.00,NULL,'Custom booth designs to showcase your products at expos.'),(9,'Corporate Meeting Setup',150.00,NULL,'Professional setup and branding materials for corporate meetings.'),(10,'Workshop Whiteboard & Markers',50.00,NULL,'Whiteboards and markers for interactive workshops.'),(11,'Sports Event Banners',150.00,NULL,'Large banners and flags to enhance the sports event atmosphere.');
/*!40000 ALTER TABLE `decoration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `decororder`
--

DROP TABLE IF EXISTS `decororder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `decororder` (
  `decorOrderID` int NOT NULL AUTO_INCREMENT,
  `bookingID` int NOT NULL,
  `decorationID` int NOT NULL,
  PRIMARY KEY (`decorOrderID`),
  KEY `bookingID` (`bookingID`),
  KEY `decorationID` (`decorationID`),
  CONSTRAINT `decororder_ibfk_1` FOREIGN KEY (`decorationID`) REFERENCES `decoration` (`decorationID`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `decororder`
--

LOCK TABLES `decororder` WRITE;
/*!40000 ALTER TABLE `decororder` DISABLE KEYS */;
INSERT INTO `decororder` VALUES (4,18,4),(7,29,11),(8,31,7),(12,32,8),(13,35,1);
/*!40000 ALTER TABLE `decororder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guest`
--

DROP TABLE IF EXISTS `guest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest` (
  `guestID` int NOT NULL AUTO_INCREMENT,
  `title` varchar(10) DEFAULT NULL,
  `firstName` varchar(50) NOT NULL,
  `lastName` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `enquery` text NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`guestID`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guest`
--

LOCK TABLES `guest` WRITE;
/*!40000 ALTER TABLE `guest` DISABLE KEYS */;
INSERT INTO `guest` VALUES (1000,'Mr','Dog','Worf','dog@gmail.com','31-10-2023 - Hi, do you serve dog food? -- From Guest: Dog Worf  Email: dog@gmail.com  Phone: N/A',NULL);
/*!40000 ALTER TABLE `guest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu` (
  `foodID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`foodID`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu`
--

LOCK TABLES `menu` WRITE;
/*!40000 ALTER TABLE `menu` DISABLE KEYS */;
INSERT INTO `menu` VALUES (1,'Italian Cuisine',60.00,'Italian.jpg','Enjoy a delightful array of Italian dishes, including pasta, lasagna, and tiramisu, accompanied by a selection of fine Italian wines.'),(2,'Japanese Cuisine',65.00,'Japanese.jpg','Indulge in authentic Japanese flavors with sushi, sashimi, tempura, and more. Paired with traditional sake or green tea'),(3,'Indian Cuisine',40.50,'Indian.jpg','Experience the vibrant flavors of India with dishes like butter chicken, paneer tikka, biryani, and warm naan bread.'),(4,'Mexican Cuisine',35.50,'Mexican.jpg','Savor the spicy and hearty dishes of Mexico, including tacos, enchiladas, and churros, complemented by a refreshing margarita.'),(5,'French Cuisine',55.50,'French.jpg','Delight in the sophisticated flavors of French cuisine with dishes like coq au vin, ratatouille, and crème brûlée, paired with exquisite French wine.'),(6,'Chinese Cuisine',88.88,'Chinese.jpg','Feast on authentic Chinese dishes including dim sum, Peking duck, sweet and sour pork, and kung pao chicken, complemented by a pot of warm, aromatic tea.'),(7,'Breakfast Menu',30.00,'Breakfast.jpg','Start your day right with a hearty American breakfast. Choose from a range of options including pancakes, bacon, eggs, and a cup of fresh coffee or juice.'),(8,'Platters Menu',95.50,'Platters.jpg','Enjoy a diverse array of platters featuring a mix of international flavors. Options include cheese and charcuterie boards, seafood platters, and vegetarian antipasto selections.');
/*!40000 ALTER TABLE `menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menuorder`
--

DROP TABLE IF EXISTS `menuorder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menuorder` (
  `foodOrderID` int NOT NULL AUTO_INCREMENT,
  `bookingID` int NOT NULL,
  `foodID` int NOT NULL,
  PRIMARY KEY (`foodOrderID`),
  KEY `bookingID` (`bookingID`),
  KEY `foodID` (`foodID`),
  CONSTRAINT `menuorder_ibfk_1` FOREIGN KEY (`foodID`) REFERENCES `menu` (`foodID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menuorder`
--

LOCK TABLES `menuorder` WRITE;
/*!40000 ALTER TABLE `menuorder` DISABLE KEYS */;
INSERT INTO `menuorder` VALUES (4,18,4),(5,32,8),(6,35,5);
/*!40000 ALTER TABLE `menuorder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `paymentID` int NOT NULL AUTO_INCREMENT,
  `bookingID` int DEFAULT NULL,
  `customerID` int DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `bankAccount` varchar(50) NOT NULL,
  `paymentDate` date NOT NULL,
  PRIMARY KEY (`paymentID`),
  KEY `bookingID` (`bookingID`),
  KEY `customerID` (`customerID`),
  CONSTRAINT `Payment_ibfk_1` FOREIGN KEY (`bookingID`) REFERENCES `booking` (`bookingID`),
  CONSTRAINT `Payment_ibfk_2` FOREIGN KEY (`customerID`) REFERENCES `customer` (`customerID`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (2,31,1001,2018.25,'0011111122334121','2023-10-14'),(6,31,1001,-1009.13,'0011111122334444','2023-10-16'),(7,32,1001,8662.95,'0011111122334121','2023-10-16'),(10,32,1001,-8662.95,'0011111122334444','2023-10-16'),(11,32,1001,-4331.48,'0011111122334444','2023-10-16'),(12,33,1001,6336.50,'0011111122334121','2023-10-17'),(13,33,1001,-6336.50,'0011111122334444','2023-10-17');
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `planner`
--

DROP TABLE IF EXISTS `planner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `planner` (
  `plannerID` int NOT NULL AUTO_INCREMENT,
  `userNo` varchar(25) NOT NULL,
  `title` varchar(10) NOT NULL,
  `firstName` varchar(50) NOT NULL,
  `lastName` varchar(50) NOT NULL,
  `position` varchar(50) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `profileDescription` text,
  `profilePhoto` varchar(255) DEFAULT NULL,
  `Password` varchar(255) NOT NULL,
  PRIMARY KEY (`plannerID`)
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `planner`
--

LOCK TABLES `planner` WRITE;
/*!40000 ALTER TABLE `planner` DISABLE KEYS */;
INSERT INTO `planner` VALUES (100,'p12345','Mr','Jayden','Chen','planner','02040804383','jaydenchen@email.com','3 Dufek Crescent, Christchurch','None','None','$2b$12$/uXx3cpwmnqGqyurJxGoY.Ki82ZgqctKrNmsVy.h0qBeE6GwGDfTi'),(104,'p40882','Mr','Bob','Builder','planner','0273489025','bob@email.com','123 four five six street, Auckland','10 years experience','None','$2b$12$/uXx3cpwmnqGqyurJxGoY.Ki82ZgqctKrNmsVy.h0qBeE6GwGDfTi');
/*!40000 ALTER TABLE `planner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quotation`
--

DROP TABLE IF EXISTS `quotation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quotation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bookingID` int DEFAULT NULL,
  `venue_fee` decimal(10,2) DEFAULT NULL,
  `decoration_fee` decimal(10,2) DEFAULT NULL,
  `menu_price` decimal(10,2) DEFAULT NULL,
  `additional_requirements` text,
  `discounts` decimal(10,2) DEFAULT NULL,
  `notes` text,
  `expiry_date` date DEFAULT NULL,
  `payment_terms` text,
  `total_before_tax` decimal(10,2) DEFAULT NULL,
  `gst_amount` decimal(10,2) DEFAULT NULL,
  `total_including_gst` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `additional_fee` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bookingID` (`bookingID`),
  CONSTRAINT `quotation_ibfk_1` FOREIGN KEY (`bookingID`) REFERENCES `booking` (`bookingID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quotation`
--

LOCK TABLES `quotation` WRITE;
/*!40000 ALTER TABLE `quotation` DISABLE KEYS */;
INSERT INTO `quotation` VALUES (3,31,800.00,150.00,0.00,'Sound system and lighting for the evening party.',195.00,'Client prefers eco-friendly decorations. Ensure all dishes are gluten-free.','2023-10-27','100% upfront',1755.00,263.25,2018.25,NULL,1000),(4,26,200.00,0.00,0.00,'',0.00,'','2023-10-28','100% upfront',200.00,30.00,230.00,NULL,0),(5,32,1640.00,500.00,5730.00,'better lighting and sound system',837.00,'','2023-10-26','100% upfront',7533.00,1129.95,8662.95,NULL,500),(6,33,5300.00,0.00,0.00,'Extra lightings, good sound system',290.00,'','2023-10-31','100% upfront',5510.00,826.50,6336.50,NULL,500);
/*!40000 ALTER TABLE `quotation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reminder`
--

DROP TABLE IF EXISTS `reminder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reminder` (
  `reminderID` int NOT NULL AUTO_INCREMENT,
  `reminderDate` date NOT NULL,
  `reminderType` enum('Public','Individual') NOT NULL,
  `customerID` int DEFAULT NULL,
  `adminID` int DEFAULT NULL,
  `plannerID` int DEFAULT NULL,
  `guestID` int DEFAULT NULL,
  `reminderTxt` text,
  `reminderImg` varchar(255) DEFAULT NULL,
  `status` enum('read','unread') DEFAULT 'unread',
  PRIMARY KEY (`reminderID`),
  KEY `customerID` (`customerID`),
  KEY `adminID` (`adminID`),
  KEY `plannerID` (`plannerID`),
  KEY `guestID` (`guestID`),
  CONSTRAINT `Reminder_ibfk_1` FOREIGN KEY (`customerID`) REFERENCES `customer` (`customerID`),
  CONSTRAINT `Reminder_ibfk_2` FOREIGN KEY (`adminID`) REFERENCES `admin` (`adminID`),
  CONSTRAINT `Reminder_ibfk_3` FOREIGN KEY (`plannerID`) REFERENCES `planner` (`plannerID`),
  CONSTRAINT `Reminder_ibfk_4` FOREIGN KEY (`guestID`) REFERENCES `guest` (`guestID`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reminder`
--

LOCK TABLES `reminder` WRITE;
/*!40000 ALTER TABLE `reminder` DISABLE KEYS */;
INSERT INTO `reminder` VALUES (26,'2023-10-05','Individual',1001,NULL,100,NULL,'Your booking at Elegant Mansion Wedding Venue has been successfully assigned to a planner.',NULL,'read'),(27,'2023-10-10','Individual',1001,NULL,100,NULL,'Your booking at Elegant Mansion Wedding Venue has been successfully assigned to a planner.',NULL,'read'),(28,'2023-10-12','Individual',1001,NULL,100,NULL,'Your booking at Elegant Mansion Wedding Venue has been successfully assigned to a planner.',NULL,'read'),(29,'2023-10-12','Individual',1003,1,NULL,NULL,'hello testing',NULL,'read'),(30,'2023-10-12','Individual',1003,1,NULL,NULL,'hello testing',NULL,'read'),(31,'2023-10-12','Individual',1003,1,NULL,NULL,'hello testing',NULL,'read'),(33,'2023-10-14','Individual',1001,NULL,100,NULL,'Your booking at Elegant Mansion Wedding Venue has been successfully assigned to a planner.',NULL,'unread'),(34,'2023-10-14','Individual',1001,NULL,100,NULL,'Your booking at Elegant Mansion Wedding Venue has been successfully assigned to a planner.',NULL,'unread'),(35,'2023-10-14','Individual',1001,NULL,100,NULL,'Your booking at Corporate Conference Center has been successfully assigned to a planner.',NULL,'unread'),(36,'2023-10-14','Individual',1001,NULL,100,NULL,'Your quote for booking at Corporate Conference Center is ready!',NULL,'unread'),(37,'2023-10-16','Individual',1001,NULL,100,NULL,'Booking for Indoor Team Building Space has been cancelled by Naomi Chen on 2023-10-16.',NULL,'unread'),(38,'2023-10-16','Individual',1001,NULL,100,NULL,'Your quote for booking at Indoor Team Building Space is ready!',NULL,'read'),(39,'2023-10-16','Individual',1001,NULL,100,NULL,'Booking for Indoor Team Building Space has been cancelled by Naomi Chen on 2023-10-16.',NULL,'unread'),(40,'2023-10-16','Individual',1001,NULL,100,NULL,'Booking for Indoor Team Building Space has been cancelled by Naomi Chen on 2023-10-16.',NULL,'unread'),(41,'2023-10-16','Individual',1001,NULL,100,NULL,'Booking for Indoor Team Building Space has been cancelled by Naomi Chen on 2023-10-16.',NULL,'unread'),(42,'2023-10-16','Individual',1001,NULL,100,NULL,'Booking for Indoor Team Building Space has been cancelled by Naomi Chen on 2023-10-16.',NULL,'unread'),(43,'2023-10-17','Individual',1001,NULL,100,NULL,'Your quote for booking at Contemporary Art Gallery is ready!',NULL,'read'),(44,'2023-10-17','Individual',1001,NULL,100,NULL,'Booking for Contemporary Art Gallery has been cancelled by Naomi Chen on 2023-10-17.',NULL,'unread'),(45,'2023-10-29','Individual',1003,NULL,NULL,NULL,'2023-10-29 - Hi Jondy Zhen, Your booking at Mystic Hall has been updated. Please feel free to contact us if you have any questions. -- From Admin Kevin Feige',NULL,'unread'),(46,'2023-10-29','Individual',NULL,NULL,NULL,NULL,'2023-10-29 - Hi None, Your assigned job at Mystic Hall has some changes, please check your bookings. -- From Admin Kevin Feige',NULL,'unread'),(47,'2023-10-29','Individual',1003,NULL,NULL,NULL,'Hi Jondy Zhen, your booking at Mystic Hall has been cancelled. If you have any questions please feel free to contact us. -- From Admin Kevin Feige',NULL,'unread'),(48,'2023-10-29','Individual',NULL,NULL,NULL,NULL,'Hi None, your job at Mystic Hall has been cancelled, please check your bookings. -- From Admin Kevin Feige',NULL,'unread'),(49,'2023-10-31','Individual',NULL,1,NULL,1000,'31-10-2023 - Hi, do you serve dog food? -- From Guest: Dog Worf  Email: dog@gmail.com  Phone: N/A',NULL,'unread');
/*!40000 ALTER TABLE `reminder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venue`
--

DROP TABLE IF EXISTS `venue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venue` (
  `venueID` int NOT NULL AUTO_INCREMENT,
  `venueName` varchar(255) NOT NULL,
  `eventArea` decimal(10,2) NOT NULL,
  `maxCapacity` int NOT NULL,
  `location` varchar(255) NOT NULL,
  `status` enum('Active','Inactive') NOT NULL DEFAULT 'Active',
  `dailyPrice` decimal(10,2) DEFAULT NULL,
  `hourlyPrice` decimal(10,2) DEFAULT NULL,
  `description` text,
  `rented` tinyint DEFAULT NULL,
  `image` json DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`venueID`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venue`
--

LOCK TABLES `venue` WRITE;
/*!40000 ALTER TABLE `venue` DISABLE KEYS */;
INSERT INTO `venue` VALUES (1,'Elegant Mansion Wedding Venue',300.00,200,'Romantic Lakeside','Active',1200.00,150.00,'A luxurious mansion with a lakeside view, perfect for elegant weddings and receptions.',0,'[\"https://media.istockphoto.com/id/1177485677/photo/table-setting-for-an-event-party-or-wedding-reception.jpg?s=1024x1024&w=is&k=20&c=b71LRf6D0bHp8FLoThQrczlQbXTtX3S2Ne-hX-LqLwU=\", \"https://media.istockphoto.com/id/1184628725/photo/3d-wedding-reception-background-illustration.jpg?s=1024x1024&w=is&k=20&c=0m3iJMQ2gPO07dNt_qwL9vkn0UJ_DOGJ5w8t73ZFxPk=\", \"https://media.istockphoto.com/id/479977238/photo/table-setting-for-an-event-party-or-wedding-reception.jpg?s=1024x1024&w=is&k=20&c=qti63rRq16bK0FPyjd6Jngc0U5zSVLfYf1_u5wtT9Oc=\"]','wedding'),(2,'Intimate Garden Wedding Venue',200.00,150,'Enchanted Gardens','Active',800.00,120.00,'A charming garden venue, ideal for intimate and romantic weddings.',0,'[\"https://cloudfront.slrlounge.com/wp-content/uploads/2018/09/wedding-reception-ballroom-photography-800x400.jpg\", \"https://img.freepik.com/free-photo/decorated-table-setting-wedding-celebration_181624-4606.jpg?w=826&t=st=1696239889~exp=1696240489~hmac=b07b9f680d6e11097be01e32949ad82167f5631dc1369502a4653b85538506c4\", \"https://img.freepik.com/premium-photo/festive-table-decoration-elements-flora-luxury-hall_174350-888.jpg?w=826\"]','wedding, indoor'),(3,'Corporate Conference Center',600.00,500,'Downtown Business District','Active',800.00,100.00,'State-of-the-art conference facilities in the heart of the business district, perfect for corporate conferences.',0,'[\"https://www.iino.co.jp/hall/en/assets/img/guide/conferencecenter/img_01.png\", \"https://www.ppic.org/wp-content/uploads/bcc-option-1-1280x576.jpg\", \"https://www.iino.co.jp/hall/en/assets/img/guide/conferencecenter/img_00.png\"]','conference, meeting, indoor'),(4,'Executive Boardroom',40.00,30,'City Center','Active',600.00,80.00,'An exclusive boardroom with modern amenities, suitable for high-profile meetings.',0,'[\"https://media.extron.com/public/img/mktg/boardroom_header.jpg\", \"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLB1ruOPGfUzNHFBKBfayENgRlGT4vl83hLprnjJdDkOAKHail82yWFzjnmoFzewXoX4E&usqp=CAU\", \"https://olathe.k-state.edu/images/rooms/board-room.jpg\", \"https://olathe.k-state.edu/images/.private_ldp/a292593/production/master/a22d6543-7cc0-4c7f-a05d-dbba1912776a.jpg\", \"https://olathe.k-state.edu/images/.private_ldp/a292593/production/master/6ed1eaa6-c395-4dc6-abc4-0588f6b484c0.jpg\"]','conference, meeting, indoor'),(5,'Adventure Team Building Center',150.00,100,'Scenic Wilderness','Active',500.00,70.00,'An outdoor adventure center designed for team building activities, including ropes courses and team challenges.',0,'[\"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQa8DGiiCwTtPC9y5-inI-p5A9GEqqmvOIG4ui_eJrezQpO8-jQWeznEZaDeUvZCrh-e0s&usqp=CAU\", \"https://www.outlife.in/uploads/6/1/9/7/6197204/published/1-7.jpg?1604628862\", \"https://i.pinimg.com/originals/51/80/d5/5180d59a36d240cfd7e650ff76d13836.jpg\", \"https://static.wixstatic.com/media/a4989e_c9ce76bb84ec48d0a90810678dc86298~mv2_d_3600_2400_s_4_2.jpg/v1/fill/w_640,h_426,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/a4989e_c9ce76bb84ec48d0a90810678dc86298~mv2_d_3600_2400_s_4_2.jpg\"]','meeting, team building, indoor'),(6,'Indoor Team Building Space',120.00,80,'Downtown Loft','Active',400.00,60.00,'A versatile indoor space with team-building games and activities, ideal for fostering team spirit.',0,'[\"https://white-rhino.co.uk/wp-content/uploads/2014/12/Indoor-Team-Building-Venues.jpg\", \"https://www.experiential-training.com/wp-content/uploads/2013/12/RI-Blindfold.jpg\", \"https://www.outbackteambuilding.com/media/blog-featured/minute-to-win-it-indoor-team-building.jpg\"]','meeting, team building, indoor'),(7,'Contemporary Art Gallery',400.00,300,'Artistic District','Active',1000.00,150.00,'A spacious art gallery showcasing contemporary art, perfect for art exhibitions and cultural events.',0,'[\"https://artgallery.yale.edu/sites/default/files/styles/hero_small/public/2023-01/ag-doc-2201-0001-pub.jpg?h=589f04c2&itok=5ItkOKKN\", \"https://mcasd.org/client-uploads/images/_mcasd_image_1_62x1_1200px_w/MCASD-LJ-1.jpg\", \"https://www.arts.uci.edu/sites/default/files/IMG_5020.JPG\"]','gallery, indoor'),(8,'Exhibition Hall & Convention Center',900.00,800,'Expo Park','Active',1500.00,200.00,'A massive exhibition hall with convention facilities, ideal for large-scale expos and trade shows.',0,'[\"https://www.bcec.com.au/wp-content/uploads/2018/08/EXHIBITION_HALL_Expo_1.jpg\", \"https://signatureboston.s3.amazonaws.com/assets/made/images/remote/http_s3.amazonaws.com/signatureboston/2column/BCEC_ExhibitHall1_670_376.jpg\", \"https://kyconvention.imgix.net/2022/12/2QOZwEwL-LbrStbLy-LargeExhibitHall-Hero.jpg?fm=jpg&ixlib=php-3.3.1&auto=compress&ar=211:100&w=1055&h=500&fit=crop&crop=top\"]','Exhibition, indoor'),(9,'Grand Ballroom Party Venue',400.00,300,'Luxury Hotel','Active',1200.00,180.00,'A grand ballroom in a luxury hotel, perfect for hosting extravagant parties and gala dinners.',0,'[\"https://images.prismic.io/the-grand/824afabe-1dd6-470f-82a9-190196deee51_gallery-ballroom-08.jpg?auto=compress,format\", \"https://edqkvt6c5r7.exactdn.com/wp-content/uploads/2019/07/grand-ballroom-at-hgc-brisbane-venue-maestro-function-room-2.jpg?strip=all&lossy=1&ssl=1\", \"https://spalbastaging.s3.ap-south-1.amazonaws.com/venue_images/1667202252603-Grand%20Ballroom%20-%20TOGk%20Banquet%20Hall.png\"]','party, indoor'),(10,'Cozy Lounge & Bar',100.00,80,'Downtown Lounge','Active',800.00,120.00,'A stylish lounge and bar with a cozy atmosphere, ideal for intimate parties and cocktail events.',0,'[\"https://cdn.vox-cdn.com/thumbor/3lTM4_ZYVHjC4Hvt5hgZBRR-BUY=/0x69:960x572/fit-in/1200x630/cdn.vox-cdn.com/uploads/chorus_asset/file/10470919/whiskey_library2.jpg\", \"https://www.freep.com/gcdn/presto/2022/09/29/PDTF/4174cc77-0b85-4edc-b25b-255b076e305a-DSC_3556.jpg?width=660&height=374&fit=crop&format=pjpg&auto=webp\", \"https://www.kimptonhotels.com/blog/wp-content/uploads/2013/01/aspen-1024x792.jpg\"]','party, indoor'),(11,'Executive Meeting Room',30.00,20,'Business Park','Active',500.00,70.00,'A high-end executive meeting room with a modern design, suitable for executive board meetings and strategy sessions.',0,'[\"https://images.ctfassets.net/osq47g2esuw5/5rcK0U3uY4jzVcsr9d2XM/3c9ebe552ef1031251671b55cf01149b/Executive_Meeting_-_F_G_H_-_CISCO_WALL_FINISH.jpg?w=2880&h=1620&fl=progressive&q=35&fm=jpg\", \"https://www.lottehotel.com/content/dam/lotte-hotel/lotte/seoul/facilities/business/executive-tower-meeting-room/191114-1-2000-fac-LTSE.jpg.thumb.768.768.jpg\", \"https://www.executivecentre.com/wp-content/uploads/2020/10/img-meetingroomrental_meetingroom.jpg\"]','meeting, indoor'),(12,'Tech Startup Collaboration Space',60.00,50,'Innovation Hub','Active',400.00,60.00,'A collaborative workspace for tech startups, equipped with the latest technology for innovation-driven meetings.',0,'[\"https://www.acquisition-international.com/wp-content/uploads/2021/02/co-working-space.jpg\", \"https://canvasoffices.co.uk/wp-content/uploads/2019/07/Team-at-work-for-video-stills-.jpg\", \"https://downtowntampaoffice.com/wp-content/uploads/2017/11/law-office-coworking-space-Tampa.jpg\"]','meeting, indoor'),(13,'Creative Workshop Studio',50.00,40,'Artistic Quarter','Active',600.00,90.00,'A creative studio space with natural light, perfect for hands-on workshops and artistic sessions.',0,'[\"https://subsites-newsroom.imgix.net/sites/pinnews/files/post_main_content_image/2018-01/Pinfluencers-1168.jpg?ixlib=php-3.3.1&s=69a7f1de670b236229752290d36c9b4a\", \"https://headbox-media.imgix.net/uploads/space_photo/filename/59105/StudioLune1.jpg?auto=format&ar=3%3A2&fit=crop&q=60&ixlib=react-9.5.4\", \"https://images.pexels.com/photos/10322846/pexels-photo-10322846.jpeg?auto=compress&cs=tinysrgb&w=400\"]','workshop, lab, indoor'),(14,'Tech Workshop Lab',80.00,60,'Tech Hub','Active',450.00,70.00,'A tech workshop lab equipped with cutting-edge tools and equipment, ideal for tech-focused workshops and training sessions.',0,'[\"https://pu.edu.lb/sites/default/files/technical-workshop_0.jpg\", \"https://vignanits.ac.in/wp-content/uploads/2020/07/106.jpg\", \"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQF87E0n5W965GAqbeO0nf0vUnTKLSdPf8fz6RWDJmia0QlONbW9Q9W8dTgZgpvuh7h_c0&usqp=CAU\"]','workshop, lab, indoor'),(15,'Stadium Arena',12000.00,10000,'Sports Complex','Active',3000.00,450.00,'A massive stadium arena with seating for thousands, suitable for major sports events and tournaments.',0,'[\"https://ungerboeckdotcomassets.blob.core.windows.net/volumes/content/articles/_wide/shutterstock_1912601503-1.jpg\", \"https://img.fcbayern.com/image/upload/v1601458426/cms/public/images/allianz-arena/stadion-innenraum/aa_haupttribuene.jpg\", \"https://ccc.govt.nz/assets/Images/The-Council/Future-projects/Low_DD_fieldofView__ResizedImageWzg1NSw0MDBd.jpg\"]','stadium, outdoor'),(16,'Indoor Sports Facility',600.00,500,'Sports Park','Active',1800.00,260.00,'A versatile indoor sports facility, perfect for smaller sports events and competitions.',0,'[\"https://hoovermetcomplex.com/wp-content/uploads/2019/06/Indoor-sports-complex-basketball-courts.jpg\", \"https://integralspor.com/uploads/facility/list/2000-kisilik-kapali-spor-salonlari-img-1.jpg\", \"https://cdn1.sportngin.com/attachments/photo/ceb9-157252725/SportsExpoweb_large.jpg\"]','stadium, indoor'),(18,'Mystic Hall',350.00,250,'123 Magic Street, Wonderland','Active',3000.00,350.00,'Mystic Hall is an enchanting venue that sits at the heart of Wonderland. With its magical ambiance and stunning architecture, it\'s the perfect place for fairy-tale weddings, grand balls, and memorable events. The venue boasts a grand hall with crystal chandeliers, a spacious dance floor, and a beautiful garden view. Complemented by top-notch facilities and a dedicated staff, Mystic Hall promises an event like no other.',0,'[\"https://images.pexels.com/photos/13278413/pexels-photo-13278413.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1\\r\", \"https://images.pexels.com/photos/11093767/pexels-photo-11093767.jpeg?auto=compress&cs=tinysrgb&w=600&lazy=load\\r\", \"https://images.pexels.com/photos/15878186/pexels-photo-15878186/free-photo-of-columns-under-ornamented-ceiling.jpeg?auto=compress&cs=tinysrgb&w=400&lazy=load\"]','gallery, indoor');
/*!40000 ALTER TABLE `venue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venueorder`
--

DROP TABLE IF EXISTS `venueorder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venueorder` (
  `venueOrderID` int NOT NULL AUTO_INCREMENT,
  `venueID` int NOT NULL,
  `bookingID` int NOT NULL,
  `plannerID` int DEFAULT NULL,
  PRIMARY KEY (`venueOrderID`),
  KEY `venueID` (`venueID`),
  KEY `bookingID` (`bookingID`),
  KEY `plannerID` (`plannerID`),
  CONSTRAINT `VenueOrder_ibfk_1` FOREIGN KEY (`venueID`) REFERENCES `venue` (`venueID`),
  CONSTRAINT `VenueOrder_ibfk_2` FOREIGN KEY (`plannerID`) REFERENCES `planner` (`plannerID`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venueorder`
--

LOCK TABLES `venueorder` WRITE;
/*!40000 ALTER TABLE `venueorder` DISABLE KEYS */;
INSERT INTO `venueorder` VALUES (4,1,18,NULL),(12,3,26,NULL),(13,8,27,NULL),(14,3,28,NULL),(15,8,29,NULL),(17,6,31,NULL),(18,6,32,NULL),(19,7,33,NULL),(20,8,34,NULL),(21,1,35,NULL),(22,7,36,NULL),(23,1,37,NULL),(24,1,38,NULL),(25,1,39,NULL),(26,1,40,NULL),(27,1,41,NULL),(28,1,42,NULL),(29,1,43,NULL),(30,1,44,NULL),(31,1,45,NULL),(32,1,46,NULL),(33,1,47,NULL),(34,1,48,NULL),(35,1,49,NULL),(39,1,53,NULL),(40,18,54,NULL);
/*!40000 ALTER TABLE `venueorder` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-10-31 13:19:03
