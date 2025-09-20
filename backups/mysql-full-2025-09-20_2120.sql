/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.14-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: api_creative
-- ------------------------------------------------------
-- Server version	10.11.14-MariaDB

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
-- Table structure for table `admin_backend_final_admin`
--

DROP TABLE IF EXISTS `admin_backend_final_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_admin` (
  `admin_id` varchar(100) NOT NULL,
  `admin_name` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`admin_id`),
  KEY `admin_backend_final_admin_admin_name_76f5d876` (`admin_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_admin`
--

LOCK TABLES `admin_backend_final_admin` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_admin` DISABLE KEYS */;
INSERT INTO `admin_backend_final_admin` VALUES
('AAAN-CU-001','Ahsan','Creative@2025','2025-09-05 13:17:12.116802','2025-09-05 13:17:12.116825'),
('AAIN-SU-001','admin','Yasir140786@','2025-09-01 11:41:19.254893','2025-09-01 11:41:19.254917'),
('ATST-SU-001','test','test','2025-08-29 06:40:40.486552','2025-08-29 06:40:40.486580');
/*!40000 ALTER TABLE `admin_backend_final_admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_adminrole`
--

DROP TABLE IF EXISTS `admin_backend_final_adminrole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_adminrole` (
  `role_id` varchar(100) NOT NULL,
  `role_name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `access_pages` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`access_pages`)),
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`role_id`),
  KEY `admin_backend_final_adminrole_role_name_131e7def` (`role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_adminrole`
--

LOCK TABLES `admin_backend_final_adminrole` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_adminrole` DISABLE KEYS */;
INSERT INTO `admin_backend_final_adminrole` VALUES
('R-Custom Role','Custom Role','Custom Role role','[\"Manage Categories\", \"Inventory\", \"Navbar\", \"Products Section\", \"Media Library\"]','2025-09-05 13:17:12.114736','2025-09-05 13:17:12.114763'),
('R-Super Admin','Super Admin','Super Admin role','[\"Dashboard\", \"Products Section\", \"Blog\", \"Settings\", \"First Carousel\", \"Media Library\", \"Notifications\", \"Testimonials\", \"Second Carousel\", \"Hero Banner\", \"Manage Categories\", \"Orders\", \"Inventory\", \"Google Analytics\", \"New Account\", \"Google Settings\", \"Navbar\", \"User View\", \"Blog View\"]','2025-08-29 06:39:25.381954','2025-08-29 06:39:25.381985');
/*!40000 ALTER TABLE `admin_backend_final_adminrole` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_adminrolemap`
--

DROP TABLE IF EXISTS `admin_backend_final_adminrolemap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_adminrolemap` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `admin_id` varchar(100) NOT NULL,
  `role_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_backe_admin_i_28e7f2_idx` (`admin_id`),
  KEY `admin_backe_role_id_198918_idx` (`role_id`),
  CONSTRAINT `admin_backend_final__admin_id_1fe6e44c_fk_admin_bac` FOREIGN KEY (`admin_id`) REFERENCES `admin_backend_final_admin` (`admin_id`),
  CONSTRAINT `admin_backend_final__role_id_101187a2_fk_admin_bac` FOREIGN KEY (`role_id`) REFERENCES `admin_backend_final_adminrole` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_adminrolemap`
--

LOCK TABLES `admin_backend_final_adminrolemap` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_adminrolemap` DISABLE KEYS */;
INSERT INTO `admin_backend_final_adminrolemap` VALUES
(2,'2025-08-29 06:40:40.488914','ATST-SU-001','R-Super Admin'),
(3,'2025-09-01 11:41:19.256924','AAIN-SU-001','R-Super Admin'),
(4,'2025-09-05 13:17:12.118338','AAAN-CU-001','R-Custom Role');
/*!40000 ALTER TABLE `admin_backend_final_adminrolemap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_attribute`
--

DROP TABLE IF EXISTS `admin_backend_final_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_attribute` (
  `attr_id` varchar(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `label` varchar(255) NOT NULL,
  `price_delta` decimal(10,2) DEFAULT NULL,
  `is_default` tinyint(1) NOT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  `created_at` datetime(6) NOT NULL,
  `image_id` varchar(100) DEFAULT NULL,
  `parent_id` varchar(100) DEFAULT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`attr_id`),
  KEY `admin_backend_final__image_id_444810e9_fk_admin_bac` (`image_id`),
  KEY `admin_backend_final__parent_id_f4d6804d_fk_admin_bac` (`parent_id`),
  KEY `admin_backend_final_attribute_order_41164820` (`order`),
  KEY `admin_backe_product_29293c_idx` (`product_id`,`parent_id`,`order`),
  CONSTRAINT `admin_backend_final__image_id_444810e9_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`),
  CONSTRAINT `admin_backend_final__parent_id_f4d6804d_fk_admin_bac` FOREIGN KEY (`parent_id`) REFERENCES `admin_backend_final_attribute` (`attr_id`),
  CONSTRAINT `admin_backend_final__product_id_fd802c4d_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_attribute`
--

LOCK TABLES `admin_backend_final_attribute` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_attribute` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_attribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_blogcomment`
--

DROP TABLE IF EXISTS `admin_backend_final_blogcomment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_blogcomment` (
  `comment_id` char(32) NOT NULL,
  `name` varchar(120) NOT NULL,
  `email` varchar(254) NOT NULL,
  `website` varchar(200) NOT NULL,
  `comment` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `blog_id` varchar(100) NOT NULL,
  PRIMARY KEY (`comment_id`),
  KEY `admin_backend_final_blogcomment_created_at_0c7cb353` (`created_at`),
  KEY `admin_backe_blog_id_57a798_idx` (`blog_id`),
  KEY `admin_backe_created_f0206e_idx` (`created_at`),
  CONSTRAINT `admin_backend_final__blog_id_50e4407e_fk_admin_bac` FOREIGN KEY (`blog_id`) REFERENCES `admin_backend_final_blogpost` (`blog_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_blogcomment`
--

LOCK TABLES `admin_backend_final_blogcomment` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_blogcomment` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_blogcomment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_blogimage`
--

DROP TABLE IF EXISTS `admin_backend_final_blogimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_blogimage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `caption` longtext NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  `created_at` datetime(6) NOT NULL,
  `blog_id` varchar(100) NOT NULL,
  `image_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_backend_final_blogimage_blog_id_image_id_0751615b_uniq` (`blog_id`,`image_id`),
  KEY `admin_backe_blog_id_be1e82_idx` (`blog_id`),
  KEY `admin_backe_image_i_6e0bb3_idx` (`image_id`),
  CONSTRAINT `admin_backend_final__blog_id_8e2b7fb7_fk_admin_bac` FOREIGN KEY (`blog_id`) REFERENCES `admin_backend_final_blogpost` (`blog_id`),
  CONSTRAINT `admin_backend_final__image_id_197aa43f_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_blogimage`
--

LOCK TABLES `admin_backend_final_blogimage` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_blogimage` DISABLE KEYS */;
INSERT INTO `admin_backend_final_blogimage` VALUES
(1,'',0,0,'2025-09-17 19:04:31.776274','ikrashnekiyatheekk-ff2ae602e9','IMG-180c712c'),
(3,'',0,0,'2025-09-18 13:29:19.997115','ikrashnekiyatheekk-ff2ae602e9','IMG-0c835bfc'),
(4,'',1,0,'2025-09-18 13:29:23.403049','ikrashnekiyatheekk-ff2ae602e9','IMG-d454c742');
/*!40000 ALTER TABLE `admin_backend_final_blogimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_blogpost`
--

DROP TABLE IF EXISTS `admin_backend_final_blogpost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_blogpost` (
  `blog_id` varchar(100) NOT NULL,
  `title` varchar(255) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `content_html` longtext NOT NULL,
  `author` varchar(120) NOT NULL,
  `meta_title` varchar(255) NOT NULL,
  `meta_description` longtext NOT NULL,
  `og_title` varchar(255) NOT NULL,
  `og_image_url` varchar(200) NOT NULL,
  `tags` varchar(255) NOT NULL,
  `schema_enabled` tinyint(1) NOT NULL,
  `publish_date` datetime(6) DEFAULT NULL,
  `draft` tinyint(1) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`blog_id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `admin_backend_final_blogpost_title_f6eba3e5` (`title`),
  KEY `admin_backend_final_blogpost_status_5ffc99d6` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_blogpost`
--

LOCK TABLES `admin_backend_final_blogpost` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_blogpost` DISABLE KEYS */;
INSERT INTO `admin_backend_final_blogpost` VALUES
('ikrashnekiyatheekk-ff2ae602e9','Ikrash ne kiya theek kiya????','right-app-developer','<p>pta koi nai</p>','Akrash Noman','sf','ok','noice','','begharit',0,'2025-09-17 19:04:00.000000',0,'published','2025-09-17 19:04:31.753512','2025-09-18 13:29:23.398452');
/*!40000 ALTER TABLE `admin_backend_final_blogpost` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_callbackrequest`
--

DROP TABLE IF EXISTS `admin_backend_final_callbackrequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_callbackrequest` (
  `callback_id` varchar(100) NOT NULL,
  `sender_id` varchar(100) NOT NULL,
  `contact_info` varchar(255) NOT NULL,
  `message` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`callback_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_callbackrequest`
--

LOCK TABLES `admin_backend_final_callbackrequest` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_callbackrequest` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_callbackrequest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_cart`
--

DROP TABLE IF EXISTS `admin_backend_final_cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_cart` (
  `cart_id` varchar(100) NOT NULL,
  `device_uuid` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`cart_id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `admin_backend_final_cart_device_uuid_95e54bac` (`device_uuid`),
  CONSTRAINT `admin_backend_final__user_id_2a19abda_fk_admin_bac` FOREIGN KEY (`user_id`) REFERENCES `admin_backend_final_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_cart`
--

LOCK TABLES `admin_backend_final_cart` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_cart` DISABLE KEYS */;
INSERT INTO `admin_backend_final_cart` VALUES
('2e2119db-fd5c-4fb5-b41f-5e2ced2a622e','e5a03b72-c4fe-4f39-9252-126dbce355e9','2025-08-29 05:46:24.529712','2025-08-29 05:46:24.529740',NULL),
('5321a782-7749-4a12-9fa7-7579a7b2e50e','72c22fc0-60e2-45c7-98c9-98b98b77f6df','2025-09-09 01:47:58.110780','2025-09-09 01:47:58.110831',NULL),
('6480988f-2fa8-4094-acf0-cebc88f99614','943466a6-9c2e-459b-9321-b979d9e5015c','2025-09-01 12:41:25.493487','2025-09-01 12:41:25.493518',NULL),
('701da2a3-a92a-43c4-a0e4-0cc43ef7c318','e18cad4c-a970-49e0-b166-27d1bf4435a2','2025-09-03 18:22:33.480135','2025-09-03 18:22:33.480167',NULL),
('857642ed-e074-4001-a876-b7a6de1db24e','69c97e4f-3670-4227-a6e2-4292390b0281','2025-08-29 18:12:28.919035','2025-08-29 18:12:28.919061',NULL),
('9860f18d-e06d-448d-9b37-e98280f91a20','8ce887f1-dcc6-4d2e-9e7b-86a692349eee','2025-09-17 07:54:54.473435','2025-09-17 07:54:54.473474',NULL),
('a0746c90-514d-4aa1-a47a-a8b904516300','ba033bdf-cd4e-42df-a8a9-8bba3286a01d','2025-09-03 22:05:57.353357','2025-09-03 22:05:57.353393',NULL),
('a2d098ed-4e59-4ca8-b305-0060d3eb499e','a936858f-0133-4020-aa33-900572161d64','2025-09-01 12:41:34.280304','2025-09-01 12:41:34.280326',NULL),
('ad453003-c7f0-4675-b196-85cccba4d930','468636ba-b660-4839-a673-a3368f74b976','2025-09-10 08:10:27.576518','2025-09-10 08:10:27.576554',NULL),
('b1e02d70-694c-4db4-9fbe-cdc5330ba7e3','37572105-9c1c-4b9a-81aa-a1a2248ddd71','2025-08-29 09:49:22.607815','2025-08-29 09:49:22.607839',NULL),
('eee7d907-8396-462c-88f2-468a47ef39c1','2060d0cf-f34f-4309-a524-e9f69933913b','2025-09-04 22:01:22.158305','2025-09-04 22:01:22.158340',NULL);
/*!40000 ALTER TABLE `admin_backend_final_cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_cartitem`
--

DROP TABLE IF EXISTS `admin_backend_final_cartitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_cartitem` (
  `item_id` varchar(100) NOT NULL,
  `quantity` int(10) unsigned NOT NULL CHECK (`quantity` >= 0),
  `price_per_unit` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `selected_size` varchar(50) DEFAULT NULL,
  `selected_attributes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`selected_attributes`)),
  `variant_signature` varchar(255) NOT NULL,
  `attributes_price_delta` decimal(10,2) NOT NULL,
  `cart_id` varchar(100) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`item_id`),
  KEY `admin_backend_final__cart_id_7cb8dfbd_fk_admin_bac` (`cart_id`),
  KEY `admin_backend_final__product_id_4dce6ecb_fk_admin_bac` (`product_id`),
  KEY `admin_backend_final_cartitem_variant_signature_fff9a23e` (`variant_signature`),
  CONSTRAINT `admin_backend_final__cart_id_7cb8dfbd_fk_admin_bac` FOREIGN KEY (`cart_id`) REFERENCES `admin_backend_final_cart` (`cart_id`),
  CONSTRAINT `admin_backend_final__product_id_4dce6ecb_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_cartitem`
--

LOCK TABLES `admin_backend_final_cartitem` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_cartitem` DISABLE KEYS */;
INSERT INTO `admin_backend_final_cartitem` VALUES
('178fd9c7-efb4-4d97-9971-109ac6bc36cc',1,0.00,0.00,'','{}','size:',0.00,'eee7d907-8396-462c-88f2-468a47ef39c1','PR-CO-001'),
('2b0953f9-372c-4c6b-8f42-9e8c30a858c1',1,0.00,0.00,'','{}','size:',0.00,'a2d098ed-4e59-4ca8-b305-0060d3eb499e','CE-TT-001'),
('94d81849-9aed-4d8b-9f27-b1539ee48083',1,0.00,0.00,'','{}','size:',0.00,'a0746c90-514d-4aa1-a47a-a8b904516300','SP-WB-001'),
('b86f307e-9f76-42cf-b05e-c112680333c0',2,0.00,0.00,'','{}','size:',0.00,'6480988f-2fa8-4094-acf0-cebc88f99614','CE-CE-001'),
('eac8f647-7aac-4ec6-884c-631d94c44de3',1,0.00,0.00,'','{}','size:',0.00,'6480988f-2fa8-4094-acf0-cebc88f99614','CE-WC-001'),
('f1f1b8b4-2e9b-4162-b792-79de4c05c80f',4,0.00,0.00,'','{}','size:',0.00,'5321a782-7749-4a12-9fa7-7579a7b2e50e','EV-TW-001');
/*!40000 ALTER TABLE `admin_backend_final_cartitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_category`
--

DROP TABLE IF EXISTS `admin_backend_final_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_category` (
  `category_id` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL,
  `caption` varchar(255) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  PRIMARY KEY (`category_id`),
  KEY `admin_backend_final_category_name_b3bb22e0` (`name`),
  KEY `admin_backend_final_category_status_3def70a0` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_category`
--

LOCK TABLES `admin_backend_final_category` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_category` DISABLE KEYS */;
INSERT INTO `admin_backend_final_category` VALUES
('B&T-1','Bags & Travel','visible','Personalized Bags & Travel Accessories Dubai.','Shop tote bags, jute bags, laptop bags, travel accessories, and tech gadgets with logo printing. Premium printing services in Dubai.','SuperAdmin','2025-08-28 18:19:47.531026','2025-08-29 11:25:16.450807',6),
('BD&F-1','Banner Display & Flags','visible','Custom Banner, Display & Flags Printing Dubai','Durable banners, displays & flags printing in Dubai perfect for events, exhibitions, promotions & outdoor advertising in the UAE.','SuperAdmin','2025-09-03 07:01:22.544520','2025-09-03 12:27:37.179814',10),
('CAA-1','Clothing and Apparel','visible','Custom Apparel, Polo Shirts & Printed Hoodies Dubai.','From printed tees and polos to hoodies, caps, and event sashes, get premium custom apparel in Dubai with fast, high-quality branding services.','SuperAdmin','2025-08-28 18:22:59.501649','2025-09-02 10:16:25.066693',3),
('D-1','Drinkware','visible','Custom Mugs, Bottles & Drinkware Printing Dubai.','Explore custom drinkware,mugs, tumblers, and bottles with logo printing. Premium print shop in Dubai offering fast, high-quality service.','SuperAdmin','2025-08-28 18:16:14.269813','2025-09-02 08:44:55.951080',5),
('EG&S-1','Events & Giveaway Items','visible','Custom Giveaways, Event Gifts & Printing Dubai.','Personalized notebooks, pens, mugs, T-shirts, power banks, umbrellas, and more. Premium event giveaways with printing services in Dubai.','SuperAdmin','2025-08-29 06:10:26.482121','2025-09-03 06:00:51.142110',8),
('O&S-1','Office & Stationery','visible','Branded Office Supplies & Personalized Printing Dubai.','Shop stylish notebooks, spiral notebooks, document holders, and desk organizers with logo printing. Quality printing services in Dubai, fast delivery.','SuperAdmin','2025-08-28 18:21:27.229454','2025-08-29 12:50:43.165126',2),
('P&MM-1','Print & Marketing Material','visible','Custom Cards, Flyers, Stickers & Printing Dubai.','High-quality printing in Dubai for business cards, flyers, stickers, brochures, banners, and more. Fast service with professional designs.','SuperAdmin','2025-08-28 18:24:41.012776','2025-09-02 09:52:18.159815',1),
('S-1','Signage','visible',NULL,NULL,'SuperAdmin','2025-09-02 17:44:17.014881','2025-09-02 17:46:51.102590',9),
('T-1','Technology','visible','Custom USBs, Power Banks & Printing in Dubai.','Shop custom USB drives, power banks, and wireless chargers with logo printing. Premium printing services in Dubai for gifts and promotions.','SuperAdmin','2025-08-28 18:18:28.028602','2025-08-29 11:03:32.262587',7),
('WI-1','Writing Instrument','visible','Premium Pens & Printing Services in Dubai.','Discover premium writing instruments,branded pens, notebooks with pens, ballpoint pens & wooden pencils. Top printing services in Dubai, fast delivery.','SuperAdmin','2025-08-28 18:14:06.543795','2025-09-02 10:46:33.827029',4);
/*!40000 ALTER TABLE `admin_backend_final_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_categoryimage`
--

DROP TABLE IF EXISTS `admin_backend_final_categoryimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_categoryimage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `category_id` varchar(100) NOT NULL,
  `image_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_backend_final__category_id_6eb3fe2e_fk_admin_bac` (`category_id`),
  KEY `admin_backend_final__image_id_0fc772e5_fk_admin_bac` (`image_id`),
  CONSTRAINT `admin_backend_final__category_id_6eb3fe2e_fk_admin_bac` FOREIGN KEY (`category_id`) REFERENCES `admin_backend_final_category` (`category_id`),
  CONSTRAINT `admin_backend_final__image_id_0fc772e5_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_categoryimage`
--

LOCK TABLES `admin_backend_final_categoryimage` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_categoryimage` DISABLE KEYS */;
INSERT INTO `admin_backend_final_categoryimage` VALUES
(9,'2025-08-29 11:03:32.278006','T-1','IMG-c2c696f0'),
(10,'2025-08-29 11:25:16.470329','B&T-1','IMG-b396651e'),
(12,'2025-08-29 12:50:43.179184','O&S-1','IMG-58a7bd2a'),
(13,'2025-09-02 08:44:55.965362','D-1','IMG-4cb9bb0d'),
(14,'2025-09-02 09:52:18.175671','P&MM-1','IMG-0e25b715'),
(15,'2025-09-02 10:16:25.082429','CAA-1','IMG-35346e01'),
(17,'2025-09-02 10:46:33.845574','WI-1','IMG-7c41237c'),
(18,'2025-09-02 17:09:46.949479','EG&S-1','IMG-5406e21f'),
(20,'2025-09-02 17:46:51.116848','S-1','IMG-a90746cc'),
(21,'2025-09-03 12:27:37.187671','BD&F-1','IMG-93bcfd8b');
/*!40000 ALTER TABLE `admin_backend_final_categoryimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_categorysubcategorymap`
--

DROP TABLE IF EXISTS `admin_backend_final_categorysubcategorymap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_categorysubcategorymap` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `category_id` varchar(100) NOT NULL,
  `subcategory_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_backend_final_cate_category_id_subcategory__eae5f853_uniq` (`category_id`,`subcategory_id`),
  KEY `admin_backe_categor_542279_idx` (`category_id`),
  KEY `admin_backe_subcate_36cce4_idx` (`subcategory_id`),
  CONSTRAINT `admin_backend_final__category_id_63ce5c5f_fk_admin_bac` FOREIGN KEY (`category_id`) REFERENCES `admin_backend_final_category` (`category_id`),
  CONSTRAINT `admin_backend_final__subcategory_id_423e5a43_fk_admin_bac` FOREIGN KEY (`subcategory_id`) REFERENCES `admin_backend_final_subcategory` (`subcategory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_categorysubcategorymap`
--

LOCK TABLES `admin_backend_final_categorysubcategorymap` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_categorysubcategorymap` DISABLE KEYS */;
INSERT INTO `admin_backend_final_categorysubcategorymap` VALUES
(7,'B&T-1','B&T-BACKPACKS-001'),
(6,'B&T-1','B&T-EVERYDAY-001'),
(8,'B&T-1','B&T-TRAVEL-001'),
(35,'BD&F-1','BD&F-BANNERS-001'),
(39,'BD&F-1','BD&F-DISPLAY-001'),
(40,'BD&F-1','BD&F-FLAGS-001'),
(16,'CAA-1','CAA-ACCESSORIES-001'),
(34,'CAA-1','CAA-CAPS-001'),
(14,'CAA-1','CAA-HOODIES-001'),
(13,'CAA-1','CAA-KIDS\'-001'),
(12,'CAA-1','CAA-T-SHIRTS-001'),
(15,'CAA-1','CAA-UNIFORMS-001'),
(33,'D-1','D-CERAMIC-001'),
(23,'D-1','D-ECO-FRIENDLY-001'),
(22,'D-1','D-SPORTS-001'),
(24,'D-1','D-TABLE-001'),
(21,'D-1','D-TRAVEL-001'),
(27,'EG&S-1','EG&S-BRANDED-001'),
(26,'EG&S-1','EG&S-DECORATIVE-001'),
(25,'EG&S-1','EG&S-EVENT-001'),
(29,'EG&S-1','EG&S-PET-001'),
(28,'EG&S-1','EG&S-PREMIUM-001'),
(30,'EG&S-1','EG&S-SIGNAGE-001'),
(11,'O&S-1','O&S-CALENDARS-001'),
(10,'O&S-1','O&S-EXECUTIVE-001'),
(43,'O&S-1','O&S-INVOICE-001'),
(9,'O&S-1','O&S-NOTEBOOKS-001'),
(17,'P&MM-1','P&MM-BUSINESS-001'),
(20,'P&MM-1','P&MM-CERAMIC-001'),
(41,'P&MM-1','P&MM-ENVELOPE-001'),
(42,'P&MM-1','P&MM-LETTERHEADS-001'),
(19,'P&MM-1','P&MM-OFFICE-001'),
(37,'P&MM-1','P&MM-PREMIUM-001'),
(18,'P&MM-1','P&MM-PROMOTIONAL-001'),
(44,'S-1','S-CHANNEL-001'),
(2,'T-1','T-COMPUTER-001'),
(36,'T-1','T-CUSTOM-001'),
(32,'T-1','T-POWER-001'),
(31,'WI-1','WI-GIFT-001'),
(4,'WI-1','WI-METAL-001'),
(3,'WI-1','WI-PLASTIC-001'),
(5,'WI-1','WI-WOODEN-001');
/*!40000 ALTER TABLE `admin_backend_final_categorysubcategorymap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_dashboardsnapshot`
--

DROP TABLE IF EXISTS `admin_backend_final_dashboardsnapshot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_dashboardsnapshot` (
  `dashboard_id` varchar(100) NOT NULL,
  `snapshot_type` varchar(50) NOT NULL,
  `snapshot_date` date NOT NULL,
  `new_users` int(11) NOT NULL,
  `orders_placed` int(11) NOT NULL,
  `orders_cancelled` int(11) NOT NULL,
  `orders_delivered` int(11) NOT NULL,
  `total_revenue` decimal(12,2) NOT NULL,
  `active_users` int(11) NOT NULL,
  `order_growth_rate` double NOT NULL,
  `user_growth_rate` double NOT NULL,
  `active_user_growth_rate` double NOT NULL,
  `top_visited_pages` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`top_visited_pages`)),
  `top_companies` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`top_companies`)),
  `countries_ordered_from` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`countries_ordered_from`)),
  `data_source` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` varchar(100) NOT NULL,
  PRIMARY KEY (`dashboard_id`),
  KEY `admin_backend_final__created_by_id_70a902db_fk_admin_bac` (`created_by_id`),
  CONSTRAINT `admin_backend_final__created_by_id_70a902db_fk_admin_bac` FOREIGN KEY (`created_by_id`) REFERENCES `admin_backend_final_admin` (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_dashboardsnapshot`
--

LOCK TABLES `admin_backend_final_dashboardsnapshot` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_dashboardsnapshot` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_dashboardsnapshot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_deleteditemscache`
--

DROP TABLE IF EXISTS `admin_backend_final_deleteditemscache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_deleteditemscache` (
  `cache_id` varchar(100) NOT NULL,
  `table_name` varchar(100) NOT NULL,
  `record_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`record_data`)),
  `deleted_at` datetime(6) NOT NULL,
  `deleted_reason` longtext NOT NULL,
  `restored` tinyint(1) NOT NULL,
  `restored_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`cache_id`),
  KEY `admin_backend_final_deleteditemscache_table_name_90701ca2` (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_deleteditemscache`
--

LOCK TABLES `admin_backend_final_deleteditemscache` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_deleteditemscache` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_deleteditemscache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_firstcarousel`
--

DROP TABLE IF EXISTS `admin_backend_final_firstcarousel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_firstcarousel` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_firstcarousel`
--

LOCK TABLES `admin_backend_final_firstcarousel` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_firstcarousel` DISABLE KEYS */;
INSERT INTO `admin_backend_final_firstcarousel` VALUES
(1,'Default First Carousel Title','Default First Carousel Description');
/*!40000 ALTER TABLE `admin_backend_final_firstcarousel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_firstcarouselimage`
--

DROP TABLE IF EXISTS `admin_backend_final_firstcarouselimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_firstcarouselimage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `caption` varchar(255) NOT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  `created_at` datetime(6) NOT NULL,
  `carousel_id` bigint(20) NOT NULL,
  `image_id` varchar(100) NOT NULL,
  `subcategory_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_backend_final__carousel_id_e1eb71fd_fk_admin_bac` (`carousel_id`),
  KEY `admin_backend_final__image_id_1cf5a5fc_fk_admin_bac` (`image_id`),
  KEY `admin_backend_final__subcategory_id_a2b8920a_fk_admin_bac` (`subcategory_id`),
  CONSTRAINT `admin_backend_final__carousel_id_e1eb71fd_fk_admin_bac` FOREIGN KEY (`carousel_id`) REFERENCES `admin_backend_final_firstcarousel` (`id`),
  CONSTRAINT `admin_backend_final__image_id_1cf5a5fc_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`),
  CONSTRAINT `admin_backend_final__subcategory_id_a2b8920a_fk_admin_bac` FOREIGN KEY (`subcategory_id`) REFERENCES `admin_backend_final_subcategory` (`subcategory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_firstcarouselimage`
--

LOCK TABLES `admin_backend_final_firstcarouselimage` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_firstcarouselimage` DISABLE KEYS */;
INSERT INTO `admin_backend_final_firstcarouselimage` VALUES
(1,'Product 1','',0,'2025-09-18 16:44:47.519757',1,'IMG-e16a985a',NULL);
/*!40000 ALTER TABLE `admin_backend_final_firstcarouselimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_herobanner`
--

DROP TABLE IF EXISTS `admin_backend_final_herobanner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_herobanner` (
  `hero_id` varchar(100) NOT NULL,
  `alt_text` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`hero_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_herobanner`
--

LOCK TABLES `admin_backend_final_herobanner` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_herobanner` DISABLE KEYS */;
INSERT INTO `admin_backend_final_herobanner` VALUES
('HERO-3ca56c57','Homepage Hero Banner','2025-08-28 18:05:36.336799');
/*!40000 ALTER TABLE `admin_backend_final_herobanner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_herobannerimage`
--

DROP TABLE IF EXISTS `admin_backend_final_herobannerimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_herobannerimage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `device_type` varchar(20) NOT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  `created_at` datetime(6) NOT NULL,
  `banner_id` varchar(100) NOT NULL,
  `image_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_backend_final__banner_id_3eab55cb_fk_admin_bac` (`banner_id`),
  KEY `admin_backend_final__image_id_e15da41f_fk_admin_bac` (`image_id`),
  KEY `admin_backend_final_herobannerimage_device_type_51874f8a` (`device_type`),
  CONSTRAINT `admin_backend_final__banner_id_3eab55cb_fk_admin_bac` FOREIGN KEY (`banner_id`) REFERENCES `admin_backend_final_herobanner` (`hero_id`),
  CONSTRAINT `admin_backend_final__image_id_e15da41f_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_herobannerimage`
--

LOCK TABLES `admin_backend_final_herobannerimage` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_herobannerimage` DISABLE KEYS */;
INSERT INTO `admin_backend_final_herobannerimage` VALUES
(1,'desktop',0,'2025-08-28 18:05:36.363748','HERO-3ca56c57','IMG-7b4d623f'),
(2,'desktop',1,'2025-08-28 18:05:36.366563','HERO-3ca56c57','IMG-4ea41499'),
(3,'desktop',2,'2025-08-28 18:05:36.403772','HERO-3ca56c57','IMG-fd407b3d'),
(4,'desktop',3,'2025-08-28 18:05:36.412163','HERO-3ca56c57','IMG-820bea1a');
/*!40000 ALTER TABLE `admin_backend_final_herobannerimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_image`
--

DROP TABLE IF EXISTS `admin_backend_final_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_image` (
  `image_id` varchar(100) NOT NULL,
  `image_file` varchar(100) DEFAULT NULL,
  `alt_text` varchar(255) NOT NULL,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`tags`)),
  `image_type` varchar(50) NOT NULL,
  `linked_table` varchar(100) NOT NULL,
  `linked_id` varchar(100) NOT NULL,
  `linked_page` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`image_id`),
  KEY `admin_backend_final_image_linked_id_a70c4c7c` (`linked_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_image`
--

LOCK TABLES `admin_backend_final_image` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_image` DISABLE KEYS */;
INSERT INTO `admin_backend_final_image` VALUES
('IMG-008d33de','uploads/13104e57-ee81-4263-ae54-9b62af5130c9.jpeg','',1000,1000,'[]','.jpeg','product','CE-BC-001','product-page','2025-09-01 10:02:44.941641'),
('IMG-009d7870','uploads/Metal_Ball_point_3e1ekZO.png','Alt-text',2250,1500,'[]','.png','subcategory','WI-METAL-001','CategorySubCategoryPage','2025-09-09 10:23:27.438854'),
('IMG-00bf4ed2','uploads/9a4c7749-a864-4ef4-9c1e-ff91acbc6c71.jpeg','',1000,1000,'[]','.jpeg','product','EV-TW-001','product-page','2025-09-01 10:13:10.534929'),
('IMG-00f08103','uploads/ab37c905-467f-44ff-be6a-f38371e8ccac.webp','',1000,1000,'[]','.webp','product','DE-BF-001','product-page','2025-09-01 10:22:47.042300'),
('IMG-0120f4f8','uploads/cde61b6c-420a-4b27-8adc-01ec9d1f69fa.jpeg','',260,260,'[]','.jpeg','product','PR-CC-002','product-page','2025-09-04 07:54:34.991524'),
('IMG-013cc75d','uploads/bcb9130f-b090-46ef-a1e1-ea6d0f96f1f2.jpeg','',260,260,'[]','.jpeg','product','PR-CP-002','product-page','2025-09-04 07:56:17.780005'),
('IMG-014758bb','uploads/ea4bfd34-5688-491b-9571-ea130328b7b0.webp','',1000,1000,'[]','.webp','product','SP-RT-001','product-page','2025-09-01 11:35:38.983584'),
('IMG-02445113','uploads/2e71391a-e51f-4cdd-813b-b1175fe8bcc7.jpeg','',1000,1000,'[]','.jpeg','product','EX-WP-001','product-page','2025-09-01 12:28:37.706050'),
('IMG-02c7cf35','uploads/bedd6434-9bdb-4505-b92c-7c833b05197c.jpeg','',1000,1000,'[]','.jpeg','product','NO-SN-002','product-page','2025-09-01 12:14:18.332521'),
('IMG-031667ed','uploads/ef7deea9-38c3-4f0f-9186-8f4313d12254.webp','',1417,1102,'[]','.webp','product','BA-FB-002','product-page','2025-09-11 07:34:28.067945'),
('IMG-0394efdd','uploads/18fe0439-3697-4738-890d-dbe98c1e1370.jpeg','',850,850,'[]','.jpeg','product','FL-LS-001','product-page','2025-09-11 06:16:07.822575'),
('IMG-039b10ff','uploads/5d57e221-599c-48af-a704-6f53c227fe7b.jpeg','',1000,1000,'[]','.jpeg','product','SP-RB-001','product-page','2025-09-01 11:20:18.625151'),
('IMG-03c622ff','uploads/91cfc8cd-0a4b-436b-8ebe-5c4f3235eee0.webp','',1000,1000,'[]','.webp','product','DE-BF-001','product-page','2025-09-01 10:22:47.044328'),
('IMG-03db3b6d','uploads/b9c88e6b-c461-4373-b63b-3eedfb39dbe0.jpeg','',260,260,'[]','.jpeg','product','CO-DU-001','product-page','2025-09-04 08:28:56.007260'),
('IMG-04335be7','uploads/7adc119a-835e-4bcc-914a-fbd514ffc771.jpeg','',1000,1000,'[]','.jpeg','product','EV-CL-001','product-page','2025-09-01 10:10:07.073248'),
('IMG-04c3d7d6','uploads/7d8791ec-94f6-4a01-8e1f-e0dc26faab08.jpeg','',1000,1000,'[]','.jpeg','product','TR-DS-001','product-page','2025-09-03 13:08:57.662549'),
('IMG-04f465d8','uploads/8aea0d9e-312b-490c-9b18-8608e529fe30.jpeg','',1000,1000,'[]','.jpeg','product','CE-BC-001','product-page','2025-09-01 10:02:44.939745'),
('IMG-05e0a404','uploads/6025f537-5b12-44cd-90e4-28185332185b.jpeg','',1000,1000,'[]','.jpeg','product','TA-HT-001','product-page','2025-09-02 08:09:44.174595'),
('IMG-05e0edd6','uploads/732f06ad-71bb-4e6c-b0aa-a9dc97de34e3.jpeg','',1000,1000,'[]','.jpeg','product','SP-TB-001','product-page','2025-09-01 10:38:01.214041'),
('IMG-06b66025','uploads/589b405e-e1ef-48a2-842d-2e0f358d6f21.jpeg','',1000,1000,'[]','.jpeg','product','CO-WU-001','product-page','2025-09-04 07:54:01.443816'),
('IMG-078aa2bf','uploads/c8575977-5e64-4c42-bb74-bbe6fc8537f8.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-002','product-page','2025-09-01 09:19:55.171953'),
('IMG-08549a12','uploads/53016b0f-e15c-4d79-baca-65f08b775609.jpeg','',1000,1000,'[]','.jpeg','product','CO-BE-001','product-page','2025-09-01 06:38:34.676056'),
('IMG-08e65b34','uploads/6b0500f9-3e85-4f59-af07-5e373b65d230.jpeg','',1000,1000,'[]','.jpeg','product','SP-WB-002','product-page','2025-09-01 11:15:09.145054'),
('IMG-09053827','uploads/Travel_Accessories.png','Alt-text',2250,1500,'[]','.png','subcategory','B&T-TRAVEL-001','CategorySubCategoryPage','2025-09-09 11:14:27.938816'),
('IMG-091a18a7','uploads/9608a24b-7c24-4003-996e-e1c85bea33b7.jpeg','',1000,1000,'[]','.jpeg','product','NO-PD-001','product-page','2025-09-01 11:56:03.030221'),
('IMG-0a70aaa1','uploads/96f50b21-a074-40ea-84cd-8594c313920d.jpeg','',1000,1000,'[]','.jpeg','product','SP-RB-001','product-page','2025-09-01 11:20:18.626971'),
('IMG-0b9ef7cd','uploads/ac79e336-e145-47a9-8d60-08c90e9eaa2a.jpeg','',1000,1000,'[]','.jpeg','product','SP-SS-001','product-page','2025-09-01 11:06:03.143185'),
('IMG-0bc8a510','uploads/c1d64245-6eec-46b6-a5e6-729760c01f46.jpeg','',260,260,'[]','.jpeg','product','CO-CU-001','product-page','2025-09-04 08:31:25.931946'),
('IMG-0c1dccb5','uploads/eb66432a-3521-4942-a299-fd65f3e9eaa9.jpeg','',1000,1000,'[]','.jpeg','product','BR-CA-001','product-page','2025-09-01 08:38:07.660102'),
('IMG-0c46e145','uploads/e1e1a816-6dee-46ba-a9c5-9007c5d8bac8.jpeg','',1000,1000,'[]','.jpeg','product','NO-PD-001','product-page','2025-09-01 11:56:03.040507'),
('IMG-0c616e3d','uploads/cf3125e7-c57e-478b-bb4f-3d456a387405.jpeg','',1000,1000,'[]','.jpeg','product','AC-CP-001','product-page','2025-09-01 08:21:39.595114'),
('IMG-0c835bfc','uploads/319139a0-05ae-46c5-948e-62a43ba8ca73.jpeg','Ikrash ne kiya theek kiya???? featured image',1400,1400,'[\"blog\", \"featured\"]','.jpeg','blog','ikrashnekiyatheekk-ff2ae602e9','BlogManagementPage','2025-09-18 13:29:19.994085'),
('IMG-0d389188','uploads/7b6487bf-53ec-47f6-a7e4-cd0b2026262e.jpeg','',1000,1000,'[]','.jpeg','product','AC-CC-001','product-page','2025-09-01 08:08:19.106298'),
('IMG-0d9f4c4b','uploads/f916d204-46ed-4fa4-8801-bd6af17968eb.jpeg','',1000,1000,'[]','.jpeg','product','CE-CG-001','product-page','2025-09-01 08:07:35.356895'),
('IMG-0e25b715','uploads/Print_and_Marketing_Material.png','Booklet printing with full-color design for presentations',2250,1500,'[]','.png','category','P&MM-1','CategorySubCategoryPage','2025-09-02 09:52:18.174755'),
('IMG-0e94d4ba','uploads/1ee3c2b3-e4dc-4a65-a69a-94b11860946e.jpeg','',260,260,'[]','.jpeg','product','EV-CE-001','product-page','2025-09-04 08:16:40.245667'),
('IMG-0fb58b53','uploads/f3ce494d-cdf1-41f1-a801-b1b79df51c59.jpeg','',1000,1000,'[]','.jpeg','product','PO-MD-001','product-page','2025-09-01 06:56:25.396333'),
('IMG-0fcde3c8','uploads/ab018bb0-ba45-4bdd-a704-4dd1b4de1a2a.jpeg','',260,260,'[]','.jpeg','product','EV-CR-002','product-page','2025-09-04 08:21:03.962015'),
('IMG-112e730a','uploads/8fe0bf23-95c7-4677-8849-0e0421ab512d.webp','',1000,1000,'[]','.webp','product','PR-CO-001','product-page','2025-09-04 07:33:10.692331'),
('IMG-11e169da','uploads/8e8186eb-07d8-4449-8bcd-5c876d00e7fa.jpeg','',1000,1000,'[]','.jpeg','product','BR-CM-001','product-page','2025-09-01 08:20:03.124485'),
('IMG-13063ec3','uploads/ac333f73-5540-4017-b97e-bf44da6c403f.webp','Alt-text',1000,1000,'[]','.webp','product','SP-PS-001','product-page','2025-09-01 10:57:46.927983'),
('IMG-13371bdd','uploads/33551a39-c72a-4ec2-a1d9-9a764e6272c7.jpeg','',1000,1000,'[]','.jpeg','product','CA-2T-001','product-page','2025-09-01 11:05:36.369258'),
('IMG-13ccf61b','uploads/9d364200-86b9-4f90-b541-49e11f0e2041.jpeg','',1000,1000,'[]','.jpeg','product','DE-SF-001','product-page','2025-09-01 10:26:26.201535'),
('IMG-13cf4853','uploads/c4c5e671-3662-47b0-808e-c9abebcfeb11.jpeg','',1000,1000,'[]','.jpeg','product','CA-MN-001','product-page','2025-09-01 11:20:26.652546'),
('IMG-13f7b170','uploads/84869c49-6f4b-4218-9840-0a2737ed1c7d.jpeg','',1000,1000,'[]','.jpeg','product','AC-WA-001','product-page','2025-09-01 08:23:31.501015'),
('IMG-148c3f94','uploads/d2c392b1-a801-4b5a-ae50-bea046b7dc3b.jpeg','',1000,1000,'[]','.jpeg','product','BR-CA-001','product-page','2025-09-01 08:38:07.658217'),
('IMG-1498ba93','uploads/4630c735-4a34-4250-a6eb-f43bb58b480c.jpeg','',1000,1000,'[]','.jpeg','product','CE-BS-001','product-page','2025-09-01 08:18:56.303846'),
('IMG-14cf3f40','uploads/c9655cfa-645e-4e49-a3e5-82492545c5bf.jpeg','',260,260,'[]','.jpeg','product','EX-CC-001','product-page','2025-09-04 08:09:59.942554'),
('IMG-1557d4e9','uploads/7bc5b5d2-807e-433a-a5e6-b4262ba159bd.jpeg','',1000,1000,'[]','.jpeg','product','CE-BS-001','product-page','2025-09-01 08:18:56.297666'),
('IMG-157ce22f','uploads/825ad307-c9a3-4759-94ac-a5258e1096a3.jpeg','',1000,1000,'[]','.jpeg','product','CA-AN-001','product-page','2025-09-01 11:26:58.736519'),
('IMG-159565aa','uploads/0237f3bc-b570-41cb-a420-8452f8ac6797.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-001','product-page','2025-09-01 07:19:05.013506'),
('IMG-162f6a84','uploads/5a9ea0a6-d8c3-4ad8-94c7-ba97fb9cdd45.jpeg','',260,260,'[]','.jpeg','product','EX-CC-002','product-page','2025-09-04 08:11:46.933312'),
('IMG-16b44dda','uploads/958913d0-98f3-4db2-965a-51cf18030171.jpeg','',1000,1000,'[]','.jpeg','product','UN-PC-001','product-page','2025-09-01 08:04:25.010668'),
('IMG-16bfc789','uploads/3768f627-ebd6-45ac-9a0b-b2f2a5a93411.jpeg','',260,260,'[]','.jpeg','product','CO-DU-001','product-page','2025-09-04 08:28:56.011267'),
('IMG-16ca3651','uploads/81acf214-8f4f-4004-befa-3a6e16ef19b8.jpeg','',1000,1000,'[]','.jpeg','product','CO-BE-001','product-page','2025-09-01 06:38:34.680361'),
('IMG-172d77d5','uploads/a2cbf353-f4bd-4698-b69e-ff9d87b23a3c.jpeg','',260,260,'[]','.jpeg','product','BR-PP-001','product-page','2025-09-04 07:59:19.782835'),
('IMG-17407275','uploads/5386865c-a0e8-4dd3-95c0-f613d173ed76.jpeg','',1000,1000,'[]','.jpeg','product','EV-RV-001','product-page','2025-09-01 08:04:31.885098'),
('IMG-1790e8c6','uploads/cef95c82-3477-44f5-a15d-16694882ccdf.jpeg','',1000,1000,'[]','.jpeg','product','AC-WA-001','product-page','2025-09-01 08:23:31.504575'),
('IMG-17e568db','uploads/5053de0f-6de0-4357-aebc-3e3cb211094a.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.509420'),
('IMG-180c712c','uploads/938e4822-aae2-42a0-833a-576b47d01de1.jpeg','Ikrash ne kiya theek kiya???? featured image',1400,1400,'[\"blog\", \"featured\"]','.jpeg','blog','ikrashnekiyatheekk-ff2ae602e9','BlogManagementPage','2025-09-17 19:04:31.770148'),
('IMG-1893485a','uploads/Everyday__Tote_Bags.png','Alt-text',2250,1500,'[]','.png','subcategory','B&T-EVERYDAY-001','CategorySubCategoryPage','2025-09-09 10:35:42.783463'),
('IMG-18a079b8','uploads/9f11f23d-8d88-4328-9f09-8b78595b7ab7.webp','',1000,1000,'[]','.webp','product','GI-LP-001','product-page','2025-09-01 06:24:30.096657'),
('IMG-1918c9ce','uploads/320445ed-d3c7-4b09-995c-d754887a3e02.jpeg','',1000,1000,'[]','.jpeg','product','EV-VN-001','product-page','2025-09-01 08:01:45.623155'),
('IMG-199cb2a3','uploads/d04003fa-5e21-4077-842f-409a2bb43265.jpeg','',1000,1000,'[]','.jpeg','product','EV-VN-001','product-page','2025-09-01 08:01:45.625013'),
('IMG-19c9d494','uploads/4e43542a-1b26-429d-9ae6-60d32b54b68a.jpeg','',1000,1000,'[]','.jpeg','product','EX-PL-001','product-page','2025-09-04 07:39:52.253625'),
('IMG-1aa9d885','uploads/87626097-710e-4b9c-b4c4-233cd3ef6d0e.webp','',1000,1000,'[]','.webp','product','TR-CC-001','product-page','2025-09-01 08:10:42.742394'),
('IMG-1ac605fa','uploads/370732a4-809f-4f6d-8fe6-a75b9d2153c2.jpeg','',1000,1000,'[]','.jpeg','product','TA-HT-001','product-page','2025-09-02 08:09:44.176409'),
('IMG-1afac751','uploads/813572f0-ae66-45d0-8871-05cc3562eefe.jpeg','',1000,1000,'[]','.jpeg','product','BR-CR-001','product-page','2025-09-01 08:34:53.202660'),
('IMG-1c52f3d3','uploads/6ebc689b-db21-4b1c-a9df-4da8bfb51a82.jpeg','',1000,1000,'[]','.jpeg','product','SP-PB-001','product-page','2025-09-04 06:52:49.238481'),
('IMG-1c8930e0','uploads/37575d57-5490-42f2-92f5-5d54259e6ec0.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','SP-PS-001','product-page','2025-09-01 10:57:46.932094'),
('IMG-1ccf3047','uploads/c367ca0c-5cab-417d-bcd4-6c5c807d9e9f.jpeg','',1000,1000,'[]','.jpeg','product','EC-BF-001','product-page','2025-09-04 07:10:08.128619'),
('IMG-1cd04b7d','uploads/d988eea8-700a-44e3-b4fe-254e9b837fae.jpeg','',1000,1000,'[]','.jpeg','product','BA-BA-001','product-page','2025-09-01 06:14:41.100143'),
('IMG-1df38173','uploads/01e269e0-bd80-4a29-9946-b715395aeb90.jpeg','',1000,1000,'[]','.jpeg','product','CA-FC-001','product-page','2025-09-01 11:13:10.368870'),
('IMG-1f29c190','uploads/c543369f-9ad7-465e-8112-b4d790180ddc.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-002','product-page','2025-09-01 08:41:07.078417'),
('IMG-1f606dfa','uploads/eae5d271-b223-47c6-92c0-fdae91667632.jpeg','',1000,1000,'[]','.jpeg','product','EV-TW-001','product-page','2025-09-01 10:13:10.536965'),
('IMG-1f7eb1f3','uploads/01269d32-47e4-4e64-914e-d976aaac6923.jpeg','',1000,1000,'[]','.jpeg','product','CE-WS-001','product-page','2025-09-01 09:09:17.546160'),
('IMG-1f88b890','uploads/7671ec65-66c5-4a5c-b556-bc9fb8bc6119.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-001','product-page','2025-09-01 08:47:14.770818'),
('IMG-2055ddd2','uploads/56d0b1c0-4cce-45a0-bba4-c27e30824aa0.jpeg','',886,886,'[]','.jpeg','product','FL-PT-001','product-page','2025-09-11 06:19:06.457735'),
('IMG-21bbb569','uploads/36684c86-2fea-4472-aaff-424ffae821cf.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-003','product-page','2025-09-01 09:41:51.596824'),
('IMG-21da0231','uploads/7676b2d8-aafb-4290-999c-de454db4dec6.jpeg','',1000,1000,'[]','.jpeg','product','SP-PB-001','product-page','2025-09-04 06:52:49.244151'),
('IMG-22b1d3f7','uploads/a58ef75b-ad37-45f9-9d24-c3d2ec1ea394.jpeg','',260,260,'[]','.jpeg','product','CO-EF-001','product-page','2025-09-04 08:23:28.444564'),
('IMG-22b943a3','uploads/e4a43301-624a-43c9-b651-96919969ae92.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-002','product-page','2025-09-01 08:41:07.082311'),
('IMG-230422a4','uploads/1a5e7fce-9767-47f1-9a61-3ad8908ed624.jpeg','',1000,1000,'[]','.jpeg','product','CA-BC-001','product-page','2025-09-01 11:01:10.796596'),
('IMG-23a2f1c5','uploads/3f4719aa-9e8f-451b-8442-cd2d76850165.webp','Alt-text',1000,1000,'[]','.webp','product','SP-PS-001','product-page','2025-09-01 10:57:46.925829'),
('IMG-246f53e9','uploads/d6a0e41a-b3a5-49e2-a240-0982a602786e.jpeg','',1000,1000,'[]','.jpeg','product','BR-CP-001','product-page','2025-09-01 08:13:41.690321'),
('IMG-2582d1aa','uploads/f1bd858e-6fad-4c48-9dd0-0438e9162e0a.jpeg','',260,260,'[]','.jpeg','product','EX-CC-002','product-page','2025-09-04 08:11:46.936920'),
('IMG-267e51ee','uploads/821d1e51-c1cd-4429-bb82-0d7b33d98983.jpeg','',260,260,'[]','.jpeg','product','BR-PP-001','product-page','2025-09-04 07:59:19.778796'),
('IMG-26822b81','uploads/68a87f5d-5569-4277-80d3-4047f0c8ed89.jpeg','',1000,1000,'[]','.jpeg','product','EX-PL-001','product-page','2025-09-04 07:39:52.251607'),
('IMG-26e7613c','uploads/0eccaba3-9df2-4181-9ab2-ed0071de5bf3.jpeg','',1000,1000,'[]','.jpeg','product','NO-PD-001','product-page','2025-09-01 11:56:03.034398'),
('IMG-2749e1fe','uploads/Backpacks__Laptop_Bag.png','Alt-text',2250,1500,'[]','.png','subcategory','B&T-BACKPACKS-001','CategorySubCategoryPage','2025-09-09 11:20:03.604120'),
('IMG-277c0367','uploads/a83a09a3-bad7-481d-bc4d-6649e2736d6e.webp','',1000,1000,'[]','.webp','product','SP-RT-001','product-page','2025-09-01 11:35:38.981235'),
('IMG-2997f25c','uploads/823fa8c2-554d-445d-99b3-2e78a729ccee.webp','',1000,1000,'[]','.webp','product','BA-EC-002','product-page','2025-09-01 06:31:13.164958'),
('IMG-29b92b35','uploads/8cae8908-d3af-471e-90b9-46f86d091552.webp','',900,700,'[]','.webp','product','BA-FB-001','product-page','2025-09-11 07:23:36.151083'),
('IMG-2a6d22a0','uploads/3c27e6d4-0f0d-45a9-8379-581767450bff.webp','',1000,1000,'[]','.webp','product','CE-TT-003','product-page','2025-09-01 09:41:51.594778'),
('IMG-2a759109','uploads/a3ec848c-ea91-4787-81a2-a9d7a8f90d5f.jpeg','',260,260,'[]','.jpeg','product','CO-SC-001','product-page','2025-09-04 08:26:58.042502'),
('IMG-2a8ef7d0','uploads/53f0e943-9abf-49f1-ac04-75a1d88d8f97.jpeg','',1000,1000,'[]','.jpeg','product','DE-SF-001','product-page','2025-09-01 10:26:26.203373'),
('IMG-2aab538f','uploads/Hoodies__Jackets.png','Alt-text',2250,1500,'[]','.png','subcategory','CAA-HOODIES-001','CategorySubCategoryPage','2025-09-09 08:23:46.659903'),
('IMG-2ac93dc5','uploads/8f0700f3-cb43-4c4d-8265-36210a9f1866.jpeg','',800,600,'\"\"','.jpeg','product','PR-CC-001','product-page','2025-09-04 07:52:14.612727'),
('IMG-2b33afa9','uploads/0791529d-9bdf-4057-96e4-71938b5c6116.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-002','product-page','2025-09-01 07:31:27.154724'),
('IMG-2b4f9016','uploads/d5fb1ad1-4969-4bfe-8e6b-a7dd0d2a05a2.jpeg','',260,260,'[]','.jpeg','product','EV-CR-002','product-page','2025-09-04 08:21:03.963861'),
('IMG-2b630fd5','uploads/7869fc8d-47ff-4457-adb8-7eb7d12c8859.jpeg','',1000,1000,'[]','.jpeg','product','BR-CR-001','product-page','2025-09-01 08:34:53.206892'),
('IMG-2bdd130b','uploads/23280df1-20d6-41aa-8b56-134a280da3f0.webp','',1000,1000,'[]','.webp','product','CO-CC-001','product-page','2025-09-01 06:50:01.399460'),
('IMG-2beb5efe','uploads/e1269b87-b202-49c5-94a0-d3372a88e3a3.webp','',1000,1000,'[]','.webp','product','SP-RT-001','product-page','2025-09-01 11:35:38.985546'),
('IMG-2cc15757','uploads/9c8b2784-0b66-44b7-8bfe-f3aef15cb91a.jpeg','',260,260,'[]','.jpeg','product','EX-CB-001','product-page','2025-09-04 08:07:29.831068'),
('IMG-2cc81568','uploads/d32130be-2df5-4b9a-a4d1-638aa1205648.jpeg','',1000,1000,'[]','.jpeg','product','EV-DP-001','product-page','2025-09-01 10:11:31.286214'),
('IMG-2de523f2','uploads/f9c74fd7-d104-4e8d-94d5-8be9bfd6bd06.jpeg','',260,260,'[]','.jpeg','product','CO-UM-001','product-page','2025-09-04 08:33:25.917961'),
('IMG-2e42ad6e','uploads/ec93c75c-3066-4b8f-b81b-4c128b428926.webp','',1000,1000,'[]','.webp','product','TR-LT-001','product-page','2025-09-01 12:06:27.321232'),
('IMG-2e63454c','uploads/73c44b26-5c76-41bd-8b09-646e5786c2ad.jpeg','',260,260,'[]','.jpeg','product','CO-UM-001','product-page','2025-09-04 08:33:25.912803'),
('IMG-2ebfef2b','uploads/61f24a51-bcc8-483c-a357-a363cc4544ec.jpeg','',1000,1000,'[]','.jpeg','product','BA-BA-001','product-page','2025-09-01 06:14:41.104585'),
('IMG-2ed292c2','uploads/Banners.png','Alt-text',2250,1500,'[]','.png','subcategory','BD&F-BANNERS-001','CategorySubCategoryPage','2025-09-10 16:14:27.378749'),
('IMG-2ef5fbd1','uploads/879cb7c5-c289-48be-a5d7-6b31b9a624b3.jpeg','',260,260,'[]','.jpeg','product','EV-CR-001','product-page','2025-09-04 08:18:38.175995'),
('IMG-2fb0946b','uploads/a7246b04-3fcc-491b-a810-b79c96594c1d.jpeg','',1000,1000,'[]','.jpeg','product','CO-WU-001','product-page','2025-09-04 07:54:01.445774'),
('IMG-2fe06a97','uploads/538fdcb8-5bb4-4677-bd2d-81b8427305b2.jpeg','',1000,1000,'[]','.jpeg','product','CE-WS-002','product-page','2025-09-01 10:20:26.375346'),
('IMG-3065b02c','uploads/4a80de69-d306-4547-b560-efadbcee23ee.jpeg','',1000,1000,'[]','.jpeg','product','CA-BC-001','product-page','2025-09-01 11:01:10.804532'),
('IMG-313428fd','uploads/5e3c44ba-3e39-4b3b-9a40-6b2d79951c47.webp','',1000,1000,'[]','.webp','product','DE-BF-001','product-page','2025-09-01 10:22:47.046768'),
('IMG-313f8278','uploads/7c1808ba-06b1-4787-9c95-abf1f6e2a908.jpeg','',1000,1000,'[]','.jpeg','product','NO-BA-001','product-page','2025-09-01 11:49:22.077208'),
('IMG-32ae0bf8','uploads/2398df81-5f05-4d28-aa49-0d03b6c6fabf.jpeg','',1000,1000,'[]','.jpeg','product','TA-HT-001','product-page','2025-09-02 08:09:44.172583'),
('IMG-3337e230','uploads/de40fc5d-9f73-4c01-ae49-a7c14c5b5c62.jpeg','',1000,1000,'[]','.jpeg','product','CE-CG-001','product-page','2025-09-01 08:07:35.351372'),
('IMG-34280d49','uploads/472be67e-97ae-46e0-9ca0-09597cf6ba51.webp','',1000,1000,'[]','.webp','product','CE-CM-001','product-page','2025-09-01 09:32:14.759087'),
('IMG-345e4196','uploads/b7dba1d0-5c6d-4691-b93a-5fa51abef9e4.webp','',1000,1000,'[]','.webp','product','CA-FW-001','product-page','2025-09-01 11:08:15.432594'),
('IMG-34a0b93a','uploads/12d27daf-c207-4b1a-a991-65193fc5dcb9.jpeg','',1000,1000,'[]','.jpeg','product','CE-PC-001','product-page','2025-09-01 09:24:05.826161'),
('IMG-34a4a948','uploads/a2937a56-d1cc-4924-80a8-26c3373d029c.webp','',1000,1000,'[]','.webp','product','BR-PE-001','product-page','2025-09-01 08:29:05.912354'),
('IMG-34dd79d6','uploads/7536b07b-8dc3-443e-9979-bfad4972e624.jpeg','',1000,1000,'[]','.jpeg','product','NO-CB-001','product-page','2025-09-01 11:45:09.067483'),
('IMG-34eb3b15','uploads/981050fb-0549-4e3f-9c54-1247a5e45373.jpeg','',1000,1000,'[]','.jpeg','product','SP-TB-001','product-page','2025-09-01 10:38:01.217798'),
('IMG-352d1723','uploads/2c2efd44-32ff-4038-969c-4ebf7fddb240.jpeg','',260,260,'[]','.jpeg','product','CO-SC-001','product-page','2025-09-04 08:26:58.044250'),
('IMG-35346e01','uploads/Clothing_And_Apparel.png','Branded polo shirt with embroidered logo for corporate uniforms in UAE.',2250,1500,'[]','.png','category','CAA-1','CategorySubCategoryPage','2025-09-02 10:16:25.081749'),
('IMG-354ff69f','uploads/558852f3-8da6-4c3a-8673-0b291ae5a8e8.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-001','product-page','2025-09-01 08:47:14.774882'),
('IMG-358d9b82','uploads/8765d28c-ae53-4b3d-852c-63363adf4568.webp','',1000,1000,'[]','.webp','product','BA-EC-001','product-page','2025-09-01 06:24:50.900258'),
('IMG-35bb3c10','uploads/0c5dcf83-fb71-431b-ab5a-5cc7efc29d0e.webp','',1000,1000,'[]','.webp','product','BR-PG-001','product-page','2025-09-01 08:24:54.983786'),
('IMG-35c206e9','uploads/b77bff66-6bfb-444b-b237-5e454e2f58fe.jpeg','',1000,1000,'[]','.jpeg','product','AC-EU-001','product-page','2025-09-01 08:09:50.076319'),
('IMG-36183ff3','uploads/IMG-2905b22e.png','abd',2250,1500,'[]','.png','subcategory','P&MM-IKRASH-001','CategorySubCategoryPage','2025-08-29 05:42:53.384116'),
('IMG-364f36f6','uploads/4e22c48b-a8f3-4d6f-941f-57bf3d49820e.jpeg','',1000,1000,'[]','.jpeg','product','AC-CP-001','product-page','2025-09-01 08:21:39.591280'),
('IMG-365e8ff8','uploads/b97978ad-0da8-4c60-b720-3d88e497ad34.jpeg','',1000,1000,'[]','.jpeg','product','CA-BC-001','product-page','2025-09-01 11:01:10.800557'),
('IMG-3664f11d','uploads/1b7fec1d-42b3-4614-971e-98e61aadae54.jpeg','',1000,1000,'[]','.jpeg','product','EV-VN-001','product-page','2025-09-01 08:01:45.619359'),
('IMG-369f26d9','uploads/51325459-4d3c-410b-92b4-7345e416b9d0.jpeg','',1000,1000,'[]','.jpeg','product','BA-MC-001','product-page','2025-09-01 06:22:17.270799'),
('IMG-3815eb6a','uploads/ad981bbf-ae81-49f1-8c6a-759854bce777.jpeg','',260,260,'[]','.jpeg','product','EV-CR-001','product-page','2025-09-04 08:18:38.169582'),
('IMG-384ce930','uploads/Custom_USB_Drives.png','Alt-text',2250,1500,'[]','.png','subcategory','T-CUSTOM-001','CategorySubCategoryPage','2025-09-11 13:27:09.087441'),
('IMG-39068fca','uploads/c829dd6f-f9a1-43a9-8f58-1fd6eaa73b8d.jpeg','',1000,1000,'[]','.jpeg','product','UN-CH-001','product-page','2025-09-01 08:28:05.088817'),
('IMG-39453d68','uploads/a7f3d543-75b2-435a-8794-4086345b30d6.jpeg','',1000,1000,'[]','.jpeg','product','NO-LP-001','product-page','2025-09-01 12:06:56.682387'),
('IMG-39d8dd2e','uploads/c6d4f9d2-bffd-4c19-9cba-ea57373db5c7.jpeg','',1000,1000,'[]','.jpeg','product','SP-WB-001','product-page','2025-09-01 10:44:45.889643'),
('IMG-3a0dde5f','uploads/2213fed6-1de9-4b3c-a324-50123aa0113e.jpeg','',1000,1000,'[]','.jpeg','product','SP-SS-001','product-page','2025-09-01 11:06:03.146653'),
('IMG-3a7dba1c','uploads/4f4394c3-3664-44e9-a310-c194594cbda0.jpeg','',1000,1000,'[]','.jpeg','product','AC-WA-001','product-page','2025-09-01 08:23:31.499231'),
('IMG-3af523c9','uploads/7a6ce966-3375-4a2c-97ea-709a3e07db2b.jpeg','',260,260,'[]','.jpeg','product','EV-CR-002','product-page','2025-09-04 08:21:03.956728'),
('IMG-3b135005','uploads/65dc94fb-9800-460e-87ba-0c4301eec0e0.jpeg','',1000,1000,'[]','.jpeg','product','EV-LW-001','product-page','2025-09-01 10:08:07.439052'),
('IMG-3b16c02e','uploads/b5de3b53-5b42-422d-8f9d-fa21a45aad34.jpeg','',260,260,'[]','.jpeg','product','CO-UM-001','product-page','2025-09-04 08:33:25.920451'),
('IMG-3b4ca488','uploads/Office_Stationery.png','Alt-text',2250,1500,'[]','.png','subcategory','P&MM-OFFICE-001','CategorySubCategoryPage','2025-09-04 12:02:45.095940'),
('IMG-3bc78bd4','uploads/f16aec46-18b7-41d5-96b9-d9afd35c8cb4.webp','',1000,1000,'[]','.webp','product','GI-LP-001','product-page','2025-09-01 06:24:30.085333'),
('IMG-3c01d8a1','uploads/49dd52f1-edfd-4017-880b-a76eb82130c2.jpeg','',1000,1000,'[]','.jpeg','product','PO-BB-001','product-page','2025-09-01 06:54:02.146926'),
('IMG-3c2e178b','uploads/eb88f3b7-69b3-46d4-9f85-b36d02c74fca.jpeg','',260,260,'[]','.jpeg','product','EV-CR-001','product-page','2025-09-04 08:18:38.171767'),
('IMG-3c3ca2e1','uploads/d91d9262-9ed6-4559-a83f-22952b402537.jpeg','',1000,1000,'[]','.jpeg','product','SP-TT-001','product-page','2025-09-01 11:48:00.463263'),
('IMG-3c52bb72','uploads/886abf63-54b7-48c0-a43c-2f015f8f090f.jpeg','',1000,1000,'[]','.jpeg','product','BA-MC-001','product-page','2025-09-01 06:22:17.272783'),
('IMG-3cee1d2e','uploads/88de8255-7aa7-417c-a431-985291c388a9.jpeg','',260,260,'[]','.jpeg','product','CA-CO-001','product-page','2025-09-04 08:13:38.308401'),
('IMG-3d2264ab','uploads/bfc7a22e-935b-41ae-b8b0-160f082070ea.jpeg','',1000,1000,'[]','.jpeg','product','BR-CM-001','product-page','2025-09-01 08:20:03.122530'),
('IMG-3d6c2f60','uploads/Plastic_Ball_point_2LuEQnf.png','Alt-text',2250,1500,'[]','.png','subcategory','WI-PLASTIC-001','CategorySubCategoryPage','2025-09-09 10:23:39.701414'),
('IMG-3ddb71cd','uploads/ab4bd961-97d2-4294-8882-08fe457db5eb.jpeg','',1000,1000,'[]','.jpeg','product','TR-CT-001','product-page','2025-09-01 07:50:09.476176'),
('IMG-3de67620','uploads/ae66c0e6-a24a-4340-aca8-c74a8dd2f27b.webp','',1000,1000,'[]','.webp','product','DE-BF-001','product-page','2025-09-01 10:22:47.037516'),
('IMG-3e06507b','uploads/77d45e1e-2608-47bd-bba8-549997cac366.jpeg','',1000,1000,'[]','.jpeg','product','PO-BB-001','product-page','2025-09-01 06:54:02.152962'),
('IMG-3e538203','uploads/8eb9b869-20cd-4c5f-9d82-0984f07c6aca.jpeg','',260,195,'[]','.jpeg','product','PR-CP-002','product-page','2025-09-04 07:56:17.778134'),
('IMG-3f218c43','uploads/446bccc3-2d1b-4328-9a70-7bafb0b7abdc.jpeg','',1000,1000,'[]','.jpeg','product','CE-BS-001','product-page','2025-09-01 08:18:56.308004'),
('IMG-3f3ea6f7','uploads/31ed961e-91a6-452b-b23f-df516509caad.jpeg','',1000,1000,'[]','.jpeg','product','EV-TW-001','product-page','2025-09-01 10:13:10.531453'),
('IMG-3f7aac6d','uploads/04c5774b-9b29-4423-a309-cc81c9dcd7ad.jpeg','',1000,1000,'[]','.jpeg','product','PL-SM-001','product-page','2025-09-01 06:27:33.392188'),
('IMG-4000a29d','uploads/57508255-e7c3-4518-ac1c-fab9bbccee44.jpeg','',1000,1000,'[]','.jpeg','product','CA-BC-001','product-page','2025-09-01 11:01:10.798531'),
('IMG-41eed264','uploads/610c67fe-5e94-4701-bcb5-0fc9baa3118f.jpeg','',1000,1000,'[]','.jpeg','product','BA-BA-001','product-page','2025-09-01 06:14:41.102423'),
('IMG-4267efed','uploads/af6eee80-5e8e-43c4-9558-db7a194aca27.jpeg','',1000,1000,'[]','.jpeg','product','CE-GB-001','product-page','2025-09-01 09:04:01.018001'),
('IMG-4319fcf9','uploads/48efdd93-213c-4ec3-b528-5a89cc2e7f4b.jpeg','',1000,1000,'[]','.jpeg','product','EV-RV-001','product-page','2025-09-01 08:04:31.883101'),
('IMG-43635dfe','uploads/23789d7a-7ce5-4908-8232-c7f4e831ef9f.jpeg','',1000,1000,'[]','.jpeg','product','TA-SG-001','product-page','2025-09-02 08:11:13.966336'),
('IMG-4471d1cc','uploads/12d25bf5-a631-4382-bfd9-3fe0791e0e28.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-001','product-page','2025-09-01 07:19:05.011109'),
('IMG-4491b2b6','uploads/332935fe-35f3-43ae-9fea-7f8608204623.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.517978'),
('IMG-44a4fdc4','uploads/c0252d7c-fcf9-4ac1-9afd-2115ff059d57.jpeg','',260,260,'[]','.jpeg','product','CA-CO-001','product-page','2025-09-04 08:13:38.313172'),
('IMG-45ef33a6','uploads/961bd4f7-2dfa-450f-b9c2-315ebba56ffc.webp','',1000,1000,'[]','.webp','product','PR-CO-001','product-page','2025-09-04 07:33:10.697051'),
('IMG-461245fb','uploads/b4b82066-bd40-4f2b-bf40-839b10c0bfe9.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.499467'),
('IMG-466857fc','uploads/61c902e8-e414-4694-bdd8-58e1a5e9905d.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.507080'),
('IMG-466e40e2','uploads/71520f16-d43a-453d-bb21-24513c3a0c89.webp','',1000,1000,'[]','.webp','product','PR-CO-001','product-page','2025-09-04 07:33:10.687615'),
('IMG-4672ac1d','uploads/258f26de-bc8c-4e85-97c3-d514e0a07bc1.webp','',1000,1000,'[]','.webp','product','TR-CC-001','product-page','2025-09-01 08:10:42.736515'),
('IMG-48298749','uploads/745303a3-0a2d-43eb-9089-e212324ad8bc.jpeg','',1000,1000,'[]','.jpeg','product','UN-PC-001','product-page','2025-09-01 08:04:25.008000'),
('IMG-48558fe5','uploads/650702f8-48e0-42ec-b20a-9887cf8e66b8.jpeg','',1000,1000,'[]','.jpeg','product','PO-MD-001','product-page','2025-09-01 06:56:25.400646'),
('IMG-4918456e','uploads/d26bdda7-3111-4691-b46f-8c262428327a.jpeg','',1000,1000,'[]','.jpeg','product','NO-AS-001','product-page','2025-09-01 12:17:14.135909'),
('IMG-4a1544af','uploads/024eb1c2-8da7-43d7-8e3c-cde9e8c33a98.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-001','product-page','2025-09-01 08:47:14.776904'),
('IMG-4a256a0c','uploads/3587b210-aad8-4d09-8640-769b32dbfabb.jpeg','',1000,1000,'[]','.jpeg','product','EC-BF-001','product-page','2025-09-04 07:10:08.140254'),
('IMG-4af10ebd','uploads/830abf98-a450-4f62-911d-e1d7c5647271.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.504271'),
('IMG-4b1a2d9f','uploads/c6c26b4d-e786-442d-8dbd-382ac4a2630e.jpeg','',260,260,'[]','.jpeg','product','BR-PP-001','product-page','2025-09-04 07:59:19.776841'),
('IMG-4bb94150','uploads/371b06d3-3bd5-47c8-ae07-2488e64f51f2.jpeg','',1000,1000,'[]','.jpeg','product','AC-EU-001','product-page','2025-09-01 08:09:50.078615'),
('IMG-4c4b4a3f','uploads/f4f6556a-9c00-4a90-8668-ca4210ebc973.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.149894'),
('IMG-4c9ea229','uploads/Flags.png','Alt-text',2250,1500,'[]','.png','subcategory','BD&F-FLAGS-001','CategorySubCategoryPage','2025-09-10 16:49:58.785391'),
('IMG-4cb9bb0d','uploads/DrinkWare.png','Printing services in Dubai for mugs, bottles, and custom drinkware.',2250,1500,'[]','.png','category','D-1','CategorySubCategoryPage','2025-09-02 08:44:55.964675'),
('IMG-4d12d2d7','uploads/deafbcb0-6c86-4173-8c32-b6304a82a1bc.jpeg','',1000,1000,'[]','.jpeg','product','SP-RB-001','product-page','2025-09-01 11:20:18.623220'),
('IMG-4d31882b','uploads/dcc517d5-1620-4f2a-9b0a-b16a1c546cae.webp','',1000,1000,'[]','.webp','product','EV-SC-001','product-page','2025-09-01 06:32:55.789516'),
('IMG-4d4f4247','uploads/9c8e1f01-912a-47d2-8ea4-0ee907c3aaee.jpeg','',1000,1000,'[]','.jpeg','product','EV-DP-001','product-page','2025-09-01 10:11:31.284313'),
('IMG-4dadea86','uploads/d997b40d-d55f-4936-86c5-adcaa1f06d29.jpeg','',1000,1000,'[]','.jpeg','product','WO-EC-001','product-page','2025-09-01 06:29:30.118505'),
('IMG-4e7d6313','uploads/e766629e-7f27-41d3-840f-34c0f09e0971.jpeg','',260,260,'[]','.jpeg','product','EV-CE-001','product-page','2025-09-04 08:16:40.243936'),
('IMG-4ea41499','uploads/a93fffee-88ab-467a-88ab-c40f8729bb3a.webp','Hero Desktop Image',4320,1200,'[\"hero\", \"desktop\"]','.webp','HeroBanner','HERO-3ca56c57','hero-banner','2025-08-28 18:05:36.365376'),
('IMG-4f221bd1','uploads/0d79ee46-cd77-47d8-b76b-867ef2600c80.jpeg','',1000,1000,'[]','.jpeg','product','TR-CT-001','product-page','2025-09-01 07:50:09.480256'),
('IMG-4f6bae05','uploads/58bcca3f-92a7-4179-b63c-6b00fe723968.jpeg','',1000,1000,'[]','.jpeg','product','TR-TT-001','product-page','2025-09-01 12:10:47.294050'),
('IMG-500a553f','uploads/61a630f7-1bff-4b70-ae57-4714a7dde25e.jpeg','',1000,1000,'[]','.jpeg','product','BA-BA-001','product-page','2025-09-01 06:14:41.107337'),
('IMG-5061fa9d','uploads/51458f8c-0174-4b4d-8e03-8adfc961e772.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.511872'),
('IMG-5148c283','uploads/Premium_Business_Cards.png','Alt-text',2250,1500,'[]','.png','subcategory','P&MM-PREMIUM-001','CategorySubCategoryPage','2025-09-04 11:35:27.334934'),
('IMG-5219a9aa','uploads/278e6b0c-5cb3-4dff-9a70-33ec0ee41c23.jpeg','',1000,1000,'[]','.jpeg','product','TR-CT-001','product-page','2025-09-01 07:50:09.482029'),
('IMG-52b11f67','uploads/dbcf9dd8-9aa5-48a8-8fae-cb52067cb47f.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','TR-DW-002','product-page','2025-09-01 12:03:05.322013'),
('IMG-52b960ed','uploads/9aaed60d-620b-4ca1-9238-f53c3b717360.jpeg','',260,260,'[]','.jpeg','product','NO-CC-001','product-page','2025-09-04 08:05:19.039446'),
('IMG-5312cb0c','uploads/00a67b6c-33f4-47f4-8d07-c7019d72fddf.jpeg','',1000,1000,'[]','.jpeg','product','EC-EF-001','product-page','2025-09-04 07:01:28.061626'),
('IMG-53618f0d','uploads/2a8e94c8-19f4-465f-87b3-92f4c1f97f2d.jpeg','',600,600,'[]','.jpeg','product','CA-IC-001','product-page','2025-09-01 11:34:30.757231'),
('IMG-53b05885','uploads/f1325116-6b6e-43ed-b2dd-0058c02af5d7.jpeg','',1000,1000,'[]','.jpeg','product','PL-SM-001','product-page','2025-09-01 06:27:33.390302'),
('IMG-5406e21f','uploads/Events_and_Giveaway.png','Alt-text',2250,1500,'[]','.png','category','EG&S-1','CategorySubCategoryPage','2025-09-02 17:09:46.948559'),
('IMG-547229ed','uploads/53038cc4-f729-4493-94e8-66ef8c81b053.jpeg','',1000,1000,'[]','.jpeg','product','TR-TT-001','product-page','2025-09-01 12:10:47.295815'),
('IMG-553b12d9','uploads/009a4262-8612-48f6-b019-a30d9811cc22.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','CE-CE-001','product-page','2025-09-01 08:23:54.310227'),
('IMG-55569b5c','uploads/de9bc884-e0ec-4540-b26d-ea4be7173987.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','SP-PS-001','product-page','2025-09-01 10:57:46.929926'),
('IMG-56f89ba8','uploads/63cce809-5fd5-44fa-a7d7-aa8c681cb169.webp','',1000,1000,'[]','.webp','product','TR-LT-001','product-page','2025-09-01 12:06:27.310590'),
('IMG-575d2f43','uploads/14b4a171-20cf-4601-95b0-5df8fad5c367.jpeg','',1000,1000,'[]','.jpeg','product','CE-CG-001','product-page','2025-09-01 08:07:35.353260'),
('IMG-58114c8d','uploads/702fcf81-7e10-4e23-b0b9-f01e9cffb460.jpeg','',260,260,'[]','.jpeg','product','CO-UM-001','product-page','2025-09-04 08:33:25.915519'),
('IMG-581fecf0','uploads/b8596148-3b9c-44f0-9ec1-59201141ecff.jpeg','',260,260,'[]','.jpeg','product','CO-DU-001','product-page','2025-09-04 08:28:56.009344'),
('IMG-58a7bd2a','uploads/Office__Corporate_Stationery.png','Local print shop near me for custom office products.',2250,1500,'[]','.png','category','O&S-1','CategorySubCategoryPage','2025-08-29 12:50:43.178506'),
('IMG-5c419ff2','uploads/019fd9b0-6158-4d7b-8de5-ee5be8578239.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-003','product-page','2025-09-01 09:41:51.588096'),
('IMG-5d1d3732','uploads/7159e183-04e5-49be-a611-751af26486b0.jpeg','',1000,1000,'[]','.jpeg','product','AC-CP-001','product-page','2025-09-01 08:21:39.589238'),
('IMG-5d328142','uploads/Display.png','Alt-text',2250,1500,'[]','.png','subcategory','BD&F-DISPLAY-001','CategorySubCategoryPage','2025-09-10 16:21:31.094260'),
('IMG-5d45c1d7','uploads/Ceramic_Mug_Color_HKt9RZU.png','Alt-text',2250,1500,'[]','.png','subcategory','P&MM-CERAMIC-001','CategorySubCategoryPage','2025-09-04 11:39:10.553127'),
('IMG-5e2582bf','uploads/d991caa8-bcdb-4c83-9bdd-fe52775177dd.jpeg','',1000,1000,'[]','.jpeg','product','TR-DW-001','product-page','2025-09-01 11:55:58.682723'),
('IMG-5eb80941','uploads/03e4478c-c532-413f-83b8-bae266aebc86.jpeg','',850,850,'[]','.jpeg','product','FL-HT-002','product-page','2025-09-11 06:14:38.848999'),
('IMG-5f11373e','uploads/dc1f1f70-7bea-47f2-9093-b508ab14cd69.jpeg','',1000,1000,'[]','.jpeg','product','CA-AN-001','product-page','2025-09-01 11:26:58.733768'),
('IMG-5f2c2964','uploads/5e3f6c25-7404-46d5-aab5-2dd3f315d5cd.jpeg','',1000,1000,'[]','.jpeg','product','CE-GC-001','product-page','2025-09-01 09:12:16.141517'),
('IMG-5f41d42c','uploads/c753d27a-0586-4edd-b553-794c2641c799.jpeg','',1000,1000,'[]','.jpeg','product','PO-BB-001','product-page','2025-09-01 06:54:02.156845'),
('IMG-5f72ff19','uploads/9ab49ed5-ffcf-4028-b67a-3135011edbbd.jpeg','',1000,1000,'[]','.jpeg','product','EV-CL-001','product-page','2025-09-01 10:10:07.081840'),
('IMG-60265f8a','uploads/7f606bcf-6070-4c4d-8ab1-a3653797aacd.jpeg','',1000,1000,'[]','.jpeg','product','NO-PD-001','product-page','2025-09-01 11:56:03.036588'),
('IMG-611e83b8','uploads/f472c014-5f60-4c02-8f3f-e84e3bf99754.jpeg','',1000,1000,'[]','.jpeg','product','SP-TB-001','product-page','2025-09-01 10:38:01.221320'),
('IMG-616e763c','uploads/1a891326-c56a-4274-9a6e-b7cbabd8f070.jpeg','',1000,1000,'[]','.jpeg','product','SP-SS-001','product-page','2025-09-01 11:06:03.148298'),
('IMG-62111a90','uploads/9f52dc48-a655-48c7-8cab-1312616f12ae.jpeg','',260,260,'[]','.jpeg','product','EX-CC-001','product-page','2025-09-04 08:09:59.948291'),
('IMG-62b5e27a','uploads/6fa9d842-c546-4063-bb0d-6d7237b7494b.webp','',1000,1000,'[]','.webp','product','BR-PG-001','product-page','2025-09-01 08:24:54.987109'),
('IMG-6301f369','uploads/e9a0fcff-76b5-4e42-ac91-6835d379bc7f.jpeg','',1000,1000,'[]','.jpeg','product','EX-WP-001','product-page','2025-09-01 12:28:37.700794'),
('IMG-632e17ba','uploads/903846e3-8f85-47e4-9f5e-9e50bfbdbf55.webp','',1000,1000,'[]','.webp','product','PR-CO-001','product-page','2025-09-04 07:33:10.682982'),
('IMG-632f38d4','uploads/a0ae38e0-9e7b-4102-961b-fe2a1cf41847.jpeg','',1000,1000,'[]','.jpeg','product','TA-EF-001','product-page','2025-09-02 08:05:42.227980'),
('IMG-64395d03','uploads/3b506b4c-f905-4591-9ffd-97751becd095.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.515719'),
('IMG-654a20fb','uploads/d1fc61bd-cbac-4284-a94e-af64269423e1.jpeg','',1000,1000,'[]','.jpeg','product','WO-EC-001','product-page','2025-09-01 06:29:30.120632'),
('IMG-65519455','uploads/57e254ee-144c-4d86-a079-33f00cd1e373.jpeg','',1000,1000,'[]','.jpeg','product','TR-DS-001','product-page','2025-09-03 13:08:57.658850'),
('IMG-657e5683','uploads/3d6a6377-4656-4a39-ae66-f1fa08efb59a.jpeg','',1000,1000,'[]','.jpeg','product','NO-CB-001','product-page','2025-09-01 11:45:09.072896'),
('IMG-659ef9f1','uploads/59890163-4378-4ea4-a426-82394294c412.jpeg','',1000,1000,'[]','.jpeg','product','EV-RJ-001','product-page','2025-09-01 07:04:51.898669'),
('IMG-6614dce2','uploads/42fe67b0-50c8-413b-8d07-3d23cdd00692.webp','',1000,1000,'[]','.webp','product','BA-EC-002','product-page','2025-09-01 06:31:13.168962'),
('IMG-66262117','uploads/Decorative__Promotional.png','Alt-text',2250,1500,'[]','.png','subcategory','EG&S-DECORATIVE-001','CategorySubCategoryPage','2025-09-09 14:05:51.018795'),
('IMG-663e2f00','uploads/5b16caa7-d592-4c8a-b8ad-ebe6a95e8177.jpeg','',260,260,'[]','.jpeg','product','EV-CR-001','product-page','2025-09-04 08:18:38.177828'),
('IMG-667a30ef','uploads/befe282a-6432-4a1d-93c3-ddf740a8eb65.webp','',1000,1000,'[]','.webp','product','CO-CC-001','product-page','2025-09-01 06:50:01.396241'),
('IMG-668cf9a1','uploads/5086ae54-8542-4112-b427-ebe644cd24db.jpeg','',1000,1000,'[]','.jpeg','product','CA-MN-001','product-page','2025-09-01 11:20:26.656367'),
('IMG-66b7ad6c','uploads/85afe4ac-71f8-454e-868a-9080d6999004.jpeg','',1000,1000,'[]','.jpeg','product','CA-FW-001','product-page','2025-09-01 11:08:15.437448'),
('IMG-66bb8f21','uploads/11f78d42-6cfe-40b1-a581-eda665be9847.jpeg','',1000,1000,'[]','.jpeg','product','NO-SN-001','product-page','2025-09-01 12:10:13.236722'),
('IMG-6731ec59','uploads/e1881ef2-6fa5-4db1-aff1-f44ff11e2abc.jpeg','',500,403,'[]','.jpeg','product','PR-CC-002','product-page','2025-09-04 07:54:34.985397'),
('IMG-67545d12','uploads/0ecd2757-5dab-4684-850a-6ad884dc7d5a.jpeg','',1000,1000,'[]','.jpeg','product','AC-WA-001','product-page','2025-09-01 08:23:31.502783'),
('IMG-67701935','uploads/Kids_Apparel.png','Alt-text',2250,1500,'[]','.png','subcategory','CAA-KIDS\'-001','CategorySubCategoryPage','2025-09-09 08:08:14.674226'),
('IMG-679aa922','uploads/accaedf8-91de-4305-9e2a-cbc1bf1eed07.jpeg','',1000,1000,'[]','.jpeg','product','EV-VN-001','product-page','2025-09-01 08:01:45.627018'),
('IMG-6802c018','uploads/17763d6b-1c49-49b2-97da-a32e92c11248.jpeg','',1000,1000,'[]','.jpeg','product','WO-BW-001','product-page','2025-09-01 06:22:19.839340'),
('IMG-6838e974','uploads/8450bfc9-0be5-4626-8130-8657fd569821.jpeg','',1000,1000,'[]','.jpeg','product','CE-CG-001','product-page','2025-09-01 08:07:35.355077'),
('IMG-68393e7e','uploads/ea71d370-1406-4a57-9552-26e8a508ba00.jpeg','',260,260,'[]','.jpeg','product','EX-CC-002','product-page','2025-09-04 08:11:46.929263'),
('IMG-68bc4912','uploads/2120102f-632b-477c-b0fb-086bfd9f1810.jpeg','',1000,1000,'[]','.jpeg','product','TR-TT-001','product-page','2025-09-01 12:10:47.297596'),
('IMG-68c4468c','uploads/51917980-6c5c-46fc-bf41-152136e6b8f3.jpeg','',1000,1000,'[]','.jpeg','product','CO-CL-001','product-page','2025-09-01 06:44:22.465961'),
('IMG-68d44310','uploads/793678cf-f490-4e52-8116-1ff23f124f12.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.157435'),
('IMG-68eaa16a','uploads/3c1a3bf3-5faa-4862-a449-3ef8acfade16.webp','',1000,1000,'[]','.webp','product','PR-CO-001','product-page','2025-09-04 07:33:10.671039'),
('IMG-698d63a5','uploads/36a88d9d-32ed-416f-ad75-b09dc99ded45.webp','',1000,1000,'[]','.webp','product','SP-RT-001','product-page','2025-09-01 11:35:38.987506'),
('IMG-69fcb131','uploads/fec61b85-035d-4f0e-8299-c36c681c5b9c.webp','',1000,1000,'[]','.webp','product','GI-LP-001','product-page','2025-09-01 06:24:30.078635'),
('IMG-6a0e10fa','uploads/db5a0050-2aad-4172-9a00-b0ee56e07468.jpeg','',1000,1000,'[]','.jpeg','product','EV-VN-001','product-page','2025-09-01 08:01:45.621284'),
('IMG-6a29db2c','uploads/f48ac8de-55c8-4bbe-ad42-6a6f88f7598f.jpeg','',1000,1000,'[]','.jpeg','product','EC-BF-001','product-page','2025-09-04 07:10:08.133664'),
('IMG-6a5a85a4','uploads/45f5b162-1f0a-4cdb-b6f4-d33b193e9219.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-002','product-page','2025-09-01 09:19:55.181347'),
('IMG-6a6d3891','uploads/80a80bcf-428e-4cf3-9ddf-0e7e32bae534.jpeg','',1000,1000,'[]','.jpeg','product','TR-CW-001','product-page','2025-09-01 08:07:06.739070'),
('IMG-6b29b145','uploads/a6f6e6a5-417e-42ac-b0fe-41554b9ec19c.jpeg','',1000,1000,'[]','.jpeg','product','PO-MD-001','product-page','2025-09-01 06:56:25.398569'),
('IMG-6b749965','uploads/e29abd19-348b-41a7-a6f7-89e92096c115.jpeg','',1000,1000,'[]','.jpeg','product','AC-CC-001','product-page','2025-09-01 08:08:19.108127'),
('IMG-6d142d84','uploads/44673597-596d-4a40-b863-6730231f7cbf.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.155477'),
('IMG-6d3a0ac3','uploads/fd9a97a8-df82-4290-ab82-7b9cf4b83e0d.jpeg','',1000,1000,'[]','.jpeg','product','CA-MN-001','product-page','2025-09-01 11:20:26.654473'),
('IMG-6d77c983','uploads/74bddbc4-e3a7-46e6-a4ff-d75bb1fa0f5f.jpeg','',1000,1000,'[]','.jpeg','product','CO-BE-001','product-page','2025-09-01 06:38:34.683992'),
('IMG-6ddf0d9a','uploads/8e443ec4-cf0e-40c9-b2fe-8f531e902708.jpeg','',1000,1000,'[]','.jpeg','product','PO-HC-001','product-page','2025-09-01 06:52:00.850083'),
('IMG-6e501b3b','uploads/60cd4620-7703-4f9a-8c11-cd477467f0b8.jpeg','',1000,1000,'[]','.jpeg','product','CA-2T-001','product-page','2025-09-01 11:05:36.367364'),
('IMG-6e5adecb','uploads/56f2caaa-84b8-4bce-a01e-7911361c2e8f.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.159287'),
('IMG-6f2ebc42','uploads/9c5c2374-d52d-4024-afaf-a14d133c5e47.jpeg','',1000,1000,'[]','.jpeg','product','NO-LP-001','product-page','2025-09-01 12:06:56.680406'),
('IMG-703739c0','uploads/ac9b33ba-c6fc-4df8-a449-6b46e48dfe2a.jpeg','',1000,1000,'[]','.jpeg','product','NO-BA-001','product-page','2025-09-01 11:49:22.084281'),
('IMG-70bc8e44','uploads/af50a05f-4b56-4192-9a47-4075fe149e96.jpeg','',1000,1000,'[]','.jpeg','product','AC-WA-001','product-page','2025-09-01 08:23:31.506476'),
('IMG-71a00eff','uploads/a9daa749-80a8-494c-a342-79264ff7b4aa.jpeg','',1000,1000,'[]','.jpeg','product','EX-PL-001','product-page','2025-09-04 07:39:52.247930'),
('IMG-71ad1748','uploads/9fa8f099-05a0-4feb-9ec0-cad6391febaa.jpeg','',260,260,'[]','.jpeg','product','EX-CB-001','product-page','2025-09-04 08:07:29.832830'),
('IMG-71c7cfdf','uploads/f7d1a53f-a5e4-4429-8ad0-617d4f5ac13e.jpeg','',1000,1000,'[]','.jpeg','product','PO-MD-001','product-page','2025-09-01 06:56:25.394123'),
('IMG-71ef152d','uploads/adc87134-56f4-4942-bc95-477e9f765964.jpeg','',1000,1000,'[]','.jpeg','product','CE-PC-001','product-page','2025-09-01 09:24:05.824433'),
('IMG-720e2398','uploads/9bd04875-66f1-485d-a774-a440cbfd73f8.png','',2250,1500,'[]','.png','product','PR-CP-001','product-page','2025-09-01 12:12:10.700006'),
('IMG-721ceacf','uploads/37b5bd57-033f-436e-85e1-d280cf6420fb.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','CE-CE-001','product-page','2025-09-01 08:23:54.311848'),
('IMG-728ff72e','uploads/7e044986-0fac-4801-b812-6b9d1236ab8b.jpeg','',1000,1000,'[]','.jpeg','product','CA-BC-001','product-page','2025-09-01 11:01:10.802582'),
('IMG-7291ea57','uploads/b0a20306-387d-443e-83ee-c3adeb5e0130.jpeg','',260,260,'[]','.jpeg','product','BR-PP-001','product-page','2025-09-04 07:59:19.774874'),
('IMG-73004b4b','uploads/d3378c82-7af9-47e6-820e-dbcab6e6cec7.jpeg','',1000,1000,'[]','.jpeg','product','WO-EF-001','product-page','2025-09-03 13:05:04.526367'),
('IMG-7323ea7e','uploads/f25849c4-d4d1-4f29-94ca-249dbe41d6aa.jpeg','',1000,1000,'[]','.jpeg','product','CE-WS-001','product-page','2025-09-01 09:09:17.544434'),
('IMG-74a0dd0a','uploads/b353dac3-9a8f-4b6b-a9cc-7a59b0ee845b.jpeg','',1000,1000,'[]','.jpeg','product','PO-BB-001','product-page','2025-09-01 06:54:02.151136'),
('IMG-74b2dc03','uploads/baab166e-b485-4a07-b238-08b7240370e2.jpeg','',260,260,'[]','.jpeg','product','CO-UM-001','product-page','2025-09-04 08:33:25.910370'),
('IMG-7504d57b','uploads/9b6126cd-28c8-4788-b88c-75909469277b.jpeg','',850,850,'[]','.jpeg','product','FL-CF-001','product-page','2025-09-11 06:08:39.769626'),
('IMG-7538c760','uploads/17e0c9c7-362b-4c15-98f4-c27e53c04682.webp','',1000,1000,'[]','.webp','product','PL-SM-001','product-page','2025-09-01 06:27:33.395829'),
('IMG-754806e8','uploads/1d47840f-1d79-41fd-8a8c-cda83b2c9193.jpeg','',260,260,'[]','.jpeg','product','EV-CE-001','product-page','2025-09-04 08:16:40.242226'),
('IMG-754b9060','uploads/T-Shirts__Polo_Shirts.png','Alt-text',2250,1500,'[]','.png','subcategory','CAA-T-SHIRTS-001','CategorySubCategoryPage','2025-09-09 07:59:03.203487'),
('IMG-75f1f9a7','uploads/b602d649-e0f0-40e6-b97f-89f05781abfc.webp','',1000,1000,'[]','.webp','product','TR-CC-001','product-page','2025-09-01 08:10:42.753138'),
('IMG-7645a4bc','uploads/eec4c01e-f7a4-4a6a-8033-22d81fab4fec.jpeg','',1000,1000,'[]','.jpeg','product','PO-HC-001','product-page','2025-09-01 06:52:00.860863'),
('IMG-76be8052','uploads/Standard_Business_Card_0zjLDUJ.png','Alt-text',2250,1500,'[]','.png','subcategory','P&MM-BUSINESS-001','CategorySubCategoryPage','2025-09-03 15:26:41.917036'),
('IMG-7702a4ac','uploads/23788b6a-38bc-446a-bb57-ef68955aeb75.jpeg','',886,886,'[]','.jpeg','product','FL-HD-001','product-page','2025-09-11 06:13:31.006185'),
('IMG-770fbc43','uploads/703fe375-404e-4b01-9594-868b12d74a0a.jpeg','',260,260,'[]','.jpeg','product','CO-EF-001','product-page','2025-09-04 08:23:28.453277'),
('IMG-7761582f','uploads/36da3ebc-0bf3-49b3-9507-a255364061e7.jpeg','',1000,1000,'[]','.jpeg','product','AC-CP-001','product-page','2025-09-01 08:21:39.599256'),
('IMG-77bbf26f','uploads/dc7d7d19-7fe9-4512-94f0-078fa21ea312.jpeg','',1000,1000,'[]','.jpeg','product','EX-WP-001','product-page','2025-09-01 12:28:37.702610'),
('IMG-78d1256d','uploads/6d5cd885-a880-467b-a25e-d55945ec087b.jpeg','',1000,1000,'[]','.jpeg','product','EV-CL-001','product-page','2025-09-01 10:10:07.083790'),
('IMG-78e0bfdf','uploads/ffc541a0-a8e6-4094-a93c-452e359848db.jpeg','',1000,1000,'[]','.jpeg','product','NO-BA-001','product-page','2025-09-01 11:49:22.086150'),
('IMG-7915fee0','uploads/78f462ad-7a0e-4a28-8a5a-d36a5af2938b.webp','',900,700,'[]','.webp','product','BA-FB-001','product-page','2025-09-11 07:23:36.143125'),
('IMG-7a4c3e2b','uploads/018d5034-e19b-4df3-a45f-4a9221c3fd3c.webp','',1000,1000,'[]','.webp','product','SP-RT-001','product-page','2025-09-01 11:35:38.989910'),
('IMG-7a6bbc91','uploads/d74a8812-13fc-4de1-a016-683950ca273d.jpeg','',1000,1000,'[]','.jpeg','product','TA-EF-001','product-page','2025-09-02 08:05:42.229951'),
('IMG-7a73e3ea','uploads/8c367ca9-4e59-43da-90f3-6c6d59c9c010.jpeg','',1000,1000,'[]','.jpeg','product','CA-PS-001','product-page','2025-09-02 07:54:11.380551'),
('IMG-7ab332e8','uploads/99461599-dea8-4f63-93ce-681cafb1d5d5.webp','',1000,1000,'[]','.webp','product','BR-CR-001','product-page','2025-09-01 08:34:53.200322'),
('IMG-7b4d623f','uploads/235db482-4e7f-4156-8402-dc11eebf8e6f.webp','Hero Desktop Image',4320,1200,'[\"hero\", \"desktop\"]','.webp','HeroBanner','HERO-3ca56c57','hero-banner','2025-08-28 18:05:36.362513'),
('IMG-7b5f8d9f','uploads/bf949c09-3289-4dfd-9dcc-fd47a3ae9efa.jpeg','',1000,1000,'[]','.jpeg','product','EV-TW-001','product-page','2025-09-01 10:13:10.529627'),
('IMG-7c325476','uploads/58dc354f-ab07-4d79-86bf-a54874613713.webp','',1000,1000,'[]','.webp','product','CO-CC-001','product-page','2025-09-01 06:50:01.401919'),
('IMG-7c41237c','uploads/Writing_Instruments.png','Best Ballpoint Pen in Dubai, High-quality smooth-writing pen for everyday use.',2250,1500,'[]','.png','category','WI-1','CategorySubCategoryPage','2025-09-02 10:46:33.844632'),
('IMG-7c498fc2','uploads/9cd006d5-c56d-4e10-9d9c-909e6168e711.webp','',1000,1000,'[]','.webp','product','PL-SM-001','product-page','2025-09-01 06:27:33.387562'),
('IMG-7ce74dd1','uploads/92947b23-f953-4e69-bed0-08c095484cb6.jpeg','',1000,1000,'[]','.jpeg','product','PO-MD-001','product-page','2025-09-01 06:56:25.389626'),
('IMG-7dd06ebd','uploads/c8f486ee-9c8e-4828-9b7a-6986841c0c1c.jpeg','',1000,1000,'[]','.jpeg','product','NO-SN-002','product-page','2025-09-01 12:14:18.334397'),
('IMG-7e382c65','uploads/65953bb8-7174-47b6-aceb-2b27bb60d942.jpeg','',1000,1000,'[]','.jpeg','product','BR-CP-001','product-page','2025-09-01 08:13:41.692334'),
('IMG-7e679969','uploads/d326331c-b959-44de-9ce5-2099e1bb3f71.jpeg','',300,300,'[]','.jpeg','product','CA-PR-001','product-page','2025-09-01 11:36:48.054612'),
('IMG-7ec1f3f3','uploads/64157329-a243-41d8-a1cd-811054d5c0fc.jpeg','',850,850,'[]','.jpeg','product','FL-HB-001','product-page','2025-09-11 06:24:47.288284'),
('IMG-7f14cfee','uploads/6ac00c52-7e70-4cb2-8840-da586b7ddb69.jpeg','',1000,1000,'[]','.jpeg','product','BA-MC-001','product-page','2025-09-01 06:22:17.266833'),
('IMG-7f2278b4','uploads/03d4fbd7-d82e-466a-a9fb-07f477b9d9e2.jpeg','',1000,1000,'[]','.jpeg','product','CE-MC-001','product-page','2025-09-01 07:59:30.667064'),
('IMG-7fe22d24','uploads/387e85ee-59f2-4c6b-b496-901513ad64eb.jpeg','',571,571,'[]','.jpeg','product','CA-IC-001','product-page','2025-09-01 11:34:30.760690'),
('IMG-7ff3975c','uploads/b5cee250-69e3-4c80-9815-8042700d3452.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.153547'),
('IMG-8085ea97','uploads/Premium__Corporate_Gifts.png','Alt-text',2250,1500,'[]','.png','subcategory','EG&S-PREMIUM-001','CategorySubCategoryPage','2025-09-10 05:51:12.720510'),
('IMG-8176b50f','uploads/0bfdd34a-a1f3-457a-81a2-128e0c5180c2.jpeg','',850,850,'[]','.jpeg','product','FL-YS-001','product-page','2025-09-11 06:28:30.541023'),
('IMG-81c7034d','uploads/6007f55c-3dc8-4719-aaad-cd55a5c46017.jpeg','',1169,1169,'[]','.jpeg','product','FL-VC-001','product-page','2025-09-11 06:27:31.068492'),
('IMG-81dde5a6','uploads/b954519f-c174-4715-9d38-a6d0a9e23bf3.jpeg','',1000,1000,'[]','.jpeg','product','TR-DW-001','product-page','2025-09-01 11:55:58.684546'),
('IMG-81f01c37','uploads/a04b0546-93b1-4c9d-8234-4aa61ac0ca58.jpeg','',260,260,'[]','.jpeg','product','NO-CC-001','product-page','2025-09-04 08:05:19.045741'),
('IMG-820bea1a','uploads/2a909aef-6879-4240-a6aa-9777590db566.webp','Hero Desktop Image',4320,1200,'[\"hero\", \"desktop\"]','.webp','HeroBanner','HERO-3ca56c57','hero-banner','2025-08-28 18:05:36.410687'),
('IMG-82107623','uploads/48c508e1-a06d-451a-a965-e53f45fa9055.webp','',1000,1000,'[]','.webp','product','CE-TT-003','product-page','2025-09-01 09:41:51.591588'),
('IMG-828a05b5','uploads/f52ffc08-c508-4592-88d9-99e517b1d3dc.jpeg','',1000,1000,'[]','.jpeg','product','PO-BB-001','product-page','2025-09-01 06:54:02.149282'),
('IMG-831826fc','uploads/a71df3d5-f884-4034-89b7-f197425a3189.jpeg','',1000,1000,'[]','.jpeg','product','CE-GB-001','product-page','2025-09-01 09:04:01.020022'),
('IMG-8321a94b','uploads/43b2a670-e54a-4cca-8d96-35be27ff12b2.jpeg','',1280,1280,'[]','.jpeg','product','FL-PF-002','product-page','2025-09-11 06:31:34.726145'),
('IMG-8383d894','uploads/Travel__Insulated_Mugs.png','Alt-text',2250,1500,'[]','.png','subcategory','D-TRAVEL-001','CategorySubCategoryPage','2025-09-09 11:40:59.154047'),
('IMG-83f98cfb','uploads/907737a5-4520-4d07-bff2-5da77fb7e2f4.webp','',1000,1000,'[]','.webp','product','EV-SC-001','product-page','2025-09-01 06:32:55.784083'),
('IMG-8476f5ae','uploads/f6660e80-831f-4906-872d-e3f3371b4553.jpeg','',1000,1000,'[]','.jpeg','product','EV-LW-001','product-page','2025-09-01 10:08:07.441031'),
('IMG-847b4963','uploads/44992b23-be67-46d3-9da2-0bffe30dc29e.jpeg','',1000,1000,'[]','.jpeg','product','NO-BA-001','product-page','2025-09-01 11:49:22.075414'),
('IMG-84e5a747','uploads/773077ac-10fe-40a9-9d9c-b336e6385195.jpeg','',1000,1000,'[]','.jpeg','product','TR-CT-001','product-page','2025-09-01 07:50:09.478435'),
('IMG-85f2c99d','uploads/0d995968-9e0e-4af3-a86a-3d6944edb6ec.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-002','product-page','2025-09-01 09:19:55.177588'),
('IMG-85fe45aa','uploads/19c8f84e-421c-4386-b0fe-1d6dd841bb3f.jpeg','',1000,1000,'[]','.jpeg','product','NO-BA-001','product-page','2025-09-01 11:49:22.078982'),
('IMG-8670d875','uploads/20f08056-d690-42f4-ab0f-7cd3bb96ce39.jpeg','',1000,1000,'\"\"','.jpeg','product','PR-CC-001','product-page','2025-09-04 07:52:14.610852'),
('IMG-875034b4','uploads/4ed86d48-7f04-4b20-8b74-a433116f5811.webp','',1000,1000,'[]','.webp','product','DE-BF-001','product-page','2025-09-01 10:22:47.028786'),
('IMG-885c5232','uploads/659b5703-8347-4b6e-b1d1-16f4a8b52593.jpeg','',1000,1000,'[]','.jpeg','product','CE-WS-001','product-page','2025-09-01 09:09:17.542762'),
('IMG-888834ff','uploads/2bdef768-3527-49da-8505-ecc60151569e.webp','',1000,1000,'[]','.webp','product','CA-MN-001','product-page','2025-09-01 11:20:26.664625'),
('IMG-88f2bbd9','uploads/1a825949-5c81-4369-900d-0263530dd643.jpeg','',260,260,'[]','.jpeg','product','EX-CC-002','product-page','2025-09-04 08:11:46.931359'),
('IMG-89396cbe','uploads/886412ec-5145-496e-8cad-1d9485d92d33.jpeg','',260,260,'[]','.jpeg','product','NO-CC-001','product-page','2025-09-04 08:05:19.047645'),
('IMG-89a1519e','uploads/3822a98d-40a7-439d-b597-ad68e0a5d0ce.jpeg','',1000,1000,'[]','.jpeg','product','EX-WP-001','product-page','2025-09-01 12:28:37.704348'),
('IMG-89ab784e','uploads/e67e1166-1a8b-4ec1-9e9a-4680283364d2.jpeg','',1000,1000,'[]','.jpeg','product','SP-TB-001','product-page','2025-09-01 10:38:01.219557'),
('IMG-89b74a01','uploads/049b2691-e908-4c48-be6b-0d353f40492b.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','CE-CE-001','product-page','2025-09-01 08:23:54.308495'),
('IMG-89bfe62e','uploads/6d0639af-2b54-4e82-9486-320294ce1f8b.jpeg','',1000,1000,'[]','.jpeg','product','WO-BW-001','product-page','2025-09-01 06:22:19.834143'),
('IMG-8a2614da','uploads/Pen_Gift_Set_pIxyC3c.png','Alt-text',2250,1500,'[]','.png','subcategory','WI-GIFT-001','CategorySubCategoryPage','2025-09-09 10:24:15.916969'),
('IMG-8a6b07a1','uploads/34a8635e-0ce7-469f-8d60-a50122572532.webp','',1000,1000,'[]','.webp','product','BA-EC-001','product-page','2025-09-01 06:24:50.906765'),
('IMG-8a9e908c','uploads/22c966de-49f7-421d-ab15-2e6ba579ec21.webp','',1000,1000,'[]','.webp','product','BA-EC-001','product-page','2025-09-01 06:24:50.902827'),
('IMG-8aa6f019','uploads/08d2247a-6208-4670-996c-c86dc8c47d7b.webp','',1000,1000,'[]','.webp','product','CE-CM-001','product-page','2025-09-01 09:32:14.775355'),
('IMG-8b13e30c','uploads/28d671a5-f4b8-4286-80b5-927cd2b2d91a.jpeg','',1000,1000,'[]','.jpeg','product','PL-AP-001','product-page','2025-09-03 12:56:02.081937'),
('IMG-8b1fa8cf','uploads/88d1b557-810f-46b0-ab13-2d9f3f11fbda.jpeg','',260,260,'[]','.jpeg','product','CA-CO-001','product-page','2025-09-04 08:13:38.310746'),
('IMG-8b40b12a','uploads/354a5133-ac84-4b34-9e31-4b9e1453c638.jpeg','',1000,1000,'[]','.jpeg','product','SP-RB-001','product-page','2025-09-01 11:20:18.621356'),
('IMG-8b5a9108','uploads/10f87def-b21e-4434-8f44-74250b1c3f1f.jpeg','',260,260,'[]','.jpeg','product','NO-CC-001','product-page','2025-09-04 08:05:19.041778'),
('IMG-8bb0daf5','uploads/f4e62272-3003-4e34-9132-433aae625fd7.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-002','product-page','2025-09-01 09:19:55.173882'),
('IMG-8c9d6f93','uploads/31d9e377-dfb5-455a-9386-1ebe12914e41.jpeg','',1000,1000,'[]','.jpeg','product','CE-GC-001','product-page','2025-09-01 09:12:16.139309'),
('IMG-8cc8296d','uploads/d96f1f25-ed80-453c-99f6-a4f22b495a0a.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-001','product-page','2025-09-01 07:19:05.015676'),
('IMG-8cd146bb','uploads/f21460f9-3954-49d9-944e-15c9f3af4bbf.jpeg','',1000,1000,'[]','.jpeg','product','BR-CA-001','product-page','2025-09-01 08:38:07.661942'),
('IMG-8d1b9a64','uploads/33db8e4d-2391-4beb-91e8-3b845e3f870a.webp','',1000,1000,'[]','.webp','product','BA-EC-002','product-page','2025-09-01 06:31:13.167027'),
('IMG-8d91f595','uploads/899f25ec-18d3-4596-9018-9343c5feb75d.jpeg','',1000,1000,'[]','.jpeg','product','NO-PD-001','product-page','2025-09-01 11:56:03.027529'),
('IMG-8e21f431','uploads/fcd33663-7f6d-4e38-a0e8-24d1434b3a75.jpeg','',1000,1000,'[]','.jpeg','product','EC-BF-001','product-page','2025-09-04 07:10:08.138239'),
('IMG-8e28d2ef','uploads/c01da23c-9ee7-4bc6-bb04-dd3b17be8410.jpeg','',1000,1000,'[]','.jpeg','product','CE-MC-001','product-page','2025-09-01 07:59:30.663281'),
('IMG-8e5b8105','uploads/4661f91e-690c-474d-9152-d66c9178c6eb.webp','',1000,1000,'[]','.webp','product','PR-CO-001','product-page','2025-09-04 07:33:10.673534'),
('IMG-8e8a12b3','uploads/52dcd471-0fa7-4cd2-9758-a9e105317960.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-003','product-page','2025-09-01 07:52:59.452206'),
('IMG-8f3eff4b','uploads/d749d85e-12ba-4b18-b595-94b94cbd2217.jpeg','',1000,1000,'[]','.jpeg','product','PO-HC-001','product-page','2025-09-01 06:52:00.852896'),
('IMG-8fe5c707','uploads/5d4058e3-f4ac-4f1c-aca7-cce2a745f4ba.jpeg','',1000,1000,'[]','.jpeg','product','CO-BE-001','product-page','2025-09-01 06:38:34.678489'),
('IMG-90d14e5a','uploads/71874f4b-d50f-47e7-ba1d-3efa2a2eb39c.jpeg','',1000,1000,'[]','.jpeg','product','TA-SG-001','product-page','2025-09-02 08:11:13.964517'),
('IMG-91512092','uploads/7fed43c7-8dd0-4747-9e8d-453a192ca823.jpeg','',1000,1000,'[]','.jpeg','product','SP-WB-001','product-page','2025-09-01 10:44:45.887717'),
('IMG-91e5db93','uploads/a336267c-2b5f-4d32-b332-79fd5fd57ceb.jpeg','',260,260,'[]','.jpeg','product','EX-CC-001','product-page','2025-09-04 08:09:59.944556'),
('IMG-928b28ce','uploads/b58a2673-529d-4a85-ad9f-f08990c5812e.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-002','product-page','2025-09-01 08:41:07.080346'),
('IMG-93bcfd8b','uploads/Banners_Displays_and_Flags.png','Alt-text',2250,1500,'[]','.png','category','BD&F-1','CategorySubCategoryPage','2025-09-03 12:27:37.186785'),
('IMG-93cd23f4','uploads/125aa1b2-af93-4111-9084-10c88feb9f54.jpeg','',1000,1000,'[]','.jpeg','product','TA-HT-001','product-page','2025-09-02 08:09:44.178140'),
('IMG-94829de1','uploads/c80a266f-3fbb-4529-8332-626c5cc23e1a.jpeg','',1000,1000,'[]','.jpeg','product','TR-PT-001','product-page','2025-09-01 07:54:24.527583'),
('IMG-95303739','uploads/91f041ea-5804-4a1c-b8a3-ea225d877dec.jpeg','',600,600,'[]','.jpeg','product','EV-CE-001','product-page','2025-09-04 08:16:40.247545'),
('IMG-953874b3','uploads/77740382-0e18-4f90-a02e-d61906f883b3.webp','',1000,1000,'[]','.webp','product','TR-LT-001','product-page','2025-09-01 12:06:27.323408'),
('IMG-955072d4','uploads/71ab07d5-d2b1-4a63-9ea3-2be811de719e.jpeg','',1000,1000,'[]','.jpeg','product','CE-LM-001','product-page','2025-09-01 10:13:38.514045'),
('IMG-958f5197','uploads/Executive_Diaries__Planners.png','Alt-text',2250,1500,'[]','.png','subcategory','O&S-EXECUTIVE-001','CategorySubCategoryPage','2025-09-04 14:08:36.346696'),
('IMG-95ed8196','uploads/177ee4ff-bfe0-4f46-a763-822cf6512785.jpeg','',1000,1001,'\"\"','.jpeg','product','PR-CC-001','product-page','2025-09-04 07:52:14.604983'),
('IMG-96244a00','uploads/3bd78e56-3ae6-43ab-b840-660adf5a127f.jpeg','',260,260,'[]','.jpeg','product','EV-CR-002','product-page','2025-09-04 08:21:03.958622'),
('IMG-96bf55dc','uploads/a96da26c-8c0d-4547-bda7-98d60fc9aaef.jpeg','',1000,1000,'[]','.jpeg','product','TA-RG-001','product-page','2025-09-02 08:12:46.436626'),
('IMG-978efc93','uploads/c006f952-12da-42b4-ae49-5abb35f16bd5.jpeg','',1000,1000,'[]','.jpeg','product','PL-AP-001','product-page','2025-09-03 12:56:02.083901'),
('IMG-97e03640','uploads/6bbd4497-d04a-4ea7-a841-08082e11abb1.jpeg','',640,640,'[]','.jpeg','product','BA-EC-001','product-page','2025-09-01 06:24:50.913765'),
('IMG-98329af8','uploads/19c041ee-5ac2-4cdb-b5e2-f4c604905b4f.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.147958'),
('IMG-9832cb2d','uploads/4ca951f1-358f-4317-8380-01cc27e60bed.jpeg','',260,260,'[]','.jpeg','product','CA-CO-001','product-page','2025-09-04 08:13:38.305925'),
('IMG-98879c49','uploads/c5090c31-6da9-4ccd-869e-e74cb12fd342.webp','',1000,1000,'[]','.webp','product','GI-LP-001','product-page','2025-09-01 06:24:30.069500'),
('IMG-98e02991','uploads/581cf243-ad35-4adc-96aa-ada441324180.jpeg','',260,260,'[]','.jpeg','product','EX-CB-001','product-page','2025-09-04 08:07:29.834522'),
('IMG-98e3e26b','uploads/20a19c4d-31c8-4bdb-aeb1-1488b0e6d9d6.jpeg','',1000,1000,'[]','.jpeg','product','EC-EF-001','product-page','2025-09-04 07:01:28.063574'),
('IMG-992b1460','uploads/232e89a0-46db-485f-a537-5570c50da790.jpeg','',260,260,'[]','.jpeg','product','CO-DU-001','product-page','2025-09-04 08:28:56.005213'),
('IMG-995af78f','uploads/b345a0f6-dcb3-48b5-a763-5900cd44fb0f.jpeg','',260,260,'[]','.jpeg','product','EX-CC-002','product-page','2025-09-04 08:11:46.935112'),
('IMG-99862e54','uploads/e1542cff-5f44-41e1-b28c-98d149e6641b.jpeg','',1000,1000,'[]','.jpeg','product','AC-CC-001','product-page','2025-09-01 08:08:19.103883'),
('IMG-99eb4f8e','uploads/47d54de3-5f97-4ca7-a8d7-76f0124df281.jpeg','',1000,1000,'[]','.jpeg','product','EV-CL-001','product-page','2025-09-01 10:10:07.079835'),
('IMG-9a1a2d60','uploads/873856c6-5840-4c5f-a6f6-e9354886d466.webp','',1000,1000,'[]','.webp','product','CO-CC-001','product-page','2025-09-01 06:50:01.406439'),
('IMG-9a6001cc','uploads/92ceea6c-1c32-467b-b855-b282c40102ca.jpeg','',1000,1000,'[]','.jpeg','product','CA-RA-001','product-page','2025-09-01 11:24:13.359788'),
('IMG-9aa926df','uploads/05e3646f-033e-4a75-a29f-3545e19b9155.jpeg','',1000,1000,'[]','.jpeg','product','SP-WB-002','product-page','2025-09-01 11:15:09.143302'),
('IMG-9abe2491','uploads/5644d9df-afe7-4b2d-98c0-f92f6e3d2cf4.jpeg','',260,173,'[]','.jpeg','product','PR-CP-002','product-page','2025-09-04 07:56:17.776267'),
('IMG-9b20e839','uploads/83122546-2a7d-48ba-a56d-d42232358edc.jpeg','',1000,1000,'[]','.jpeg','product','CA-MN-001','product-page','2025-09-01 11:20:26.650609'),
('IMG-9b36a5fc','uploads/6277dea4-c2ca-4b05-95df-5a5ee48075fa.jpeg','',260,260,'[]','.jpeg','product','EX-CB-001','product-page','2025-09-04 08:07:29.829273'),
('IMG-9b8dcf07','uploads/e5b39328-c6f5-4672-8137-d91a2e9ee89c.jpeg','',1000,1000,'[]','.jpeg','product','CE-BS-001','product-page','2025-09-01 08:18:56.299872'),
('IMG-9bd7e6bb','uploads/3d1cdaa4-3f93-42ee-b683-417b52db05ec.jpeg','',1000,1000,'[]','.jpeg','product','EX-PL-001','product-page','2025-09-04 07:39:52.255659'),
('IMG-9be8a6cd','uploads/4c4b8ff3-0236-4471-ac63-f12ee486fd1f.jpeg','',260,260,'[]','.jpeg','product','EV-CR-001','product-page','2025-09-04 08:18:38.173911'),
('IMG-9c2bc050','uploads/61595073-9fc0-4135-87aa-c1726f3f8973.jpeg','',260,139,'[]','.jpeg','product','CO-EF-001','product-page','2025-09-04 08:23:28.446354'),
('IMG-9cf43281','uploads/1b949cdf-304c-4e7d-9a63-64493b018bed.jpeg','',1000,1000,'[]','.jpeg','product','SP-PB-001','product-page','2025-09-04 06:52:49.246521'),
('IMG-9d0cd24d','uploads/105ce268-e469-4bdf-a9fd-24bb65e79963.jpeg','',1000,1000,'[]','.jpeg','product','TR-PT-001','product-page','2025-09-01 07:54:24.531886'),
('IMG-9d1ad4d1','uploads/108ffe95-50e9-4763-b7f1-5cdd7c22b5d2.jpeg','',260,348,'[]','.jpeg','product','PR-CP-002','product-page','2025-09-04 07:56:17.781862'),
('IMG-9d244602','uploads/fd59c384-f66d-4501-820b-59813c248015.jpeg','',1000,1000,'[]','.jpeg','product','CE-WS-001','product-page','2025-09-01 09:09:17.541063'),
('IMG-9d826841','uploads/88b6afd7-06d5-4580-bf05-dd1b3b229209.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-003','product-page','2025-09-01 10:09:15.173108'),
('IMG-9deb33c4','uploads/e002560b-67f2-4f6a-bda2-261a43278b34.jpeg','',1000,1000,'[]','.jpeg','product','PO-HC-001','product-page','2025-09-01 06:52:00.858520'),
('IMG-9e4b8fe2','uploads/7a132427-7073-4440-8554-b1762f209ad1.jpeg','',1000,1000,'[]','.jpeg','product','CA-AN-001','product-page','2025-09-01 11:26:58.731505'),
('IMG-9ef164eb','uploads/2fcf4fe9-b4f3-46ba-ba13-12bbae03bdab.jpeg','',1000,1000,'[]','.jpeg','product','TA-RG-001','product-page','2025-09-02 08:12:46.432862'),
('IMG-9f445a64','uploads/4fef965e-cdec-4953-b54f-5ef609cf0504.jpeg','',1000,1000,'[]','.jpeg','product','NO-CB-001','product-page','2025-09-01 11:45:09.071067'),
('IMG-a0037312','uploads/83013515-6747-46ae-8363-b4ef9efc7c84.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','TR-DW-002','product-page','2025-09-01 12:03:05.325780'),
('IMG-a03d1936','uploads/32d0dcaf-4dca-4c24-9867-0f584eb4fb88.jpeg','',1000,1000,'[]','.jpeg','product','EC-EF-001','product-page','2025-09-04 07:01:28.068128'),
('IMG-a067fe27','uploads/7ce6ebaa-4d90-4f14-88b4-5fe44da2cf03.jpeg','',260,260,'[]','.jpeg','product','CO-EF-001','product-page','2025-09-04 08:23:28.448102'),
('IMG-a12f42ce','uploads/a60e1732-3fe5-4375-846c-ea0b5bfeda7d.jpeg','',1000,1000,'[]','.jpeg','product','CA-PS-001','product-page','2025-09-02 07:54:11.377929'),
('IMG-a16bc0c2','uploads/48b0e758-f1ec-4435-9957-48b2b54871e5.jpeg','',1000,1000,'[]','.jpeg','product','SP-SS-001','product-page','2025-09-01 11:06:03.144952'),
('IMG-a186b8cf','uploads/40567058-c9aa-4ce2-9e67-36e887a26775.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.145360'),
('IMG-a189fe32','uploads/0fa6cff9-f757-4d36-bf2c-9e0e271d4580.webp','',1000,1000,'[]','.webp','product','BA-EC-002','product-page','2025-09-01 06:31:13.159515'),
('IMG-a27dee20','uploads/a00b8ea2-f9ca-407d-8197-55b32cff8194.jpeg','',1000,1000,'[]','.jpeg','product','CA-PS-001','product-page','2025-09-02 07:54:11.385669'),
('IMG-a4958986','uploads/1f2b482a-075b-4076-b163-967b4bc85435.jpeg','',1000,1000,'[]','.jpeg','product','BR-CR-001','product-page','2025-09-01 08:34:53.208726'),
('IMG-a4a9356d','uploads/Pet_BBgkrX0.png','Alt-text',2250,1500,'[]','.png','subcategory','EG&S-PET-001','CategorySubCategoryPage','2025-09-10 05:55:16.869071'),
('IMG-a4b70fb2','uploads/Ceramic_Mug_dbqrgx1.png','Alt-text',2250,1500,'[]','.png','subcategory','D-CERAMIC-001','CategorySubCategoryPage','2025-09-09 11:28:27.829283'),
('IMG-a4e6352a','uploads/3fc7ecc2-eea4-4b45-a43e-91f153dc1893.jpeg','',1000,1000,'[]','.jpeg','product','SP-WB-001','product-page','2025-09-01 10:44:45.893746'),
('IMG-a4f96415','uploads/e0f8dda0-fa4d-490e-9d91-4b7626b2524c.jpeg','',260,173,'[]','.jpeg','product','PR-CP-002','product-page','2025-09-04 07:56:17.774417'),
('IMG-a522fb04','uploads/03a0829d-272b-4bff-8177-64388e59bbee.jpeg','',1000,1000,'[]','.jpeg','product','EV-TW-001','product-page','2025-09-01 10:13:10.533219'),
('IMG-a5c0449c','uploads/bcbeebfe-da9e-4d79-a460-b773260825ff.webp','',1000,1000,'[]','.webp','product','DE-BF-001','product-page','2025-09-01 10:22:47.040120'),
('IMG-a65c1b25','uploads/2c9436ea-e320-4a11-a35e-036a01026c60.jpeg','',1000,1000,'[]','.jpeg','product','SP-RB-001','product-page','2025-09-01 11:20:18.619448'),
('IMG-a699a20c','uploads/a8b4677f-f284-4251-bf01-d2df20937bac.webp','',1000,1000,'[]','.webp','product','BA-EC-002','product-page','2025-09-01 06:31:13.161948'),
('IMG-a725c48d','uploads/47645a3f-831b-4967-9c4c-2a1d140ff788.jpeg','',1000,1000,'[]','.jpeg','product','PR-CW-001','product-page','2025-09-01 12:13:47.813687'),
('IMG-a76ac0e3','uploads/64bcf575-6151-4f43-99cf-16a1ba6ed58f.jpeg','',1000,1000,'[]','.jpeg','product','SP-TT-001','product-page','2025-09-01 11:48:00.461330'),
('IMG-a820c2e2','uploads/3023b240-352d-4a9c-aaad-e2d7683ac271.jpeg','',1000,1000,'[]','.jpeg','product','CA-PS-001','product-page','2025-09-02 07:54:11.374929'),
('IMG-a836833d','uploads/edde6d2c-70d9-4006-a520-6843065c553e.webp','',1000,1000,'[]','.webp','product','BR-CA-001','product-page','2025-09-01 08:38:07.654041'),
('IMG-a8772df1','uploads/cf3878ff-8e90-4738-a5bc-af8fea96cbbd.jpeg','',1000,1000,'[]','.jpeg','product','CA-2T-001','product-page','2025-09-01 11:05:36.363530'),
('IMG-a90746cc','uploads/Signage.png','Signage category image',2250,1500,'[]','.png','category','S-1','CategorySubCategoryPage','2025-09-02 17:46:51.115954'),
('IMG-a9673b22','uploads/60447544-9413-482f-9d59-9acc2d4d2c03.jpeg','',1000,1000,'[]','.jpeg','product','PR-CW-001','product-page','2025-09-01 12:13:47.817887'),
('IMG-a9e4fb62','uploads/d511ab39-84af-4e64-bc2d-9c539cbd08cc.jpeg','',1000,1000,'[]','.jpeg','product','CA-FC-001','product-page','2025-09-01 11:13:10.362157'),
('IMG-aaabf99b','uploads/1115fa4b-c19b-48a7-aba6-3bda4fe07edd.jpeg','',1000,1000,'[]','.jpeg','product','TA-SG-001','product-page','2025-09-02 08:11:13.962651'),
('IMG-aaccf612','uploads/9ac75392-730a-440e-bc40-062013139ae9.jpeg','',1000,1000,'[]','.jpeg','product','NO-PD-001','product-page','2025-09-01 11:56:03.032449'),
('IMG-ab276ed5','uploads/Signage_For_Sale_Signs_Welcome_Signs_r2byuVP.png','Alt-text',2250,1500,'[]','.png','subcategory','EG&S-SIGNAGE-001','CategorySubCategoryPage','2025-09-10 05:55:46.094319'),
('IMG-ab5b668b','uploads/1c47ab7c-3bb0-4982-bd1c-1229c6391ac9.jpeg','',1000,1000,'[]','.jpeg','product','NO-CB-001','product-page','2025-09-01 11:45:09.074908'),
('IMG-abe3d81b','uploads/9e5c0bce-9dce-49a8-880a-f5280fb27dd9.jpeg','',1000,1000,'[]','.jpeg','product','CA-SB-001','product-page','2025-09-01 11:03:33.076746'),
('IMG-ac78a314','uploads/db825e89-13b9-4e39-a75e-aa9fe902f136.jpeg','',1000,1000,'[]','.jpeg','product','WO-BW-001','product-page','2025-09-01 06:22:19.836714'),
('IMG-acc76146','uploads/2c866d3f-e6db-4b85-ba8e-85de1e463c95.jpeg','',1280,1280,'[]','.jpeg','product','FL-CT-001','product-page','2025-09-11 06:35:12.922991'),
('IMG-ad2561f7','uploads/9d8a5926-a1e6-4d13-bdfe-2eaa5d05f929.webp','',1000,1000,'[]','.webp','product','EV-SC-001','product-page','2025-09-01 06:32:55.787096'),
('IMG-ad8c60df','uploads/c73dd18e-340b-4070-a92b-2cc69b103fb0.jpeg','',1000,1000,'[]','.jpeg','product','CE-BS-001','product-page','2025-09-01 08:18:56.305972'),
('IMG-ae636d4b','uploads/bb928f41-8ab8-4b6a-b96e-db59b0284777.jpeg','',1000,1000,'[]','.jpeg','product','UN-PC-001','product-page','2025-09-01 08:04:25.005381'),
('IMG-b1523439','uploads/1fceda2e-e989-4e06-b548-4063427a2464.webp','',1000,1000,'[]','.webp','product','BR-PG-001','product-page','2025-09-01 08:24:54.975159'),
('IMG-b16081be','uploads/35f91274-e286-4ca7-ac17-a5cf035173de.jpeg','',1000,1000,'[]','.jpeg','product','CE-GC-001','product-page','2025-09-01 09:12:16.143307'),
('IMG-b1a23b0e','uploads/5aaa656f-27a4-4452-8a61-84909137b875.jpeg','',1000,1000,'[]','.jpeg','product','TR-PT-001','product-page','2025-09-01 07:54:24.529520'),
('IMG-b36679aa','uploads/aa1656aa-1b08-4933-a352-574ca5eff44f.jpeg','',1000,1000,'[]','.jpeg','product','TA-RG-001','product-page','2025-09-02 08:12:46.434721'),
('IMG-b3669b2d','uploads/Uniforms__Workwear.png','Alt-text',2250,1500,'[]','.png','subcategory','CAA-UNIFORMS-001','CategorySubCategoryPage','2025-09-09 08:46:17.856368'),
('IMG-b396651e','uploads/Bags_and_Travel.png','Print shop near me in Dubai for custom bags and travel accessories.',2250,1500,'[]','.png','category','B&T-1','CategorySubCategoryPage','2025-08-29 11:25:16.469436'),
('IMG-b3dd5f50','uploads/21bb7c2f-84c3-446e-b25d-3569c8bb16c2.jpeg','',1000,1000,'[]','.jpeg','product','PR-CH-001','product-page','2025-09-01 12:14:53.453874'),
('IMG-b4303324','uploads/63a79b4b-198c-4ee6-99fd-da9794567da5.jpeg','',1000,1000,'[]','.jpeg','product','SP-TT-001','product-page','2025-09-01 11:48:00.459120'),
('IMG-b48ff8e8','uploads/62fe9715-4f97-4235-aa00-bbf86175f0d1.jpeg','',1000,1000,'[]','.jpeg','product','PO-HC-001','product-page','2025-09-01 06:52:00.863315'),
('IMG-b4e2bc85','uploads/d43a11e0-d93b-41ba-be80-b81f1b995229.jpeg','',1000,1000,'[]','.jpeg','product','BA-MC-001','product-page','2025-09-01 06:22:17.264609'),
('IMG-b4e2e4fc','uploads/e983021e-7a69-45ba-ad95-08ecfec6de34.jpeg','',800,800,'\"\"','.jpeg','product','PR-CC-001','product-page','2025-09-04 07:52:14.606971'),
('IMG-b507881e','uploads/0a678d06-abb5-4e9a-b19d-e2b99d824565.jpeg','',260,260,'[]','.jpeg','product','NO-CC-001','product-page','2025-09-04 08:05:19.043822'),
('IMG-b5dd9d85','uploads/3e75c176-dfe3-4d58-ae66-94e04266a5ac.jpeg','',1000,1000,'[]','.jpeg','product','CO-CL-001','product-page','2025-09-01 06:44:22.469568'),
('IMG-b61ccc41','uploads/f2365bcb-26d8-47da-a583-b786f74f0aef.jpeg','',1000,1000,'[]','.jpeg','product','PL-SM-001','product-page','2025-09-01 06:27:33.393994'),
('IMG-b634ffe7','uploads/10107936-c791-4c64-91a0-594c44eabb53.jpeg','',1000,1000,'[]','.jpeg','product','NO-SN-002','product-page','2025-09-01 12:14:18.330684'),
('IMG-b6cfd82b','uploads/579c8c74-2963-4615-8acd-1186aacb09a3.jpeg','',1000,1000,'[]','.jpeg','product','BR-CM-001','product-page','2025-09-01 08:20:03.126404'),
('IMG-b6f43385','uploads/9514c061-fa71-4abb-97de-4b70b99cc045.jpeg','',850,850,'[]','.jpeg','product','FL-TD-001','product-page','2025-09-11 06:39:46.617531'),
('IMG-b6ffb142','uploads/910f22d6-56ca-432a-8d10-6e55f333d9c1.jpeg','',1000,1000,'[]','.jpeg','product','EV-DP-001','product-page','2025-09-01 10:11:31.292051'),
('IMG-b70381cf','uploads/e392265e-6fbe-43c4-9333-71b082c17f77.jpeg','',1000,1000,'[]','.jpeg','product','EV-DP-001','product-page','2025-09-01 10:11:31.288248'),
('IMG-b75b200e','uploads/Sports_Bottles.png','Alt-text',2250,1500,'[]','.png','subcategory','D-SPORTS-001','CategorySubCategoryPage','2025-09-09 12:42:35.558210'),
('IMG-b7faec87','uploads/1308f7c4-08bb-45d5-b855-a5b0bc7be714.jpeg','',1000,1000,'[]','.jpeg','product','NO-LP-001','product-page','2025-09-01 12:06:56.678419'),
('IMG-b8140e0e','uploads/4699128f-6e5a-4677-ac11-acaaa4b70684.jpeg','',300,300,'[]','.jpeg','product','CA-PR-001','product-page','2025-09-01 11:36:48.052173'),
('IMG-b84a7c06','uploads/Computer__Office_Gadgets.png','Alt-text',2250,1500,'[]','.png','subcategory','T-COMPUTER-001','CategorySubCategoryPage','2025-09-04 10:23:19.104333'),
('IMG-b84cbb46','uploads/66f73f47-b5bd-4952-8b59-ff599d213460.jpeg','',1000,1000,'[]','.jpeg','product','EV-LW-001','product-page','2025-09-01 10:08:07.437019'),
('IMG-b8940c7e','uploads/910914af-62d7-4396-87b4-7eba80fcadbf.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-001','product-page','2025-09-01 07:19:05.017741'),
('IMG-b9019475','uploads/1e7ae41e-baaa-4ce5-9c77-d13777c573f2.webp','',1000,1000,'[]','.webp','product','CA-FW-001','product-page','2025-09-01 11:08:15.435336'),
('IMG-b9357941','uploads/8a40f7d2-fce2-44ce-862c-56a7c3d99f1e.webp','',900,700,'[]','.webp','product','BA-FB-002','product-page','2025-09-11 07:34:28.078652'),
('IMG-b9617570','uploads/ddedbee4-1955-42d4-ae96-239c69f00c0c.jpeg','',260,260,'[]','.jpeg','product','EX-CC-001','product-page','2025-09-04 08:09:59.949978'),
('IMG-b9e3a773','uploads/aabeabfd-bf60-451d-b274-efa758754a7b.jpeg','',260,173,'[]','.jpeg','product','PR-CC-002','product-page','2025-09-04 07:54:34.989439'),
('IMG-babaedf9','uploads/814e8917-d05a-435b-8d33-2fff6c647210.webp','',1000,1000,'[]','.webp','product','PL-SM-001','product-page','2025-09-01 06:27:33.402427'),
('IMG-baee5290','uploads/1be7865c-72d8-4419-a35a-3e5db3b89f59.jpeg','',1000,1000,'[]','.jpeg','product','CE-MC-001','product-page','2025-09-01 07:59:30.665178'),
('IMG-bb7b46e5','uploads/cb1c5677-17fb-432c-a1a8-512489287ac0.jpeg','',1000,1000,'[]','.jpeg','product','PL-AP-001','product-page','2025-09-03 12:56:02.079781'),
('IMG-bbd21882','uploads/10ce22db-4f51-425c-9bea-7c4b479e1ee3.jpeg','',1000,1000,'[]','.jpeg','product','SP-WB-001','product-page','2025-09-01 10:44:45.891747'),
('IMG-bc15618a','uploads/1d843283-a038-41bb-bbcd-052722424044.jpeg','',1000,1000,'[]','.jpeg','product','BA-MC-001','product-page','2025-09-01 06:22:17.268826'),
('IMG-bc41f433','uploads/ede02cc2-84b1-4c8f-a941-8306e939cd74.jpeg','',1000,1000,'[]','.jpeg','product','BR-CP-001','product-page','2025-09-01 08:13:41.694310'),
('IMG-bc658e57','uploads/3d9c4d18-2d1d-4b18-85ec-82edc3e2b064.jpeg','',1000,1000,'[]','.jpeg','product','CA-RA-001','product-page','2025-09-01 11:24:13.357100'),
('IMG-bc851705','uploads/feddcfe9-df32-4f83-a662-b221757ab348.jpeg','',1000,1000,'[]','.jpeg','product','CO-CL-001','product-page','2025-09-01 06:44:22.467758'),
('IMG-bc983ddb','uploads/b4f89f88-b76f-481e-b47e-4d8922e9d0bb.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-002','product-page','2025-09-01 08:41:07.076493'),
('IMG-bc9eccd4','uploads/136e5aa4-f8c1-4e28-b040-1fbd5b047862.jpeg','',260,260,'[]','.jpeg','product','BR-PP-001','product-page','2025-09-04 07:59:19.780689'),
('IMG-bd03fa83','uploads/2628c640-d1b3-4213-9b16-de35e471e79e.webp','',1000,1000,'[]','.webp','product','BA-EC-002','product-page','2025-09-01 06:31:13.171033'),
('IMG-bd2b0a51','uploads/df0d47bb-3e5b-4753-8025-a4fa2f9f1eaa.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-002','product-page','2025-09-01 09:19:55.184205'),
('IMG-bdbb38df','uploads/9b118436-ab86-48d5-82ee-98adf35a75b4.jpeg','',1000,1000,'[]','.jpeg','product','SP-WB-002','product-page','2025-09-01 11:15:09.146831'),
('IMG-bdd5c5a2','uploads/fb77f5e4-3eb0-4d62-b985-267070009b57.jpeg','',1000,1000,'[]','.jpeg','product','PO-MD-001','product-page','2025-09-01 06:56:25.391475'),
('IMG-be808af9','uploads/42a61414-256e-4d66-b9c1-5f7a7e7d7ab1.jpeg','',1000,1000,'[]','.jpeg','product','CO-BE-001','product-page','2025-09-01 06:38:34.686539'),
('IMG-bf8671c9','uploads/6bcd47f3-05ed-4c2e-964e-fde21d4d5ece.jpeg','',1000,1000,'[]','.jpeg','product','CE-GB-001','product-page','2025-09-01 09:04:01.015841'),
('IMG-bfb42902','uploads/10312ab0-8464-479d-87b2-77a7d686a9f6.jpeg','',1000,1000,'[]','.jpeg','product','CA-2T-001','product-page','2025-09-01 11:05:36.371305'),
('IMG-bfc216f5','uploads/932e947d-90a7-4442-9e2a-276cd5d5ecdd.jpeg','',1000,1000,'[]','.jpeg','product','BR-CA-001','product-page','2025-09-01 08:38:07.663683'),
('IMG-c02c0a34','uploads/8def939a-5f0c-4ffd-add4-8f0989fae8eb.webp','',900,700,'[]','.webp','product','BA-FB-001','product-page','2025-09-11 07:23:36.138362'),
('IMG-c03eb01d','uploads/1eb243c3-5ce3-4aca-abe5-50007b6f0932.jpeg','',1000,1000,'[]','.jpeg','product','BR-CM-001','product-page','2025-09-01 08:20:03.128255'),
('IMG-c075f19c','uploads/Accessories.png','Alt-text',2250,1500,'[]','.png','subcategory','CAA-ACCESSORIES-001','CategorySubCategoryPage','2025-09-09 09:48:49.363341'),
('IMG-c0f93105','uploads/42ab537b-c66c-49eb-b1ca-30b579a7b4d5.jpeg','',1000,1000,'[]','.jpeg','product','PR-CH-001','product-page','2025-09-01 12:14:53.452182'),
('IMG-c1d81296','uploads/f212662b-498f-4a29-a3eb-7924b63f3006.webp','',1000,1000,'[]','.webp','product','CO-CC-001','product-page','2025-09-01 06:50:01.404230'),
('IMG-c1db34d3','uploads/142e81ce-8d3e-412d-9c27-005008be6d7a.jpeg','',1000,1000,'[]','.jpeg','product','DE-SF-001','product-page','2025-09-01 10:26:26.206938'),
('IMG-c246e58d','uploads/Eco-Friendly_Drinkware.png','Alt-text',2250,1500,'[]','.png','subcategory','D-ECO-FRIENDLY-001','CategorySubCategoryPage','2025-09-09 12:54:31.286273'),
('IMG-c29428fc','uploads/ecca9635-1606-4dec-8582-52645043d7b2.jpeg','',1000,1000,'[]','.jpeg','product','CE-PM-001','product-page','2025-09-01 08:34:20.725913'),
('IMG-c2c696f0','uploads/Technology.png','Wireless charger with printed logo for tech gifts and events in Dubai.',2250,1500,'[]','.png','category','T-1','CategorySubCategoryPage','2025-08-29 11:03:32.277274'),
('IMG-c33d73cc','uploads/0aae35da-2465-4fdd-b221-c5cffc3ae6d1.jpeg','',1000,1000,'[]','.jpeg','product','CE-LM-001','product-page','2025-09-01 10:13:38.516017'),
('IMG-c3431cdb','uploads/fea8d279-f5e4-4a9f-976f-1efadf59016e.webp','Alt-text',1000,1000,'[]','.webp','product','SP-PS-001','product-page','2025-09-01 10:57:46.934450'),
('IMG-c367948d','uploads/f911971a-287c-4010-be87-37e94c15f099.webp','',1000,1000,'[]','.webp','product','BA-EC-001','product-page','2025-09-01 06:24:50.908623'),
('IMG-c4364a98','uploads/4796748d-006d-4e09-94cb-3a13506bcbb3.jpeg','',1000,702,'[]','.jpeg','product','PR-CC-002','product-page','2025-09-04 07:54:34.983071'),
('IMG-c47a8cb4','uploads/8d2676ee-ec3d-4e27-ad04-4571bfe7b5d7.jpeg','',1000,1000,'[]','.jpeg','product','CA-SB-001','product-page','2025-09-01 11:03:33.074738'),
('IMG-c4a99238','uploads/afcbecce-2e8a-47d2-b71e-4ac6f2f86b9f.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-001','product-page','2025-09-01 08:47:14.781014'),
('IMG-c4b6a33c','uploads/doraemon.jpg','Alt-text',735,725,'[]','.jpg','subcategory','S-CHANNEL-001','CategorySubCategoryPage','2025-09-20 09:33:07.704413'),
('IMG-c5057079','uploads/6d96f256-e192-4a49-8355-343e8e496326.jpeg','',1000,1000,'[]','.jpeg','product','CA-PS-001','product-page','2025-09-02 07:54:11.372038'),
('IMG-c530670a','uploads/7b82fd35-4193-455c-937b-c1d38ae7bffa.webp','',1000,1000,'[]','.webp','product','TR-CC-001','product-page','2025-09-01 08:10:42.758245'),
('IMG-c595dd3e','uploads/d095495c-333d-4506-b3bc-4ee4b8a60b6f.jpeg','',1000,1000,'[]','.jpeg','product','PL-AP-001','product-page','2025-09-03 12:56:02.087857'),
('IMG-c5a566a2','uploads/036455b5-4b36-4b61-a50d-e1af27005dfc.jpeg','',1000,1000,'[]','.jpeg','product','CE-MC-001','product-page','2025-09-01 07:59:30.668842'),
('IMG-c5dc32c0','uploads/1c92a7cd-b6f9-4e7a-9a08-f4a40ac5650d.webp','',1000,1000,'[]','.webp','product','TR-CC-001','product-page','2025-09-01 08:10:42.747785'),
('IMG-c601ccc7','uploads/5a9a966e-f092-4f87-88e5-2647ee1d38b9.webp','',1000,1000,'[]','.webp','product','CE-TT-003','product-page','2025-09-01 09:41:51.585468'),
('IMG-c63feac7','uploads/c17f64db-1b9b-4b74-af75-384edfcecbc4.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.151734'),
('IMG-c79095ac','uploads/43c41b4b-93f4-4a54-9d15-59e7382f0d1a.jpeg','',1000,1000,'[]','.jpeg','product','CA-SB-001','product-page','2025-09-01 11:03:33.078679'),
('IMG-c7ebca1d','uploads/22e4164f-4577-476e-ae56-66e8ac5788ac.jpeg','',1000,1000,'[]','.jpeg','product','NO-AS-001','product-page','2025-09-01 12:17:14.133267'),
('IMG-c85a56ba','uploads/7fe76ca9-5949-4afd-a606-95a8e21ae7a8.webp','',1000,1000,'[]','.webp','product','GI-LP-001','product-page','2025-09-01 06:24:30.091263'),
('IMG-c91a529a','uploads/e131a581-4927-4447-b4e6-d398051dc090.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-001','product-page','2025-09-01 08:47:14.779009'),
('IMG-c91da05a','uploads/2317865b-98d9-41e9-9f10-c2dec24a830b.jpeg','',1000,1000,'[]','.jpeg','product','SP-WB-002','product-page','2025-09-01 11:15:09.141332'),
('IMG-c97a3e4c','uploads/e9524a8d-a289-442c-a1ff-f8cedc5478d7.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-001','product-page','2025-09-01 08:47:14.772858'),
('IMG-cb1b9e3e','uploads/Notebooks__Writing_Pads.png','Alt-text',2250,1500,'[]','.png','subcategory','O&S-NOTEBOOKS-001','CategorySubCategoryPage','2025-09-04 12:39:34.068552'),
('IMG-cb405a1c','uploads/a0f84fbb-25af-4492-b7fa-957440d2e496.jpeg','',1000,1000,'[]','.jpeg','product','UN-CH-001','product-page','2025-09-01 08:28:05.086859'),
('IMG-cbbfa155','uploads/ab5dafbe-7a45-4aee-9e6a-3f164e6a56c4.webp','',1000,1000,'[]','.webp','product','CE-CM-001','product-page','2025-09-01 09:32:14.767309'),
('IMG-cbcbb5b8','uploads/7251dd41-d73b-47bb-ad7a-f0d5067b05c5.jpeg','',1000,1000,'[]','.jpeg','product','SP-TT-001','product-page','2025-09-01 11:48:00.465171'),
('IMG-cd289b90','uploads/c23d2043-7575-48ef-a964-11fe7cbbfb2f.jpeg','',1000,1000,'[]','.jpeg','product','TR-PT-001','product-page','2025-09-01 07:54:24.525654'),
('IMG-cd3e933d','uploads/9213fa92-503d-4a0b-9df2-973bcc50e7f8.jpeg','',1000,1000,'[]','.jpeg','product','EX-WP-001','product-page','2025-09-01 12:28:37.697136'),
('IMG-cd9e1ee7','uploads/2119b87f-62e9-423c-b0fa-9ccf5ef5efbc.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.513685'),
('IMG-cda91a3d','uploads/Caps__Hats.png','Alt-text',2250,1500,'[]','.png','subcategory','CAA-CAPS-001','CategorySubCategoryPage','2025-09-09 10:19:59.810213'),
('IMG-cddb1a49','uploads/0c620b20-d0ef-408b-8b6e-585a467a8e86.jpeg','',1000,1000,'[]','.jpeg','product','CA-2T-001','product-page','2025-09-01 11:05:36.361310'),
('IMG-ce10a2d2','uploads/20434aa9-2437-4668-9086-cd61e2961dfe.jpeg','',1000,1000,'[]','.jpeg','product','NO-PD-001','product-page','2025-09-01 11:56:03.038624'),
('IMG-ce1c1ab0','uploads/c77dc7e7-1450-4f3e-a7e8-4fe1095afe29.jpeg','',260,260,'[]','.jpeg','product','EX-CC-001','product-page','2025-09-04 08:09:59.946495'),
('IMG-ce363763','uploads/eb7e7534-c943-4c2e-b83f-99183962cf3f.jpeg','',1000,1000,'[]','.jpeg','product','SP-SS-001','product-page','2025-09-01 11:06:03.151253'),
('IMG-ce43d0d6','uploads/a80a6b25-1248-4930-8c2a-54b144f70fd9.jpeg','',1000,1000,'[]','.jpeg','product','CO-BE-001','product-page','2025-09-01 06:38:34.682189'),
('IMG-ce5b425a','uploads/9ef94cf2-ba67-4a97-b17d-5b1446c923a2.jpeg','',1000,1000,'[]','.jpeg','product','CE-WS-001','product-page','2025-09-01 09:09:17.539169'),
('IMG-ce7655df','uploads/4586a732-138a-4001-9a8c-82d6430750b7.webp','',1000,1000,'[]','.webp','product','CE-CM-001','product-page','2025-09-01 09:32:14.771507'),
('IMG-cec0f6b8','uploads/503a8660-cf5c-43ed-954f-ac3dfa6b6d2c.jpeg','',1000,1000,'[]','.jpeg','product','CA-FC-001','product-page','2025-09-01 11:13:10.370963'),
('IMG-cfcd1cb5','uploads/daa5352a-1e6d-4819-9795-ee216cfe626b.jpeg','',1000,1000,'[]','.jpeg','product','EX-WP-001','product-page','2025-09-01 12:28:37.699028'),
('IMG-d153cd43','uploads/f7ac8630-fa00-4939-b645-871bd0fc5830.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-003','product-page','2025-09-01 10:09:15.171188'),
('IMG-d16033af','uploads/9d786fd0-80e6-43a0-b1c2-9ad8b69cc4b0.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-002','product-page','2025-09-01 09:19:55.170133'),
('IMG-d1a4ea45','uploads/8bc20f1f-b649-4d51-9e01-0c4438145ffc.jpeg','',1000,1000,'[]','.jpeg','product','EV-VN-001','product-page','2025-09-01 08:01:45.617389'),
('IMG-d209e3e8','uploads/31a0e98a-e6be-4078-92ef-4c4afce180a1.jpeg','',260,260,'[]','.jpeg','product','CO-CB-001','product-page','2025-09-04 08:30:04.885440'),
('IMG-d21e63ff','uploads/87144091-4a88-4fe8-86bd-163740eaccd9.jpeg','',1000,1000,'[]','.jpeg','product','BR-CR-001','product-page','2025-09-01 08:34:53.204739'),
('IMG-d32a9bb9','uploads/b03a5a68-5c01-4c59-b937-d496edcfc2c4.jpeg','',1000,1000,'[]','.jpeg','product','EC-BF-001','product-page','2025-09-04 07:10:08.136089'),
('IMG-d33ffa7b','uploads/89f01068-29c4-4738-90bc-9f3cbe719965.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-003','product-page','2025-09-01 07:52:59.450327'),
('IMG-d38427f4','uploads/bebaf1cb-04f8-4c98-9f62-be9fb36fb29b.jpeg','',1000,1000,'[]','.jpeg','product','EC-BF-001','product-page','2025-09-04 07:10:08.131175'),
('IMG-d39ace7e','uploads/b600a00f-e059-4759-a2ec-cd768e35f2f4.jpeg','',300,300,'[]','.jpeg','product','CA-PR-001','product-page','2025-09-01 11:36:48.047618'),
('IMG-d401cc24','uploads/Ceramic_Mug_GdMyxpc.png','Printing services in Dubai for mugs, bottles, and custom drinkware.',2250,1500,'[]','.png','category','D-1','CategorySubCategoryPage','2025-08-28 18:16:09.724088'),
('IMG-d432a836','uploads/31c6a4d5-19c1-4bde-bfb0-1b30bc005353.jpeg','',1000,1000,'[]','.jpeg','product','CA-MN-001','product-page','2025-09-01 11:20:26.658171'),
('IMG-d454c742','uploads/b3013854-6db9-4240-a6d1-1ff130335b91.jpeg','Ikrash ne kiya theek kiya???? featured image',1400,1400,'[\"blog\", \"featured\"]','.jpeg','blog','ikrashnekiyatheekk-ff2ae602e9','BlogManagementPage','2025-09-18 13:29:23.401020'),
('IMG-d4653943','uploads/26c71650-0ec5-494e-92a9-a91f251395e6.jpeg','',1000,1000,'[]','.jpeg','product','CE-PC-001','product-page','2025-09-01 09:24:05.822644'),
('IMG-d4937651','uploads/Power_Accessories.png','Alt-text',2250,1500,'[]','.png','subcategory','T-POWER-001','CategorySubCategoryPage','2025-09-04 08:44:04.760939'),
('IMG-d4a85de9','uploads/2eb22e8a-cf87-4e45-9f63-9c8376131770.jpeg','',1000,1000,'[]','.jpeg','product','SP-PB-001','product-page','2025-09-04 06:52:49.241557'),
('IMG-d55935d2','uploads/6972c495-90b0-4abc-a5d2-8942cf916e95.jpeg','',1000,1000,'[]','.jpeg','product','TR-DS-001','product-page','2025-09-03 13:08:57.656826'),
('IMG-d5ec4353','uploads/acadf6c7-cfde-4787-ad44-cbbb046e66e9.webp','',1000,1000,'[]','.webp','product','GI-LP-001','product-page','2025-09-01 06:24:30.102120'),
('IMG-d5fccc38','uploads/52149257-cab7-4289-a74f-cf26c1560410.jpeg','',260,260,'[]','.jpeg','product','EV-CR-002','product-page','2025-09-04 08:21:03.960319'),
('IMG-d64bff64','uploads/47aa2ddd-4e25-4108-acae-80ba4a258979.jpeg','',1000,1000,'[]','.jpeg','product','BA-MC-001','product-page','2025-09-01 06:22:17.262150'),
('IMG-d6d970c8','uploads/baad8877-43aa-4c01-8478-82d8fe0110ad.jpeg','',1000,1000,'[]','.jpeg','product','EV-CL-001','product-page','2025-09-01 10:10:07.075416'),
('IMG-d7144707','uploads/5e7d2e72-0f0a-436e-b702-f4cbb362449e.jpeg','',260,260,'[]','.jpeg','product','CO-SC-001','product-page','2025-09-04 08:26:58.038798'),
('IMG-d77536bf','uploads/a0002f9e-a18a-439f-b3d2-032adf5ca447.jpeg','',1000,1000,'[]','.jpeg','product','NO-SN-001','product-page','2025-09-01 12:10:13.234946'),
('IMG-d7881dff','uploads/cdb6acb6-9ba0-4498-8c0e-4c1f53d0746b.jpeg','',1000,1000,'[]','.jpeg','product','CA-2T-001','product-page','2025-09-01 11:05:36.365306'),
('IMG-d7c50560','uploads/77eb20c2-de02-401f-a122-a02fce09d4dd.jpeg','',1000,1000,'[]','.jpeg','product','PO-BB-001','product-page','2025-09-01 06:54:02.154975'),
('IMG-d800f7e3','uploads/3e2c5f31-b3cc-435d-bcdb-4b21d0db8cb2.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-001','product-page','2025-09-01 08:14:06.501931'),
('IMG-d861dac5','uploads/eb29f780-f654-47f3-9ed1-33ddc77cdd4e.jpeg','',1000,1000,'[]','.jpeg','product','EV-TW-001','product-page','2025-09-01 10:13:10.539073'),
('IMG-d97f352e','uploads/31d24274-7643-41f7-aad5-fc7c5e40b141.jpeg','',260,260,'[]','.jpeg','product','CO-DU-001','product-page','2025-09-04 08:28:56.002949'),
('IMG-d98123ca','uploads/f64cc02b-06d0-40a4-811a-87a3712e7a0a.jpeg','',1000,1000,'[]','.jpeg','product','TR-CW-001','product-page','2025-09-01 08:07:06.736883'),
('IMG-d9adb4c5','uploads/8a02893d-8f75-4c01-b15d-f90ca828e271.jpeg','',1000,1000,'[]','.jpeg','product','AC-WA-001','product-page','2025-09-01 08:23:31.508280'),
('IMG-d9c66a32','uploads/146277fc-5596-4b7c-b360-a882023e23f0.jpeg','',1000,1000,'[]','.jpeg','product','AC-CC-001','product-page','2025-09-01 08:08:19.099916'),
('IMG-d9dfcc10','uploads/b2a9de08-95f7-4f32-8c04-428b4619220b.jpeg','',1000,1000,'[]','.jpeg','product','PL-AP-001','product-page','2025-09-03 12:56:02.090045'),
('IMG-dabc4cb8','uploads/479d4aa6-ef87-441d-b988-562c0dcdf1a9.jpeg','',600,600,'[]','.jpeg','product','EV-CE-001','product-page','2025-09-04 08:16:40.240409'),
('IMG-db1ad6ec','uploads/4805de04-01ea-4330-8f20-cc7f0160921b.jpeg','',260,260,'[]','.jpeg','product','EX-CB-001','product-page','2025-09-04 08:07:29.836344'),
('IMG-db937163','uploads/f4811bd2-f94b-4e73-8548-258c1de22e74.jpeg','',260,260,'[]','.jpeg','product','CA-CO-001','product-page','2025-09-04 08:13:38.315549'),
('IMG-dbd55727','uploads/7b23b6e6-43e5-4999-bfd6-ae28aa49ab8d.webp','',1000,1000,'[]','.webp','product','EV-SC-001','product-page','2025-09-01 06:32:55.776704'),
('IMG-dcc3ff2c','uploads/0e45975b-8aeb-4398-810a-869cd544ac22.jpeg','',1000,1000,'[]','.jpeg','product','BA-BA-001','product-page','2025-09-01 06:14:41.110041'),
('IMG-dd50389b','uploads/1bab52f0-f9bf-4806-ac15-ae114d4d3006.jpeg','',1000,1000,'[]','.jpeg','product','DE-SF-001','product-page','2025-09-01 10:26:26.205142'),
('IMG-dd74cb3e','uploads/4aa77261-4397-4094-bad2-e4d3d314bc67.jpeg','',1000,1000,'[]','.jpeg','product','PR-CH-001','product-page','2025-09-01 12:14:53.450322'),
('IMG-de2de8b5','uploads/Ceramic_Mug_dzUp6lA.png','Alt-text',2250,1500,'[]','.png','subcategory','D-CERAMIC-002','CategorySubCategoryPage','2025-09-04 11:38:33.938248'),
('IMG-deec7112','uploads/7b6f6b56-3692-4063-9faf-2a2091093793.jpeg','',1000,1000,'[]','.jpeg','product','CA-AN-001','product-page','2025-09-01 11:26:58.738653'),
('IMG-df357fa5','uploads/9bd0d212-d7b0-4415-93fd-78b2eb19c258.jpeg','',1000,1000,'[]','.jpeg','product','WO-BW-001','product-page','2025-09-01 06:22:19.844499'),
('IMG-dfa5fc8e','uploads/8f90aaa3-134c-4b3d-b779-782dbb0488d3.jpeg','',1000,1000,'[]','.jpeg','product','EX-PL-001','product-page','2025-09-04 07:39:52.249843'),
('IMG-e16a985a','uploads/46bd0a7d-2479-45a2-80db-98e84a973a45.jpeg','Carousel Image',2000,2000,'[\"carousel\"]','.jpeg','FirstCarousel','1','first-carousel','2025-09-18 16:44:47.518606'),
('IMG-e1931548','uploads/8e5164ab-7b4f-46d6-8686-381143c36177.jpeg','',1000,1000,'[]','.jpeg','product','WO-BW-001','product-page','2025-09-01 06:22:19.847059'),
('IMG-e1f75197','uploads/a55743b2-859f-4c6b-870c-7a42bb44b9cb.jpeg','',1000,1000,'[]','.jpeg','product','TR-DS-001','product-page','2025-09-03 13:08:57.660732'),
('IMG-e21bdb4b','uploads/Bamboo_Pen.png','Alt-text',2250,1500,'[]','.png','subcategory','WI-WOODEN-001','CategorySubCategoryPage','2025-09-09 10:23:55.947831'),
('IMG-e27d60be','uploads/b0aac217-b1bc-4836-83d1-424bd7b401f6.jpeg','',1000,1000,'[]','.jpeg','product','WO-EC-001','product-page','2025-09-01 06:29:30.124855'),
('IMG-e29544b2','uploads/b319c11e-937f-4bf5-a988-df83e16d95d3.jpeg','',1000,1000,'[]','.jpeg','product','CA-PS-001','product-page','2025-09-02 07:54:11.383691'),
('IMG-e398a0e3','uploads/81ec0df7-e5d2-4697-baf1-7d766d4384c1.jpeg','',260,260,'[]','.jpeg','product','CO-CB-001','product-page','2025-09-04 08:30:04.879515'),
('IMG-e41277bf','uploads/90b186e5-c158-4bc2-85ce-b448457d15fe.jpeg','',1000,1000,'[]','.jpeg','product','SP-PB-001','product-page','2025-09-04 06:52:49.248754'),
('IMG-e45abb16','uploads/d4aba709-189c-4c98-b51a-e956334a0659.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-001','product-page','2025-09-01 07:19:05.022515'),
('IMG-e502e048','uploads/d466ca7e-abdc-4131-b999-02210dcb0054.jpeg','',886,886,'[]','.jpeg','product','FL-ST-001','product-page','2025-09-11 06:21:40.735246'),
('IMG-e52fbc38','uploads/b1b95503-3a14-4668-a295-f2c964045949.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-002','product-page','2025-09-01 07:31:27.152417'),
('IMG-e5970917','uploads/170842a9-5fe6-4615-965c-4c7504f85ff8.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-002','product-page','2025-09-01 09:19:55.175691'),
('IMG-e59c27db','uploads/f01704b9-cf0e-4fa0-8c23-954419d77072.jpeg','',850,850,'[]','.jpeg','product','FL-HT-001','product-page','2025-09-11 06:11:57.660781'),
('IMG-e5b5fe4e','uploads/a36f574a-59d6-423a-8c60-e4a74e79dcb3.jpeg','',1000,1000,'[]','.jpeg','product','UN-CH-001','product-page','2025-09-01 08:28:05.084832'),
('IMG-e5ea3a7e','uploads/750c3e37-0999-4ead-9778-3f89868b1d87.jpeg','',1000,1000,'[]','.jpeg','product','TA-EF-001','product-page','2025-09-02 08:05:42.231957'),
('IMG-e5f768e6','uploads/47c193ce-61ae-4359-841b-5dc7cb155469.jpeg','',1000,1000,'[]','.jpeg','product','SP-TB-001','product-page','2025-09-01 10:38:01.215912'),
('IMG-e6356e5d','uploads/14f73bcc-029a-47e9-8e10-ebd265b6395f.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','TR-DW-002','product-page','2025-09-01 12:03:05.323888'),
('IMG-e704e69d','uploads/Event_Essentials.png','Alt-text',2250,1500,'[]','.png','subcategory','EG&S-EVENT-001','CategorySubCategoryPage','2025-09-09 13:33:58.154266'),
('IMG-e7296d10','uploads/e64f4ca8-f16d-447b-90dc-021220a4f4d0.jpeg','',1000,1000,'[]','.jpeg','product','NO-BA-001','product-page','2025-09-01 11:49:22.080782'),
('IMG-e783811f','uploads/570d9a1b-c667-4f9d-be23-c8b44c2939c1.jpeg','',1000,1000,'[]','.jpeg','product','WO-EC-001','product-page','2025-09-01 06:29:30.122817'),
('IMG-e8798d0c','uploads/2abb7256-c368-4984-9b08-76de1e758e47.jpeg','',300,300,'[]','.jpeg','product','CA-PR-001','product-page','2025-09-01 11:36:48.049855'),
('IMG-e9013275','uploads/7f3ea56e-ec32-4528-8bb6-0526c5685110.jpeg','',738,738,'[]','.jpeg','product','FL-PF-001','product-page','2025-09-11 06:17:21.249753'),
('IMG-e91d5a1b','uploads/cb39c606-96fb-4760-873f-9205c706533c.jpeg','',1000,1000,'[]','.jpeg','product','BR-CA-001','product-page','2025-09-01 08:38:07.656376'),
('IMG-e95fab36','uploads/f2577291-ac94-47f6-b5c2-6a88d4a7c58e.jpeg','',1169,1169,'[]','.jpeg','product','FL-CF-002','product-page','2025-09-11 06:10:06.900277'),
('IMG-e972c837','uploads/19003915-bd4a-40c2-828e-10903891b587.jpeg','',1000,1000,'[]','.jpeg','product','WO-BW-001','product-page','2025-09-01 06:22:19.841879'),
('IMG-e99efd16','uploads/2c930242-686d-44ae-961d-0ba99b0aab43.jpeg','',1000,1000,'[]','.jpeg','product','CE-BS-001','product-page','2025-09-01 08:18:56.301976'),
('IMG-ea14febd','uploads/864eb7b0-5039-4ce5-b16c-c3e9d0027834.jpeg','',1000,1000,'[]','.jpeg','product','EV-RJ-001','product-page','2025-09-01 07:04:51.892287'),
('IMG-ea1e1ec0','uploads/9082d418-8b84-4815-91f7-c280dd4ecaf0.jpeg','',1000,1000,'[]','.jpeg','product','TR-TT-001','product-page','2025-09-01 12:10:47.299334'),
('IMG-ea73bfd9','uploads/54488591-cce6-4456-88a1-b9b7e05e6965.jpeg','',1000,1000,'[]','.jpeg','product','AC-CC-001','product-page','2025-09-01 08:08:19.101928'),
('IMG-eb823f14','uploads/46a8a834-71e4-4ea5-baf5-95ebab7f67a9.jpeg','',1000,1000,'[]','.jpeg','product','CA-FC-001','product-page','2025-09-01 11:13:10.366845'),
('IMG-ebab6fc4','uploads/84b2f100-81e8-419b-b245-dd584b9c44b3.png','Carousel Image',2250,1500,'[\"carousel\"]','.png','SecondCarousel','1','second-carousel','2025-08-29 05:45:51.067147'),
('IMG-ebd32a9f','uploads/82fadba9-71d2-4012-bb32-76f1e3e24edd.jpeg','',1000,1000,'[]','.jpeg','product','CA-FW-001','product-page','2025-09-01 11:08:15.417476'),
('IMG-ebffc30c','uploads/ca3b840f-43af-4faf-a2ea-c95466e168c0.jpeg','',1000,1000,'[]','.jpeg','product','CO-CL-001','product-page','2025-09-01 06:44:22.473800'),
('IMG-ec10886f','uploads/1285de77-6509-4b5e-bccd-6f85ab9b026b.jpeg','',1000,1000,'[]','.jpeg','product','AC-CP-001','product-page','2025-09-01 08:21:39.597086'),
('IMG-ec1f279f','uploads/e4e43fd0-2737-41fd-b015-993e3419a7e6.jpeg','',260,260,'[]','.jpeg','product','CO-CB-001','product-page','2025-09-04 08:30:04.881285'),
('IMG-ed26f117','uploads/5191a020-9b98-4872-8f89-14ac92d5ee77.jpeg','',1000,1000,'[]','.jpeg','product','CE-LM-001','product-page','2025-09-01 10:13:38.517909'),
('IMG-ed4badac','uploads/4a85d9f7-f2a7-4267-bd78-c872e51ffe8b.jpeg','',1000,1000,'[]','.jpeg','product','DE-SF-001','product-page','2025-09-01 10:26:26.199554'),
('IMG-edf2c28c','uploads/9b173339-261f-4687-aec8-178a94bd04bb.jpeg','',1000,1000,'[]','.jpeg','product','NO-AS-001','product-page','2025-09-01 12:17:14.138266'),
('IMG-ef5cb0de','uploads/6f923bf9-04e9-40f5-9020-7a5093f5e70e.jpeg','',1000,1000,'[]','.jpeg','product','EV-RJ-001','product-page','2025-09-01 07:04:51.894515'),
('IMG-ef829147','uploads/e24df5ed-5f2e-4283-80aa-096562418444.jpeg','',1000,1000,'[]','.jpeg','product','CE-WS-002','product-page','2025-09-01 10:20:26.371665'),
('IMG-ef9cfa50','uploads/Calendars__Miscellaneous_Items.png','Alt-text',2250,1500,'[]','.png','subcategory','O&S-CALENDARS-001','CategorySubCategoryPage','2025-09-04 14:19:46.776397'),
('IMG-efe4de17','uploads/5ee28e70-8acc-425f-b7b3-1c229b6eb284.jpeg','',1000,1000,'[]','.jpeg','product','BA-BA-001','product-page','2025-09-01 06:14:41.112112'),
('IMG-f070b115','uploads/Branded_Giveaway_Items.png','Alt-text',2250,1500,'[]','.png','subcategory','EG&S-BRANDED-001','CategorySubCategoryPage','2025-09-09 14:13:17.248642'),
('IMG-f0796806','uploads/0c33e7a0-d33b-47fd-b85f-6b783874f23c.jpeg','',260,260,'[]','.jpeg','product','CO-EF-001','product-page','2025-09-04 08:23:28.451312'),
('IMG-f08eabd7','uploads/178c7587-d3e0-4519-a5b4-4ab16968338a.jpeg','',260,181,'[]','.jpeg','product','PR-CC-002','product-page','2025-09-04 07:54:34.987418'),
('IMG-f0a16988','uploads/95b77b24-d47a-41b4-8e9d-5cb1a50ee23b.jpeg','',1000,1000,'[]','.jpeg','product','EV-RJ-001','product-page','2025-09-01 07:04:51.896552'),
('IMG-f0c0b43f','uploads/5018cc0e-05e2-4ce6-9578-fe777f9791b7.jpeg','',886,886,'[]','.jpeg','product','FL-TS-001','product-page','2025-09-11 06:37:42.495993'),
('IMG-f1221aed','uploads/41a6d57d-4138-49b6-a249-93bd3404a0ad.jpeg','',1000,1000,'[]','.jpeg','product','TR-DW-001','product-page','2025-09-01 11:55:58.680799'),
('IMG-f1ad9fbf','uploads/e1423dd0-afc4-4172-a307-a20495657fa1.jpeg','',260,260,'[]','.jpeg','product','CO-CB-001','product-page','2025-09-04 08:30:04.887711'),
('IMG-f30263bf','uploads/46f894fb-5d23-49a9-8afd-dc410eefa00f.jpeg','',1000,1000,'[]','.jpeg','product','CA-SB-001','product-page','2025-09-01 11:03:33.080639'),
('IMG-f34b6617','uploads/Coaster_Set_sRaMsD0.png','Alt-text',2250,1500,'[]','.png','subcategory','D-TABLE-001','CategorySubCategoryPage','2025-09-09 11:27:40.720557'),
('IMG-f34d7616','uploads/fd3352fc-04be-4b24-b330-b789d6f7d8b1.webp','',1000,1000,'[]','.webp','product','CE-CC-001','product-page','2025-09-01 08:55:48.161423'),
('IMG-f355d515','uploads/270f5328-53b2-4a6f-8ba7-e8cdd2e6a60a.jpeg','',640,640,'[]','.jpeg','product','BA-EC-001','product-page','2025-09-01 06:24:50.910970'),
('IMG-f3fe1f83','uploads/a04d794c-f180-4c83-a551-438d7e480a9f.jpeg','',1000,1000,'[]','.jpeg','product','TR-DW-001','product-page','2025-09-01 11:55:58.686414'),
('IMG-f522ab8d','uploads/de767903-c0d9-4b5c-857f-d1cc3143b31a.jpeg','',260,172,'[]','.jpeg','product','CO-CB-001','product-page','2025-09-04 08:30:04.883164'),
('IMG-f5670c89','uploads/0f155025-0318-4fed-b6b9-532f487a91cc.jpeg','',1000,1000,'[]','.jpeg','product','PO-HC-001','product-page','2025-09-01 06:52:00.855249'),
('IMG-f5cf819c','uploads/b85f6f8c-924b-4f9c-bafd-39c23a202ff7.jpeg','',1000,1000,'[]','.jpeg','product','CE-TT-002','product-page','2025-09-01 09:19:55.179510'),
('IMG-f5e1bef9','uploads/1ef150b9-4105-4294-a2e4-c964b47ec26b.jpeg','',260,260,'[]','.jpeg','product','CO-SC-001','product-page','2025-09-04 08:26:58.040760'),
('IMG-f619dc9c','uploads/dba27f7c-102e-475f-bc9f-dc9b4ea952e0.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-003','product-page','2025-09-01 07:52:59.448116'),
('IMG-f61d3086','uploads/28aebe81-ede3-4251-93bb-aa3606dfffc6.jpeg','',1000,1000,'[]','.jpeg','product','CE-PM-001','product-page','2025-09-01 08:34:20.728158'),
('IMG-f6cf4e7b','uploads/c00f8e70-3a1e-42db-8050-06a0f734f67a.jpeg','',1000,1000,'\"\"','.jpeg','product','PR-CC-001','product-page','2025-09-04 07:52:14.609041'),
('IMG-f6ef068e','uploads/b0e02cfc-e000-42f1-864a-dd11c70fda27.jpeg','',1280,1280,'[]','.jpeg','product','FL-VS-001','product-page','2025-09-11 06:26:33.957828'),
('IMG-f77966a0','uploads/938dae50-4443-45c3-aec6-5b08b6d972cc.jpeg','',1000,1000,'[]','.jpeg','product','CE-BS-001','product-page','2025-09-01 08:18:56.295589'),
('IMG-f7896a7b','uploads/a4b7e02e-056b-435d-b623-aa55a31592ff.jpeg','',1000,1000,'[]','.jpeg','product','NO-SN-001','product-page','2025-09-01 12:10:13.233054'),
('IMG-f79ab9c9','uploads/99ec9c27-4304-4ef6-90c5-e0ff8363770e.webp','',1000,1000,'[]','.webp','product','BR-PE-001','product-page','2025-09-01 08:29:05.905383'),
('IMG-f802f2fc','uploads/272c9f83-fda0-4552-8776-b147ea17f830.jpeg','',1000,1000,'[]','.jpeg','product','BR-CM-001','product-page','2025-09-01 08:20:03.130125'),
('IMG-f844ef78','uploads/5e33c1fe-626e-4d71-a37f-6b420cfc8018.jpeg','',1000,1000,'[]','.jpeg','product','CO-CL-001','product-page','2025-09-01 06:44:22.475516'),
('IMG-f86c11e7','uploads/e7e1d097-0bd4-4f8e-a19a-684b96a4ea2a.jpeg','',1000,1000,'[]','.jpeg','product','EV-CL-001','product-page','2025-09-01 10:10:07.077768'),
('IMG-f930ea4a','uploads/ec9884bb-4f27-4750-9877-82de9eb00254.jpeg','',1000,1000,'[]','.jpeg','product','NO-BA-001','product-page','2025-09-01 11:49:22.082513'),
('IMG-f984f02b','uploads/c9398a97-af3a-4402-8e68-a0f7bc7af9b4.webp','',1000,1000,'[]','.webp','product','TR-LT-001','product-page','2025-09-01 12:06:27.318935'),
('IMG-f9952801','uploads/2a3424c1-8c02-4ce9-b50c-0aadd89e2759.jpeg','',1000,1000,'[]','.jpeg','product','NO-CB-001','product-page','2025-09-01 11:45:09.069261'),
('IMG-f9f07b76','uploads/f67f0ca0-b2fe-41df-8f0c-85089cbf420f.jpeg','',1000,1000,'[]','.jpeg','product','TA-EF-001','product-page','2025-09-02 08:05:42.233893'),
('IMG-f9f9c44e','uploads/ac196e8d-59aa-4775-bec5-208151224e19.jpeg','',1000,1000,'[]','.jpeg','product','EV-DP-001','product-page','2025-09-01 10:11:31.290084'),
('IMG-fa24368d','uploads/7e15bf18-39f9-471f-b9c2-461f79ee5953.webp','',686,534,'[]','.webp','product','BA-FB-001','product-page','2025-09-11 07:23:36.147407'),
('IMG-faa59694','uploads/854f2d49-3376-4bec-9ff1-38cb0d45c70d.jpeg','',1000,1000,'[]','.jpeg','product','AC-CP-001','product-page','2025-09-01 08:21:39.593057'),
('IMG-fab760e2','uploads/b6393ee6-2e6f-40c7-8f3a-01813e42f039.webp','',900,700,'[]','.webp','product','BA-FB-002','product-page','2025-09-11 07:34:28.074788'),
('IMG-fb065cbe','uploads/980dee60-c37a-415f-b1f1-831836827d41.jpeg','',1000,1000,'[]','.jpeg','product','CE-PM-001','product-page','2025-09-01 08:34:20.724021'),
('IMG-fb22c7e3','uploads/71c7ed41-3ff0-4d06-8f06-277a9e87d36e.webp','',1000,1000,'[]','.webp','product','BR-PE-001','product-page','2025-09-01 08:29:05.903070'),
('IMG-fb357ec6','uploads/cb5f0a26-6aa4-4726-aa12-59470d2a06a0.jpeg','',1000,1000,'[]','.jpeg','product','PR-CW-001','product-page','2025-09-01 12:13:47.815940'),
('IMG-fb6380af','uploads/1f73109f-889f-4cd2-8d06-6bb6993aee5d.jpeg','Alt-text',1000,1000,'[]','.jpeg','product','TR-DW-002','product-page','2025-09-01 12:03:05.320059'),
('IMG-fbbfae6d','uploads/803e91fa-b198-45e0-b996-d954b7c4e898.jpeg','',1000,1000,'[]','.jpeg','product','EC-EF-001','product-page','2025-09-04 07:01:28.066344'),
('IMG-fc597b89','uploads/c2f761e3-1805-466d-af62-42d0546411c4.jpeg','',1000,1000,'[]','.jpeg','product','CE-WS-002','product-page','2025-09-01 10:20:26.373544'),
('IMG-fc7d4da0','uploads/5ba2ab53-d5f8-4252-9e4c-e7f27d081553.jpeg','',1000,1000,'[]','.jpeg','product','CE-WC-003','product-page','2025-09-01 10:09:15.174779'),
('IMG-fcc5b88e','uploads/Brochures__Booklets.png','Alt-text',2250,1500,'[]','.png','subcategory','P&MM-PROMOTIONAL-001','CategorySubCategoryPage','2025-09-03 15:27:53.276481'),
('IMG-fcd19ce1','uploads/f8782013-6f9e-4088-b985-05d3f4eb87fb.jpeg','',1000,1000,'[]','.jpeg','product','EV-CJ-001','product-page','2025-09-01 07:19:05.020522'),
('IMG-fcd78f5d','uploads/0f6fa386-7c1a-48b5-8c33-17a9b3f14d64.jpeg','',1000,1000,'[]','.jpeg','product','TR-PT-001','product-page','2025-09-01 07:54:24.533886'),
('IMG-fd195f64','uploads/ef40e3c3-56fc-4129-8150-a180f0cc1f53.jpeg','',1000,1000,'[]','.jpeg','product','CO-CL-001','product-page','2025-09-01 06:44:22.471983'),
('IMG-fd407b3d','uploads/f0c7524c-33db-4a9c-a8f4-bcffc6f052b4.webp','Hero Desktop Image',4320,1200,'[\"hero\", \"desktop\"]','.webp','HeroBanner','HERO-3ca56c57','hero-banner','2025-08-28 18:05:36.402120'),
('IMG-fd561462','uploads/72c78d77-0b6c-4fcf-95f4-3ecd3a919d84.webp','',1000,1000,'[]','.webp','product','CO-CC-001','product-page','2025-09-01 06:50:01.393477'),
('IMG-fd5ac9a8','uploads/81a04588-de5b-45a6-a612-21cdd336c482.jpeg','',1000,1000,'[]','.jpeg','product','PL-AP-001','product-page','2025-09-03 12:56:02.085863'),
('IMG-fe4cbbc1','uploads/0827d8cc-01fd-44b2-ac66-50f2bed1db6a.jpeg','',1000,1000,'[]','.jpeg','product','CA-FC-001','product-page','2025-09-01 11:13:10.364719'),
('IMG-ffb0688b','uploads/2369ec8f-e5ca-4387-8ffa-20c661d0d770.jpeg','',1000,1000,'[]','.jpeg','product','CO-WU-001','product-page','2025-09-04 07:54:01.441492');
/*!40000 ALTER TABLE `admin_backend_final_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_notification`
--

DROP TABLE IF EXISTS `admin_backend_final_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_notification` (
  `notification_id` varchar(100) NOT NULL,
  `type` varchar(100) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` longtext NOT NULL,
  `recipient_id` varchar(100) NOT NULL,
  `recipient_type` varchar(10) NOT NULL,
  `source_table` varchar(100) NOT NULL,
  `source_id` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`notification_id`),
  KEY `admin_backend_final_notification_type_ed21c7bb` (`type`),
  KEY `admin_backend_final_notification_recipient_id_97e96bf8` (`recipient_id`),
  KEY `admin_backend_final_notification_recipient_type_62986ae1` (`recipient_type`),
  KEY `admin_backend_final_notification_status_d4b0b7fe` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_notification`
--

LOCK TABLES `admin_backend_final_notification` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_notification` DISABLE KEYS */;
INSERT INTO `admin_backend_final_notification` VALUES
('013b5d8a-e496-4e1f-b880-dcd83c2f04ab','admin_model_change','Admin Change Detected','Product \'Custom Ceramic Mug with Lid & Cork Base 385ml | Coffee Cup & Tea Mug Dubai\' was deleted.','superadmin','admin','Product','TR-CC-001','read','2025-09-01 07:02:38.882380'),
('019df423-eac7-47f4-8890-f79ff85b19f4','admin_model_change','Admin Change Detected','Admin \'admin\' was deleted.','superadmin','admin','Admin','1','read','2025-08-29 06:55:22.784254'),
('0208f607-5d8d-4590-b9e2-24a834c406ca','admin_model_change','Admin Change Detected','Product \'Rustic Jute Carry Bag\' was created.','superadmin','admin','Product','EV-RJ-001','read','2025-09-01 06:59:40.560490'),
('02187586-9210-405f-a026-3e9903ace898','admin_model_change','Admin Change Detected','Product \'Custom Printed Corporate T-Shirts Dubai & UAE\' was created.','superadmin','admin','Product','T-CP-001','read','2025-09-01 08:16:56.005440'),
('021f36fb-21a2-442e-bdf2-8b7ca314322a','admin_model_change','Admin Change Detected','Product \'Custom Corporate USB Memory Sticks\' was created.','superadmin','admin','Product','CO-CC-001','read','2025-09-01 06:50:01.372514'),
('0262bec8-4b24-4057-b449-b8710d7d0b93','admin_model_change','Admin Change Detected','Product \'Promotional Mugs with Logo | Custom Branded Coffee & Tea Mugs Dubai\' was created.','superadmin','admin','Product','CE-PM-001','read','2025-09-01 08:34:20.713999'),
('026bfc4d-89ef-4d2c-974c-fffae1a48b9b','admin_model_change','Admin Change Detected','Blog \'Ikrash ne kiya theek kiya????\' was saved as draft.','superadmin','admin','Blog','ikrashnekiyatheekk-ff2ae602e9','read','2025-09-17 19:04:31.754331'),
('038ebcdc-4f59-4d14-8bae-8c32fdb88243','admin_model_change','Admin Change Detected','Product \'Curve Edge Mugs | Custom Ceramic Coffee & Tea Mug Dubai\' was created.','superadmin','admin','Product','CE-CE-001','read','2025-09-01 08:22:50.533547'),
('0397a9c8-7fc3-4d6b-bcf6-5a8b312ff0c5','admin_model_change','Admin Change Detected','Product \'Logo Branded Ceramic Coffee Mug\' was deleted.','superadmin','admin','Product','TR-LBCCM-001','read','2025-09-01 06:10:02.118729'),
('041d02f1-0047-41a2-a27c-13113da9aebd','admin_model_change','Admin Change Detected','Product \'Personalized Cotton Aprons with Embroidery\' was created.','superadmin','admin','Product','UN-PC-001','read','2025-09-01 08:04:24.993667'),
('046bca78-9c83-45d7-b889-637420e971a4','admin_model_change','Admin Change Detected','Product \'Custom Printed Jute Conference Bag\' was created.','superadmin','admin','Product','EV-CPJCB-001','read','2025-08-29 10:21:17.640710'),
('048089a9-d056-4077-bc8e-cefb153b5462','admin_model_change','Admin Change Detected','Subcategory \'Premium & Corporate Gifts\' was created.','superadmin','admin','SubCategory','EG&S-PREMIUM-001','read','2025-08-29 07:22:39.962599'),
('04b25396-a759-457c-81b4-6c92224b29af','admin_model_change','Admin Change Detected','Product \'Custom Printed Jute Conference Bag\' was deleted.','superadmin','admin','Product','EV-CPJCB-001','read','2025-09-01 06:10:01.950128'),
('05108d18-a174-489f-bcf1-7d4a625c528e','admin_model_change','Admin Change Detected','Product \'Custom Printed Children’s Apparel Dubai & UAE\' was created.','superadmin','admin','Product','T-CP-002','read','2025-09-04 08:01:39.527603'),
('068b5c1f-e3ae-479f-a738-f484d38f1a9e','admin_model_change','Admin Change Detected','Product \'Vertical Non-Woven Bags Printing in Dubai  Custom Reusable Tote Bags & Branded Eco Bags UAE\' was created.','superadmin','admin','Product','EV-VN-001','read','2025-09-01 08:01:45.607240'),
('069b6217-583a-4adf-a353-a7cf2be9d175','admin_model_change','Admin Change Detected','Admin \'admin\' was created.','superadmin','admin','Admin','AAIN-SU-001','read','2025-09-01 11:41:19.255893'),
('084908b5-13e1-48e2-9d92-0450ed6897da','admin_model_change','Admin Change Detected','Subcategory \'Signage\' was updated.','superadmin','admin','SubCategory','EG&S-SIGNAGE-001','read','2025-09-10 05:55:46.080992'),
('08c9bc57-e347-49e8-84a6-d3d288c109a4','admin_model_change','Admin Change Detected','Product \'Custom NFC & Premium Business Card Printing Dubai & UAE\' was created.','superadmin','admin','Product','BU-CN-001','read','2025-09-01 12:03:11.991137'),
('0982932d-0cd8-453f-973a-f8b7bce86459','admin_model_change','Admin Change Detected','Product \'Custom Universal Charging Cables Corporate Gifts Dubai & UAE\' was created.','superadmin','admin','Product','CO-CU-001','read','2025-09-04 08:31:25.920327'),
('0a30707b-3e6d-4e04-a6c1-e5420e36079c','admin_model_change','Admin Change Detected','Product \'Bi-Fold Umbrella in White Color with Velcro Closure and Pouch\' was created.','superadmin','admin','Product','DE-BF-001','read','2025-09-01 10:22:47.018107'),
('0a5c1c4d-ca1c-4f5b-9e92-df198f3ce56b','admin_model_change','Admin Change Detected','Product \'Sustainable Seed Paper Calendar with Wooden Easel\' was created.','superadmin','admin','Product','CA-SS-002','read','2025-08-30 06:34:07.501282'),
('0a99d9ec-2993-44f1-b9b5-6c943e1c4255','admin_model_change','Admin Change Detected','Subcategory \'Computer & Office Gadgets\' was created.','superadmin','admin','SubCategory','T-COMPUTER-001','read','2025-08-29 06:29:23.422407'),
('0ae10cb0-30c7-40ae-b607-d019c25bb168','admin_model_change','Admin Change Detected','New order \'OAS-MA-001\' was placed.','superadmin','admin','Orders','OAS-MA-001','read','2025-09-10 08:19:51.856897'),
('0b2e0a3f-9111-4e14-8b35-d14adfdd8f6f','admin_model_change','Admin Change Detected','New order \'OCH-CH-001\' was placed.','superadmin','admin','Orders','OCH-CH-001','read','2025-09-11 12:22:29.350430'),
('0c0858e7-9f13-4ea2-a6b3-58a7ad246c13','admin_model_change','Admin Change Detected','Product \'Detox Infuser Bottle with Flip Lid\' was created.','superadmin','admin','Product','EC-DIBWFL-001','read','2025-08-29 11:12:13.316081'),
('0c454ded-1deb-4d43-acfd-692f766f4af6','admin_model_change','Admin Change Detected','Product \'Slim Custom USB Flash Drives for Corporate Gifts Dubai & UAE\' was created.','superadmin','admin','Product','CO-SC-001','read','2025-09-04 08:26:58.017994'),
('0cb13158-be7d-4081-b4e0-b7897b473e9d','admin_model_change','Admin Change Detected','Order \'OAK-IT-001\' status changed to \'processing\'.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 16:16:19.424822'),
('0d803172-7602-4ef0-b3c3-8152f4549e1a','admin_model_change','Admin Change Detected','Product \'ikresh\' was deleted.','superadmin','admin','Product','IK-I-001','read','2025-08-29 08:50:34.661211'),
('0efffc7a-b9ba-4431-8fc4-15feca1343a4','admin_model_change','Admin Change Detected','Product \'Custom Printed Hi-Vis Safety Vest – Yellow\' was deleted.','superadmin','admin','Product','UN-CPHVSVY-001','read','2025-09-01 06:10:01.939671'),
('0f3008dd-8ca5-4d2a-b039-99b94d58d761','admin_model_change','Admin Change Detected','Product \'Promotional Cork Mouse Pad with Storage Slots\' was created.','superadmin','admin','Product','CA-PC-001','read','2025-08-30 06:37:15.677688'),
('0f5f04e0-66c2-4d79-80e0-d180f9bce6de','admin_model_change','Admin Change Detected','Admin \'admin\' was deleted.','superadmin','admin','Admin','AAIN-SU-001','read','2025-08-29 06:41:04.593964'),
('104d6b71-bb57-40e0-8d93-b0622148df2d','admin_model_change','Admin Change Detected','Product \'Luxury Business Gift Set with Logo Printing\' was deleted.','superadmin','admin','Product','PR-LB-001','read','2025-08-30 07:25:04.529286'),
('11364852-3af4-4ae0-ad3e-4f8ad96e01df','admin_model_change','Admin Change Detected','Subcategory \'Office Stationery\' was created.','superadmin','admin','SubCategory','P&MM-OFFICE-001','read','2025-08-29 07:09:54.408650'),
('1224a88d-fe2c-43ff-9c44-8aca7dee26cc','admin_model_change','Admin Change Detected','Product \'Business Anti-Theft Backpack with USB Charger\' was updated.','superadmin','admin','Product','BA-BA-001','read','2025-09-04 12:07:59.605694'),
('122c30bb-2710-46ef-b5ce-33fad2ccb705','admin_model_change','Admin Change Detected','Subcategory \'Display\' was updated.','superadmin','admin','SubCategory','BD&F-DISPLAY-001','read','2025-09-10 16:21:31.086331'),
('12c92dc6-9b00-4688-961e-05899f5b2f3f','admin_model_change','Admin Change Detected','Subcategory \'Branded Giveaway Items\' was created.','superadmin','admin','SubCategory','EG&S-BRANDED-001','read','2025-08-29 07:21:08.518232'),
('135c394a-cbf4-4b92-b990-6a4cce11a6a5','admin_model_change','Admin Change Detected','Product \'Promotional Polyester Umbrella with Logo Print\' was created.','superadmin','admin','Product','DE-PP-001','read','2025-08-30 05:30:24.116568'),
('14554d73-4263-4fa1-88ba-614427716396','admin_model_change','Admin Change Detected','Product \'UAE Flag Celebration Stole with Arabic Calligraphy\' was created.','superadmin','admin','Product','AC-UFCSWAC-001','read','2025-08-29 10:35:54.652893'),
('1496a0a3-89d6-4a93-982c-4851e4af526a','admin_model_change','Admin Change Detected','Category \'Events & Giveaway Items\' was updated.','superadmin','admin','Category','EG&S-1','read','2025-09-03 06:00:51.142819'),
('14fbe990-b4b2-4fb4-bfe8-d74c3275d14a','admin_model_change','Admin Change Detected','Product \'Spiral Notebook with Sticky Note and Pen\' was deleted.','superadmin','admin','Product','NO-SNWSNAP-001','read','2025-09-01 06:10:02.315927'),
('16054ab8-f18a-4e23-b5ca-f530d6d22fcc','admin_model_change','Admin Change Detected','Product \'Promotional Fabric Strap Keyring with Metal Plate\' was created.','superadmin','admin','Product','BR-PF-001','read','2025-08-30 05:18:15.817547'),
('16eecb3f-5685-431b-847e-b1a443d97eca','admin_model_change','Admin Change Detected','Subcategory \'Executive Diaries & Planners\' was updated.','superadmin','admin','SubCategory','O&S-EXECUTIVE-001','read','2025-09-04 14:08:36.337269'),
('1792571b-0097-4895-8974-97f2bc63fc67','admin_model_change','Admin Change Detected','Product \'A5 Size Milk Paper Spiral Notebooks, 70 Sheets 80 GSM\' was created.','superadmin','admin','Product','NO-AS-001','read','2025-09-01 12:17:14.121515'),
('182d29b8-f9a8-4187-8ffa-d39ad3b34937','admin_model_change','Admin Change Detected','Subcategory \'Banners\' was created.','superadmin','admin','SubCategory','BD&F-BANNERS-001','read','2025-09-03 07:09:32.769940'),
('1833e725-8331-47bb-ae10-57be1b79dd2b','admin_model_change','Admin Change Detected','Subcategory \'Computer & Office Gadgets\' was updated.','superadmin','admin','SubCategory','T-COMPUTER-001','read','2025-09-03 12:29:17.767583'),
('18bd3afb-206b-497b-8826-cd4058664446','admin_model_change','Admin Change Detected','Subcategory \'Invoice Book\' was created.','superadmin','admin','SubCategory','O&S-INVOICE-001','read','2025-09-18 11:47:46.934368'),
('1a40a304-22c9-41e2-8a2f-a4d9ad34bb47','admin_model_change','Admin Change Detected','Product \'Travel Tumbler with Cork Base 450ml Stainless Steel | Custom Branded Tumblers Dubai\' was created.','superadmin','admin','Product','SP-TT-001','read','2025-09-01 11:48:00.448326'),
('1aacd2e0-6da5-4b5f-8090-0f6fdbf6c48b','admin_model_change','Admin Change Detected','Product \'Eco-Friendly Polo Shirt with Custom Branding\' was created.','superadmin','admin','Product','T-EFPSWCB-001','read','2025-08-29 10:49:49.290570'),
('1af0a4e3-847a-4dd4-a862-02ee94227173','admin_model_change','Admin Change Detected','Product \'White PU Leather A5 Notebooks with Band & Bookmark Loop\' was created.','superadmin','admin','Product','NO-WP-001','read','2025-09-01 11:41:35.322800'),
('1b2a9bbc-be6f-4d54-bef1-75ed9ba42e68','admin_model_change','Admin Change Detected','Product \'Metal Name Badges in Gold & Silver Plated\' was updated.','superadmin','admin','Product','CA-MN-001','read','2025-09-01 11:20:26.639050'),
('1b4fa2bc-50bf-47f6-8967-be7446ef9fb2','admin_model_change','Admin Change Detected','Product \'Custom Printed Name Badges\' was created.','superadmin','admin','Product','CA-CPNB-001','read','2025-08-29 10:26:14.775335'),
('1c65b2eb-4c07-44c7-9f13-7ebce605ef63','admin_model_change','Admin Change Detected','Product \'Reusable BPA-Free Plastic Water Bottle with Handle\' was created.','superadmin','admin','Product','EC-RBFPWBWH-001','read','2025-08-29 11:13:30.704088'),
('1c7a6e45-fcde-4372-babd-95690c082eb9','admin_model_change','Admin Change Detected','Subcategory \'Caps & Hats\' was updated.','superadmin','admin','SubCategory','CAA-CAPS-001','read','2025-09-09 10:19:59.801060'),
('1cb05a96-42c9-4b3a-b59e-9d4c7c3f3415','admin_model_change','Admin Change Detected','Product \'German Beer Mugs | Custom Branded Beer Mugs & Glassware Dubai\' was created.','superadmin','admin','Product','CE-GB-001','read','2025-09-01 09:04:00.890335'),
('1cf5fd62-cecf-4ce8-992c-eb934d82e40d','admin_model_change','Admin Change Detected','Product \'Promotional Gift Set with Black Cardboard Box\' was created.','superadmin','admin','Product','BR-PGSWBCB-001','read','2025-08-29 08:55:48.457106'),
('1db31a7c-69e6-4f87-9f94-747483f13025','admin_model_change','Admin Change Detected','Product \'Waterproof Adjustable Adhesive Event Wristbands Dubai & UAE\' was created.','superadmin','admin','Product','AC-WA-001','read','2025-09-01 08:23:31.489854'),
('1e7e243a-f5ac-4d41-b54c-4a05935fe67b','admin_model_change','Admin Change Detected','Product \'Two-Tone Ceramic Mugs | Custom Color Coffee & Tea Mugs Dubai\' was updated.','superadmin','admin','Product','CE-TT-002','read','2025-09-01 09:33:45.706587'),
('1e90198f-ea9b-4de7-a63e-69ebaffe7886','admin_model_change','Admin Change Detected','Blog \'Ikrash ne kiya theek kiya????\' was published.','superadmin','admin','Blog','ikrashnekiyatheekk-ff2ae602e9','read','2025-09-18 13:29:23.399146'),
('1ebf1d27-0d32-4d8d-be79-58633dd5bd9c','admin_model_change','Admin Change Detected','Product \'Eco-friendly glass bottles with straw\' was created.','superadmin','admin','Product','EC-EF-001','read','2025-09-04 07:01:28.039016'),
('1ed3bf85-a323-4c50-9608-fc7015ee7508','admin_model_change','Admin Change Detected','Subcategory \'Pet & Specialty Item\' was updated.','superadmin','admin','SubCategory','EG&S-PET-001','read','2025-09-10 05:55:16.862631'),
('1f33b81a-75c4-4526-87f4-7e77bed5b6b3','admin_model_change','Admin Change Detected','Product \'Two-Toned Ceramic Mugs with Clay Bottom & Bamboo Lid | Custom Coffee Mugs Dubai\' was updated.','superadmin','admin','Product','CE-TT-001','read','2025-09-01 09:33:17.721519'),
('1f48d520-fa76-4796-b2b6-e874152757d8','admin_model_change','Admin Change Detected','Product \'Corporate Name Tag with Branding\' was created.','superadmin','admin','Product','CA-CN-001','read','2025-08-30 06:39:50.466011'),
('1f5f1453-7705-427e-a8a8-96b02e3b5cda','admin_model_change','Admin Change Detected','Product \'rPET Bottles with Cork Base & Twist-Off Lid 720ml | Eco-Friendly Water Bottles Dubai\' was created.','superadmin','admin','Product','SP-RB-001','read','2025-09-01 11:20:18.607645'),
('1f7c9648-16a8-40ed-a7ec-e9c8eb24f056','admin_model_change','Admin Change Detected','Product \'Travel Bottles | Custom Branded Water & Sports Bottles Dubai\' was created.','superadmin','admin','Product','SP-TB-001','read','2025-09-01 10:38:01.205639'),
('1f88d31f-9f0f-46c0-b6e5-1e82e407b638','admin_model_change','Admin Change Detected','Subcategory \'Custom USB Drives\' was created.','superadmin','admin','SubCategory','T-CUSTOM-001','read','2025-09-03 15:22:56.144967'),
('1fb3d04f-3524-4b0b-be42-9cae6fe909df','admin_model_change','Admin Change Detected','Product \'Printed ID Card Holder with Lanyard\' was created.','superadmin','admin','Product','CA-PICHWL-001','read','2025-08-29 10:37:32.804227'),
('1ff0c735-bf20-44f4-8aeb-f603d29e7bd7','admin_model_change','Admin Change Detected','Subcategory \'Calendars & Miscellaneous Items\' was created.','superadmin','admin','SubCategory','O&S-CALENDARS-001','read','2025-08-29 07:00:36.226872'),
('2099f30b-7864-46e8-a50c-613307c5f69a','admin_model_change','Admin Change Detected','Product \'Multi-Device Wireless Charger Power Bank\' was updated.','superadmin','admin','Product','PO-MD-001','read','2025-09-04 11:51:43.614288'),
('20dbae5f-5f42-40a1-952c-1d56e3285ff1','admin_model_change','Admin Change Detected','Product \'2025 Table Calendars with Plantable Seeds\' was created.','superadmin','admin','Product','CA-2T-001','read','2025-09-01 11:05:36.352225'),
('21cc46a2-df4c-4529-815e-64db6c7bfb64','admin_model_change','Admin Change Detected','Product \'Durable stainless steel travel mugs\' was updated.','superadmin','admin','Product','TR-DS-001','read','2025-09-04 11:25:05.726618'),
('21d06eb7-8958-4883-8f2c-c7b7a9a85c86','admin_model_change','Admin Change Detected','Order \'OHS-AA-001\' status changed to \'processing\'.','superadmin','admin','Orders','OHS-AA-001','read','2025-09-09 06:31:15.539427'),
('222b2675-f444-46bf-9183-d32ff32a0cfd','admin_model_change','Admin Change Detected','Subcategory \'T-Shirts & Polo Shirts\' was created.','superadmin','admin','SubCategory','CAA-T-SHIRTS-001','read','2025-08-29 07:01:59.243634'),
('22c7b78d-c619-46e6-89e2-739faac7024d','admin_model_change','Admin Change Detected','Subcategory \'Table Accessories\' was updated.','superadmin','admin','SubCategory','D-TABLE-001','read','2025-09-09 11:27:40.710053'),
('22f47e5b-45d1-491b-bdc2-0b9080b5749f','admin_model_change','Admin Change Detected','Product \'Sturdy Cotton Tote Bag\' was updated.','superadmin','admin','Product','EV-SC-001','read','2025-09-04 11:55:39.710288'),
('2303c288-e9a0-4fbe-91d0-37282f99cdbb','admin_model_change','Admin Change Detected','Product \'Sunshades for Cars in White Tyvek\' was deleted.','superadmin','admin','Product','BR-SF-001','read','2025-09-01 10:20:57.931325'),
('23b87494-4d18-42e4-b07c-f91a40c1762e','admin_model_change','Admin Change Detected','Product \'Branded Plastic Pen with Twisted Barrel for Promotions\' was created.','superadmin','admin','Product','PL-BP-001','read','2025-08-30 07:27:12.511348'),
('23cddada-3f58-485f-b6f4-0665e9cfb01a','admin_model_change','Admin Change Detected','Product \'Branded Eco Bluetooth Speaker with Long Battery Life\' was created.','superadmin','admin','Product','CO-BE-001','read','2025-09-01 06:38:34.661439'),
('24294a13-aa06-4778-8f26-010a8238187c','admin_model_change','Admin Change Detected','Subcategory \'Uniforms & Workwear\' was updated.','superadmin','admin','SubCategory','CAA-UNIFORMS-001','read','2025-09-09 08:46:17.848762'),
('24672446-b1c5-4e2e-bff0-a3ec27ed11ea','admin_model_change','Admin Change Detected','Product \'Custom Branded Corporate Planners & Organizers Dubai & UAE\' was created.','superadmin','admin','Product','EX-CB-001','read','2025-09-04 08:07:29.820020'),
('2494aff5-6d79-4a59-9bfb-7fc356be5ed8','admin_model_change','Admin Change Detected','Subcategory \'T-Shirts & Polo Shirts\' was updated.','superadmin','admin','SubCategory','CAA-T-SHIRTS-001','read','2025-09-09 07:59:03.193865'),
('25030141-8210-4a8c-a941-a3227af976f0','admin_model_change','Admin Change Detected','Category \'Signage\' was updated.','superadmin','admin','Category','S-1','read','2025-09-02 17:46:51.103765'),
('2538bb77-b3d0-4405-bb5f-04a2e6c09b09','admin_model_change','Admin Change Detected','Product \'Fast Wireless Charging Mousepad 15W with Foldable Design & Type-C Branded Tech Accessories Dubai UAE\' was updated.','superadmin','admin','Product','CA-FW-001','read','2025-09-04 11:53:58.367320'),
('25a1357c-3a3a-4a2f-8afd-ce652fb6082f','admin_model_change','Admin Change Detected','Product \'Frosted Custom Business Card Printing Dubai & UAE\' was created.','superadmin','admin','Product','BU-FC-001','read','2025-09-01 12:08:42.226926'),
('269dcbc6-b34e-4a55-a25b-ff053329b1af','admin_model_change','Admin Change Detected','Product \'RPET & Chrome Metal Business Card Holder\' was deleted.','superadmin','admin','Product','BU-RC-001','read','2025-09-15 18:01:22.796832'),
('26e5d1f3-d957-4206-84c7-23306cfc0344','admin_model_change','Admin Change Detected','Product \'Promotional Logo Keyrings for Corporate Branding\' was deleted.','superadmin','admin','Product','BR-PL-001','read','2025-08-30 07:23:08.294452'),
('274343f5-fc4f-4d09-8827-d9501f64cdef','admin_model_change','Admin Change Detected','Product \'Promotional UAE Flag Scarf with Fringes\' was created.','superadmin','admin','Product','AC-PUFSWF-001','read','2025-08-29 10:43:06.824646'),
('2746c881-5c6e-4785-9658-ea2099e650f6','admin_model_change','Admin Change Detected','Product \'Corporate Branded Stainless Steel Water Bottle\' was created.','superadmin','admin','Product','SP-CBSSWB-001','read','2025-08-29 11:11:05.767325'),
('2748844e-dfac-4d70-a732-793c2428485a','admin_model_change','Admin Change Detected','Product \'Custom Printed Jute Tote for Promotions\' was deleted.','superadmin','admin','Product','EV-CPJTFP-001','read','2025-09-01 06:10:01.959399'),
('27736ca8-08de-4ee9-832e-45526e7b11c7','admin_model_change','Admin Change Detected','Order \'OAK-IT-001\' status changed to \'shipped\'.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 16:16:17.742799'),
('27aae515-7c62-4a85-b63a-4291423e4ac1','admin_model_change','Admin Change Detected','Product \'German Beer Mugs | Custom Branded Beer Mugs & Glassware Dubai\' was updated.','superadmin','admin','Product','CE-GB-001','read','2025-09-01 09:04:00.999905'),
('27d0f02d-4aa7-4235-802b-f0406e79e66e','admin_model_change','Admin Change Detected','Product \'High Visibility Workwear Corporate Branding Dubai & UAE\' was created.','superadmin','admin','Product','UN-HV-001','read','2025-09-01 08:18:55.410273'),
('2813b8d7-45ed-4b1b-84e3-ea1206778cd5','admin_model_change','Admin Change Detected','Product \'Polyester Wristbands\' was created.','superadmin','admin','Product','EV-PW-001','read','2025-08-29 09:36:53.144956'),
('281a493c-3037-4164-8609-24d2d48abab6','admin_model_change','Admin Change Detected','Product \'Custom Cotton Apron\' was created.','superadmin','admin','Product','UN-CCA-001','read','2025-08-29 09:44:51.553775'),
('2864cf88-0469-4e73-ad41-4bb8c39a3f64','admin_model_change','Admin Change Detected','Blog \'Ikrash ne kiya theek kiya????\' was published.','superadmin','admin','Blog','ikrashnekiyatheekk-c273f913f5','read','2025-09-17 19:04:53.276635'),
('286e7a7d-a1be-4b07-84b2-0b3b1286bc33','admin_model_change','Admin Change Detected','Product \'Durable Reusable Name Tag with Logo Branding\' was updated.','superadmin','admin','Product','CA-DR-001','read','2025-08-30 06:40:53.799711'),
('28c90ae4-a04a-4485-819f-b379d3d14f03','admin_model_change','Admin Change Detected','Product \'Custom Round Bamboo & Metal Keychains 32mm\' was updated.','superadmin','admin','Product','BR-CR-001','read','2025-09-01 09:04:32.050242'),
('29ce10c6-f7dc-4ebe-b26a-a5d88f6591ff','admin_model_change','Admin Change Detected','Product \'Eco Jute Drawstring Pouches A4 & A5\' was deleted.','superadmin','admin','Product','EV-EJDPAA-001','read','2025-09-01 06:10:02.030324'),
('2a1a8cfc-be10-41e5-b65a-aefe8860bcbd','admin_model_change','Admin Change Detected','Product \'Ceramic Coffee Mugs with Bamboo Handle & Lid 380ml | Custom Coffee Mugs Dubai\' was created.','superadmin','admin','Product','CE-CC-001','read','2025-09-01 08:55:48.133494'),
('2a1bb782-a0d4-4ee4-a66b-f5ac798e84fd','admin_model_change','Admin Change Detected','Product \'Aluminum Name Plate\' was deleted.','superadmin','admin','Product','CA-ANP-001','read','2025-09-01 06:10:01.763260'),
('2b33bc50-5f43-4ddc-9b27-40db9380dce8','admin_model_change','Admin Change Detected','Product \'Premium Laser Engraved Metal Visiting Card\' was created.','superadmin','admin','Product','BU-PL-001','read','2025-08-30 07:54:06.536767'),
('2babd3d4-2fb3-4e18-912d-976733f47620','admin_model_change','Admin Change Detected','Subcategory \'Executive Diaries & Planners\' was created.','superadmin','admin','SubCategory','O&S-EXECUTIVE-001','read','2025-08-29 06:59:19.863495'),
('2bec32a5-9173-4d34-a500-b52a285d8b41','admin_model_change','Admin Change Detected','Product \'Bamboo fiber cups with silicone lid\' was created.','superadmin','admin','Product','EC-BF-001','read','2025-09-04 07:10:08.102809'),
('2c454985-846b-4322-9b49-acb837cb9fc8','admin_model_change','Admin Change Detected','Product \'add\' was created.','superadmin','admin','Product','IK-A-001','read','2025-08-29 08:46:30.772722'),
('2cf89903-1a2e-4940-91aa-4f73322a024c','admin_model_change','Admin Change Detected','Product \'Custom Reusable Eco Bags Dubai & UAE\' was updated.','superadmin','admin','Product','EV-CR-002','read','2025-09-04 12:00:55.865264'),
('2d5bb271-6460-4946-9eb6-3a5d53b8b630','admin_model_change','Admin Change Detected','Product \'Mousepad\' was deleted.','superadmin','admin','Product','CA-M-001','read','2025-09-01 06:10:02.147354'),
('2d701be9-edea-4b2e-9e4b-f15ddd8da7f9','admin_model_change','Admin Change Detected','Product \'test\' was deleted.','superadmin','admin','Product','CE-T-004','read','2025-09-01 12:36:24.069441'),
('2e79c4bb-b2d2-49c2-88e2-e483dfbca5ac','admin_model_change','Admin Change Detected','Product \'White Sublimation Mugs | Custom Printed Coffee & Tea Mugs Dubai\' was created.','superadmin','admin','Product','CE-WS-002','read','2025-09-01 10:20:26.363441'),
('2ece4fe8-6e91-46f1-bffc-c9afaa994ae0','admin_model_change','Admin Change Detected','Subcategory \'Premium Business Card\' was created.','superadmin','admin','SubCategory','P&MM-PREMIUM-001','read','2025-09-04 11:35:27.326311'),
('2ee00a5a-dc3b-45cf-bf8f-eff1d5c09e47','admin_model_change','Admin Change Detected','Order \'OAK-IT-001\' status changed to \'pending\'.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 16:16:28.577897'),
('2fe88850-e59e-40ba-89a8-740be842bfa7','admin_model_change','Admin Change Detected','Product \'Fabric Banners\' was created.','superadmin','admin','Product','BA-FB-001','read','2025-09-11 07:23:36.083792'),
('30a9ef35-ee04-4284-a474-f4e9707758ce','admin_model_change','Admin Change Detected','Product \'Promotional Polyester Umbrella with Logo Print\' was deleted.','superadmin','admin','Product','DE-PP-001','read','2025-08-30 07:23:08.303980'),
('31290410-bcc5-4935-9ebc-83249c004e0b','admin_model_change','Admin Change Detected','Product \'Personalized Promotional Badges Dubai & UAE\' was created.','superadmin','admin','Product','BR-PP-001','read','2025-09-04 07:59:19.766132'),
('318fd480-bacc-430e-8351-51a3ea2a44d7','admin_model_change','Admin Change Detected','Product \'Spiral Notebook with Sticky Note and Pen\' was created.','superadmin','admin','Product','NO-SNWSNAP-001','read','2025-08-29 11:03:24.484726'),
('3198ab26-769d-4216-aaa1-cfacf6439c1d','admin_model_change','Admin Change Detected','Subcategory \'Wooden & Eco Pens\' was updated.','superadmin','admin','SubCategory','WI-WOODEN-001','read','2025-09-09 10:23:55.943806'),
('31b7bcdd-7930-489b-aa37-229f97b26e11','admin_model_change','Admin Change Detected','Product \'Round Metal & Wooden Keychain\' was created.','superadmin','admin','Product','BR-RMWK-001','read','2025-08-29 08:58:31.318359'),
('3208f0c0-bdac-4fc0-b9cd-6ff39cdba05f','admin_model_change','Admin Change Detected','Subcategory \'Plastic Pens\' was created.','superadmin','admin','SubCategory','WI-PLASTIC-001','read','2025-08-29 06:45:48.545237'),
('329e9ca1-757e-4262-949a-3b8715823dbe','admin_model_change','Admin Change Detected','Product \'Double Wall Stainless Steel Tumblers 591ml with Slide-Lock PP Lid | Custom Travel Tumblers Dubai\' was updated.','superadmin','admin','Product','TR-DW-002','read','2025-09-01 12:00:45.872420'),
('32b640f5-5e2a-4646-8b62-dcb2e16f1ddc','admin_model_change','Admin Change Detected','Product \'Custom Corporate Diaries & Executive Notebooks Dubai & UAE\' was created.','superadmin','admin','Product','NO-CC-001','read','2025-09-04 08:05:19.027212'),
('32d4175c-8600-4cf6-bb59-b63d087a266b','admin_model_change','Admin Change Detected','Product \'RPET & Chrome Metal Business Card Holder\' was updated.','superadmin','admin','Product','BU-RC-001','read','2025-09-04 10:35:46.032842'),
('32e00755-d28f-467f-8e5e-2b2493cf767b','admin_model_change','Admin Change Detected','Subcategory \'Office Stationery\' was updated.','superadmin','admin','SubCategory','P&MM-OFFICE-001','read','2025-09-04 12:02:45.090174'),
('33326d42-074e-4bd5-bd97-ec9f9195bc00','admin_model_change','Admin Change Detected','Category \'Banner Display & Flags\' was created.','superadmin','admin','Category','BD&F-1','read','2025-09-03 07:01:22.545868'),
('33e653dc-1038-4786-b378-17dbc7addba8','admin_model_change','Admin Change Detected','Product \'Premium Business Cards for Corporate Branding\' was deleted.','superadmin','admin','Product','BU-PB-001','read','2025-09-01 06:09:07.399184'),
('344b7165-b80a-4454-91ef-c7d09d24e436','admin_model_change','Admin Change Detected','Product \'Anti-Stress Balls with Logo Printing\' was deleted.','superadmin','admin','Product','BR-ASBWLP-001','read','2025-09-01 06:10:01.773745'),
('3493612d-c02c-46c5-bd3f-103bea4efa7e','admin_model_change','Admin Change Detected','Product \'Custom Mesh Trucker Cap\' was deleted.','superadmin','admin','Product','AC-CMTC-001','read','2025-09-01 06:10:01.918183'),
('35043168-c4d4-4862-bb63-fc29e060c00d','admin_model_change','Admin Change Detected','Subcategory \'Decorative & Promotional\' was created.','superadmin','admin','SubCategory','EG&S-DECORATIVE-001','read','2025-08-29 07:19:39.806419'),
('3545c929-40c0-4652-b72b-73ccfd54e979','admin_model_change','Admin Change Detected','Product \'Lanyards with Double Hook\' was deleted.','superadmin','admin','Product','BR-LW-001','read','2025-09-01 10:05:48.280649'),
('35d8e7e3-2d66-4ee7-99e4-a8e0dff0b0f3','admin_model_change','Admin Change Detected','Product \'Stainless Steel Business Card Holder\' was created.','superadmin','admin','Product','CA-SSBCH-001','read','2025-08-29 10:07:38.251559'),
('35f4d571-5ed7-4d71-9631-612663009d63','admin_model_change','Admin Change Detected','Product \'Corporate Stylus Writing Pen – Metal Grip Design\' was created.','superadmin','admin','Product','ME-CS-001','read','2025-08-30 07:25:22.948380'),
('35f62a43-2307-44c6-8113-887b6bd12bcf','admin_model_change','Admin Change Detected','Product \'Promotional Sports Bottles 750ml | Custom Branded Sports Water Bottles Dubai\' was created.','superadmin','admin','Product','SP-PS-001','read','2025-09-01 10:55:15.544970'),
('373cf11d-0a16-43b9-a3fd-4748a49f7049','admin_model_change','Admin Change Detected','Product \'Pennant Flags\' was created.','superadmin','admin','Product','FL-PF-001','read','2025-09-11 06:17:21.218190'),
('37abfad8-59ee-4ee9-8ee0-0e4bdce3f3f6','admin_model_change','Admin Change Detected','Subcategory \'Ceramic Mugs\' was created.','superadmin','admin','SubCategory','D-CERAMIC-001','read','2025-09-01 06:44:08.561916'),
('381ec19b-3075-4718-83af-77c3ce73af3c','admin_model_change','Admin Change Detected','Subcategory \'Flags\' was updated.','superadmin','admin','SubCategory','BD&F-FLAGS-001','read','2025-09-10 16:49:58.773503'),
('38962ced-cbbe-46ff-be8e-bd96c2c3e235','admin_model_change','Admin Change Detected','Product \'Custom Pull Up & Retractable Banners Dubai & UAE\' was created.','superadmin','admin','Product','PR-CP-002','read','2025-09-04 07:56:17.763782'),
('390eeafc-7e2e-4d47-b9fa-8cf527c0d211','admin_model_change','Admin Change Detected','Product \'Business Card Holders with RFID Protection – GLASGOW\' was created.','superadmin','admin','Product','CA-BC-001','read','2025-08-30 06:24:02.457746'),
('39d17321-e268-4bb5-85b6-89443d079743','admin_model_change','Admin Change Detected','Product \'White Sublimation Ceramic Mugs with Box 11oz | Custom Printed Coffee Mugs Dubai\' was created.','superadmin','admin','Product','CE-WS-001','read','2025-09-01 09:09:17.528885'),
('39f753f1-116b-404e-abca-3f493a8916df','admin_model_change','Admin Change Detected','Category \'Print & Marketing Material\' was created.','superadmin','admin','Category','P&MM-1','read','2025-08-28 18:24:41.013829'),
('39ffc7dc-71dd-4945-bbaf-38afda098dc9','admin_model_change','Admin Change Detected','Product \'Dual USB Flash Drives for Mobile & Laptop Dubai & UAE\' was updated.','superadmin','admin','Product','CO-DU-001','read','2025-09-04 11:41:53.286657'),
('3aa657c5-94dd-427d-be9d-88c4c54be900','admin_model_change','Admin Change Detected','Product \'Eco-Friendly Custom USB Sticks Dubai & UAE\' was created.','superadmin','admin','Product','CO-EF-001','read','2025-09-04 08:23:28.436060'),
('3ac74498-9295-4a71-8b1d-a859503cc5c2','admin_model_change','Admin Change Detected','Order \'OAK-IT-001\' status changed to \'completed\'.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 16:16:31.736300'),
('3b8a756a-36ce-4aa8-bb69-b2a89242da95','admin_model_change','Admin Change Detected','Subcategory \'Travel Accessories\' was updated.','superadmin','admin','SubCategory','B&T-TRAVEL-001','read','2025-09-09 11:14:27.932630'),
('3bff6d2a-edbc-4e56-93fc-8cbd4b041e93','admin_model_change','Admin Change Detected','Product \'Custom Recycled PET Shopping Bags Dubai & UAE\' was created.','superadmin','admin','Product','EV-CR-001','read','2025-09-04 08:18:38.159495'),
('3c199b80-320b-4802-acfa-613b2a58cc15','admin_model_change','Admin Change Detected','New order \'OTA-TU-001\' was placed.','superadmin','admin','Orders','OTA-TU-001','read','2025-09-17 07:56:58.590571'),
('3c9b322d-5f6a-4522-bb05-4a140d050638','admin_model_change','Admin Change Detected','Product \'Custom Promotional Flyers & Leaflets Dubai & UAE\' was created.','superadmin','admin','Product','PR-CP-001','read','2025-09-01 12:12:10.689619'),
('3c9e1bcb-1be7-42db-a3bf-ab7777943f9d','admin_model_change','Admin Change Detected','Product \'Eco Cork PU Keychain with 32mm Metal Ring\' was deleted.','superadmin','admin','Product','BR-ECPKW3MR-001','read','2025-09-01 06:10:02.392109'),
('3cd982d0-5933-480b-93c9-54a0e87870e9','admin_model_change','Admin Change Detected','Subcategory \'Accessories\' was created.','superadmin','admin','SubCategory','CAA-ACCESSORIES-001','read','2025-08-29 07:06:12.616388'),
('3d5ee0c9-a2d4-4646-acac-4ad32774faea','admin_model_change','Admin Change Detected','Product \'Personalized Flash Drive with Logo Printing\' was deleted.','superadmin','admin','Product','CO-PF-001','read','2025-09-01 06:10:02.166617'),
('3ea807ec-74ea-46da-8da7-4749d4e81b27','admin_model_change','Admin Change Detected','Product \'Adjustable Promotional Silicone Bracelets\' was created.','superadmin','admin','Product','AC-APSB-001','read','2025-08-29 11:04:49.967639'),
('3ed47630-8b8d-46a5-b8cf-8bbbeccc21c1','admin_model_change','Admin Change Detected','Product \'Business Anti-Theft Backpack with USB Charger\' was updated.','superadmin','admin','Product','BA-BA-001','read','2025-09-04 12:05:21.966252'),
('3ed5b043-f3ca-4ef8-aecc-b3f0157eca1a','admin_model_change','Admin Change Detected','Product \'Custom Reusable Eco Bags Dubai & UAE\' was created.','superadmin','admin','Product','EV-CR-002','read','2025-09-04 08:21:03.936212'),
('3ef4a235-5328-46a6-91b6-ab9264862452','admin_model_change','Admin Change Detected','Product \'White PU Leather A5 Diaries with Band & Bookmark Loop\' was created.','superadmin','admin','Product','EX-WP-001','read','2025-09-01 12:28:37.688148'),
('3f10f4ec-195e-4d7b-8eae-a4cdbeec17cb','admin_model_change','Admin Change Detected','Product \'Custom Bluetooth Earphones Corporate Gifts Dubai & UAE\' was created.','superadmin','admin','Product','CO-CB-001','read','2025-09-04 08:30:04.869865'),
('3f1f000c-8c01-43d4-94d2-aa6b3c70fe05','admin_model_change','Admin Change Detected','Product \'Dual USB Flash Drives for Mobile & Laptop Dubai & UAE\' was created.','superadmin','admin','Product','CO-DU-001','read','2025-09-04 08:28:55.993631'),
('400a9820-4e41-476e-89ad-207b332d5c0b','admin_model_change','Admin Change Detected','Product \'Promotional Metal Name Plate – Office & Events\' was created.','superadmin','admin','Product','CA-PM-001','read','2025-08-30 06:43:42.079566'),
('4038cc24-dcb5-4bbd-983d-cba400a98954','admin_model_change','Admin Change Detected','Product \'Promotional Travel Mugs | Custom Coffee Mug & Branded Travel Mug Dubai\' was created.','superadmin','admin','Product','TR-PT-001','read','2025-09-01 07:54:24.514440'),
('4087739b-4f0a-4d8f-9070-4dbaaf148200','admin_model_change','Admin Change Detected','Product \'Event & Conference ID Card with Logo Printing\' was deleted.','superadmin','admin','Product','CA-EC-001','read','2025-09-01 06:10:02.069807'),
('410f0bbd-30c1-4ce3-9fc6-06496af158ab','admin_model_change','Admin Change Detected','Product \'asdasdsa\' was created.','superadmin','admin','Product','CE-A-001','read','2025-09-01 12:17:49.657441'),
('4126e5cb-f3da-4af7-8b6e-0d8e65a0b75b','admin_model_change','Admin Change Detected','Subcategory \'Envelope\' was created.','superadmin','admin','SubCategory','P&MM-ENVELOPE-001','read','2025-09-18 10:24:52.134379'),
('41edf557-ba66-4647-8b64-ca2c9f6247d8','admin_model_change','Admin Change Detected','Subcategory \'Gift Sets\' was updated.','superadmin','admin','SubCategory','WI-GIFT-001','read','2025-09-09 10:24:15.905537'),
('42349436-c44c-4d02-98d2-f3c91cf1ebc6','admin_model_change','Admin Change Detected','Product \'Security Tyvek Wristbands for Access Control\' was deleted.','superadmin','admin','Product','AC-STWFAC-001','read','2025-09-01 06:10:02.286193'),
('4245d53a-db81-436b-99d9-9ce0de31dcbe','admin_model_change','Admin Change Detected','Product \'Durable stainless steel travel mugs\' was created.','superadmin','admin','Product','TR-DS-001','read','2025-09-03 13:08:57.646211'),
('42d64706-79e6-4106-ac04-d75f0e624573','admin_model_change','Admin Change Detected','Subcategory \'Travel & Insulated Mugs\' was updated.','superadmin','admin','SubCategory','D-TRAVEL-001','read','2025-09-09 11:26:33.757374'),
('436a802f-8a29-4f01-b820-4635fdad97a3','admin_model_change','Admin Change Detected','Product \'White PU Leather A5 Notebooks with Band & Bookmark Loop\' was deleted.','superadmin','admin','Product','NO-WP-001','read','2025-09-01 12:24:18.679613'),
('43c86191-3a6a-40db-bda4-89f092a7cac0','admin_model_change','Admin Change Detected','Product \'Promotional UAE Flag Scarf with Fringes\' was deleted.','superadmin','admin','Product','AC-PUFSWF-001','read','2025-09-01 06:10:02.246110'),
('441ca3c7-6f59-431b-982a-eaaa05a3dd2f','admin_model_change','Admin Change Detected','Product \'Silicone Wristbands\' was created.','superadmin','admin','Product','EV-SW-001','read','2025-08-29 09:40:20.197234'),
('44f720f3-4255-49a4-b3cb-2a133f465e02','admin_model_change','Admin Change Detected','Product \'Corporate Catalogs, Profiles & Manuals Dubai & UAE\' was created.','superadmin','admin','Product','PR-CC-002','read','2025-09-04 07:54:34.958983'),
('4573cc5c-34db-4810-a743-358696680133','admin_model_change','Admin Change Detected','Product \'Custom Printed Cotton Tote 170gsm\' was deleted.','superadmin','admin','Product','EV-CPCT1-001','read','2025-09-01 06:10:01.929155'),
('459866f7-d167-4de4-97d0-b42b02c267d4','admin_model_change','Admin Change Detected','Product \'Eco Jute Blend Shopping Bag 250gsm\' was created.','superadmin','admin','Product','EV-EJBSB2-001','read','2025-08-29 09:19:42.911458'),
('462da4f0-3a3c-4ae5-9cfb-995bd0a68981','admin_model_change','Admin Change Detected','Product \'kutta\' was created.','superadmin','admin','Product','BU-K-001','read','2025-08-29 18:11:29.708880'),
('467bb05a-caab-4fd6-8217-610b062eaef6','admin_model_change','Admin Change Detected','Product \'Magic Color Changing Mugs | Custom Heat Sensitive Mug Dubai\' was created.','superadmin','admin','Product','CE-MC-001','read','2025-09-01 07:59:30.652517'),
('46900e31-10b9-41e4-9451-2071d96d329a','admin_model_change','Admin Change Detected','Product \'Leather Card Holder Wallet\' was created.','superadmin','admin','Product','CA-LCHW-001','read','2025-08-29 10:03:02.053227'),
('46e55749-64b4-4273-b57d-c19a179f22ec','admin_model_change','Admin Change Detected','Subcategory \'Metal Ballpoint Pen\' was updated.','superadmin','admin','SubCategory','WI-METAL-001','read','2025-09-09 10:23:27.432707'),
('46ed15fb-d941-49cd-ab5b-b7a989cb8cad','admin_model_change','Admin Change Detected','Product \'Double Hook Lanyard\' was deleted.','superadmin','admin','Product','EV-DHL-001','read','2025-08-30 07:25:25.459999'),
('4831386a-c265-4d15-ba38-df80813531be','admin_model_change','Admin Change Detected','Subcategory \'Sports Bottles\' was updated.','superadmin','admin','SubCategory','D-SPORTS-001','read','2025-09-09 11:26:52.376595'),
('485513aa-14e3-421f-ad07-dabe36fa8e93','admin_model_change','Admin Change Detected','Admin \'admin\' was created.','superadmin','admin','Admin','1','read','2025-08-29 06:07:37.111645'),
('495ed0da-0a57-49fd-be47-5abfd2ca577b','admin_model_change','Admin Change Detected','Product \'Custom Corporate Brochures & Booklets Dubai & UAE\' was updated.','superadmin','admin','Product','PR-CC-001','read','2025-09-18 05:57:32.256769'),
('4a27c1fb-86ca-4f72-b2de-f6db5211264e','admin_model_change','Admin Change Detected','Product \'Promotional Cotton Polo Shirts with Embroidery\' was created.','superadmin','admin','Product','T-PC-001','read','2025-09-01 08:11:37.476825'),
('4a5547ec-0c19-4a66-90b4-ba3e71d64ed6','admin_model_change','Admin Change Detected','Product \'Spiral Notebook with Sticky Note and Pen\' was created.','superadmin','admin','Product','NO-SN-002','read','2025-09-01 12:14:18.322354'),
('4afe8ee9-2f9c-442b-8cfd-fc3b303fbab2','admin_model_change','Admin Change Detected','Product \'Branded Wooden Pens\' was updated.','superadmin','admin','Product','WO-BW-001','read','2025-09-04 10:48:09.995244'),
('4b0f87a3-bb6e-4c0e-9581-21c63ac48265','admin_model_change','Admin Change Detected','Category \'Print & Marketing Material\' was updated.','superadmin','admin','Category','P&MM-1','read','2025-09-02 09:52:18.161269'),
('4b36cc09-e1e8-47b1-95cd-ed4df9c42ba4','admin_model_change','Admin Change Detected','Subcategory \'Travel & Insulated Mugs\' was updated.','superadmin','admin','SubCategory','D-TRAVEL-001','read','2025-09-09 11:40:59.145356'),
('4b6fb069-fa24-47d8-aa97-f39226f44e1e','admin_model_change','Admin Change Detected','Product \'Custom Jute Shopping Bags in Dubai\' was updated.','superadmin','admin','Product','EV-CJ-002','read','2025-09-04 11:58:30.309783'),
('4b7075e4-8c4b-424b-8bc0-3b61951f304b','admin_model_change','Admin Change Detected','Product \'Custom Logo Wooden Pencil & Ruler Gift Set\' was deleted.','superadmin','admin','Product','WO-CL-001','read','2025-09-01 06:10:01.907477'),
('4bdc3c85-521b-4785-9713-22bb063e9044','admin_model_change','Admin Change Detected','Product \'Durable polyester wristbands\' was created.','superadmin','admin','Product','EV-DP-001','read','2025-09-01 10:11:31.274964'),
('4c9fda41-f641-479d-b0e2-af3437aa313b','admin_model_change','Admin Change Detected','Product \'100% Cotton Polo T-Shirts for Branding\' was created.','superadmin','admin','Product','T-1CPTSFB-001','read','2025-08-29 10:47:07.100267'),
('4ccd829b-8fa8-45bf-ba3e-77915fe88356','admin_model_change','Admin Change Detected','Product \'Business Anti-Theft Backpack with USB Charger\' was created.','superadmin','admin','Product','BA-BA-001','read','2025-09-01 06:14:41.088339'),
('4d4ea09c-84e9-4dfa-bbe3-2ed5a6cc6896','admin_model_change','Admin Change Detected','Product \'Business Card Holder with RFID Protection PREMIO\' was updated.','superadmin','admin','Product','CA-BC-001','read','2025-09-01 11:01:10.783271'),
('4d714d4e-af4b-4a78-afb4-64f28321b8d1','admin_model_change','Admin Change Detected','Product \'Custom Lanyards with Hook, Safety Lock & Buckle 20mm\' was deleted.','superadmin','admin','Product','BR-CL-001','read','2025-09-01 10:05:48.260498'),
('4d8d7df4-b9f4-4ef8-a78b-03058056383a','admin_model_change','Admin Change Detected','Product \'Personalized Flash Drive with Logo Printing\' was created.','superadmin','admin','Product','CO-PF-001','read','2025-08-30 07:34:21.784334'),
('4df1ea57-c3d8-4f9e-af77-9b22ee53d730','admin_model_change','Admin Change Detected','Product \'Detox Infuser Bottle with Flip Lid\' was deleted.','superadmin','admin','Product','EC-DIBWFL-001','read','2025-09-01 06:10:01.968256'),
('4dfe81b8-0be5-46be-9b37-020a9b032f6b','admin_model_change','Admin Change Detected','Product \'Premium Dorniel A5 PU notebooks with front pocket & magnetic flap\' was updated.','superadmin','admin','Product','NO-PD-001','read','2025-09-04 12:20:56.379106'),
('4e36e53c-1d7d-4bb5-a559-835444b9a5c6','admin_model_change','Admin Change Detected','Product \'Softcover Notebooks\' was created.','superadmin','admin','Product','NO-SN-001','read','2025-09-01 12:10:13.224232'),
('4e5cc6ff-3c99-4e6b-911f-0f037a72d845','admin_model_change','Admin Change Detected','Subcategory \'Display\' was created.','superadmin','admin','SubCategory','BD&F-DISPLAY-001','read','2025-09-10 11:17:56.107495'),
('4e684e30-9096-4cf4-883b-9ad76ac6ff56','admin_model_change','Admin Change Detected','Product \'Durable 20mm Lanyards with Buckle & Hook\' was created.','superadmin','admin','Product','EV-D2LWBH-001','read','2025-08-29 09:25:54.746225'),
('4f39034b-88c1-47e3-9d17-3beba8bc42b8','admin_model_change','Admin Change Detected','Product \'Luxury Custom Business Card Printing Dubai & UAE”\' was deleted.','superadmin','admin','Product','BU-LC-001','read','2025-09-16 10:01:14.126027'),
('4f5ddb56-d889-4f9a-9219-66320393b291','admin_model_change','Admin Change Detected','Category \'Technology\' was created.','superadmin','admin','Category','T-1','read','2025-08-28 18:18:28.029696'),
('4f880cd2-2204-4b4b-867b-357bf62e7e84','admin_model_change','Admin Change Detected','Product \'Personalized Soft Mesh Caps for Corporate Gifts\' was deleted.','superadmin','admin','Product','AC-PS-001','read','2025-09-02 07:40:15.293540'),
('4fbbcb00-9ef1-4558-9550-1cb1a696709e','admin_model_change','Admin Change Detected','Product \'Custom Jute Shopping Bags in Dubai\' was updated.','superadmin','admin','Product','EV-CJ-002','read','2025-09-01 07:49:12.508681'),
('5018ac77-24fa-42d8-b8a5-beae5970d0ba','admin_model_change','Admin Change Detected','Category \'Writing Instrument\' was updated.','superadmin','admin','Category','WI-1','read','2025-09-02 10:46:33.827864'),
('503d8b8a-1a4c-4c65-99ae-ee5bbd908284','admin_model_change','Admin Change Detected','Product \'Polyester Wristbands\' was deleted.','superadmin','admin','Product','EV-PW-001','read','2025-09-01 06:10:02.185860'),
('507861c6-c798-41a2-87d9-ce9206dd6564','admin_model_change','Admin Change Detected','Subcategory \'Event Essentials\' was updated.','superadmin','admin','SubCategory','EG&S-EVENT-001','read','2025-09-09 13:33:58.144777'),
('51dc792d-fbd2-443e-ba17-a3dcc3720cfa','admin_model_change','Admin Change Detected','Product \'Vertical Non-Woven Tote Bag\' was created.','superadmin','admin','Product','EV-VNWTB-001','read','2025-08-29 09:38:03.876066'),
('536ea43f-2096-41e9-bb4d-bc25e81eaf4e','admin_model_change','Admin Change Detected','Product \'Ceramic Mugs with Lid & Cork Base 385ml | Custom Coffee Mugs Dubai\' was created.','superadmin','admin','Product','CE-CM-001','read','2025-09-01 09:32:14.746797'),
('53ca3989-3ea7-465e-ad5f-ed079ed585f8','admin_model_change','Admin Change Detected','Product \'Aluminum Name Plate\' was created.','superadmin','admin','Product','CA-ANP-001','read','2025-08-29 10:31:02.891297'),
('540dd859-dc71-4353-b0a2-5b41a5bdb97d','admin_model_change','Admin Change Detected','Category \'Office & Stationery\' was created.','superadmin','admin','Category','O&S-1','read','2025-08-28 18:21:27.230521'),
('54163a65-e48d-4a07-a36f-e5294559d7ae','admin_model_change','Admin Change Detected','Product \'add\' was deleted.','superadmin','admin','Product','IK-A-001','read','2025-08-29 08:50:34.640978'),
('5459c30d-d314-4770-b03c-ba53b762617b','admin_model_change','Admin Change Detected','Subcategory \'Everyday & Tote Bags\' was updated.','superadmin','admin','SubCategory','B&T-EVERYDAY-001','read','2025-09-09 10:35:42.771892'),
('55652026-9fb9-4a48-919b-855c0ec46be8','admin_model_change','Admin Change Detected','Product \'Promotional Retractable ID Badge Holder\' was created.','superadmin','admin','Product','CA-PR-001','read','2025-09-01 11:36:48.038511'),
('559c7486-f841-4219-99e8-8589def8b978','admin_model_change','Admin Change Detected','Subcategory \'Computer & Office Gadgets\' was updated.','superadmin','admin','SubCategory','T-COMPUTER-001','read','2025-09-04 10:23:19.092550'),
('55c9bcb5-044c-4688-b65e-21c1dd7e11e9','admin_model_change','Admin Change Detected','Product \'Custom Jute Shopping Bags in Dubai\' was created.','superadmin','admin','Product','EV-CJ-002','read','2025-09-01 07:31:27.143490'),
('561db637-ad92-481d-a7ea-5522ee1ce6a3','admin_model_change','Admin Change Detected','Subcategory \'Pet & Specialty Item\' was created.','superadmin','admin','SubCategory','EG&S-PET-001','read','2025-08-29 07:24:01.471372'),
('5686b69a-be65-448b-bb70-4a11e6d57ac8','admin_model_change','Admin Change Detected','Product \'Windshield Sun Shade with Color Trim\' was deleted.','superadmin','admin','Product','DE-WSSWCT-001','read','2025-09-01 06:10:02.382351'),
('56e163ca-90f3-479e-aa33-c049ccf141f3','admin_model_change','Admin Change Detected','Product \'White Ceramic Mugs | Custom Coffee & Tea Mug Printing Dubai\' was created.','superadmin','admin','Product','CE-WC-002','read','2025-09-01 08:41:07.067084'),
('56fda32c-12ef-4d77-b3c2-acc209424902','admin_model_change','Admin Change Detected','Product \'Custom Jute Drawstring Pouches A4 & A5 Size | Eco-Friendly Gift & Travel Bags Dubai\' was updated.','superadmin','admin','Product','EV-CJ-001','read','2025-09-04 12:11:23.942611'),
('570ad55e-6f74-4807-b2f1-bc0158460f85','admin_model_change','Admin Change Detected','Subcategory \'Sports Bottles\' was created.','superadmin','admin','SubCategory','D-SPORTS-001','read','2025-08-29 07:14:13.996725'),
('574b5ded-fc22-4e1b-8ae1-0f376119f103','admin_model_change','Admin Change Detected','Product \'White Ceramic Mugs with Silicone Cap and Base | Custom Coffee Mug Dubai\' was updated.','superadmin','admin','Product','CE-WC-001','read','2025-09-04 11:37:35.930423'),
('57f7f81c-b148-4cfa-a741-4f7fb5d65c5f','admin_model_change','Admin Change Detected','Subcategory \'Flags\' was created.','superadmin','admin','SubCategory','BD&F-FLAGS-001','read','2025-09-10 11:20:54.208184'),
('58084966-f902-4278-bcf2-10e0ff2ab51d','admin_model_change','Admin Change Detected','Product \'Custom Jute Drawstring Pouches A4 & A5 Size | Eco-Friendly Gift & Travel Bags Dubai\' was created.','superadmin','admin','Product','EV-CJ-001','read','2025-09-01 07:19:04.998780'),
('5814d7ad-7e92-42d9-aee3-4f7dfc8cd115','admin_model_change','Admin Change Detected','Product \'Custom Logo Expandable Phone Grip & Stand\' was updated.','superadmin','admin','Product','CO-CL-001','read','2025-09-04 11:47:12.709403'),
('59a1597e-26dd-499b-8891-e6990c37eba1','admin_model_change','Admin Change Detected','Product \'Hanging Banner\' was created.','superadmin','admin','Product','FL-HB-001','read','2025-09-11 06:24:47.272171'),
('59c2109e-c566-48bf-b958-550ad32b5066','admin_model_change','Admin Change Detected','Product \'Branded Metal Strap Keychain\' was created.','superadmin','admin','Product','BR-BMSK-001','read','2025-08-29 08:06:36.730219'),
('5a9a930a-f5e7-4d74-a546-a253386f8e77','admin_model_change','Admin Change Detected','Product \'Premium Dorniel A5 PU notebooks with front pocket & magnetic flap\' was created.','superadmin','admin','Product','NO-PD-001','read','2025-09-01 11:56:03.018160'),
('5b6e912f-6d72-4e69-91f6-1198ed75b101','admin_model_change','Admin Change Detected','Product \'RPET Business Card Holder with Metal Finish\' was created.','superadmin','admin','Product','CA-RBCHWMF-001','read','2025-08-29 10:05:03.829674'),
('5c4bf22a-2e68-4ff6-ab40-391cfc8e4a11','admin_model_change','Admin Change Detected','Product \'Luxury Custom Business Card Printing Dubai & UAE”\' was updated.','superadmin','admin','Product','BU-LC-001','read','2025-09-03 06:49:17.742840'),
('5c9c4c31-744a-4d8c-a410-9d538d874fc5','admin_model_change','Admin Change Detected','Product \'Foldable Wireless Charging Mousepad\' was created.','superadmin','admin','Product','CA-FWCM-001','read','2025-08-29 10:19:17.557516'),
('5d77c9d0-8a90-4867-aefc-5e409c06a024','admin_model_change','Admin Change Detected','Product \'Metal Name Badges in Gold & Silver Plated\' was created.','superadmin','admin','Product','CA-MN-001','read','2025-09-01 11:18:35.740798'),
('5de3507b-ba25-40fc-8484-ffa2c97c9b35','admin_model_change','Admin Change Detected','Product \'Custom Engraved Metal Visiting Card Case\' was deleted.','superadmin','admin','Product','CA-CE-001','read','2025-08-30 07:32:43.015882'),
('5e1eef90-6383-4f38-b920-d2616c1e0c82','admin_model_change','Admin Change Detected','Product \'Logo Printed Promotional Wrist Sweatbands\' was deleted.','superadmin','admin','Product','AC-LPPWS-001','read','2025-09-01 06:10:02.128049'),
('5e29c801-1f7d-4958-a285-19282fa4b887','admin_model_change','Admin Change Detected','Subcategory \'Ceramic Mugs\' was created.','superadmin','admin','SubCategory','P&MM-CERAMIC-001','read','2025-08-29 07:11:00.048384'),
('5e73197d-352d-4b73-b140-b2398daa0ef1','admin_model_change','Admin Change Detected','Product \'Custom Printed Corporate T-Shirts Dubai & UAE\' was deleted.','superadmin','admin','Product','T-CP-001','read','2025-09-13 10:39:48.912326'),
('5f36f2f6-eb58-4674-b5f3-e8a83d059fa9','admin_model_change','Admin Change Detected','Product \'ChasePlus Credit Card Holder with RFID Protection GLASGOW\' was created.','superadmin','admin','Product','TR-CC-001','read','2025-09-01 08:10:42.723405'),
('5f556363-f236-4f5e-8312-53a0e2bd54d7','admin_model_change','Admin Change Detected','Product \'Stndard Business Cards\' was deleted.','superadmin','admin','Product','BU-SB-001','read','2025-09-16 10:01:14.085691'),
('60a13b0b-200e-493b-8e6f-14ccaccca05c','admin_model_change','Admin Change Detected','Product \'White Bi-Fold Umbrella with Velcro Closure & Pouch\' was deleted.','superadmin','admin','Product','DE-WBFUWVCP-001','read','2025-09-01 06:10:02.363713'),
('60a79aee-63c3-4c13-ab45-e182a19bc8e2','admin_model_change','Admin Change Detected','Product \'ikresh\' was created.','superadmin','admin','Product','IK-I-001','read','2025-08-29 05:45:15.136842'),
('613faf24-4657-437a-819b-d8aa677267f4','admin_model_change','Admin Change Detected','Product \'White Bi-Fold Umbrella with Velcro Closure & Pouch\' was created.','superadmin','admin','Product','DE-WBFUWVCP-001','read','2025-08-29 09:18:43.901481'),
('62080aa7-9c7e-4d68-b524-922d8af26213','admin_model_change','Admin Change Detected','Product \'High Capacity Powerbank 30,000 mAh\' was created.','superadmin','admin','Product','PO-HC-001','read','2025-09-01 06:52:00.837627'),
('621860fa-c9f9-4e49-981f-750b607a7601','admin_model_change','Admin Change Detected','Product \'PU Leather Diaries\' was created.','superadmin','admin','Product','EX-PL-001','read','2025-09-04 07:39:52.239148'),
('621ce010-7c32-4e22-b446-92475aac947c','admin_model_change','Admin Change Detected','Product \'Custom Logo Portable Wireless Speaker\' was deleted.','superadmin','admin','Product','CO-CL-001','read','2025-09-01 06:10:01.895252'),
('62274f10-4a52-43c2-87c3-765cf0382081','admin_model_change','Admin Change Detected','Product \'Eco-Friendly Bamboo Pen with Silver Clip\' was deleted.','superadmin','admin','Product','WO-EF-001','read','2025-09-01 06:10:02.040918'),
('62532edb-5892-43dc-96de-51ba80519227','admin_model_change','Admin Change Detected','Subcategory \'Promotional & Corporate Print\' was updated.','superadmin','admin','SubCategory','P&MM-PROMOTIONAL-001','read','2025-09-03 15:27:53.270744'),
('62828994-1417-4970-86b0-dd0595f9a57f','admin_model_change','Admin Change Detected','Product \'Water Bottle with Fruit Infuser | Custom Infuser Sports Bottles Dubai\' was updated.','superadmin','admin','Product','SP-WB-002','read','2025-09-04 11:34:05.961362'),
('631fe4e4-ebe8-4c81-a1f4-f3a7b1684fb5','admin_model_change','Admin Change Detected','Product \'Custom Logo Expandable Phone Grip & Stand\' was created.','superadmin','admin','Product','CO-CL-001','read','2025-09-01 06:44:22.454726'),
('63d40302-4b8b-489f-a34c-d59609d9c662','admin_model_change','Admin Change Detected','Product \'Eco-Friendly Notebook with Pen Holder\' was created.','superadmin','admin','Product','NO-EFNWPH-001','read','2025-08-29 10:42:51.798343'),
('64038ad4-36d0-4fca-9598-6a6e371643f9','admin_model_change','Admin Change Detected','Subcategory \'Power & Charging Accessories\' was updated.','superadmin','admin','SubCategory','T-POWER-001','read','2025-09-04 08:44:04.755674'),
('6429c4da-7604-40e3-9f95-8b965c2c7554','admin_model_change','Admin Change Detected','Category \'Clothing and Apparel\' was updated.','superadmin','admin','Category','CAA-1','read','2025-09-02 10:16:25.067409'),
('64734da1-165c-4b9f-bc13-ec3b7b551137','admin_model_change','Admin Change Detected','Product \'Branded Plastic Pen with Twisted Barrel for Promotions\' was deleted.','superadmin','admin','Product','PL-BP-001','read','2025-09-01 06:10:01.801586'),
('654135dc-d416-48d8-b622-b16751afabf3','admin_model_change','Admin Change Detected','Subcategory \'Plastic Pens\' was updated.','superadmin','admin','SubCategory','WI-PLASTIC-001','read','2025-09-09 10:23:39.682467'),
('656e2ce4-a8e3-4812-97f1-a312e90c8f5a','admin_model_change','Admin Change Detected','Product \'A5 Size Milk Paper Spiral Notebooks\' was deleted.','superadmin','admin','Product','NO-ASMPSN-001','read','2025-09-01 06:10:01.751091'),
('6579fe44-55b7-4938-93b0-840eb8ce02c8','admin_model_change','Admin Change Detected','Product \'2025 Eco-Friendly Table Calendars\' was created.','superadmin','admin','Product','CA-2EFTC-001','read','2025-08-29 10:15:12.835901'),
('65de927d-f5f3-418f-902e-f703daa900d5','admin_model_change','Admin Change Detected','Product \'Custom Engraved Metal Visiting Card Case\' was created.','superadmin','admin','Product','CA-CE-001','read','2025-08-30 06:29:44.621453'),
('65fcec25-fcc7-4b16-9e8b-348b285822f7','admin_model_change','Admin Change Detected','Product \'Promotional Polyester Lanyard with Dual Hooks\' was deleted.','superadmin','admin','Product','EV-PP-001','read','2025-09-01 06:10:02.235779'),
('67048381-adca-47d4-b132-683d42f450e7','admin_model_change','Admin Change Detected','Subcategory \'Letterheads\' was created.','superadmin','admin','SubCategory','P&MM-LETTERHEADS-001','read','2025-09-18 10:27:55.154507'),
('6710d055-916b-41d1-b5d3-b24dd2ab8aab','admin_model_change','Admin Change Detected','Product \'Fast Wireless Charging Mousepad 15W with Foldable Design & Type-C Branded Tech Accessories Dubai UAE\' was created.','superadmin','admin','Product','CA-FW-001','read','2025-09-01 11:08:15.406858'),
('6723bd5c-aa41-45bd-b8f0-9e58efb80cc5','login','Login Detected','abdullah logged in.','superadmin','admin','User','','unread','2025-08-29 06:07:21.191888'),
('6728b56b-efcb-46d0-85d2-cd45744ee70b','admin_model_change','Admin Change Detected','Product \'Eco Jute Blend Shopping Bag 250gsm\' was deleted.','superadmin','admin','Product','EV-EJBSB2-001','read','2025-09-01 06:10:02.020871'),
('6781ccd0-c9d6-48c4-a189-0bb597eca466','admin_model_change','Admin Change Detected','Product \'Mousepad\' was created.','superadmin','admin','Product','CA-M-001','read','2025-08-29 10:23:57.623423'),
('681487d1-1603-4c24-a2e8-af577547bbcf','admin_model_change','Admin Change Detected','Product \'Custom Jute Shopping Bags in Dubai\' was updated.','superadmin','admin','Product','EV-CJ-002','read','2025-09-01 07:47:06.007957'),
('6828ba2c-fa22-4429-ac45-2ebbddc3fec0','admin_model_change','Admin Change Detected','Product \'Eco Cotton String Bag – 145gsm\' was created.','superadmin','admin','Product','BA-ECSB1-001','read','2025-08-29 09:08:56.360025'),
('6893d03e-27be-42eb-87ed-f6c404786670','admin_model_change','Admin Change Detected','Product \'RPET & Chrome Metal Business Card Holder\' was created.','superadmin','admin','Product','BU-RC-001','read','2025-09-01 12:10:16.115672'),
('6976a41f-7b05-4c3a-9486-e331e59f9bea','admin_model_change','Admin Change Detected','Subcategory \'Backpacks & Laptop Bags\' was updated.','superadmin','admin','SubCategory','B&T-BACKPACKS-001','read','2025-09-09 10:58:17.345958'),
('699949bc-3702-42d2-9ff7-92467e446d0f','admin_model_change','Admin Change Detected','Product \'Product\' was created.','superadmin','admin','Product','BR-P-001','read','2025-08-29 08:50:03.010298'),
('6ad1e475-8cc9-45c6-a46c-3589dfccded5','admin_model_change','Admin Change Detected','Product \'Corporate Stylus Writing Pen – Metal Grip Design\' was updated.','superadmin','admin','Product','ME-CS-001','read','2025-08-30 07:25:23.021906'),
('6ae2a458-5a17-4b52-a796-34d666ee8328','admin_model_change','Admin Change Detected','Subcategory \'Signage\' was updated.','superadmin','admin','SubCategory','EG&S-SIGNAGE-001','read','2025-09-10 05:55:44.399671'),
('6bd7980a-e690-4c24-b32b-4d444d529811','admin_model_change','Admin Change Detected','Product \'Round Bamboo Keyring with Logo Engraving\' was created.','superadmin','admin','Product','BR-RB-001','read','2025-08-30 05:22:24.427239'),
('6c3f4756-2462-4a34-9c60-cba14fda10ab','admin_model_change','Admin Change Detected','Product \'Plastic Bottles with Straw\' was created.','superadmin','admin','Product','SP-PB-001','read','2025-09-04 06:52:49.208603'),
('6d395067-f9c7-4465-a83e-59ade74b267d','admin_model_change','Admin Change Detected','Admin \'Ahsan\' was created.','superadmin','admin','Admin','AAAN-CU-001','read','2025-09-05 13:17:12.117558'),
('6da4b888-2390-420f-9f87-488671cdbbd9','admin_model_change','Admin Change Detected','Product \'Personalized Soft Mesh Caps for Corporate Gifts\' was created.','superadmin','admin','Product','AC-PS-001','read','2025-09-01 08:06:40.894370'),
('6dfd9533-f6ed-4cd6-ad04-9897fbd0b1cc','admin_model_change','Admin Change Detected','Category \'Drinkware\' was created.','superadmin','admin','Category','D-1','read','2025-08-28 18:16:09.710963'),
('6e6e1b8e-8f9f-425e-b4f2-e987c3b161db','admin_model_change','Admin Change Detected','Product \'Curve Edge Mugs | Custom Ceramic Coffee & Tea Mug Dubai\' was updated.','superadmin','admin','Product','CE-CE-001','read','2025-09-01 08:23:54.296703'),
('6e7b1036-ddd9-42a5-aaa6-c2388ac12a68','admin_model_change','Admin Change Detected','Admin \'admin\' was created.','superadmin','admin','Admin','AAIN-SU-001','read','2025-08-29 06:39:25.384356'),
('6eb9e201-45d8-4d77-a544-6b6cfbfc4112','admin_model_change','Admin Change Detected','Subcategory \'Power & Charging Accessories\' was created.','superadmin','admin','SubCategory','T-POWER-001','read','2025-09-01 06:42:08.415006'),
('6f0fddda-2095-4423-90bc-072015554fa8','admin_model_change','Admin Change Detected','Product \'Double Wall Stainless Steel Tumblers 591ml with Slide-Lock PP Lid | Custom Travel Tumblers Dubai\' was updated.','superadmin','admin','Product','TR-DW-002','read','2025-09-01 12:03:05.306881'),
('6f6ea647-8ee3-4022-9373-031f919cfa15','admin_model_change','Admin Change Detected','Subcategory \'Travel Accessories\' was created.','superadmin','admin','SubCategory','B&T-TRAVEL-001','read','2025-08-29 06:55:27.339030'),
('6fdadcf4-c17c-4a61-aa56-4dd01933f91b','admin_model_change','Admin Change Detected','Product \'ID card holder with a lanyard\' was created.','superadmin','admin','Product','CA-IC-001','read','2025-09-01 11:34:30.746258'),
('70592b55-95d7-43ed-a78b-fcf2c30dc8ce','admin_model_change','Admin Change Detected','Category \'Events, Giveaways & Signage\' was created.','superadmin','admin','Category','EG&S-1','read','2025-08-29 06:10:26.483246'),
('705a2410-24fd-4082-bb96-dc060edc8bea','admin_model_change','Admin Change Detected','Subcategory \'Eco-Friendly Drinkware\' was updated.','superadmin','admin','SubCategory','D-ECO-FRIENDLY-001','read','2025-09-09 11:27:24.657090'),
('7071472d-3880-4313-ad77-e41e3413b1c1','admin_model_change','Admin Change Detected','Product \'Silicone Wristbands\' was deleted.','superadmin','admin','Product','EV-SW-001','read','2025-09-01 06:10:02.296123'),
('70c56aaa-1fe9-419d-8c8f-dba611becd20','admin_model_change','Admin Change Detected','New order \'OAK-IT-001\' was placed.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 15:53:35.365613'),
('70f65102-3f41-4c5b-a1f9-ba47e1459cd7','admin_model_change','Admin Change Detected','Product \'NEXTT LEVEL Recycled Polo T-Shirts\' was created.','superadmin','admin','Product','T-NL-001','read','2025-09-01 08:13:22.819770'),
('7124e420-9b19-4f3e-b869-02b30b58cb6e','admin_model_change','Admin Change Detected','Subcategory \'Calendars & Miscellaneous Items\' was updated.','superadmin','admin','SubCategory','O&S-CALENDARS-001','read','2025-09-04 14:19:46.770885'),
('7157aae0-d6f3-4db2-845f-8218ebfd9d7f','admin_model_change','Admin Change Detected','Product \'Custom Logo Rubber Wristbands Dubai & UAE\' was created.','superadmin','admin','Product','AC-CL-001','read','2025-09-01 08:25:27.958653'),
('720ecf44-e2da-4eaa-85e5-2d1b3bdd575c','admin_model_change','Admin Change Detected','Product \'Branded Metal Strap Keychain\' was deleted.','superadmin','admin','Product','BR-BMSK-001','read','2025-09-01 06:10:01.792222'),
('721d9a1d-d67d-4375-a5f2-bd4a7ec57164','admin_model_change','Admin Change Detected','Product \'Custom Office Desk Accessories & Corporate Gifts Dubai & UAE\' was created.','superadmin','admin','Product','CA-CO-001','read','2025-09-04 08:13:38.294938'),
('7260bb43-89a1-421c-b439-b9b7a28a8287','admin_model_change','Admin Change Detected','Product \'Custom Lanyards with Hook, Safety Lock & Buckle 20mm\' was created.','superadmin','admin','Product','BR-CL-001','read','2025-09-01 08:54:27.495276'),
('72a55239-d1e8-424c-a0cf-39a55b7b06a9','admin_model_change','Admin Change Detected','Product \'Luxury Custom Business Card Printing Dubai & UAE”\' was created.','superadmin','admin','Product','BU-LC-001','read','2025-09-01 12:06:11.195849'),
('7302fb35-a862-4c75-94a9-cace3bd3bd65','admin_model_change','Admin Change Detected','Product \'Premium Laser Engraved Metal Visiting Card\' was deleted.','superadmin','admin','Product','BU-PL-001','read','2025-09-01 06:10:02.203957'),
('736d50a1-b7df-4df0-9dbc-b6e0136b73fe','admin_model_change','Admin Change Detected','Product \'Two-Toned Ceramic Mugs with Clay Bottom & Bamboo Lid | Custom Coffee Mugs Dubai\' was created.','superadmin','admin','Product','CE-TT-001','read','2025-09-01 08:47:14.760562'),
('73d25a7d-b3e3-4046-94ce-3046f8dc920f','admin_model_change','Admin Change Detected','Product \'Corporate Branded Stainless Steel Water Bottle\' was deleted.','superadmin','admin','Product','SP-CBSSWB-001','read','2025-09-01 06:10:01.850623'),
('73f3b9ad-9702-4660-bbf3-cf305cf1a515','admin_model_change','Admin Change Detected','Product \'Custom Logo Rubber Wristbands Dubai & UAE\' was deleted.','superadmin','admin','Product','AC-CL-001','read','2025-09-01 09:01:06.547997'),
('7434fde3-8f5f-4f1a-ab7b-4aed78fb82df','admin_model_change','Admin Change Detected','Product \'Double Wall Stainless Steel Tumbler with Clear Lid\' was created.','superadmin','admin','Product','TR-DWSSTWCL-001','read','2025-08-29 11:16:10.663260'),
('748ea274-d051-4865-b140-e98b83b36a7d','login','Login Detected','abdullah logged in.','superadmin','admin','User','','unread','2025-09-01 11:41:06.713644'),
('7492706a-866e-4e30-979c-2b841dc96ece','admin_model_change','Admin Change Detected','Product \'Hello\' was created.','superadmin','admin','Product','IK-H-001','read','2025-08-29 08:47:12.961675'),
('75bd312b-c01a-471e-9097-8bffcdb57c32','admin_model_change','Admin Change Detected','Product \'Heavy Duty Table Flags\' was created.','superadmin','admin','Product','FL-HD-001','read','2025-09-11 06:13:30.994667'),
('75d41f96-c8a9-4687-b378-0eba54c4dd43','admin_model_change','Admin Change Detected','Subcategory \'Uniforms & Workwear\' was created.','superadmin','admin','SubCategory','CAA-UNIFORMS-001','read','2025-08-29 07:04:49.910222'),
('76192894-3c81-4652-88ce-3e9499f876cf','admin_model_change','Admin Change Detected','Product \'Clear Glass Mug with Bamboo Lid and Spoon | Custom Coffee & Tea Mug Dubai\' was created.','superadmin','admin','Product','CE-CG-001','read','2025-09-01 08:07:35.340657'),
('761f2c34-3fb6-46ae-aecc-523a48d5f14f','admin_model_change','Admin Change Detected','Subcategory \'Notebooks & Writing Pads\' was updated.','superadmin','admin','SubCategory','O&S-NOTEBOOKS-001','read','2025-09-04 12:39:34.063658'),
('7670a645-1330-4cbc-ac45-041d50954e31','admin_model_change','Admin Change Detected','Product \'Logo Printed Safety Lock Lanyards with Buckle\' was deleted.','superadmin','admin','Product','EV-LP-001','read','2025-09-01 06:10:02.137437'),
('78062b91-6ada-4867-ab12-897e9965e9c6','admin_model_change','Admin Change Detected','Product \'asdasdsa\' was deleted.','superadmin','admin','Product','CE-A-001','read','2025-09-01 12:36:24.058509'),
('780c66f0-06d8-4618-9b5d-dff3ae93c1b1','admin_model_change','Admin Change Detected','Product \'Double Wall Tumblers 473ml with Flip-Top PP Lid | Custom Travel Tumblers Dubai\' was created.','superadmin','admin','Product','TR-DW-001','read','2025-09-01 11:55:58.671900'),
('799c6354-a017-4c6e-b72d-930c40f2d4b9','admin_model_change','Admin Change Detected','Product \'Vertical Non-Woven Tote Bag\' was deleted.','superadmin','admin','Product','EV-VNWTB-001','read','2025-09-01 06:10:02.354273'),
('79e70399-3b79-407a-8c70-6486c3b2de13','admin_model_change','Admin Change Detected','Product \'Round Glass Tea Coasters\' was created.','superadmin','admin','Product','TA-RG-001','read','2025-09-02 08:12:46.424182'),
('7a0381c7-e363-46d5-bd90-2ad0b35ff0bc','admin_model_change','Admin Change Detected','Product \'test\' was created.','superadmin','admin','Product','CE-T-004','read','2025-09-01 12:18:25.074783'),
('7b19014b-fb7b-4260-ae6b-c4ebbee5dc42','admin_model_change','Admin Change Detected','Product \'Durable 20mm Lanyards with Buckle & Hook\' was deleted.','superadmin','admin','Product','EV-D2LWBH-001','read','2025-09-01 06:10:01.989380'),
('7b61e235-903d-4122-b9e0-aa9640f518a1','admin_model_change','Admin Change Detected','Product \'Promotional Cork Keyring with Branding\' was created.','superadmin','admin','Product','BR-PC-001','read','2025-08-30 05:14:34.170973'),
('7b7f0de7-aaea-4967-b8f5-05c9abc42037','admin_model_change','Admin Change Detected','Subcategory \'ikrash\' was created.','superadmin','admin','SubCategory','P&MM-IKRASH-001','read','2025-08-29 05:42:53.373754'),
('7ba5d8b5-a7f3-4c4d-8011-b36db6636c34','login','Admin Logged In','abdullah just logged in.','superadmin','admin','Admin','','read','2025-08-29 06:07:21.190670'),
('7bd96fb2-e593-4925-ac56-d0d5a970c8fc','admin_model_change','Admin Change Detected','Product \'Custom Mesh Trucker Cap\' was created.','superadmin','admin','Product','AC-CMTC-001','read','2025-08-29 09:49:22.249246'),
('7d754487-8698-4cf8-b231-b98fc124367a','admin_model_change','Admin Change Detected','Product \'Promotional Gift Set with Black Cardboard Box\' was deleted.','superadmin','admin','Product','BR-PGSWBCB-001','read','2025-09-01 06:10:02.225091'),
('7ea579b3-ee24-4538-8426-07af2043b7cf','admin_model_change','Admin Change Detected','Product \'LED Temperature Display Black Tumblers 510ml Stainless Steel | Smart Custom Tumblers Dubai\' was created.','superadmin','admin','Product','TR-LT-001','read','2025-09-01 12:06:27.299743'),
('7f25499c-e377-40d5-99e5-f1c4cb3b8874','admin_model_change','Admin Change Detected','Product \'Weatherproof Gold Epoxy Vinyl Roll for Custom Stickers\' was deleted.','superadmin','admin','Product','PR-WG-001','read','2025-09-01 06:09:07.417973'),
('7fb3395c-beff-4ade-9be7-0bb259cc1f66','admin_model_change','Admin Change Detected','Product \'Bi-Fold White Umbrella with Velcro Closure & Pouch\' was deleted.','superadmin','admin','Product','BR-BF-001','read','2025-09-01 10:20:57.917719'),
('8021128d-2b31-4e91-8376-b39669d0faa9','admin_model_change','Admin Change Detected','Product \'Custom Cotton Apron\' was deleted.','superadmin','admin','Product','UN-CCA-001','read','2025-09-01 06:10:01.882474'),
('80227e1f-768d-493c-aaa0-800a211c31df','admin_model_change','Admin Change Detected','Product \'Branded Wooden Pens\' was created.','superadmin','admin','Product','WO-BW-001','read','2025-09-01 06:22:19.822411'),
('808bc829-e6e7-49fa-be5c-2ec1cea1404c','admin_model_change','Admin Change Detected','Product \'Foldable Wireless Charging Mousepad\' was deleted.','superadmin','admin','Product','CA-FWCM-001','read','2025-09-01 06:10:02.080246'),
('817925ca-4032-4313-a839-6afd0fd585e7','admin_model_change','Admin Change Detected','Subcategory \'Standard Business Cards\' was updated.','superadmin','admin','SubCategory','P&MM-BUSINESS-001','read','2025-09-03 15:26:41.901886'),
('81dc0703-99cd-46c0-bd1e-e3c963b672ef','admin_model_change','Admin Change Detected','Product \'Luxury Business Gift Set with Logo Printing\' was created.','superadmin','admin','Product','PR-LB-001','read','2025-08-30 05:20:05.802602'),
('82a080bf-b230-4e36-994f-3d9756ab00d2','admin_model_change','Admin Change Detected','Product \'Tear Drop Flag\' was created.','superadmin','admin','Product','FL-TD-001','read','2025-09-11 06:39:46.606594'),
('82fafa7b-353f-4400-bae1-c33469a2fa81','admin_model_change','Admin Change Detected','Subcategory \'Everyday & Tote Bags\' was updated.','superadmin','admin','SubCategory','B&T-EVERYDAY-001','read','2025-09-09 10:35:41.734840'),
('830db60a-023e-4805-8601-1ba7203231f4','admin_model_change','Admin Change Detected','Product \'Affordable plastic ballpoint pens\' was created.','superadmin','admin','Product','PL-AP-001','read','2025-09-03 12:56:02.068594'),
('8345e378-d954-487e-9648-dcb5cd22d5ee','admin_model_change','Admin Change Detected','Subcategory \'Channel Letters\' was created.','superadmin','admin','SubCategory','S-CHANNEL-001','unread','2025-09-20 09:33:07.679720'),
('837513bb-5a04-46c6-81e7-3ba710a424ca','admin_model_change','Admin Change Detected','Product \'Promotional Polyester Lanyard with Dual Hooks\' was created.','superadmin','admin','Product','EV-PP-001','read','2025-08-30 05:32:32.619701'),
('84026bf8-f563-44f3-a7ad-c9cc778e3346','admin_model_change','Admin Change Detected','Order \'OAS-MA-001\' status changed to \'cancelled\'.','superadmin','admin','Orders','OAS-MA-001','read','2025-09-10 08:22:58.919996'),
('8506cf59-8a59-4404-90a2-994b4b71175f','admin_model_change','Admin Change Detected','Product \'Custom White Luggage Tags Printing in Dubai\' was created.','superadmin','admin','Product','TR-CW-001','read','2025-09-01 08:07:06.724578'),
('85e00a38-6935-4512-bebf-b72f69df704b','admin_model_change','Admin Change Detected','Product \'RPET Business Card Holder with Metal Finish\' was deleted.','superadmin','admin','Product','CA-RBCHWMF-001','read','2025-09-01 06:10:02.275967'),
('864e4011-be00-4dc4-93f3-5418b2c6c9d0','admin_model_change','Admin Change Detected','Subcategory \'Accessories\' was updated.','superadmin','admin','SubCategory','CAA-ACCESSORIES-001','read','2025-09-09 09:48:49.350251'),
('86b555b5-6ecc-47fe-9633-fe26ec91ab2d','admin_model_change','Admin Change Detected','Product \'Conference Flags (3m)\' was created.','superadmin','admin','Product','FL-CF-002','read','2025-09-11 06:10:06.890222'),
('86f49f2d-3fee-46a2-a04a-c21055765308','admin_model_change','Admin Change Detected','Product \'Sustainable Seed Paper Calendar with Wooden Easel\' was deleted.','superadmin','admin','Product','CA-SS-002','read','2025-08-30 07:32:43.065059'),
('8742de9d-f94a-476d-abad-71c28d484203','admin_model_change','Admin Change Detected','Order \'OAK-IT-001\' status changed to \'pending\'.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 16:16:20.676279'),
('883af1fd-9ddd-4cf8-b02b-b88df5761f2c','admin_model_change','Admin Change Detected','Product \'Personalized Business Notebook with Elastic Band\' was deleted.','superadmin','admin','Product','CA-PBNWEB-001','read','2025-09-01 06:10:02.156921'),
('88893167-5dcb-43f4-9dbc-207a54a41b2b','admin_model_change','Admin Change Detected','Category \'Bags & Travel\' was created.','superadmin','admin','Category','B&T-1','read','2025-08-28 18:19:47.532394'),
('88e70505-44da-4440-9ee0-2050ba4dea8d','admin_model_change','Admin Change Detected','Product \'Tyvek Wristbands Waterproof, Adjustable, Adhesive\' was created.','superadmin','admin','Product','EV-TW-001','read','2025-09-01 10:13:10.521772'),
('89204257-a544-4fdc-9ae7-21a15e638cec','admin_model_change','Admin Change Detected','Product \'Logo Printed Notebook & Pen Gift Combo\' was created.','superadmin','admin','Product','GI-LP-001','read','2025-09-01 06:24:30.053176'),
('8a4d7420-d3d3-496f-a5b6-a47551c2df0c','admin_model_change','Admin Change Detected','Product \'Executive Conference Laptop Bag\' was updated.','superadmin','admin','Product','BA-EC-001','read','2025-09-04 12:09:47.089452'),
('8acbd8d7-a4ca-41ca-bb7e-147740894fb4','admin_model_change','Admin Change Detected','Category \'Drinkware\' was created.','superadmin','admin','Category','D-1','read','2025-08-28 18:16:14.270601'),
('8adc3dd2-ab91-4521-8311-e964b946d998','admin_model_change','Admin Change Detected','Product \'Eco Cotton String Bag – 145gsm\' was deleted.','superadmin','admin','Product','BA-ECSB1-001','read','2025-09-01 06:10:02.009867'),
('8be2bea3-4c74-4a9d-b5ef-6037e61903ae','admin_model_change','Admin Change Detected','Product \'Lanyards with Double Hook\' was created.','superadmin','admin','Product','EV-LW-001','read','2025-09-01 10:08:07.424646'),
('8bfc7882-1951-4c4f-89d6-bdd5317ac33a','admin_model_change','Admin Change Detected','Product \'Branded Retractable Badge Holders\' was created.','superadmin','admin','Product','CA-BRBH-001','read','2025-08-29 10:35:27.336638'),
('8c9461d4-3e52-4fbf-9db2-e433d5df70a3','admin_model_change','Admin Change Detected','Product \'Eco-friendly wooden pencil sets\' was created.','superadmin','admin','Product','WO-EF-001','read','2025-09-03 13:05:04.512716'),
('8ca27544-34d0-480c-8907-3a21ec6c703e','admin_model_change','Admin Change Detected','Product \'Bi-Fold White Umbrella with Velcro Closure & Pouch\' was created.','superadmin','admin','Product','BR-BF-001','read','2025-09-01 08:45:23.124313'),
('8d28482d-20db-4c43-b6ec-35395535e52f','admin_model_change','Admin Change Detected','Category \'Writing Instrument\' was created.','superadmin','admin','Category','WI-1','read','2025-08-28 18:14:06.544938'),
('8d6db3f5-040f-4bdd-9f4b-a68c1b3bec45','admin_model_change','Admin Change Detected','Subcategory \'Signage\' was created.','superadmin','admin','SubCategory','EG&S-SIGNAGE-001','read','2025-08-29 07:25:17.459253'),
('8e1be0d0-e1fd-4f7c-8538-d3a085bb96fb','admin_model_change','Admin Change Detected','Product \'Multi-Color Promotional Drawstring Bags UAE\' was created.','superadmin','admin','Product','BA-MC-001','read','2025-09-01 06:22:17.251138'),
('8f40e7ad-6c6b-431a-8988-d6b8b8108795','admin_model_change','Admin Change Detected','Product \'Elegant UAE Knit Scarf for Corporate Gifting\' was created.','superadmin','admin','Product','AC-EU-001','read','2025-09-01 08:09:50.065538'),
('8f658904-0b51-425f-9f74-943da7796b77','admin_model_change','Admin Change Detected','Product \'Cork PU Keychains with 32mm Metal Flat Key Ring\' was created.','superadmin','admin','Product','BR-CP-001','read','2025-09-01 08:13:41.679347'),
('8ff55182-8bbb-4d27-a6e4-6242a54c7bd2','admin_model_change','Admin Change Detected','Product \'Custom Round Bamboo & Metal Keychains 32mm\' was created.','superadmin','admin','Product','BR-CR-001','read','2025-09-01 08:34:53.188762'),
('90871f9c-fe84-42a4-8fc2-310ae1a26ea8','admin_model_change','Admin Change Detected','Product \'Premium Business Cards for Corporate Branding\' was created.','superadmin','admin','Product','BU-PB-001','read','2025-08-30 07:41:24.501002'),
('90cdb58a-5f5e-470a-abdc-51f2f62163ac','admin_model_change','Admin Change Detected','Product \'T Shape Table Flags\' was created.','superadmin','admin','Product','FL-TS-001','read','2025-09-11 06:23:09.815958'),
('9204b622-048a-4072-9107-070b84f32351','admin_model_change','Admin Change Detected','Product \'Double Wall Stainless Steel Tumbler with Clear Lid\' was deleted.','superadmin','admin','Product','TR-DWSSTWCL-001','read','2025-09-01 06:10:01.978534'),
('92750d9d-52ae-4220-8d74-9d7d6289e620','admin_model_change','Admin Change Detected','Product \'Custom Travel Mugs | Promotional Coffee Mug & Branded Travel Mug Dubai\' was created.','superadmin','admin','Product','TR-CT-001','read','2025-09-01 07:50:09.462721'),
('92c44bc7-b481-4464-a39e-c8be3129f89c','admin_model_change','Admin Change Detected','Product \'White Ceramic Mugs with Silicone Cap and Base | Custom Coffee Mug Dubai\' was created.','superadmin','admin','Product','CE-WC-001','read','2025-09-01 08:14:06.487950'),
('92faa43b-76f9-4959-aaf3-6f4535b8b748','admin_model_change','Admin Change Detected','Product \'Branded Bamboo Wireless Fast Charging Pad\' was created.','superadmin','admin','Product','PO-BB-001','read','2025-09-01 06:54:02.135850'),
('9314706d-e058-4739-a810-50d235c21dfc','admin_model_change','Admin Change Detected','Subcategory \'Eco-Friendly Drinkware\' was created.','superadmin','admin','SubCategory','D-ECO-FRIENDLY-001','read','2025-08-29 07:15:31.412350'),
('93895163-31e2-46d4-ab78-ae375c32c4c0','admin_model_change','Admin Change Detected','Product \'Custom Printed Jute Tote for Promotions\' was created.','superadmin','admin','Product','EV-CPJTFP-001','read','2025-08-29 10:19:06.127120'),
('93be70ac-e380-4717-bc34-f7bcb0bc766b','logout','Logout Detected','abdullah logged out.','superadmin','admin','User','','unread','2025-09-01 11:41:02.946864'),
('94776039-8240-434e-b0d8-c7fb636a8796','admin_model_change','Admin Change Detected','Product \'Hoisting Type Table Flags\' was created.','superadmin','admin','Product','FL-HT-002','read','2025-09-11 06:14:38.837312'),
('9486ecac-af7c-41db-93e1-0aa7fa7c2604','admin_model_change','Admin Change Detected','Order \'OAK-IT-001\' status changed to \'processing\'.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 16:16:27.205511'),
('94c4e45e-cc1a-4a71-964b-2785c5285f87','admin_model_change','Admin Change Detected','Product \'Square Glass Tea Coasters\' was created.','superadmin','admin','Product','TA-SG-001','read','2025-09-02 08:11:13.953681'),
('964c853e-0045-4676-bb67-14b450626ca9','admin_model_change','Admin Change Detected','Product \'Reusable vertical non-woven shopping bags\' was created.','superadmin','admin','Product','EV-RV-001','read','2025-09-01 08:04:31.872645'),
('96b75be2-504a-49ba-898d-1283537e9e1a','admin_model_change','Admin Change Detected','Product \'Custom NFC & Premium Business Card Printing Dubai & UAE\' was deleted.','superadmin','admin','Product','BU-CN-001','read','2025-09-16 10:01:14.103047'),
('96ba2eb2-975b-4bcf-986a-e9ef018d186a','admin_model_change','Admin Change Detected','Product \'Multi-Device Wireless Charger Power Bank\' was created.','superadmin','admin','Product','PO-MD-001','read','2025-09-01 06:56:25.380709'),
('977c300e-9556-470b-b910-7ee04bca0c26','admin_model_change','Admin Change Detected','Product \'Stainless Steel Business Card Holder\' was updated.','superadmin','admin','Product','CA-SSBCH-001','read','2025-08-29 10:10:35.966793'),
('994aaa71-22be-4d0f-b578-4d17eed2d5e0','admin_model_change','Admin Change Detected','Product \'Custom White Luggage Tags Printing in Dubai\' was updated.','superadmin','admin','Product','TR-CW-001','read','2025-09-04 12:13:07.309536'),
('9966bf72-8b6c-4b4f-920f-a7fa7f4d0ed0','admin_model_change','Admin Change Detected','Product \'Frosted Custom Business Card Printing Dubai & UAE\' was deleted.','superadmin','admin','Product','BU-FC-001','read','2025-09-16 10:01:14.115130'),
('99c10fab-38b7-4086-9565-ef454497e629','admin_model_change','Admin Change Detected','Category \'Drinkware\' was updated.','superadmin','admin','Category','D-1','read','2025-09-02 08:44:55.951738'),
('9a7c0d87-8dca-4a59-86e2-4d72ad78dc6c','admin_model_change','Admin Change Detected','Product \'Product\' was deleted.','superadmin','admin','Product','BR-P-001','read','2025-08-29 08:50:34.629383'),
('9a8570d1-7383-45cd-a137-30fec945566b','admin_model_change','Admin Change Detected','Subcategory \'Kids\' Apparel\' was created.','superadmin','admin','SubCategory','CAA-KIDS\'-001','read','2025-08-29 07:02:59.679806'),
('9a8fac85-1c35-4d5d-af8e-7dc51bf72c47','admin_model_change','Admin Change Detected','Product \'Y Shape Table Flags\' was created.','superadmin','admin','Product','FL-YS-001','read','2025-09-11 06:28:30.528817'),
('9b6980e9-0e53-451c-8c37-8feac1c22092','admin_model_change','Admin Change Detected','Product \'Personalized Stress Balls – Corporate Giveaway\' was created.','superadmin','admin','Product','BR-PS-001','read','2025-08-30 05:24:57.488680'),
('9b84607a-d9d8-4c41-a26a-f49e8a1c7b21','admin_model_change','Admin Change Detected','Product \'Logo Printed Safety Lock Lanyards with Buckle\' was created.','superadmin','admin','Product','EV-LP-001','read','2025-08-30 05:33:58.608807'),
('9be76ae3-13ac-43d6-81fe-28d0cd7f2cf0','admin_model_change','Admin Change Detected','Subcategory \'Banners\' was updated.','superadmin','admin','SubCategory','BD&F-BANNERS-001','read','2025-09-10 16:14:27.344054'),
('9cb06ecb-e40f-4231-a813-7128f10d1598','admin_model_change','Admin Change Detected','Product \'V Shape Table Flags\' was created.','superadmin','admin','Product','FL-VS-001','read','2025-09-11 06:26:33.943850'),
('9cc8c013-8b46-4a9b-8c7c-455ec7556251','admin_model_change','Admin Change Detected','Product \'Collapsible Phone Stand & Grip with Logo Printing\' was created.','superadmin','admin','Product','CO-CP-001','read','2025-08-30 07:32:49.092401'),
('9cd14980-bae5-4475-9d35-46778acab44b','admin_model_change','Admin Change Detected','Product \'100% Cotton Polo T-Shirts for Branding\' was deleted.','superadmin','admin','Product','T-1CPTSFB-001','read','2025-09-01 06:10:01.718936'),
('9cf04656-69db-43e5-92a3-e208c2363a60','admin_model_change','Admin Change Detected','Order \'OAK-IT-001\' status changed to \'completed\'.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 16:16:10.862369'),
('9d19a54c-dde9-466d-b218-7f05e80e7f6e','admin_model_change','Admin Change Detected','Product \'Executive Conference Laptop Bag\' was created.','superadmin','admin','Product','BA-EC-001','read','2025-09-01 06:24:50.888575'),
('9d29b2ba-239d-456e-bc23-aec77352d223','admin_model_change','Admin Change Detected','Subcategory \'Everyday & Tote Bags\' was created.','superadmin','admin','SubCategory','B&T-EVERYDAY-001','read','2025-08-29 06:52:07.369155'),
('9d607917-e794-4892-96e4-fdf811539163','admin_model_change','Admin Change Detected','Product \'VIP Conference Flag (2.9m)\' was created.','superadmin','admin','Product','FL-VC-001','read','2025-09-11 06:27:31.056795'),
('9d77d799-decd-4ff6-936f-638148ed07a5','admin_model_change','Admin Change Detected','Product \'Hardboard Tea Coasters\' was created.','superadmin','admin','Product','TA-HT-001','read','2025-09-02 08:09:44.160473'),
('9deb20dc-3823-42ab-8a1a-b9b87c15f69f','admin_model_change','Admin Change Detected','Product \'Eco-Friendly Custom Branded Coaster Printing\' was created.','superadmin','admin','Product','TA-EF-001','read','2025-09-02 08:05:42.217702'),
('9f6adbaf-b67a-41cc-9537-bb51d932eac4','admin_model_change','Admin Change Detected','Product \'T Shape Table Flags\' was updated.','superadmin','admin','Product','FL-TS-001','read','2025-09-11 06:37:42.481822'),
('9f80440d-fba1-48a9-b91b-c3b765bf1bfd','admin_model_change','Admin Change Detected','Product \'Affordable plastic ballpoint pens\' was updated.','superadmin','admin','Product','PL-AP-001','read','2025-09-04 10:32:42.486873'),
('a03b63cb-c7ab-46d8-8503-03c8d3a08067','admin_model_change','Admin Change Detected','Product \'Business Card Holder with RFID Protection PREMIO\' was created.','superadmin','admin','Product','CA-BC-001','read','2025-09-01 10:37:38.754049'),
('a1502797-ceda-4836-af4e-4891a9e6eadc','admin_model_change','Admin Change Detected','Category \'Clothing and Apparel\' was created.','superadmin','admin','Category','CAA-1','read','2025-08-28 18:22:59.503066'),
('a1d873e5-13f2-45c4-8772-0f4c268b54d6','admin_model_change','Admin Change Detected','Subcategory \'Ceramic Mugs\' was updated.','superadmin','admin','SubCategory','P&MM-CERAMIC-001','read','2025-09-04 11:39:10.548102'),
('a280aefe-e5ea-40c4-8e9f-404f71b5d98d','admin_model_change','Admin Change Detected','Product \'Windshield Sun Shade with Color Trim\' was created.','superadmin','admin','Product','DE-WSSWCT-001','read','2025-08-29 09:06:26.599140'),
('a3ed571e-05b9-496d-963f-030565b760e5','admin_model_change','Admin Change Detected','Product \'Custom Metal Keychain with Strap\' was created.','superadmin','admin','Product','BR-CM-001','read','2025-09-01 08:20:03.112871'),
('a45b7cb2-4e21-44ef-8d0e-ab744106fb0b','admin_model_change','Admin Change Detected','Product \'Water Bottles | Custom Branded Sports & Travel Bottles Dubai\' was created.','superadmin','admin','Product','SP-WB-001','read','2025-09-01 10:44:45.879406'),
('a465cdfb-d1fe-4041-bedd-d948d8c6b753','admin_model_change','Admin Change Detected','Category \'Writing Instrument\' was updated.','superadmin','admin','Category','WI-1','read','2025-09-02 10:46:33.220774'),
('a571c5d2-e774-4608-b2bb-9872b11e6f14','admin_model_change','Admin Change Detected','Product \'Executive Colored Pencil Set with Wooden Box\' was created.','superadmin','admin','Product','WO-EC-001','read','2025-09-01 06:29:30.109076'),
('a59624e2-180d-4ee5-8abb-f8902825d2ca','admin_model_change','Admin Change Detected','Product \'Stylus Metal Pens with Textured Grip\' was created.','superadmin','admin','Product','PL-SM-001','read','2025-09-01 06:27:33.353731'),
('a5e32e1e-d0cb-4b7b-b1a5-a485fb013a7e','admin_model_change','Admin Change Detected','Product \'Premium Embossed Business Cards\' was deleted.','superadmin','admin','Product','BU-PE-001','read','2025-09-01 06:10:02.194946'),
('a632aa44-36ec-4a5a-bf29-b33ad92b48c4','admin_model_change','Admin Change Detected','Product \'Sunshades for Cars in White Tyvek Material\' was created.','superadmin','admin','Product','DE-SF-001','read','2025-09-01 10:26:26.188171'),
('a65ad522-eaba-4a25-930b-350268ed726f','admin_model_change','Admin Change Detected','Product \'Corporate Office Gift Set in Color Themed Box with Ribbon Handle\' was created.','superadmin','admin','Product','PR-CO-001','read','2025-09-04 07:33:10.623134'),
('a6636b7f-efab-464b-a029-e95f98236aad','admin_model_change','Admin Change Detected','Product \'Personalized Stress Balls – Corporate Giveaway\' was deleted.','superadmin','admin','Product','BR-PS-001','read','2025-08-30 07:23:08.264226'),
('a6645fdb-f5ca-4808-a6ef-51e8eae3f25b','admin_model_change','Admin Change Detected','Product \'Security Tyvek Wristbands for Access Control\' was created.','superadmin','admin','Product','AC-STWFAC-001','read','2025-08-29 11:01:29.772055'),
('a6b0733a-7bde-4a57-aa12-bd493c30cac4','admin_model_change','Admin Change Detected','Product \'Branded A5 Hardcover Notebooks\' was created.','superadmin','admin','Product','NO-BA-001','read','2025-09-01 11:49:22.067087'),
('a6f50541-317b-43e5-ae8e-8e1b1cc0390f','admin_model_change','Admin Change Detected','Product \'Foldable Cork + PU Mousepad with Mobile & Pen Holder\' was created.','superadmin','admin','Product','CA-FC-001','read','2025-09-01 11:13:10.349790'),
('a726a0e4-02c9-49ac-aff2-473801340cb7','admin_model_change','Admin Change Detected','Subcategory \'Backpacks & Laptop Bags\' was updated.','superadmin','admin','SubCategory','B&T-BACKPACKS-001','read','2025-09-09 11:20:03.593617'),
('a7417257-6851-4f42-9c36-616e1094187a','admin_model_change','Admin Change Detected','Product \'Leather Portfolio with Zipper and Calculator\' was created.','superadmin','admin','Product','NO-LP-001','read','2025-09-01 12:06:56.668250'),
('a7b956d7-a30b-4f35-b7d6-fe13a71073b4','admin_model_change','Admin Change Detected','Product \'Promotional Sports Bottles 750ml | Custom Branded Sports Water Bottles Dubai\' was updated.','superadmin','admin','Product','SP-PS-001','read','2025-09-01 10:55:48.448978'),
('a7d01ac7-0c96-4ac0-8cf3-b98409806a04','admin_model_change','Admin Change Detected','Product \'Reusable Acrylic Name Badges\' was created.','superadmin','admin','Product','CA-RA-001','read','2025-09-01 11:24:13.346258'),
('a7ee6774-691e-425c-b044-f8c7cd62ebb8','admin_model_change','Admin Change Detected','Product \'White Ceramic Mugs | Custom Tall Coffee & Tea Mugs Dubai\' was created.','superadmin','admin','Product','CE-WC-003','read','2025-09-01 10:09:15.159567'),
('a84c03d7-809e-487b-bf64-fc5b2635d90a','admin_model_change','Admin Change Detected','Product \'Promotional Sports Bottles 750ml | Custom Branded Sports Water Bottles Dubai\' was updated.','superadmin','admin','Product','SP-PS-001','read','2025-09-01 10:57:46.899882'),
('a8e73e29-6aa3-4213-9fb6-cf591cb9d4ac','admin_model_change','Admin Change Detected','Product \'Slim Fabric Wireless Charger for Corporate Gifting\' was created.','superadmin','admin','Product','CA-SF-001','read','2025-08-30 06:35:41.693816'),
('a9eee1f1-9150-42ef-b637-9c628dd2ac8d','admin_model_change','Admin Change Detected','Product \'Curved Top Flags\' was created.','superadmin','admin','Product','FL-CT-001','read','2025-09-11 06:35:12.911454'),
('a9fec863-26ea-42b0-bcb4-3c0ed01e2674','admin_model_change','Admin Change Detected','Product \'Branded A5 Hardcover Notebooks\' was updated.','superadmin','admin','Product','NO-BA-001','read','2025-09-04 12:14:54.004542'),
('aa0034fb-264b-4387-aea3-cf447cfaa368','admin_model_change','Admin Change Detected','Product \'Promotional Car Sun Visor Shade – Double Panel\' was created.','superadmin','admin','Product','DE-PC-001','read','2025-08-30 05:28:09.106375'),
('aa5c25ee-d230-4eea-b5b3-ff5ddbac82d7','admin_model_change','Admin Change Detected','Product \'Promotional Visiting Card Holder with Branding\' was created.','superadmin','admin','Product','CA-PV-001','read','2025-08-30 06:26:32.358070'),
('aa6f809f-1a45-41a0-bfdb-7685791660a0','admin_model_change','Admin Change Detected','New order \'OHS-AA-001\' was placed.','superadmin','admin','Orders','OHS-AA-001','read','2025-09-08 11:23:21.888166'),
('aa7a3110-474a-4f47-97cb-0fa3abfda5ed','admin_model_change','Admin Change Detected','Product \'Custom Anti Stress Balls\' was created.','superadmin','admin','Product','BR-CA-001','read','2025-09-01 08:38:07.644474'),
('aae7c55b-b1f4-4ede-87f7-57a16acb9d8e','admin_model_change','Admin Change Detected','Subcategory \'Backpacks & Laptop Bags\' was created.','superadmin','admin','SubCategory','B&T-BACKPACKS-001','read','2025-08-29 06:53:28.323136'),
('ab7bce57-f87a-47fd-8fd5-5b9676dea504','admin_model_change','Admin Change Detected','Product \'Promotional Cork Keyring with Branding\' was deleted.','superadmin','admin','Product','BR-PC-001','read','2025-08-30 07:23:08.284676'),
('aba5b64f-8411-4bae-97f0-be885245763b','admin_model_change','Admin Change Detected','Product \'Gold Ceramic Mugs | Custom Metallic Coffee & Tea Mugs Dubai\' was created.','superadmin','admin','Product','CE-GC-001','read','2025-09-01 09:12:16.130384'),
('abe12f58-e4a1-47c7-8522-a7053c26a5fd','admin_model_change','Admin Change Detected','Product \'Branded Acrylic Name Badges\' was deleted.','superadmin','admin','Product','CA-BANB-001','read','2025-09-01 06:10:01.783139'),
('acf0a87a-c17f-4c23-8fd2-171d989e725c','admin_model_change','Admin Change Detected','Order \'OAS-MA-001\' status changed to \'completed\'.','superadmin','admin','Orders','OAS-MA-001','read','2025-09-10 08:22:43.622458'),
('ada8fdbf-4047-4a1a-b344-2a73515e28a4','admin_model_change','Admin Change Detected','Subcategory \'Custom USB Drives\' was updated.','superadmin','admin','SubCategory','T-CUSTOM-001','read','2025-09-11 13:27:09.068682'),
('aebe365c-34ce-4247-8d08-f3c241ab2033','admin_model_change','Admin Change Detected','Product \'Custom Printed Cotton Tote 170gsm\' was created.','superadmin','admin','Product','EV-CPCT1-001','read','2025-08-29 09:55:56.851392'),
('b015ff73-ce7f-4e9f-bac8-7902f6c0174c','admin_model_change','Admin Change Detected','Category \'Bags & Travel\' was updated.','superadmin','admin','Category','B&T-1','read','2025-08-29 11:25:16.451625'),
('b04a131d-d81b-4af3-868b-1476d34a60ca','admin_model_change','Admin Change Detected','Product \'Hardcover Promotional Notebooks in Multiple Colors\' was updated.','superadmin','admin','Product','NO-HPNIMC-001','read','2025-08-29 11:08:35.790542'),
('b06fc24c-b1b6-4069-8a7d-e4b446af9707','admin_model_change','Admin Change Detected','Product \'Eco-Friendly Notebook with Pen Holder\' was deleted.','superadmin','admin','Product','NO-EFNWPH-001','read','2025-09-01 06:10:02.050282'),
('b1608537-807c-4fdc-9c9c-48021b1697d3','admin_model_change','Admin Change Detected','Product \'Double Hook Lanyard\' was created.','superadmin','admin','Product','EV-DHL-001','read','2025-08-29 09:22:25.927076'),
('b174acec-6cbe-4857-b002-e273724f4edc','admin_model_change','Admin Change Detected','Subcategory \'Event Essentials\' was created.','superadmin','admin','SubCategory','EG&S-EVENT-001','read','2025-08-29 07:18:20.167460'),
('b1cbe557-106f-4ef5-84e1-5122a87658b7','admin_model_change','Admin Change Detected','Product \'Conference Flags (2m)\' was created.','superadmin','admin','Product','FL-CF-001','read','2025-09-11 06:08:39.740966'),
('b1f6ece9-8485-4dbe-87a7-82e286258275','admin_model_change','Admin Change Detected','Product \'Promotional Flyers with Logo – Custom Business Handouts\' was deleted.','superadmin','admin','Product','PR-PF-001','read','2025-09-01 06:09:07.408715'),
('b21bec43-a880-4eb1-86b7-5dcf7751bb94','admin_model_change','Admin Change Detected','Product \'Custom Holographic Waterproof Stickers Dubai & UAE\' was created.','superadmin','admin','Product','PR-CH-001','read','2025-09-01 12:14:53.441944'),
('b25a8aa0-e044-4cea-97ba-8748352b302b','admin_model_change','Admin Change Detected','Product \'Stainless Steel Bamboo Flask | Eco-Friendly Custom Flask Dubai\' was created.','superadmin','admin','Product','SP-SS-001','read','2025-09-01 11:06:03.134782'),
('b29e0d0f-ddfb-4ce3-8eaa-4b2c1902dd76','admin_model_change','Admin Change Detected','Product \'Comfortable Cotton Face Mask for Children\' was created.','superadmin','admin','Product','AC-CC-001','read','2025-09-01 08:08:19.089280'),
('b32f3721-52fb-482e-9879-9bad8e5967c7','admin_model_change','Admin Change Detected','Product \'A5 PU Notebooks with Magnetic Flap & Pocket\' was created.','superadmin','admin','Product','NO-APNWMFP-001','read','2025-08-29 10:55:34.308111'),
('b4587b7f-413c-42d1-ad70-77a08a8c8a47','admin_model_change','Admin Change Detected','Category \'Events, Giveaways & Signage\' was updated.','superadmin','admin','Category','EG&S-1','read','2025-09-02 17:09:46.933270'),
('b4cf8cda-a736-4e1d-bdbe-1473636d8ce1','admin_model_change','Admin Change Detected','Category \'Events & Giveaway Items\' was updated.','superadmin','admin','Category','EG&S-1','read','2025-09-03 05:55:44.653682'),
('b54ac24f-2668-451f-92a6-b406b6f85773','admin_model_change','Admin Change Detected','Category \'Banner Display & Flags\' was updated.','superadmin','admin','Category','BD&F-1','read','2025-09-03 12:27:37.181106'),
('b578e759-cb5b-4cc8-8712-5a61ee89bda7','admin_model_change','Admin Change Detected','Product \'Durable Reusable Name Tag with Logo Branding\' was created.','superadmin','admin','Product','CA-DR-001','read','2025-08-30 06:40:53.498451'),
('b58a2fc3-ad98-42b2-8e52-9866dfda3e46','admin_model_change','Admin Change Detected','Product \'ChasePlus Business Laptop Bag MIGLIORE\' was deleted.','superadmin','admin','Product','BA-CBLBM-001','read','2025-09-01 06:10:01.820142'),
('b5910a95-f13f-43df-a0c6-7eed8b0586a0','admin_model_change','Admin Change Detected','Subcategory \'Branded Giveaway Items\' was updated.','superadmin','admin','SubCategory','EG&S-BRANDED-001','read','2025-09-09 14:13:17.241617'),
('b6296c2e-44bd-49f1-8011-547e0fdaced1','admin_model_change','Admin Change Detected','Product \'Premium Laser Engraved Metal Visiting Card\' was updated.','superadmin','admin','Product','BU-PL-001','read','2025-08-30 07:55:30.574598'),
('b63cb2a3-243a-4b39-b853-8e71bc26f481','admin_model_change','Admin Change Detected','Product \'2025 Eco-Friendly Table Calendars\' was deleted.','superadmin','admin','Product','CA-2EFTC-001','read','2025-09-01 06:10:01.729514'),
('b64ffcca-74e6-47f3-88dd-6d6b0cb99066','admin_model_change','Admin Change Detected','Product \'Hanging Table Flags\' was created.','superadmin','admin','Product','FL-HT-001','read','2025-09-11 06:11:57.650989'),
('b69fec24-d9d9-4deb-99df-ff3658b232b7','admin_model_change','Admin Change Detected','Product \'Two-Tone Ceramic Mugs | Custom Color Coffee & Tea Mugs Dubai\' was created.','superadmin','admin','Product','CE-TT-002','read','2025-09-01 09:19:55.161179'),
('b721b1d5-571d-4782-aceb-c58e4430f44d','admin_model_change','Admin Change Detected','Subcategory \'Flags\' was updated.','superadmin','admin','SubCategory','BD&F-FLAGS-001','read','2025-09-10 16:49:51.327389'),
('b789f855-31ed-49cc-800a-4e3203dde4eb','admin_model_change','Admin Change Detected','Product \'Promotional Sports Bottles 750ml | Custom Branded Sports Water Bottles Dubai\' was updated.','superadmin','admin','Product','SP-PS-001','read','2025-09-04 11:31:16.544670'),
('b85cc1df-a9f6-471c-993f-60483d78f896','admin_model_change','Admin Change Detected','Subcategory \'Hoodies & Jackets\' was created.','superadmin','admin','SubCategory','CAA-HOODIES-001','read','2025-08-29 07:03:53.754114'),
('b8fc9cc0-ea95-4c84-a673-4e23578c51c0','admin_model_change','Admin Change Detected','Product \'Adjustable Promotional Silicone Bracelets\' was deleted.','superadmin','admin','Product','AC-APSB-001','read','2025-08-30 07:32:43.005686'),
('ba787626-d5a5-4135-8a29-9467a8a2e41e','admin_model_change','Admin Change Detected','Subcategory \'Promotional & Corporate Print\' was created.','superadmin','admin','SubCategory','P&MM-PROMOTIONAL-001','read','2025-08-29 07:08:44.675495'),
('bb7279ce-7cff-460f-aec4-722f17b0b39a','admin_model_change','Admin Change Detected','Product \'Durable Reusable Name Tag with Logo Branding\' was deleted.','superadmin','admin','Product','CA-DR-001','read','2025-08-30 07:32:43.025185'),
('bbeed748-d643-481d-9c95-da4d1f53ff7c','admin_model_change','Admin Change Detected','Product \'Polyester Spandex Face Mask for Kids\' was deleted.','superadmin','admin','Product','AC-PSFMFK-001','read','2025-09-01 06:10:02.176360'),
('bc1fa31d-a0f9-4b72-a7f9-849c11bd1fb7','admin_model_change','Admin Change Detected','Product \'Sturdy Cotton Tote Bag\' was created.','superadmin','admin','Product','EV-SC-001','read','2025-09-01 06:32:55.742250'),
('bc41cc0e-7097-4342-a80b-cd3c0dcc72ab','admin_model_change','Admin Change Detected','Product \'Eco Jute Drawstring Pouches A4 & A5\' was created.','superadmin','admin','Product','EV-EJDPAA-001','read','2025-08-29 10:13:22.869252'),
('bca8ffef-aad8-4129-be5e-e2878a28def1','admin_model_change','Admin Change Detected','Product \'Custom Eco-Friendly Tote Bags Dubai & UAE\' was created.','superadmin','admin','Product','EV-CE-001','read','2025-09-04 08:16:40.231649'),
('bd94bee5-43ec-420e-8938-03bd1fa81571','admin_model_change','Admin Change Detected','Product \'Polyester Spandex Face Mask for Kids\' was created.','superadmin','admin','Product','AC-PSFMFK-001','read','2025-08-29 10:26:53.369087'),
('be76f31a-19a6-411b-a1b5-b186d363715e','admin_model_change','Admin Change Detected','Subcategory \'Premium & Corporate Gifts\' was updated.','superadmin','admin','SubCategory','EG&S-PREMIUM-001','read','2025-09-10 05:51:12.711705'),
('bf7b2769-9dc6-4146-b7a6-d200a6ee5ae3','admin_model_change','Admin Change Detected','Product \'Personalized Soft Mesh Caps for Corporate Gifts\' was created.','superadmin','admin','Product','CA-PS-001','read','2025-09-02 07:54:11.356249'),
('c031effc-30d2-401e-a386-be1a9717c023','admin_model_change','Admin Change Detected','Product \'Promotional Flyers with Logo – Custom Business Handouts\' was created.','superadmin','admin','Product','PR-PF-001','read','2025-08-30 08:04:20.403645'),
('c0779cf5-2a40-419f-9adc-c921741cd325','admin_model_change','Admin Change Detected','Product \'UAE Flag Knitted Scarf – 17x155 cm\' was deleted.','superadmin','admin','Product','AC-UFKS1C-001','read','2025-09-01 06:10:02.344887'),
('c0a7ead9-6db9-43d0-b7a8-b4667fc7f6e1','admin_model_change','Admin Change Detected','Product \'Corporate Name Tag with Branding\' was deleted.','superadmin','admin','Product','CA-CN-001','read','2025-09-01 06:10:01.861099'),
('c0bdf709-5258-47e5-a09b-6c0b5346a8a8','admin_model_change','Admin Change Detected','Product \'Promotional Fabric Strap Keyring with Metal Plate\' was deleted.','superadmin','admin','Product','BR-PF-001','read','2025-08-30 07:25:04.542218'),
('c0ce8199-04ce-4d1a-9ed8-29402a0444cd','admin_model_change','Admin Change Detected','Product \'Bamboo & Stainless Steel Coffee Travel Mug with Handle and Lid | Eco-Friendly Travel Mug Dubai\' was created.','superadmin','admin','Product','CE-BS-001','read','2025-09-01 08:18:56.285733'),
('c0f11ae1-5e6f-47be-8a40-0f3e5ecebb92','admin_model_change','Admin Change Detected','Product \'Tyvek Wristbands Waterproof, Adjustable, Adhesive\' was deleted.','superadmin','admin','Product','BR-TW-001','read','2025-09-01 10:05:48.290443'),
('c1b6c146-2d6f-4f67-8d9e-80e356e93e82','admin_model_change','Admin Change Detected','Product \'Corporate Name Tag with Branding\' was updated.','superadmin','admin','Product','CA-CN-001','read','2025-08-30 06:39:50.570773'),
('c255c873-d240-4af7-a129-8d104e9170b8','admin_model_change','Admin Change Detected','Subcategory \'Table Accessories\' was created.','superadmin','admin','SubCategory','D-TABLE-001','read','2025-08-29 07:16:55.562418'),
('c2a3b8f4-f5e8-4275-aadb-a016a6ff87d3','admin_model_change','Admin Change Detected','Order \'OAK-IT-001\' status changed to \'shipped\'.','superadmin','admin','Orders','OAK-IT-001','read','2025-09-02 16:16:30.572320'),
('c2d48f97-f9eb-4976-962a-b69ff74331ae','admin_model_change','Admin Change Detected','Product \'Personalized Business Notebook with Elastic Band\' was created.','superadmin','admin','Product','CA-PBNWEB-001','read','2025-08-29 10:39:34.325058'),
('c2dd340a-ece1-43db-ae0c-54a3bf71eadc','admin_model_change','Admin Change Detected','Product \'Business Card Holders with RFID Protection – GLASGOW\' was deleted.','superadmin','admin','Product','CA-BC-001','read','2025-08-30 07:26:02.452141'),
('c332f838-f8a0-45a5-806e-0c158e79d460','admin_model_change','Admin Change Detected','Product \'Custom Jute Shopping Bags in Dubai\' was updated.','superadmin','admin','Product','EV-CJ-002','read','2025-09-01 07:49:46.978896'),
('c383b087-7a24-4484-8d80-26a6825f7c16','admin_model_change','Admin Change Detected','Product \'Hardcover Promotional Notebooks in Multiple Colors\' was created.','superadmin','admin','Product','NO-HPNIMC-001','read','2025-08-29 10:45:33.696653'),
('c3cf0869-741f-404b-91b8-7ef2fbd90773','admin_model_change','Admin Change Detected','Product \'White Leather Luggage Tag\' was created.','superadmin','admin','Product','TR-WLLT-001','read','2025-08-29 09:15:00.929310'),
('c400e24d-3b21-46b4-8b20-5a332bc56024','admin_model_change','Admin Change Detected','Product \'Two-Toned Ceramic Mugs with Clay Bottom & Bamboo Lid | Custom Coffee Mugs Dubai\' was updated.','superadmin','admin','Product','CE-TT-001','read','2025-09-01 09:33:17.767354'),
('c401842c-ffe5-428e-833b-2c6a659edfd3','admin_model_change','Admin Change Detected','Product \'Sunshades for Cars in White Tyvek\' was created.','superadmin','admin','Product','BR-SF-001','read','2025-09-01 08:41:21.257437'),
('c44c30aa-22e1-43d7-86f4-f12da8308345','admin_model_change','Admin Change Detected','Category \'Office & Stationery\' was updated.','superadmin','admin','Category','O&S-1','read','2025-08-29 12:50:42.615293'),
('c45f4682-a33c-4275-accd-27d8983985af','admin_model_change','Admin Change Detected','Subcategory \'Hoodies & Jackets\' was updated.','superadmin','admin','SubCategory','CAA-HOODIES-001','read','2025-09-09 08:23:46.653082'),
('c4a4d441-bdd0-41a6-a6dd-2af12740898c','admin_model_change','Admin Change Detected','Product \'Custom Printed Children’s Apparel Dubai & UAE\' was deleted.','superadmin','admin','Product','T-CP-002','read','2025-09-13 10:39:48.898495'),
('c543b80d-d2b8-4ce0-a20f-0d989cbdc143','admin_model_change','Admin Change Detected','Product \'High Visibility Workwear Corporate Branding Dubai & UAE\' was deleted.','superadmin','admin','Product','UN-HV-001','read','2025-09-01 08:20:58.094719'),
('c5d1e306-7620-4d6e-9e4a-e8de45bfa935','admin_model_change','Admin Change Detected','Product \'Stainless Steel Business Card Holder\' was deleted.','superadmin','admin','Product','CA-SSBCH-001','read','2025-09-01 06:10:02.325521'),
('c608f13f-42ac-42c1-a058-8e383ce682ef','admin_model_change','Admin Change Detected','Product \'Eco-Friendly Polo Shirt with Custom Branding\' was deleted.','superadmin','admin','Product','T-EFPSWCB-001','read','2025-09-01 06:10:02.060140'),
('c61cb91b-592a-432e-b624-a473eb165d34','admin_model_change','Admin Change Detected','Product \'ChasePlus Slim RFID Card Case GLASGOW\' was created.','superadmin','admin','Product','TR-CSRCCG-001','read','2025-08-29 09:28:48.520338'),
('c62eca62-97c9-4bf6-8af8-66d52ef0b430','admin_model_change','Admin Change Detected','Subcategory \'Caps & Hats\' was created.','superadmin','admin','SubCategory','CAA-CAPS-001','read','2025-09-02 07:51:14.354996'),
('c709cfc9-e81c-47e9-9586-82a499dd4239','admin_model_change','Admin Change Detected','Subcategory \'Wooden & Eco Pens\' was created.','superadmin','admin','SubCategory','WI-WOODEN-001','read','2025-08-29 06:51:21.405244'),
('c7302b1a-ed6c-4e58-9f3a-25e35a1b15e0','admin_model_change','Admin Change Detected','Product \'Rustic Jute Carry Bag\' was updated.','superadmin','admin','Product','EV-RJ-001','read','2025-09-01 07:04:51.874875'),
('c82c1c7c-a256-4f9c-89ec-e13153213a6a','admin_model_change','Admin Change Detected','Product \'Aluminum Name Plates\' was created.','superadmin','admin','Product','CA-AN-001','read','2025-09-01 11:26:58.722113'),
('c83795e4-3df9-475c-b6bb-2f439d31a815','admin_model_change','Admin Change Detected','Product \'Branded Retractable Badge Holders\' was deleted.','superadmin','admin','Product','CA-BRBH-001','read','2025-09-01 06:10:01.810895'),
('c84854e6-9cc2-4ff0-b6ba-ece73a9d5ce4','admin_model_change','Admin Change Detected','Product \'Lanyards with Double Hook\' was created.','superadmin','admin','Product','BR-LW-001','read','2025-09-01 08:50:01.510075'),
('c8d9ee28-0ed8-4c07-995a-70beccaa6b0e','admin_model_change','Admin Change Detected','Product \'Leather Card Holder Wallet\' was deleted.','superadmin','admin','Product','CA-LCHW-001','read','2025-09-01 06:10:02.099677'),
('c8e2357a-c737-4dfa-9e59-44964a2d52d0','admin_model_change','Admin Change Detected','Product \'Double Wall Stainless Steel Tumblers 591ml with Slide-Lock PP Lid | Custom Travel Tumblers Dubai\' was created.','superadmin','admin','Product','TR-DW-002','read','2025-09-01 12:00:22.746549'),
('c9ac8552-9c73-4553-8257-c6dfb1d95928','admin_model_change','Admin Change Detected','Product \'kutta\' was deleted.','superadmin','admin','Product','BU-K-001','read','2025-08-30 07:23:08.254161'),
('ca2d391a-4e4f-4d7c-8d7c-e77d988ee935','admin_model_change','Admin Change Detected','Product \'Custom High-Visibility Safety Vests Dubai & UAE\' was created.','superadmin','admin','Product','UN-CH-001','read','2025-09-01 08:28:05.075503'),
('ca5ff79d-c530-45b0-96fe-1d2128c39c08','admin_model_change','Admin Change Detected','Product \'UAE Flag Celebration Stole with Arabic Calligraphy\' was deleted.','superadmin','admin','Product','AC-UFCSWAC-001','read','2025-09-01 06:10:02.335268'),
('cba0c60f-f221-488a-a577-9e7314eb2089','admin_model_change','Admin Change Detected','Product \'Universal Multi-Plug Adapters Corporate Gifts Dubai & UAE\' was created.','superadmin','admin','Product','CO-UM-001','read','2025-09-04 08:33:25.899400'),
('cc43a707-c2fb-4048-93a6-ac56efcd6a9c','admin_model_change','Admin Change Detected','Product \'Branded Acrylic Name Badges\' was created.','superadmin','admin','Product','CA-BANB-001','read','2025-08-29 10:28:41.449962'),
('ccc329fb-4c40-4f53-a4c9-c5dc636b1df8','admin_model_change','Admin Change Detected','Product \'Premium Embossed Business Cards\' was created.','superadmin','admin','Product','BU-PE-001','read','2025-08-30 08:01:51.054350'),
('cd13a2a5-81f4-43b7-b1b0-823dadf4111d','admin_model_change','Admin Change Detected','Product \'Logo Printed Promotional Wrist Sweatbands\' was created.','superadmin','admin','Product','AC-LPPWS-001','read','2025-08-29 10:58:54.453143'),
('ce16b948-a905-497e-8e96-dd392d470aec','admin_model_change','Admin Change Detected','Category \'Signage\' was created.','superadmin','admin','Category','S-1','read','2025-09-02 17:44:17.016012'),
('cf7104f7-b636-4753-90dc-f7c7b9154b6f','admin_model_change','Admin Change Detected','Product \'Love Mug Sets | Custom Couple Mugs & Gift Sets Dubai\' was created.','superadmin','admin','Product','CE-LM-001','read','2025-09-01 10:13:38.505268'),
('d04b04c9-8648-4f5c-af52-13ea575533a5','admin_model_change','Admin Change Detected','Product \'Custom Ceramic Mug with Lid & Cork Base 385ml | Coffee Cup & Tea Mug Dubai\' was created.','superadmin','admin','Product','TR-CC-001','read','2025-09-01 07:02:07.953188'),
('d08c021d-ceea-4eb4-8ba2-d93cd03ff4a2','admin_model_change','Admin Change Detected','Product \'ChasePlus Business Laptop Bag MIGLIORE\' was created.','superadmin','admin','Product','BA-CBLBM-001','read','2025-08-29 09:32:19.153137'),
('d211d5a5-9074-4f4c-b666-862cf465152d','admin_model_change','Admin Change Detected','Product \'Eco-Friendly Bamboo Pen with Silver Clip\' was created.','superadmin','admin','Product','WO-EF-001','read','2025-08-30 07:19:41.202797'),
('d2b4837b-6bc7-497d-8e0a-3dba086945cc','admin_model_change','Admin Change Detected','Product \'Tyvek Wristbands Waterproof, Adjustable, Adhesive\' was created.','superadmin','admin','Product','BR-TW-001','read','2025-09-01 09:00:32.831517'),
('d30ea067-ee02-427a-b81f-fc5530b20fbb','admin_model_change','Admin Change Detected','Product \'Durable polyester wristbands\' was deleted.','superadmin','admin','Product','BR-DP-001','read','2025-09-01 10:05:48.270871'),
('d3412695-57ff-4b82-9a6a-100f51777f60','admin_model_change','Admin Change Detected','Product \'Anti-Stress Balls with Logo Printing\' was created.','superadmin','admin','Product','BR-ASBWLP-001','read','2025-08-29 09:02:26.182821'),
('d3dea46e-3966-46b5-b765-1604bd67c72d','admin_model_change','Admin Change Detected','New order \'OYA-PR-001\' was placed.','superadmin','admin','Orders','OYA-PR-001','read','2025-09-05 13:12:40.102111'),
('d3e0168d-1ad0-4977-aaed-eeb3adf2b658','admin_model_change','Admin Change Detected','Product \'Travel Tumbler with Cork Base 450ml Stainless Steel | Ramadan Corporate Gifts Dubai\' was created.','superadmin','admin','Product','TR-TT-001','read','2025-09-01 12:10:47.286064'),
('d3e18508-5b06-4bc0-b7a0-2a086c299b73','admin_model_change','Admin Change Detected','Product \'Collapsible Phone Stand & Grip with Logo Printing\' was deleted.','superadmin','admin','Product','CO-CP-001','read','2025-09-01 06:10:01.841012'),
('d445924d-cd2e-416b-8e4e-dd1d0f8592bc','admin_model_change','Admin Change Detected','Product \'Eco Cork PU Keychain with 32mm Metal Ring\' was created.','superadmin','admin','Product','BR-ECPKW3MR-001','read','2025-08-29 08:03:32.751302'),
('d60d5631-1d86-448a-a393-5de9cd99ca4a','admin_model_change','Admin Change Detected','Product \'Durable Holographic Epoxy Sticker Sheets for Branding\' was deleted.','superadmin','admin','Product','PR-DH-001','read','2025-09-01 06:10:01.999539'),
('d74e625e-11cc-46dd-bee1-9705f750d993','admin_model_change','Admin Change Detected','Product \'Water Bottle with Fruit Infuser | Custom Infuser Sports Bottles Dubai\' was created.','superadmin','admin','Product','SP-WB-002','read','2025-09-01 11:15:09.131538'),
('d7d4c235-ac7c-43dc-b51e-d03b88dad87f','admin_model_change','Admin Change Detected','Product \'Promotional Visiting Card Holder with Branding\' was deleted.','superadmin','admin','Product','CA-PV-001','read','2025-08-30 07:32:43.055677'),
('d87f1b43-6763-447b-839c-29bc7eb27ed0','admin_model_change','Admin Change Detected','Product \'Logo Branded Ceramic Coffee Mug\' was created.','superadmin','admin','Product','TR-LBCCM-001','read','2025-08-29 11:14:49.398361'),
('d897f9a3-8ca7-4b6b-b836-8dba2dc19828','admin_model_change','Admin Change Detected','Product \'Custom Corporate Diaries with Index Tabs Dubai & UAE\' was created.','superadmin','admin','Product','EX-CC-002','read','2025-09-04 08:11:46.920075'),
('d904c527-77e1-44e8-863a-ee638fbb8cac','admin_model_change','Admin Change Detected','Product \'Event & Conference ID Card with Logo Printing\' was created.','superadmin','admin','Product','CA-EC-001','read','2025-08-30 06:51:27.691265'),
('d9a944fc-68f8-40a9-9053-7bd18d2dcc5f','admin_model_change','Admin Change Detected','Product \'Durable polyester wristbands\' was created.','superadmin','admin','Product','BR-DP-001','read','2025-09-01 08:57:57.721684'),
('d9aee78b-71e0-4faa-9b1e-75615c6dc214','admin_model_change','Admin Change Detected','Subcategory \'Travel & Insulated Mugs\' was created.','superadmin','admin','SubCategory','D-TRAVEL-001','read','2025-08-29 07:12:28.319622'),
('d9b61f18-5737-492d-aa28-6427f5cd9482','admin_model_change','Admin Change Detected','Product \'Custom Printed Hi-Vis Safety Vest – Yellow\' was created.','superadmin','admin','Product','UN-CPHVSVY-001','read','2025-08-29 10:56:20.357356'),
('da9f19a6-16ac-4850-8755-78fc00ef8a2e','admin_model_change','Admin Change Detected','Product \'Personalized Coffee Mugs | Custom Printed Mugs Dubai & UAE\' was created.','superadmin','admin','Product','CE-PC-001','read','2025-09-01 09:24:05.813702'),
('daf8ca3d-185b-4ab6-a593-86baf0ef6303','admin_model_change','Admin Change Detected','Product \'Two-Tone Ceramic Mugs with Spoon 11oz | Custom Coffee & Tea Mugs Dubai\' was created.','superadmin','admin','Product','CE-TT-003','read','2025-09-01 09:41:51.562980'),
('daff9a06-a054-4901-b057-843c7f961e94','admin_model_change','Admin Change Detected','Product \'Hello\' was deleted.','superadmin','admin','Product','IK-H-001','read','2025-08-29 08:50:34.650933'),
('dbeabf26-4561-4195-b939-869ee5144fc1','admin_model_change','Admin Change Detected','Product \'Ceramic Coffee Mugs with Bamboo Handle & Lid 380ml | Custom Coffee Mugs Dubai\' was updated.','superadmin','admin','Product','CE-CC-001','read','2025-09-04 10:56:31.468593'),
('dc57757c-1814-4d13-9e8e-6bd5ae8f67b2','admin_model_change','Admin Change Detected','Product \'Custom Lanyards with Hook, Safety Lock & Buckle 20mm\' was updated.','superadmin','admin','Product','BR-CL-001','read','2025-09-01 10:01:43.536425'),
('dcdaa2ba-8c0d-4c9e-bfe6-2e613e151c6f','admin_model_change','Admin Change Detected','Product \'Stndard Business Cards\' was created.','superadmin','admin','Product','BU-SB-001','read','2025-09-12 17:19:48.144728'),
('dcdb6e63-8f3c-40b0-9a33-0860a22412a2','admin_model_change','Admin Change Detected','Subcategory \'Metal Ballpoint Pen\' was created.','superadmin','admin','SubCategory','WI-METAL-001','read','2025-08-29 06:47:54.698723'),
('dce60864-4d47-431b-b417-516b5ff9e64e','admin_model_change','Admin Change Detected','Product \'Custom Jute Shopping Bags in Dubai\' was updated.','superadmin','admin','Product','EV-CJ-002','read','2025-09-01 07:48:47.154612'),
('de9d41d7-f0c5-46e2-969b-0ddf4691c692','admin_model_change','Admin Change Detected','Subcategory \'Ceramic Mug\' was created.','superadmin','admin','SubCategory','D-CERAMIC-002','read','2025-09-04 11:38:33.930238'),
('ded36cdd-1be8-4dea-8fea-23254901985a','admin_model_change','Admin Change Detected','Subcategory \'Eco-Friendly Drinkware\' was updated.','superadmin','admin','SubCategory','D-ECO-FRIENDLY-001','read','2025-09-09 12:54:31.247106'),
('def44c61-14b9-4eab-b5e1-f05d21ae66b7','admin_model_change','Admin Change Detected','Product \'Leather Portfolio with Zipper & Calculator\' was created.','superadmin','admin','Product','NO-LPWZC-001','read','2025-08-29 10:59:29.611675'),
('e047fdde-b99a-44f4-bcab-6bf528590813','admin_model_change','Admin Change Detected','Product \'A5 PU Notebooks with Magnetic Flap & Pocket\' was deleted.','superadmin','admin','Product','NO-APNWMFP-001','read','2025-09-01 06:10:01.740893'),
('e0fc624c-51bd-4565-90c7-6f6e439a2a4a','admin_model_change','Admin Change Detected','Product \'L Shape Table Flags\' was created.','superadmin','admin','Product','FL-LS-001','read','2025-09-11 06:16:07.812052'),
('e11201ec-0f07-4a4a-a7d7-16e7e7f1a6ce','admin_model_change','Admin Change Detected','Product \'Durable Holographic Epoxy Sticker Sheets for Branding\' was created.','superadmin','admin','Product','PR-DH-001','read','2025-08-30 08:08:32.576291'),
('e13d49dc-ec93-425a-9c2e-e047c8ebffa2','admin_model_change','Admin Change Detected','Category \'Office & Stationery\' was updated.','superadmin','admin','Category','O&S-1','read','2025-08-29 12:50:43.166147'),
('e2043877-4ebc-4073-8d2f-f6a54ac249c4','admin_model_change','Admin Change Detected','Product \'Eco Cotton Tote Bag\' was created.','superadmin','admin','Product','BA-EC-002','read','2025-09-01 06:31:13.141769'),
('e2a9c3d1-6ff5-4d99-9243-eff32b23f87e','admin_model_change','Admin Change Detected','Product \'Weatherproof Gold Epoxy Vinyl Roll for Custom Stickers\' was created.','superadmin','admin','Product','PR-WG-001','read','2025-08-30 08:06:12.965287'),
('e3212729-5b42-445f-abfd-98173393c683','admin_model_change','Admin Change Detected','Product \'Custom Jute Shopping Bags with Button Eco-Friendly Reusable Branded Tote Bags Dubai & UAE\' was created.','superadmin','admin','Product','EV-CJ-003','read','2025-09-01 07:52:59.438880'),
('e4405e91-fe37-4ef9-9dde-d331986c4b10','admin_model_change','Admin Change Detected','Product \'Promotional Gift Sets in Black Cardboard Gift Box GS-029\' was created.','superadmin','admin','Product','BR-PG-001','read','2025-09-01 08:24:54.964155'),
('e4908da7-a5d2-40e0-848d-25fb226f6146','admin_model_change','Admin Change Detected','Product \'Custom Cotton Apron\' was updated.','superadmin','admin','Product','UN-CCA-001','read','2025-08-29 09:57:16.738683'),
('e4af964d-8b54-4a82-984a-1e8e9d65981a','admin_model_change','Admin Change Detected','Product \'A5 Size Milk Paper Spiral Notebooks, 70 Sheets 80 GSM\' was updated.','superadmin','admin','Product','NO-AS-001','read','2025-09-04 12:19:20.960929'),
('e501c149-67dd-45d3-842c-e59169f7b44d','admin_model_change','Admin Change Detected','Product \'Custom Printed Name Badges\' was deleted.','superadmin','admin','Product','CA-CPNB-001','read','2025-09-01 06:09:07.387269'),
('e58ea620-a179-443b-b4b5-8408cc74deb2','admin_model_change','Admin Change Detected','Product \'Softcover Notebooks\' was updated.','superadmin','admin','Product','NO-SN-001','read','2025-09-04 12:17:09.657119'),
('e5cbf698-1638-49b8-b514-0dc03ee99873','admin_model_change','Admin Change Detected','Product \'Promotional Cork Mouse Pad with Storage Slots\' was deleted.','superadmin','admin','Product','CA-PC-001','read','2025-08-30 07:32:43.035122'),
('e5f41884-a3de-4dd6-a582-c713b75dcf2f','admin_model_change','Admin Change Detected','Product \'Premium Table Flags\' was created.','superadmin','admin','Product','FL-PT-001','read','2025-09-11 06:19:06.442271'),
('e5fb605d-7516-400f-afcf-5199407e32ab','admin_model_change','Admin Change Detected','Subcategory \'Gift Sets\' was created.','superadmin','admin','SubCategory','WI-GIFT-001','read','2025-08-30 07:50:05.565379'),
('e61870f8-7336-43d2-8f83-3611a829f44b','admin_model_change','Admin Change Detected','Product \'A5 Size Milk Paper Spiral Notebooks\' was created.','superadmin','admin','Product','NO-ASMPSN-001','read','2025-08-29 11:05:53.810352'),
('e7937b64-2318-4c00-8b2d-9763d8bf91cf','admin_model_change','Admin Change Detected','Product \'ChasePlus Slim RFID Card Case GLASGOW\' was deleted.','superadmin','admin','Product','TR-CSRCCG-001','read','2025-09-01 06:10:01.831237'),
('e7e1851b-9189-4a33-b9a8-ec15ca8afaa4','admin_model_change','Admin Change Detected','Admin \'test\' was created.','superadmin','admin','Admin','ATST-SU-001','read','2025-08-29 06:40:40.487811'),
('e867b2e2-1289-4b1f-aa0f-898979004e6f','admin_model_change','Admin Change Detected','Product \'Pole Flag 10 meter\' was created.','superadmin','admin','Product','FL-PF-002','read','2025-09-11 06:31:34.713877'),
('e899466d-2f2f-4839-825a-02e6e05ffeee','admin_model_change','Admin Change Detected','Product \'Custom Printed Fabric Wristbands Dubai & UAE\' was created.','superadmin','admin','Product','AC-CP-001','read','2025-09-01 08:21:39.578514'),
('e8a5b701-be42-4570-8d9f-877ff2478086','admin_model_change','Admin Change Detected','Subcategory \'Plastic Pens\' was updated.','superadmin','admin','SubCategory','WI-PLASTIC-001','read','2025-09-03 12:30:09.568770'),
('e946f610-650d-4f51-b27a-0c7d9e2fbd3a','admin_model_change','Admin Change Detected','Product \'Promotional Car Sun Visor Shade – Double Panel\' was deleted.','superadmin','admin','Product','DE-PC-001','read','2025-08-30 07:23:08.275441'),
('e9a318e0-9bcc-45fb-bfb7-e97353ca8f99','admin_model_change','Admin Change Detected','Product \'Branded Eco Bluetooth Speaker with Long Battery Life\' was updated.','superadmin','admin','Product','CO-BE-001','read','2025-09-04 11:49:49.801338'),
('ea10eecb-ff79-4807-a4f4-576f3455b29a','admin_model_change','Admin Change Detected','Product \'Promotional Cotton Polo Shirts with Embroidery\' was deleted.','superadmin','admin','Product','T-PC-001','read','2025-09-13 10:39:48.940258'),
('ea689972-cf75-4b20-87da-3181c872692e','admin_model_change','Admin Change Detected','Product \'Custom Waterproof Gold Stickers Dubai & UAE\' was created.','superadmin','admin','Product','PR-CW-001','read','2025-09-01 12:13:47.804341'),
('eac7ca3e-2f5f-4fae-b3ac-7d04e4b22642','admin_model_change','Admin Change Detected','Product \'Promotional Metal Name Plate – Office & Events\' was deleted.','superadmin','admin','Product','CA-PM-001','read','2025-08-30 07:32:43.046432'),
('eb343c60-bf94-4abb-ab07-ff9b0adbc027','admin_model_change','Admin Change Detected','Product \'Vertical Non-Woven Bags Printing in Dubai  Custom Reusable Tote Bags & Branded Eco Bags UAE\' was updated.','superadmin','admin','Product','EV-VN-001','read','2025-09-04 12:03:12.220429'),
('eba90413-1dc9-472d-81a9-9c3d890baaa1','admin_model_change','Admin Change Detected','Product \'Wooden USB Flash Drives 4GB, 8GB, 16GB, 32GB, 64GB\' was created.','superadmin','admin','Product','CO-WU-001','read','2025-09-04 07:54:01.431680'),
('ec0626e2-c5d0-442e-9f9c-d4ddf93b3deb','admin_model_change','Admin Change Detected','Product \'Logo Printed Notebook & Pen Gift Combo\' was updated.','superadmin','admin','Product','GI-LP-001','read','2025-09-04 10:50:07.132808'),
('ec49d2d0-f794-4e7b-89b8-5eaf5b7b3715','admin_model_change','Admin Change Detected','Product \'Custom Corporate Brochures & Booklets Dubai & UAE\' was created.','superadmin','admin','Product','PR-CC-001','read','2025-09-04 07:52:14.584824'),
('ec799d65-6950-4c32-b5ef-fe58b43265b7','admin_model_change','Admin Change Detected','Subcategory \'Business Cards\' was created.','superadmin','admin','SubCategory','P&MM-BUSINESS-001','read','2025-08-29 07:07:27.773880'),
('ec9b7185-9642-4b05-b9e6-15bdb330b605','admin_model_change','Admin Change Detected','Subcategory \'Kids\' Apparel\' was updated.','superadmin','admin','SubCategory','CAA-KIDS\'-001','read','2025-09-09 08:08:14.665522'),
('ecbece20-c3fa-46e8-a9c1-3d1d852f8867','admin_model_change','Admin Change Detected','Product \'Custom Logo Wooden Pencil & Ruler Gift Set\' was created.','superadmin','admin','Product','WO-CL-001','read','2025-08-30 07:28:27.233121'),
('ee0de433-4833-4061-9a08-60a881833118','admin_model_change','Admin Change Detected','Product \'Printed ID Card Holder with Lanyard\' was deleted.','superadmin','admin','Product','CA-PICHWL-001','read','2025-09-01 06:10:02.214323'),
('eec0d7f6-b941-4000-ae15-0ca654ac6691','admin_model_change','Admin Change Detected','Product \'Round Bamboo Keyring with Logo Engraving\' was deleted.','superadmin','admin','Product','BR-RB-001','read','2025-09-01 06:10:02.265851'),
('ef3015d4-07dc-4100-b38a-6f7d7b428389','admin_model_change','Admin Change Detected','Product \'NEXTT LEVEL Recycled Polo T-Shirts\' was deleted.','superadmin','admin','Product','T-NL-001','read','2025-09-13 10:39:48.925266'),
('efc45aa9-bae0-45b4-a63a-17cee8bbed08','admin_model_change','Admin Change Detected','Category \'Technology\' was updated.','superadmin','admin','Category','T-1','read','2025-08-29 11:03:32.263251'),
('efe66d0b-1c46-4cdf-a336-8ffd8403a3fa','admin_model_change','Admin Change Detected','Product \'Black Ceramic Mugs with Printable Area | Custom Coffee Mugs Dubai\' was created.','superadmin','admin','Product','CE-BC-001','read','2025-09-01 10:02:44.928455'),
('efea124d-3c70-4db1-8e11-43dc12fbf3b5','admin_model_change','Admin Change Detected','Product \'Standard Table Flags\' was created.','superadmin','admin','Product','FL-ST-001','read','2025-09-11 06:21:40.722743'),
('f0d156a6-c7ef-4d7a-8b3b-4a2bf358b25a','admin_model_change','Admin Change Detected','Product \'Promotional Logo Keyrings for Corporate Branding\' was created.','superadmin','admin','Product','BR-PL-001','read','2025-08-30 05:16:20.953587'),
('f0dcbcea-6815-4bed-992c-4fdd3506cf97','admin_model_change','Admin Change Detected','Product \'Leather Portfolio with Zipper & Calculator\' was deleted.','superadmin','admin','Product','NO-LPWZC-001','read','2025-09-01 06:10:02.109064'),
('f1916e29-2d4a-40c2-8138-fbd15955fda7','admin_model_change','Admin Change Detected','Subcategory \'Ceramic Mugs\' was updated.','superadmin','admin','SubCategory','D-CERAMIC-001','read','2025-09-09 11:28:27.819157'),
('f2210d3f-7694-4582-8837-d399efd3016e','admin_model_change','Admin Change Detected','New order \'OAB-AB-001\' was placed.','superadmin','admin','Orders','OAB-AB-001','read','2025-09-03 18:24:28.539233'),
('f236b055-5bb3-480b-ad15-5b4c944843e3','admin_model_change','Admin Change Detected','Subcategory \'Notebooks & Writing Pads\' was created.','superadmin','admin','SubCategory','O&S-NOTEBOOKS-001','read','2025-08-29 06:57:55.766287'),
('f2c45e4a-f7bf-41ac-91e4-cc3fa7fb81a3','admin_model_change','Admin Change Detected','Product \'Affordable plastic ballpoint pens\' was updated.','superadmin','admin','Product','PL-AP-001','read','2025-09-04 10:24:45.345411'),
('f2f661f7-b381-4a9c-bee9-48538b537dda','admin_model_change','Admin Change Detected','Product \'UAE Flag Knitted Scarf – 17x155 cm\' was created.','superadmin','admin','Product','AC-UFKS1C-001','read','2025-08-29 10:32:24.067843'),
('f32ff85e-c809-4785-b5d2-e19355043185','admin_model_change','Admin Change Detected','Product \'Hardcover Promotional Notebooks in Multiple Colors\' was deleted.','superadmin','admin','Product','NO-HPNIMC-001','read','2025-09-01 06:10:02.090005'),
('f3d1f30c-4164-4a98-a3e3-6be15c4676bd','admin_model_change','Admin Change Detected','Product \'Personalized Eco-Friendly Gift Set GS-036 in Black Cardboard Box\' was created.','superadmin','admin','Product','BR-PE-001','read','2025-09-01 08:29:05.871237'),
('f3fa16c3-0432-436a-a595-d60f46664a50','admin_model_change','Admin Change Detected','Product \'White Leather Luggage Tag\' was deleted.','superadmin','admin','Product','TR-WLLT-001','read','2025-09-01 06:10:02.372869'),
('f4c0e213-422e-44d5-8a14-219ec3ad2151','admin_model_change','Admin Change Detected','Product \'Custom Corporate Diaries & Notebooks Dubai & UAE\' was created.','superadmin','admin','Product','EX-CC-001','read','2025-09-04 08:09:59.934308'),
('f50cbf33-6600-48cb-960b-1f089e05400e','admin_model_change','Admin Change Detected','Product \'Round Metal & Wooden Keychain\' was deleted.','superadmin','admin','Product','BR-RMWK-001','read','2025-08-30 07:23:08.314094'),
('f68ac361-303b-40de-9407-d0674df8cde3','admin_model_change','Admin Change Detected','Product \'Custom Branded Notebooks\' was created.','superadmin','admin','Product','NO-CB-001','read','2025-09-01 11:45:09.057654'),
('f7679836-88f7-4d72-90a0-e09b1d85ec07','admin_model_change','Admin Change Detected','Product \'Custom Lanyards with Hook, Safety Lock & Buckle 20mm\' was created.','superadmin','admin','Product','EV-CL-001','read','2025-09-01 10:10:07.060446'),
('f76b5a4b-7b78-46e6-9185-0713540728a0','login','Admin Logged In','abdullah just logged in.','superadmin','admin','Admin','','read','2025-09-01 11:41:06.713019'),
('f7b1af9d-ca36-4a7d-9eee-ffa0f7a58148','admin_model_change','Admin Change Detected','Product \'rPET Transparent Bottles 800ml with Stainless Steel Lid & Carry Handle | Eco-Friendly Water Bottles Dubai\' was created.','superadmin','admin','Product','SP-RT-001','read','2025-09-01 11:35:38.969889'),
('f85d883d-fd7e-4b32-a779-b06fc16c9cc3','admin_model_change','Admin Change Detected','Subcategory \'Decorative & Promotional\' was updated.','superadmin','admin','SubCategory','EG&S-DECORATIVE-001','read','2025-09-09 14:05:51.009835'),
('f8993845-f499-4317-982a-ff67a6260934','admin_model_change','Admin Change Detected','Product \'Reusable BPA-Free Plastic Water Bottle with Handle\' was deleted.','superadmin','admin','Product','EC-RBFPWBWH-001','read','2025-09-01 06:10:02.255981'),
('f9652b3b-90c3-4af6-a26a-395f2f07e817','admin_model_change','Admin Change Detected','Product \'Fabric Backdrop Seamless\' was created.','superadmin','admin','Product','BA-FB-002','read','2025-09-11 07:34:27.991071'),
('faabeaf8-5d42-49d6-90bf-ae2706a3fc05','admin_model_change','Admin Change Detected','Product \'Wooden USB Flash Drives 4GB, 8GB, 16GB, 32GB, 64GB\' was updated.','superadmin','admin','Product','CO-WU-001','read','2025-09-04 11:43:50.631432'),
('fac18bb7-36ba-4849-a4e3-0d759ef07c25','admin_model_change','Admin Change Detected','Product \'Corporate Stylus Writing Pen – Metal Grip Design\' was deleted.','superadmin','admin','Product','ME-CS-001','read','2025-09-01 06:10:01.871015'),
('fad8b5c5-fb6d-41d4-b148-3479c6f7f8e0','admin_model_change','Admin Change Detected','Category \'Banner & Flags\' was created.','superadmin','admin','Category','B&F-1','read','2025-09-03 06:52:48.570353'),
('fc95a95d-c48d-4631-81f2-fcbbcf3883b0','admin_model_change','Admin Change Detected','Subcategory \'Sports Bottles\' was updated.','superadmin','admin','SubCategory','D-SPORTS-001','read','2025-09-09 12:42:35.539118'),
('fcefee9d-9e5c-4f9d-842e-9bc7722dbd86','admin_model_change','Admin Change Detected','Product \'Custom Logo Portable Wireless Speaker\' was created.','superadmin','admin','Product','CO-CL-001','read','2025-08-30 07:30:23.301446'),
('fd9d682d-f99a-420a-96cf-77a1be76dd9e','admin_model_change','Admin Change Detected','Product \'Steel Business Card Holder\' was created.','superadmin','admin','Product','CA-SB-001','read','2025-09-01 11:03:33.063890'),
('fdbbd977-e632-47f3-bc9e-6da9b1433e59','admin_model_change','Admin Change Detected','Blog \'Ikrash ne kiya theek kiya????\' was published.','superadmin','admin','Blog','ikrashnekiyatheekk-ff2ae602e9','read','2025-09-18 13:29:19.975846'),
('fe477476-7a79-415e-8f33-ff59d74ff3ea','admin_model_change','Admin Change Detected','Product \'Slim Fabric Wireless Charger for Corporate Gifting\' was deleted.','superadmin','admin','Product','CA-SF-001','read','2025-09-01 06:10:02.305687'),
('fecd2688-fdb2-4dc4-9e3f-68daed0cf784','admin_model_change','Admin Change Detected','Product \'Eco-friendly wooden pencil sets\' was updated.','superadmin','admin','Product','WO-EF-001','read','2025-09-04 10:43:03.219410'),
('fee26b14-984a-472f-ad76-3d0545e35e4f','admin_model_change','Admin Change Detected','Product \'Ceramic Mugs with Lid & Cork Base 385ml | Custom Coffee Mugs Dubai\' was updated.','superadmin','admin','Product','CE-CM-001','read','2025-09-04 10:53:19.072379');
/*!40000 ALTER TABLE `admin_backend_final_notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_orderdelivery`
--

DROP TABLE IF EXISTS `admin_backend_final_orderdelivery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_orderdelivery` (
  `delivery_id` varchar(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(254) DEFAULT NULL,
  `phone` varchar(20) NOT NULL,
  `street_address` longtext NOT NULL,
  `city` varchar(100) NOT NULL,
  `zip_code` varchar(20) NOT NULL,
  `instructions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`instructions`)),
  `created_at` datetime(6) NOT NULL,
  `order_id` varchar(100) NOT NULL,
  PRIMARY KEY (`delivery_id`),
  UNIQUE KEY `order_id` (`order_id`),
  KEY `admin_backend_final_orderdelivery_city_d3fb3144` (`city`),
  KEY `admin_backend_final_orderdelivery_zip_code_a8414adc` (`zip_code`),
  CONSTRAINT `admin_backend_final__order_id_d1993bb7_fk_admin_bac` FOREIGN KEY (`order_id`) REFERENCES `admin_backend_final_orders` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_orderdelivery`
--

LOCK TABLES `admin_backend_final_orderdelivery` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_orderdelivery` DISABLE KEYS */;
INSERT INTO `admin_backend_final_orderdelivery` VALUES
('08493b5d-2b5c-44cd-aef7-c1d25ea269b4','asdfg','madarauchihay457@gmail.com','egfsdg','dfgdf','dfsgsd','1900','[\"dgfdsfg\"]','2025-09-10 08:19:51.859489','OAS-MA-001'),
('2ce3987c-1a1c-47db-97b0-248366e71c96','Akrash Noman','itgprogaming42@gmail.com','03000250425','MCS Cadets Hostel, Lalazar','Rawalpindi','46000','[]','2025-09-02 15:53:35.368387','OAK-IT-001'),
('c9802fdf-1b51-4976-8217-efcaf5ad14b8','Hshsn','Aaimn@gmail.com','03436846019','Jusnje','Jjjj','6383','[\"Hhh\"]','2025-09-08 11:23:21.895969','OHS-AA-001'),
('d08a6550-c3ca-4612-895a-507966b812f3','Abdullah .','abd03008670792@gmail.com','03146276829','128E Gulshan E Nisar ryk','Rahim yar khan','64200','[\"jn\"]','2025-09-03 18:24:28.542059','OAB-AB-001'),
('ddab235b-3d40-4154-8d00-3c5c1de9d580','tara aba ','tun_aamb_lanay@gmail.com','1234567890','6th road , royal palaza','Rawalpindi','48000','[\"lay layyyyyy\"]','2025-09-17 07:56:58.593762','OTA-TU-001'),
('de9c280c-89b0-4775-a82f-66bdd011a315','Check','checkandtest123@gmail.com','03123456789','Check Street, Development','Developer City','12300','[]','2025-09-11 12:22:29.353565','OCH-CH-001'),
('edebf0fc-5450-4752-b2e8-434a0d1cdaaf','Yasir Mehrban','printdesigndxb@gmail.com','0545396249','Shop 7, Al Madani Building, Al Nakhal Road, Niaf, Diera, Dubai','Islamabad','44000','[]','2025-09-05 13:12:40.106850','OYA-PR-001');
/*!40000 ALTER TABLE `admin_backend_final_orderdelivery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_orderitem`
--

DROP TABLE IF EXISTS `admin_backend_final_orderitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_orderitem` (
  `item_id` varchar(100) NOT NULL,
  `quantity` int(10) unsigned NOT NULL CHECK (`quantity` >= 0),
  `unit_price` decimal(10,2) NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `selected_size` varchar(50) DEFAULT NULL,
  `selected_attributes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`selected_attributes`)),
  `selected_attributes_human` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`selected_attributes_human`)),
  `variant_signature` varchar(255) DEFAULT NULL,
  `attributes_price_delta` decimal(10,2) NOT NULL,
  `price_breakdown` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`price_breakdown`)),
  `created_at` datetime(6) NOT NULL,
  `order_id` varchar(100) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`item_id`),
  KEY `admin_backend_final__order_id_69a071b0_fk_admin_bac` (`order_id`),
  KEY `admin_backend_final__product_id_ddfc9244_fk_admin_bac` (`product_id`),
  CONSTRAINT `admin_backend_final__order_id_69a071b0_fk_admin_bac` FOREIGN KEY (`order_id`) REFERENCES `admin_backend_final_orders` (`order_id`),
  CONSTRAINT `admin_backend_final__product_id_ddfc9244_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_orderitem`
--

LOCK TABLES `admin_backend_final_orderitem` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_orderitem` DISABLE KEYS */;
INSERT INTO `admin_backend_final_orderitem` VALUES
('0190f9ee-e084-479e-8e1c-eb298ad7dd9c',500,0.80,400.00,'','{}','[]','',0.00,'{\"base_price\": \"0.8\", \"attributes_delta\": \"0\", \"unit_price\": \"0.8\", \"line_total\": \"400\", \"selected_size\": \"\", \"selected_attributes_human\": []}','2025-09-05 13:12:40.104184','OYA-PR-001','PR-CO-001'),
('14927003-030e-4892-8b8e-507c2e44cd66',5,120.00,600.00,'','{}','[]','',0.00,'{\"base_price\": \"120\", \"attributes_delta\": \"0\", \"unit_price\": \"120\", \"line_total\": \"600\", \"selected_size\": \"\", \"selected_attributes_human\": []}','2025-09-05 13:12:40.105314','OYA-PR-001','PR-CP-002'),
('4c77d731-7b45-4c3f-8f96-8738334c3a2e',3,0.00,0.00,'','{}','[]','',0.00,'{\"base_price\": \"0\", \"attributes_delta\": \"0\", \"unit_price\": \"0\", \"line_total\": \"0\", \"selected_size\": \"\", \"selected_attributes_human\": []}','2025-09-08 11:23:21.895297','OHS-AA-001','PR-CH-001'),
('4de2a972-290c-4f9a-8b3a-a887728fe3bf',11,0.00,0.00,'','{}','[]','',0.00,'{\"base_price\": \"0\", \"attributes_delta\": \"0\", \"unit_price\": \"0\", \"line_total\": \"0\", \"selected_size\": \"\", \"selected_attributes_human\": []}','2025-09-17 07:56:58.593123','OTA-TU-001','TA-SG-001'),
('588ea951-32e5-42c9-9779-f8a587444231',6,0.00,0.00,'','{}','[]','',0.00,'{\"base_price\": \"0\", \"attributes_delta\": \"0\", \"unit_price\": \"0\", \"line_total\": \"0\", \"selected_size\": \"\", \"selected_attributes_human\": []}','2025-09-08 11:23:21.892887','OHS-AA-001','PR-CC-002');
/*!40000 ALTER TABLE `admin_backend_final_orderitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_orders`
--

DROP TABLE IF EXISTS `admin_backend_final_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_orders` (
  `order_id` varchar(100) NOT NULL,
  `user_name` varchar(255) NOT NULL,
  `order_date` datetime(6) NOT NULL,
  `status` varchar(50) NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `notes` longtext DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `device_uuid` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `admin_backend_final_orders_status_40487d19` (`status`),
  KEY `admin_backend_final_orders_device_uuid_84ae2935` (`device_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_orders`
--

LOCK TABLES `admin_backend_final_orders` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_orders` DISABLE KEYS */;
INSERT INTO `admin_backend_final_orders` VALUES
('OAB-AB-001','Abdullah .','2025-09-03 18:24:28.538291','pending',150.00,'Order from checkout page','2025-09-03 18:24:28.538584','2025-09-03 18:24:28.538593','e18cad4c-a970-49e0-b166-27d1bf4435a2'),
('OAK-IT-001','Akrash Noman','2025-09-02 15:53:35.364662','completed',150.00,'Order from checkout page','2025-09-02 15:53:35.364952','2025-09-02 16:16:31.735521',NULL),
('OAS-MA-001','asdfg','2025-09-10 08:19:51.855456','cancelled',150.00,'Order from checkout page','2025-09-10 08:19:51.856058','2025-09-10 08:22:58.919243','468636ba-b660-4839-a673-a3368f74b976'),
('OCH-CH-001','Check','2025-09-11 12:22:29.349467','pending',150.00,'Order from checkout page','2025-09-11 12:22:29.349850','2025-09-11 12:22:29.349859','e5a03b72-c4fe-4f39-9252-126dbce355e9'),
('OHS-AA-001','Hshsn','2025-09-08 11:23:21.887054','processing',150.00,'Order from checkout page','2025-09-08 11:23:21.887289','2025-09-09 06:31:15.538010','2060d0cf-f34f-4309-a524-e9f69933913b'),
('OTA-TU-001','tara aba ','2025-09-17 07:56:58.588907','pending',150.00,'Order from checkout page','2025-09-17 07:56:58.589331','2025-09-17 07:56:58.589341','8ce887f1-dcc6-4d2e-9e7b-86a692349eee'),
('OYA-PR-001','Yasir Mehrban','2025-09-05 13:12:40.100993','Pending',1650.00,'','2025-09-05 13:12:40.101345','2025-09-05 13:12:40.101354',NULL);
/*!40000 ALTER TABLE `admin_backend_final_orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_product`
--

DROP TABLE IF EXISTS `admin_backend_final_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_product` (
  `product_id` varchar(100) NOT NULL,
  `title` varchar(511) NOT NULL,
  `description` longtext NOT NULL,
  `brand` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `discounted_price` decimal(10,2) NOT NULL,
  `tax_rate` double NOT NULL,
  `price_calculator` longtext NOT NULL,
  `video_url` varchar(200) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_by_type` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  `rating` double NOT NULL,
  `rating_count` int(10) unsigned NOT NULL CHECK (`rating_count` >= 0),
  `long_description` longtext NOT NULL,
  PRIMARY KEY (`product_id`),
  KEY `admin_backend_final_product_title_34c2d8ca` (`title`),
  KEY `admin_backend_final_product_status_33c73c06` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_product`
--

LOCK TABLES `admin_backend_final_product` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_product` DISABLE KEYS */;
INSERT INTO `admin_backend_final_product` VALUES
('AC-CC-001','Comfortable Cotton Face Mask for Children','fffffffdsaasc','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:08:19.088827','2025-09-01 08:08:19.088841',53,0,0,''),
('AC-CP-001','Custom Printed Fabric Wristbands Dubai & UAE','erftgyhju','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:21:39.578028','2025-09-01 08:21:39.578046',52,0,0,''),
('AC-EU-001','Elegant UAE Knit Scarf for Corporate Gifting','sderfgt','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:09:50.064897','2025-09-01 08:09:50.064913',54,0,0,''),
('AC-WA-001','Waterproof Adjustable Adhesive Event Wristbands Dubai & UAE','sdfg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:23:31.489392','2025-09-01 08:23:31.489407',51,0,0,''),
('BA-BA-001','Business Anti-Theft Backpack with USB Charger','<p dir=\"ltr\">Designed for the fast-paced urban lifestyle of Dubai, this anti-theft backpack works modern style with smart security. Professionals, students, and brands all choose it because it offers safety, tech convenience, and a sleek design all in one.</p>\n<h2 dir=\"ltr\"><span>Key features</span><b></b></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong></span><span><strong> </strong>Sturdy Oxford fabric with layers that are reinforced and resistant to slashes.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong></span><span><strong> </strong>Perfect for security-oriented branding, with 2-3 working days, or delivery on the same day.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design: </strong></span><span>A sleek, minimal design that conceals storage compartments USB charger port and a laptop-sized padded sleeve.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for: </strong></span><span>Corporate gifts, technology events, promotional travel, as well as onboarding of employees.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability: </strong></span><span>It is scratch resistant, and theft-proof design with a long-lasting logo embroidery or printing.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"></p>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span> </span><span>UV printing applies full-color artwork directly onto the front panel of the anti-theft backpack. It delivers sharp, fade-resistant visuals that maintain a professional look, perfect for visible branding without compromising the bag&rsquo;s sleek design.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>UV DTF Printing:</strong></span><strong> </strong><span>UV DTF printing uses a UV-cured transfer film to wrap complex, multi-color designs around pockets or side panels. It offers high-detail branding on multiple angles of the bag, adding depth without interfering with the anti-theft features.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Embroidery:</strong><span> Embroidery stitches your logo into the fabric, creating a textured, long-lasting finish. It&rsquo;s ideal for subtle yet premium branding that complements the backpack&rsquo;s durable and professional build.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>Contact us today to customize your Anti-Theft Backpack &ndash; fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:14:41.087922','2025-09-04 12:07:59.604832',101,0,0,''),
('BA-EC-001','Executive Conference Laptop Bag','<p>This executive laptop backpack is a perfect combination of everyday functionality and stylish style that is perfect to fit into Dubai\'s cutting-edge corporate environment. This laptop bag for men and laptop bag for women offers style, durability, and smart storage, an ideal choice for the contemporary workplace.</p>\n<h2 dir=\"ltr\"><span>Key features</span><b></b></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material:</strong><span><strong> </strong>Polyester of the highest quality, PU leather or nylon with laptop compartments that are padded.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use:</strong><span> Ideal for high-end corporate branding and corporate gifts in 2-3 business days or delivery on the same day.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design:</strong><span><strong> </strong>Elegant, multiple zip pockets with shoulder straps, as well as well-organized interiors.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Best for:</strong><span> </span><span>Executives from business Welcome kits for staff, conference, and customer gratitude.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability:</strong><span> Built for day-to-day use, with reinforced handles, water resistance and personal branding.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"></p>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span> </span><span>UV printing delivers crisp, full-color artwork directly onto synthetic leather or nylon panels of the executive bag. It offers a sleek, polished finish that enhances the professional appeal of the product, ideal for logos that need to stand out in high-end environments.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing:</strong><span> </span><span>&nbsp;UV DTF printing uses a transfer film to apply intricate, multi-color designs across the bag&rsquo;s surface. This technique is perfect for detailed brand elements, ensuring a vibrant and durable finish on structured panels.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Embroidery:</strong><span> </span><span>Embroidery reinforces your brand with a stitched logo that adds texture and class. This method is long-lasting, wear-resistant, and elevates the executive look of the bag, making it ideal for premium gifts and corporate use.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Executive Laptop Bag,&nbsp; fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:24:50.888188','2025-09-04 12:09:47.088632',102,0,0,''),
('BA-EC-002','Eco Cotton Tote Bag','hhhhh','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:31:13.141290','2025-09-01 06:31:13.141302',103,0,0,''),
('BA-FB-001','Fabric Banners','<p>ghbh</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 07:23:36.083210','2025-09-11 07:23:36.083230',133,0,0,''),
('BA-FB-002','Fabric Backdrop Seamless','<p>ghihijk</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 07:34:27.990642','2025-09-11 07:34:27.990654',134,0,0,''),
('BA-MC-001','Multi-Color Promotional Drawstring Bags UAE','hgfcg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:22:17.250621','2025-09-01 06:22:17.250635',104,0,0,''),
('BR-CA-001','Custom Anti Stress Balls','ghyy','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:38:07.644054','2025-09-01 08:38:07.644067',126,0,0,''),
('BR-CM-001','Custom Metal Keychain with Strap','ghhyt','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:20:03.112496','2025-09-01 08:20:03.112508',127,0,0,''),
('BR-CP-001','Cork PU Keychains with 32mm Metal Flat Key Ring','hjk','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:13:41.678933','2025-09-01 08:13:41.678945',128,0,0,''),
('BR-CR-001','Custom Round Bamboo & Metal Keychains 32mm','mm','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:34:53.188224','2025-09-01 09:04:32.049578',129,0,0,''),
('BR-PE-001','Personalized Eco-Friendly Gift Set GS-036 in Black Cardboard Box','hgttyy','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:29:05.870705','2025-09-01 08:29:05.870718',130,0,0,''),
('BR-PG-001','Promotional Gift Sets in Black Cardboard Gift Box GS-029','hfggggggh','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:24:54.963754','2025-09-01 08:24:54.963766',131,0,0,''),
('BR-PP-001','Personalized Promotional Badges Dubai & UAE','<p>sgdsgfd</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:59:19.765726','2025-09-04 07:59:19.765737',125,0,0,''),
('CA-2T-001','2025 Table Calendars with Plantable Seeds','fhnnt','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:05:36.351840','2025-09-01 11:05:36.351851',38,0,0,''),
('CA-AN-001','Aluminum Name Plates','ghjiu','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:26:58.721614','2025-09-01 11:26:58.721630',39,4.5,230,''),
('CA-BC-001','Business Card Holder with RFID Protection PREMIO','ghfh','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:37:38.753656','2025-09-01 11:01:10.782535',40,0,0,''),
('CA-CO-001','Custom Office Desk Accessories & Corporate Gifts Dubai & UAE','<p>uhjkjhk</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:13:38.294470','2025-09-04 08:13:38.294487',37,0,0,''),
('CA-FC-001','Foldable Cork + PU Mousepad with Mobile & Pen Holder','jmhfrhm','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:13:10.349068','2025-09-01 11:13:10.349089',41,4.5,210,''),
('CA-FW-001','Fast Wireless Charging Mousepad 15W with Foldable Design & Type-C Branded Tech Accessories Dubai UAE','<p>A sleek, modern accessory for your desk that charges devices without wires. Great for gifts,work, tech giveaways, or office desks. Give your brand the power to innovate easily. This wireless charger also functions as a compact charging station for everyday convenience.</p>\n<h2 dir=\"ltr\"><span>Main Features:</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material:</strong><span> </span><span>Comes in finishes like smooth plastic, bamboo, or soft-touch fabric.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong> </span><span>It\'s perfect for modern logos and accessories for desks. 2 working days or the same day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design: </strong><span>Simple, flat design featuring LED indicators and an expansive branding surface.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for:</strong></span><span><strong> </strong>Corporate gifts promotional tech as well as home office and gifts for retail stores.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability:</strong> </span><span>It is heat-resistant and wear-resistant with a long-lasting imprint using the UV process or pad printing.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing): </strong><span>UV printing applies vivid, full-color artwork directly onto the flat surface of the charging pad, whether plastic, bamboo, or fabric. This technique ensures a sharp, durable finish that enhances your logo\'s visibility while withstanding daily use on desks or nightstands.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Laser Engraving:</strong><span> Laser engraving permanently etches your logo into wooden or bamboo charging pad surfaces, offering a natural, minimal look. It&rsquo;s perfect for eco-conscious branding or premium gifts that require a refined and long-lasting impression.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Wireless charging pad, fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:08:15.406405','2025-09-04 11:53:58.365638',42,0,0,''),
('CA-IC-001','ID card holder with a lanyard','httyh','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:34:30.745721','2025-09-01 11:34:30.745742',43,0,0,''),
('CA-MN-001','Metal Name Badges in Gold & Silver Plated','hhgtg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:18:35.740155','2025-09-01 11:20:26.638299',44,0,0,''),
('CA-PR-001','Promotional Retractable ID Badge Holder','ukfvgu','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:36:48.038064','2025-09-01 11:36:48.038075',45,0,0,''),
('CA-PS-001','Personalized Soft Mesh Caps for Corporate Gifts','hgfdr','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-02 07:54:11.355446','2025-09-02 07:54:11.355465',50,0,0,''),
('CA-RA-001','Reusable Acrylic Name Badges','hmmbk','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:24:13.345748','2025-09-01 11:24:13.345767',46,0,0,''),
('CA-SB-001','Steel Business Card Holder','trdhey','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:03:33.063189','2025-09-01 11:03:33.063256',47,0,0,''),
('CE-BC-001','Black Ceramic Mugs with Printable Area | Custom Coffee Mugs Dubai','A sleek and versatile promotional gift, these black ceramic mugs with printable area are designed to highlight your logo or artwork with maximum contrast. The smooth black exterior combined with a white printable panel makes them perfect for full-color branding. Popular across Dubai and the UAE, these mugs work well as coffee mugs, tea mugs, or corporate giveaways, ensuring your brand stands out in every sip.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:02:44.927810','2025-09-01 10:02:44.927823',61,4.5,0,''),
('CE-BS-001','Bamboo & Stainless Steel Coffee Travel Mug with Handle and Lid | Eco-Friendly Travel Mug Dubai','A premium eco-friendly promotional gift, this bamboo and stainless steel coffee travel mug with handle and lid combines durability with natural style. Perfect for branding campaigns, corporate gifts, and wellness promotions in Dubai and across the UAE, it keeps beverages hot or cold while showcasing your logo on sustainable bamboo. With its ergonomic handle and secure lid, this travel mug is a practical and stylish choice for daily use.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:18:56.285303','2025-09-01 08:18:56.285317',62,5,0,''),
('CE-CC-001','Ceramic Coffee Mugs with Bamboo Handle & Lid 380ml | Custom Coffee Mugs Dubai','<p>A vibrant, eye-catching promotional gift that boosts brand recall by matching your corporate colors ideal for events, giveaways, and everyday use. This ceramic mug also functions perfectly as a tea mug or general-purpose mug, making it a versatile branding tool.</p>\n<h2 dir=\"ltr\"><span>Key features:</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong></span><span><strong> </strong>Solid ceramic in a variety of colors (including black, red, blue, and green).</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong></span><span><strong> </strong>Excellent for personalizing promotional gifts or brand giveaways that take 2-3 days to deliver or delivery on the same day.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design:</strong></span><strong> </strong><span><strong>&nbsp;</strong>11oz with striking color contrasts and vivid full-color prints.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Perfect for:</strong><span> Cafes, Events corporate giveaways, events, unique merchandise.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability:</strong></span><strong> </strong><span>Dishwasher and microwave protected with a long-lasting, durable customisation.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing:</strong><span> </span><span>UV DTF printing uses a UV-cured transfer film to apply vibrant, full-color graphics around the exterior of the mug while preserving the colored interior. This creates a bold contrast and eye-catching finish, making your branding pop without compromising the mug&rsquo;s visual balance.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> </span><span>Silk screen printing applies a single solid color onto the mug&rsquo;s outer surface using a stencil and mesh screen. It&rsquo;s ideal for simple logos or text and works beautifully with the mug&rsquo;s inner color, resulting in a clean, coordinated design that feels both elegant and purposeful.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>A colorful, practical mug that will help your brand stand out whether used as a ceramic mug, tea mug, or stylish everyday drinkware.</span></p>\n<p dir=\"ltr\"><span>Contact us today to customize your Ceramic color Mug (11oz), fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:55:48.133082','2025-09-04 10:56:31.467390',11,4.5,0,''),
('CE-CE-001','Curve Edge Mugs | Custom Ceramic Coffee & Tea Mug Dubai','A modern twist on classic drinkware, these curve edge mugs are perfect for everyday use, gifting, and brand promotions. Their unique curved design adds elegance while providing a comfortable grip, making them ideal as coffee mugs, tea mugs, or branded promotional mugs. Widely used across Dubai and the UAE, they offer a stylish way to keep your brand visible at offices, cafés, events, and homes.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:22:50.533147','2025-09-01 08:23:54.296098',12,4.5,0,''),
('CE-CG-001','Clear Glass Mug with Bamboo Lid and Spoon | Custom Coffee & Tea Mug Dubai','A modern and eco-friendly promotional gift, this clear glass mug with bamboo lid and spoon blends style with functionality. Ideal for corporate giveaways, cafés, and wellness campaigns, it works perfectly as a coffee mug or tea mug while offering a natural bamboo touch. Popular across Dubai and the UAE, this mug is both practical and elegant, making it a thoughtful gift for employees, clients, or event attendees.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:07:35.339969','2025-09-01 08:07:35.339983',13,4,0,''),
('CE-CM-001','Ceramic Mugs with Lid & Cork Base 385ml | Custom Coffee Mugs Dubai','<p dir=\"ltr\"><span>A popular promotional gift suitable for corporate clients, welcome kits, and events, with a large surface area for effective branding. Whether used as a ceramic cup or ceramic mug, this ceramic mug makes a thoughtful corporate gift in Dubai and across the UAE. This versatile item can also be used as a ceramic cup, ceramic mug, making it an ideal everyday mug for all types of recipients.</span></p>\n<h2 dir=\"ltr\"><strong>Key features</strong></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material:</strong><span><strong> </strong>Ceramic of high-end quality with a polished, shiny surface.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use: </strong><span>Great for giveaways, branding or corporate gifts with up to 3 days of working time or next-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design:</strong> </span><span>Standard 11oz featuring vibrant full-color print and the most comfortable grip.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for:</strong> </span><span>Office spaces, special events cafes, promotions and gift packs.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability:</strong><span> Microwave-safe and dishwasher-friendly with long-lasting, fade-resistant prints.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><strong>Branding Methods</strong></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing:</strong><span> </span><span>UV DTF (Direct-to-Film) printing uses a UV-cured transfer film to wrap the entire 11oz ceramic mug in vivid, full-color artwork. This method delivers a smooth, glossy finish that resists fading, scratching, and daily wear, perfect for high-impact branding on the mug&rsquo;s entire surface.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> Silk screen printing applies one solid ink color onto the exterior of the ceramic mug using a stencil and mesh screen. Ideal for clean, minimalist logos or bold text, this method is a great option for simple, large-volume branding campaigns with a sleek finish.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Sublimation Printing:</strong><span> Sublimation printing infuses your design directly into the mug&rsquo;s glaze using heat and pressure. On the ceramic mug, this produces a vibrant, full-wrap image that&rsquo;s microwave-safe, dishwasher-friendly, and highly durable, making it perfect for everyday use with lasting brand visibility.</span><span><br></span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;Contact us today to customize your Ceramic Mug (11oz), fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 09:32:14.746173','2025-09-04 10:53:19.070512',14,4.5,0,''),
('CE-GB-001','German Beer Mugs | Custom Branded Beer Mugs & Glassware Dubai','German Beer Mugs | Custom Branded Beer Mugs & Glassware Dubai','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 09:04:00.889914','2025-09-01 09:04:00.999034',63,4.5,0,''),
('CE-GC-001','Gold Ceramic Mugs | Custom Metallic Coffee & Tea Mugs Dubai','A premium and eye-catching promotional gift, these gold ceramic mugs stand out with their metallic finish, making them perfect for luxury branding, corporate giveaways, and special events. Whether used as coffee mugs, tea mugs, or branded gift mugs, they bring sophistication and elegance to your campaigns. Popular across Dubai and the UAE, these mugs ensure your brand shines in offices, cafés, and corporate events.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 09:12:16.130003','2025-09-01 09:12:16.130015',15,5,0,''),
('CE-LM-001','Love Mug Sets | Custom Couple Mugs & Gift Sets Dubai','A charming and thoughtful promotional or personal gift, these love mug sets are designed for couples, special occasions, and branding campaigns. With their unique design and matching style, they make a memorable choice for Valentine’s Day, weddings, anniversaries, or corporate giveaways. Popular across Dubai and the UAE, these sets combine practicality with sentiment, ensuring your brand or message is cherished every day.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:13:38.504855','2025-09-01 10:13:38.504867',64,5,0,''),
('CE-MC-001','Magic Color Changing Mugs | Custom Heat Sensitive Mug Dubai','A fun and eye-catching promotional gift, these magic color changing mugs transform with heat to reveal hidden designs, making them perfect for brand reveals, special events, and corporate giveaways. Whether used as a magic mug or custom heat-sensitive mug, this product is a unique way to keep your brand memorable across Dubai and the UAE. When filled with hot liquid, the mug changes color and showcases your logo or artwork, leaving a lasting impression.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 07:59:30.652009','2025-09-01 07:59:30.652027',65,4.5,0,''),
('CE-PC-001','Personalized Coffee Mugs | Custom Printed Mugs Dubai & UAE','A best-selling promotional gift, these personalized coffee mugs are perfect for creating memorable connections through customized designs. Whether used for corporate branding, employee gifts, or retail sales, they offer endless possibilities for logos, names, or artwork. Widely popular in Dubai and across the UAE, these mugs combine daily practicality with strong branding impact, ensuring your message is seen with every sip.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 09:24:05.812349','2025-09-01 09:24:05.812362',66,5,0,''),
('CE-PM-001','Promotional Mugs with Logo | Custom Branded Coffee & Tea Mugs Dubai','A timeless and effective marketing tool, these promotional mugs with logo are perfect for boosting brand awareness and leaving a lasting impression. Widely used across Dubai and the UAE, they make excellent corporate gifts, giveaways, and retail merchandise. Whether for offices, cafés, or events, these custom mugs combine practicality with high-impact branding, ensuring your logo stays visible in daily use.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:34:20.713561','2025-09-01 08:34:20.713573',67,4.5,0,''),
('CE-TT-001','Two-Toned Ceramic Mugs with Clay Bottom & Bamboo Lid | Custom Coffee Mugs Dubai','A stylish and eco-conscious promotional gift, these two-toned ceramic mugs with clay bottom and bamboo lid combine modern aesthetics with practical branding. Perfect for offices, cafés, and corporate giveaways in Dubai and across the UAE, the natural clay base adds a rustic touch while the bamboo lid keeps beverages warm and prevents spills. These mugs work beautifully as coffee mugs, tea mugs, or branded promotional mugs, ensuring your logo makes an impact every day.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:47:14.760054','2025-09-01 09:33:17.766616',16,0,0,''),
('CE-TT-002','Two-Tone Ceramic Mugs | Custom Color Coffee & Tea Mugs Dubai','A vibrant and stylish promotional item, these two-tone ceramic mugs feature a contrasting interior and handle that highlight your brand colors. Perfect for corporate gifting, cafés, and promotional campaigns across Dubai and the UAE, they combine everyday functionality with bold design. Whether used as coffee mugs, tea mugs, or branded giveaways, these mugs ensure your logo stands out with every sip.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 09:19:55.160711','2025-09-01 09:33:45.705800',17,4.5,0,''),
('CE-TT-003','Two-Tone Ceramic Mugs with Spoon 11oz | Custom Coffee & Tea Mugs Dubai','A practical and eye-catching promotional gift, these two-tone ceramic mugs with spoon (11oz) are designed for convenience and brand impact. The color-contrasting interior and matching spoon make them perfect for cafés, offices, and promotional campaigns across Dubai and the UAE. Whether used as coffee mugs, tea mugs, or branded giveaways, they ensure your logo is visible every day with a stylish, functional design.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 09:41:51.562549','2025-09-01 09:41:51.562561',18,4,0,''),
('CE-WC-001','White Ceramic Mugs with Silicone Cap and Base | Custom Coffee Mug Dubai','<p>A compact, environmentally friendly foldable cup ideal for travelers, campers, and events best for brands that promote sustainability and convenience. Whether used as a foldable cup, this collapsible silicone cup makes a thoughtful corporate gift in Dubai and across the UAE.</p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong></span><strong> </strong><span>BPA-free, food grade silicone. an incredibly strong lid made of plastic and heat sleeves.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong></span><span><strong> </strong>It\'s ideal for environmentally friendly campaigns and travel kits that require 2 working days or the same day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design: </strong></span><span>The Design is a foldable, space-saving construction with leak-proof lid the heat-protection of the ring.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong></span><strong> </strong><span>Branding on the go, gifts that are sustainable, as well as outdoor activities.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability: </strong></span><span>It is flexible and long-lasting durable, able to withstand the elements and everyday wear with durable branding.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><strong>Branding Methods</strong></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing): </strong><span>&nbsp;UV printing uses ultraviolet light to apply full-color designs directly onto the plastic or Tritan surface of the infuser bottle. It delivers bright, long-lasting visuals that stay vibrant even with daily use, perfect for fitness brands or wellness campaigns looking to make an impact.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>UV DTF Printing:</strong> </span><span>&nbsp;UV DTF printing applies multi-color artwork via a UV-cured transfer film that wraps around the bottle. This method is ideal for high-detail, full-wrap branding that emphasizes lifestyle imagery or health-conscious messaging across the bottle\'s clear surface.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing: </strong><span>Silk screen printing applies one solid ink color to the bottle using a stencil and mesh screen. This method is excellent for clean, straightforward branding, ideal for logos or taglines that need to be bold and recognizable in health and wellness settings.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>Contact us today to customize your Collapsible Silicone Cup,&nbsp; fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:14:06.487512','2025-09-04 11:37:35.929578',19,4.5,0,''),
('CE-WC-002','White Ceramic Mugs | Custom Coffee & Tea Mug Printing Dubai','Classic and versatile, these white ceramic mugs are a staple promotional gift ideal for everyday use, corporate branding, and events. Whether used as a coffee mug, tea mug, or branded giveaway, they provide a large surface area for logos and artwork, making them one of the most popular promotional mugs in Dubai and across the UAE. Their simple yet professional design ensures your brand stands out in offices, cafés, and homes alike.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:41:07.066660','2025-09-01 08:41:07.066673',68,4,0,''),
('CE-WC-003','White Ceramic Mugs | Custom Tall Coffee & Tea Mugs Dubai','Simple, elegant, and highly effective for branding, these white ceramic mugs are a popular choice for corporate giveaways, cafés, and promotions. With their tall profile and sleek handle, they provide a modern look while offering ample space for logos or artwork. Widely used across Dubai and the UAE, these mugs are versatile, making them ideal for both coffee and tea drinkers while keeping your brand in daily view.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:09:15.158906','2025-09-01 10:09:15.158920',20,4,0,''),
('CE-WS-001','White Sublimation Ceramic Mugs with Box 11oz | Custom Printed Coffee Mugs Dubai','A best-selling promotional product, these white sublimation ceramic mugs with box (11oz) are perfect for corporate giveaways, retail branding, and personalized gifting. The included box makes them an ideal ready-to-deliver package, while the sublimation-ready surface ensures vibrant, full-wrap designs. Popular in Dubai and across the UAE, these mugs are a versatile choice for offices, cafés, and events, keeping your brand visible every day.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 09:09:17.528386','2025-09-01 09:09:17.528400',21,4,0,''),
('CE-WS-002','White Sublimation Mugs | Custom Printed Coffee & Tea Mugs Dubai','A best-seller for promotions and personalization, these white sublimation mugs are designed with a special coating that allows high-resolution, full-color printing. Perfect for corporate branding, personalized gifts, and retail promotions, they deliver vibrant, long-lasting prints. Popular across Dubai and the UAE, these mugs are the go-to choice for businesses and individuals who want custom designs that stand out.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:20:26.363046','2025-09-01 10:20:26.363059',22,5,0,''),
('CO-BE-001','Branded Eco Bluetooth Speaker with Long Battery Life','<p dir=\"ltr\"><span>A great gift for events, employee rewards, and holiday giveaways that is popular and easy to carry. Whether used as a speaker or bluetooth, this bluetooth speaker makes a thoughtful corporate gift in Dubai and across the UAE. Keep your brand front and centre while providing great sound.</span></p>\n<h2 dir=\"ltr\"><span>Main features:</span><b></b></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong> </span><span>A strong plastic or metal body with a grill made of fabric or metal mesh.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use:</strong><span><strong> </strong>It\'s&nbsp; ideal for gifting tech products and brand promotions with 3 to 5 working days of delivery or next-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design: </strong><span>Small and lightweight with crystal clear audio quality. Bluetooth connectivity and a customizable branding space.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for:</strong> </span><span>Corporate giveaways, lifestyle-related promotions Events, youth marketing.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability:</strong> </span><span>The sturdy, portable built with battery longevity that lasts for a long time and a fade-resistant logo print or engraving.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing): </strong><span>UV printing uses ultraviolet light to apply full-color graphics directly onto the flat plastic or metal surface of the speaker. This technique delivers vibrant, fade-resistant branding that remains sharp over time, perfect for eye-catching logos or artwork on compact tech items.</span><span><br><br></span><strong>Laser Engraving:</strong><span> </span><span>Laser engraving uses high-precision etching to permanently mark your logo or design into the metal casing of the speaker. It creates a subtle, premium look that enhances the speaker&rsquo;s professional appearance while ensuring the branding won\'t wear off with use.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Bluetooth Speaker,&nbsp; fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:38:34.660390','2025-09-04 11:49:49.800420',114,0,0,''),
('CO-CB-001','Custom Bluetooth Earphones Corporate Gifts Dubai & UAE','<p>jkljljl</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:30:04.869261','2025-09-04 08:30:04.869276',111,0,0,''),
('CO-CC-001','Custom Corporate USB Memory Sticks','dcfvg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:50:01.372065','2025-09-01 06:50:01.372079',110,0,0,''),
('CO-CL-001','Custom Logo Expandable Phone Grip & Stand','<p>A stylish and practical mobile accessory that improves grip for texting and selfies while also acting as a convenient media stand. Whether used as a phone holder or phone stand, this popup phone grip makes a thoughtful corporate gift in Dubai and across the UAE. This small, low-cost giveaway is ideal for high-visibility branding with any audience type.</p>\n<h2 dir=\"ltr\"><span>Key features</span><b></b></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong></span><span><strong> </strong>A durable ABS plastic that has a strong adhesive backing as well as the ability to collapse.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use: </strong></span><span>Ideal for all-day promotional giveaways and branding with 2 to 3 working days or the same day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design: </strong></span><span>Expands to provide the secure grip of a stand&nbsp; and folds down for storage when not in use. It has fully customized surfaces.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for: </strong></span><strong>&nbsp;</strong><span>Technology accessories, influencer promotions, events as well as retail merchandise.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability:</strong></span><strong> </strong><span>Reusable and secure grip with durable branding that is resistant to wear and fade.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"></p>\n<h3 dir=\"ltr\"><span>Branding Method</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span><br></span><span> UV printing uses ultraviolet light to apply full-color designs directly onto the flat surface of the pop-up phone grip. This method ensures vibrant, scratch-resistant branding that stays sharp with regular use, making it perfect for logos, slogans, or promotional artwork on this highly visible mobile accessory.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Pop-Up Phone Grip,&nbsp; fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:44:22.454190','2025-09-04 11:47:12.707783',115,0,0,''),
('CO-CU-001','Custom Universal Charging Cables Corporate Gifts Dubai & UAE','<p>gvhj</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:31:25.919779','2025-09-04 08:31:25.919798',112,0,0,''),
('CO-DU-001','Dual USB Flash Drives for Mobile & Laptop Dubai & UAE','<p>A practical, in-demand tech item ideal for sharing digital files at trade shows, meetings, and seminars, combining everyday utility with brand visibility. Whether used as a usb flash&nbsp; drive or usb, this classic usb flash drive makes a thoughtful corporate gift in Dubai and across the UAE. This USB Flash Drive is a reliable and effective USB, whether used as a promotional flash drive or a portable USB Drive for everyday use.</p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material: </strong></span><span>Durable plastic for color variety or sleek metal for a high-end feel.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use</strong><span><strong>: </strong>Perfect for corporate giveaways, digital gifts and data sharing. It can be delivered in 2 to 3 working days, or even same-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design</strong><span><strong>: </strong>A compact, light style with keyring loop and an adjustable surface.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong></span><span><strong> </strong>Tech events workshops, training exhibitions, trade shows and office promotional events.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability: </strong></span><span>Long-lasting and shock-proof with top-quality branding using Laser engraving or UV.</span><span><br><br></span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>UV Printing</strong> <strong>(Direct Printing):</strong></span><span> </span><span>UV printing uses ultraviolet light to apply vivid, full-color designs directly onto the flash drive&rsquo;s surface. This method is ideal for plastic or metal casings, offering a sleek, durable finish that keeps your brand front and center in daily use.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>UV DTF Printing:</strong></span><span><strong> </strong>UV DTF printing uses a transfer film to apply complex, multi-color graphics that can wrap around curved or angular surfaces of the USB drive. It\'s perfect for vibrant, full-coverage branding that enhances visual impact without compromising usability.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Screen Printing:</strong></span><strong> </strong><span>Screen printing applies bold, solid-color branding using a stencil and mesh screen. On USB drives, it provides a clean, professional look and is a cost-effective solution for high-volume giveaways and simple logo designs.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Laser Engraving:</strong></span><span><strong> </strong>Laser engraving uses high-precision beams to etch your logo into the metal casing of the USB. It results in a premium, permanent mark that won&rsquo;t fade or scratch, ideal for luxury giveaways or executive-level tech gifts.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>Contact us today to customize your Classic USB Flash Drive,&nbsp; fast delivery across Dubai and the UAE.</span><span></span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:28:55.993082','2025-09-04 11:41:53.284974',106,0,0,''),
('CO-EF-001','Eco-Friendly Custom USB Sticks Dubai & UAE','<p>hghghgh</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:23:28.435695','2025-09-04 08:23:28.435706',107,0,0,''),
('CO-SC-001','Slim Custom USB Flash Drives for Corporate Gifts Dubai & UAE','<p>dgg</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:26:58.017283','2025-09-04 08:26:58.017300',108,0,0,''),
('CO-UM-001','Universal Multi-Plug Adapters Corporate Gifts Dubai & UAE','<p>fghgfhgfh</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:33:25.899017','2025-09-04 08:33:25.899028',113,0,0,''),
('CO-WU-001','Wooden USB Flash Drives 4GB, 8GB, 16GB, 32GB, 64GB','<p>An eco-friendly, fashionable tech gift suitable for creative agencies, sustainable brands, and high-end giveaways for photographers or architects. Whether used as a usb or pendrive, this wooden usb flash drive makes a thoughtful corporate gift in Dubai and across the UAE. This USB is also a perfect pendrive or USB drive option for brands seeking a premium, natural look.</p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material: </strong><span>Made from sustainable bamboo or maple, each with a distinct wood grain.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong> </span><span>Excellent for long-term sustainable branding as well as digital gifts that take 2 to 3 working days, or the same day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design:</strong><span> </span><span>A smooth, minimal design with magnetic cap or swivel feature, great for laser engraving.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong> </span><span>Eco-friendly campaigns Creative agencies, photographers as well as premium giveaways.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability:</strong><span> Durable build, with durable data retention for a long time and UV-resistant personal branding.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span> </span><span>UV printing uses ultraviolet light to apply vibrant, full-color artwork directly onto the wooden surface of the USB. This method maintains the natural wood texture while adding eye-catching branding, making it ideal for colorful logos or detailed designs that stand out on bamboo or maple finishes.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing:</strong><span> UV DTF printing transfers multi-color graphics onto the USB using a durable UV-cured film. It allows wrap-around branding across curved or flat wooden surfaces, offering a high-impact, full-coverage option that preserves the eco-friendly appeal of the product.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Laser Engraving:</strong><span> Laser engraving etches your logo or message directly into the wood with precision. This technique enhances the natural aesthetic of the bamboo or maple body, giving the USB a premium, rustic look that reflects sustainability and quality.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>Contact us today to customize your Classic USB Flash Drive,&nbsp; fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:54:01.431242','2025-09-04 11:43:50.630621',109,0,0,''),
('DE-BF-001','Bi-Fold Umbrella in White Color with Velcro Closure and Pouch','hgftxht','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:22:47.017246','2025-09-01 10:22:47.017258',123,0,0,''),
('DE-SF-001','Sunshades for Cars in White Tyvek Material','yfhyt','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:26:26.187800','2025-09-01 10:26:26.187812',124,0,0,''),
('EC-BF-001','Bamboo fiber cups with silicone lid','<p>ggggggh</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:10:08.101936','2025-09-04 07:10:08.101954',85,0,0,''),
('EC-EF-001','Eco-friendly glass bottles with straw','<p>rwfrtg</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:01:28.038088','2025-09-04 07:01:28.038102',86,0,0,''),
('EV-CE-001','Custom Eco-Friendly Tote Bags Dubai & UAE','<p>ghjjghgf</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:16:40.231270','2025-09-04 08:16:40.231282',91,0,0,''),
('EV-CJ-001','Custom Jute Drawstring Pouches A4 & A5 Size | Eco-Friendly Gift & Travel Bags Dubai','<p dir=\"ltr\"><span>It is a lightweight and useful product to use for daily activities, occasions, or for giveaways. A drawstring backpack often referred to as the drawstring bag or string bag can be used for schools, gyms, as well as promotional events that are branded because it blends the power of branding and portability and makes a great drawstring bag that is printed to live an active life.</span></p>\n<h2 dir=\"ltr\"><span>Key Features:</span><span><b></b></span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material:</strong><span> Polyester, light weight nylon, or non-woven fabrics that have reinforced corners.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong> </span><span>Is ideal for promotional giveaways and events that require 2-3 days of notice or next-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design: </strong></span><span>Top closure that is simple with drawstrings that can be adjusted and an open interior.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong> </span><span>Schools, sporting events, trade shows, health and fitness programs, as well as branding while on the go.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability: </strong><span>Reusable and tear-resistant with durable stitching, strong stitching, and long-lasting printing options.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>DTF Heat Transfer:</strong></span><strong> </strong><span><strong>&nbsp;</strong>DTF heat transfer uses heat and a transfer film to apply vibrant, full-color graphics onto the fabric of the drawstring bag. It&rsquo;s ideal for detailed or photo-quality branding, offering long-lasting visuals that stand out on lightweight, flexible materials.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> </span><span>Silk screen printing applies a bold, single-color logo directly onto the drawstring bag using a stencil. It&rsquo;s a budget-friendly method well-suited for simple and high-contrast branding, perfect for large-volume giveaways.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Drawstring backpack bag, fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 07:19:04.998240','2025-09-04 12:11:23.941699',94,0,0,''),
('EV-CJ-002','Custom Jute Shopping Bags in Dubai','<p dir=\"ltr\"><span>A rustic, eco-friendly tote bag that will leave a lasting impression on your brand. Whether used as a jute bag or eco-friendly bags, this jute bag makes a thoughtful corporate gift in Dubai and across the UAE. Because it is well made, it\'s great for everyday use, organic markets, and eco-friendly events.</span></p>\n<h2 dir=\"ltr\"><span>Key Features:</span></h2>\n<p dir=\"ltr\"><span><b>&nbsp;</b></span></p>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong> </span><span>Made from natural, biodegradable Jute fibers, often laminated on the interior for water resistance and structure.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong> </span><span>It\'s great for sustainable branding as well as everyday use. 3-4 working days, or even same-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design:</strong> </span><span>Natural with sturdy handles as well as a wide printed surface.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Perfect for: </strong><span>Eco-friendly campaign, packaging for retail, corporate gifts, and events.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability:</strong><span> Reusable and tear-proof with a long-lasting screen and printing with heat.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span><b>&nbsp;</b></span></p>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing: </strong><span>UV DTF printing uses a UV-cured transfer film to apply detailed, full-color graphics onto the textured jute surface. This method allows vibrant, multi-color branding while preserving the natural appeal of the fabric, ideal for high-impact designs on rustic, eco-friendly bags.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing: </strong><span>Silk screen printing applies a single solid-color design directly onto the jute fibers using a mesh stencil. It offers a simple, durable, and eco-friendly branding method that aligns well with the bag&rsquo;s natural, earthy appearance, great for minimalist or green-focused campaigns.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Cotton Tote Bag , fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 07:31:27.143007','2025-09-04 11:58:30.308978',95,4.5,250,''),
('EV-CJ-003','Custom Jute Shopping Bags with Button Eco-Friendly Reusable Branded Tote Bags Dubai & UAE','ghhk','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 07:52:59.438511','2025-09-01 07:52:59.438522',96,0,0,''),
('EV-CL-001','Custom Lanyards with Hook, Safety Lock & Buckle 20mm','huyh','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:10:07.059956','2025-09-01 10:10:07.059971',119,0,0,''),
('EV-CR-001','Custom Recycled PET Shopping Bags Dubai & UAE','<p>ffffddsfdf</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:18:38.159006','2025-09-04 08:18:38.159020',92,0,0,''),
('EV-CR-002','Custom Reusable Eco Bags Dubai & UAE','<p>This stylish, eco bag is made from recycled plastic bottles, making it an eco-friendly tote that\'s great for everyday use, green campaigns, and giveaways. It\'s a good choice for promoting your brand\'s environmental values because it\'s light but strong.</p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong></span><span><strong> </strong>Is made using recycled PET (plastic bottles) Lightweight and environmentally conscious.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use: </strong></span><span>Is ideal to promote green and sustainable retail uses that require 2-3 days of notice or next-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design: </strong></span><span>A foldable waterproof structure, with sturdy handles as well as a large printing area.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for: </strong></span><span>Eco-friendly campaign, trade show food use, corporate giveaways.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability: </strong></span><span>Sturdy and Reusable with top-quality, fade-resistant brand choices.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>UV DTF Printing</strong>:</span><span> </span><span>UV DTF printing uses a transfer film to apply full-color artwork onto the recycled PET fabric. This method ensures vibrant, long-lasting visuals that wrap around the bag&rsquo;s surface ideal for bold, eco-friendly branding that emphasizes sustainability.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Silk Screen Printing:</strong></span><strong> </strong><span><strong>&nbsp;</strong>Silk screen printing applies one solid-color design directly onto the RPET material using a stencil. It&rsquo;s a simple, effective branding method that creates clean, high-contrast logos while maintaining the bag&rsquo;s lightweight, environmentally conscious appeal.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Eco Bag RPET , fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:21:03.935627','2025-09-04 12:00:55.864543',93,0,0,''),
('EV-DP-001','Durable polyester wristbands','jtuyt','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:11:31.274589','2025-09-01 10:11:31.274600',120,0,0,''),
('EV-LW-001','Lanyards with Double Hook','uyjj','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:08:07.423934','2025-09-01 10:08:07.423952',121,0,0,''),
('EV-RJ-001','Rustic Jute Carry Bag','fgzfg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:59:40.560042','2025-09-01 07:04:51.873987',97,0,0,''),
('EV-RV-001','Reusable vertical non-woven shopping bags','ghnnj','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:04:31.872298','2025-09-01 08:04:31.872309',98,0,0,''),
('EV-SC-001','Sturdy Cotton Tote Bag','<p>Reusable and environmentally friendly, this cotton tote bag is perfect for everyday tasks, shopping, and event giveaways. A long-term option that guarantees brand exposure and highlights the practicality of the tote bag as a promotional item.</p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong> </span><span>100% natural cotton fabric that is durable and breathable.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use: </strong><span>It\'s ideal for environmentally conscious sales and promotional giveaways that take 3-4 working days, or even same-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design:</strong><span> Large, light equipped with durable handles and a large print space to display logos or design.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong> </span><span>Trade exhibitions, shops at retail supermarket runs, as well as sustainability-based branding.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability: </strong><span>Long-lasting and washable by using high-quality screen or transfer printing.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>DTF Heat Transfer:</strong><span> </span><span>DTF (Direct-to-Film) heat transfer uses heat and pressure to apply full-color designs onto the cotton tote bag. This method creates vivid, durable prints that resist washing and wear, ideal for bold, detailed artwork or multicolor branding on fabric.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> </span><span>Silk screen printing uses a mesh stencil to apply one or two solid ink colors onto the tote&rsquo;s surface. It\'s a cost-effective and bold solution for simple logos, slogans, or graphic branding, especially for bulk promotional giveaways.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Embroidery:</strong><span> </span><span>Embroidery stitches your logo or design directly into the cotton fabric, delivering a premium, textured finish. It&rsquo;s long-lasting, won&rsquo;t fade with washes, and is perfect for upscale branding or eco-conscious promotions with a touch of elegance.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your cotton tote bag, fast delivery across Dubai and the UAE</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:32:55.741433','2025-09-04 11:55:39.709469',99,0,0,''),
('EV-TW-001','Tyvek Wristbands Waterproof, Adjustable, Adhesive','htj6j','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:13:10.521397','2025-09-01 10:13:10.521408',122,0,0,''),
('EV-VN-001','Vertical Non-Woven Bags Printing in Dubai  Custom Reusable Tote Bags & Branded Eco Bags UAE','<p>A lightweight, environmentally friendly tote suitable for large-scale promotions, retail, and everyday use. Whether used as a tote bag or branded tote bag, this nonwoven tote bag makes a thoughtful corporate gift in Dubai and across the UAE. Designed for businesses seeking for a low-cost, reusable bag that has strong branding potential.</p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong> </span><span>Non-woven polypropylene material that is lightweight and recyclable.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong> </span><span>It is perfect for cost-effective promotions and events that require 2 to 3 working days, or even same-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design:</strong> </span><span>The design is simple but spacious featuring stitched handles as well as a wide area for branding.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Perfect for: </strong><span>Shows products, packaging for conferences, trade shows and giveaways for mass distribution.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability:</strong> </span><span>Reusable and tear-resistant to use multiple times with sturdy lasting prints</span><span>.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"></p>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing:</strong><span> UV DTF printing uses a UV-cured transfer film to apply full-color, high-resolution designs onto the non-woven polypropylene surface. This method ensures maximum coverage with vibrant, long-lasting visuals, ideal for lightweight bags used in mass promotions.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Silk Screen Printing: </strong></span><span>Silk screen printing applies bold, single-color logos or messages using a stencil process. It&rsquo;s a cost-effective and durable option for clean, high-contrast branding on non-woven fabric, making it ideal for bulk distribution and event giveaways.</span></p>\n</li>\n</ul>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:01:45.606720','2025-09-04 12:03:12.218640',100,0,0,''),
('EX-CB-001','Custom Branded Corporate Planners & Organizers Dubai & UAE','<p>dfg</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:07:29.819408','2025-09-04 08:07:29.819422',32,0,0,''),
('EX-CC-001','Custom Corporate Diaries & Notebooks Dubai & UAE','<p>yjgn</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:09:59.933948','2025-09-04 08:09:59.933960',33,0,0,''),
('EX-CC-002','Custom Corporate Diaries with Index Tabs Dubai & UAE','<p>kjljljl</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:11:46.919692','2025-09-04 08:11:46.919705',34,0,0,''),
('EX-PL-001','PU Leather Diaries','<p>fverg</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:39:52.238710','2025-09-04 07:39:52.238723',35,0,0,''),
('EX-WP-001','White PU Leather A5 Diaries with Band & Bookmark Loop','fjghm','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:28:37.687687','2025-09-01 12:28:37.687699',36,0,0,''),
('FL-CF-001','Conference Flags (2m)','<p>hf4fehjl</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:08:39.739279','2025-09-11 06:08:39.739294',135,4.5,0,''),
('FL-CF-002','Conference Flags (3m)','<p>hgrhekj</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:10:06.889737','2025-09-11 06:10:06.889752',136,0,0,''),
('FL-CT-001','Curved Top Flags','<p>nfdsagfydbh</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:35:12.911027','2025-09-11 06:35:12.911039',137,0,0,''),
('FL-HB-001','Hanging Banner','<p>hgcvdf</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:24:47.271160','2025-09-11 06:24:47.271183',138,0,0,''),
('FL-HD-001','Heavy Duty Table Flags','<p>ghutt</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:13:30.994018','2025-09-11 06:13:30.994032',139,0,0,''),
('FL-HT-001','Hanging Table Flags','<p>hgbmn</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:11:57.650589','2025-09-11 06:11:57.650600',140,0,0,''),
('FL-HT-002','Hoisting Type Table Flags','<p>hbbgg</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:14:38.836762','2025-09-11 06:14:38.836779',141,0,0,''),
('FL-LS-001','L Shape Table Flags','<p>gfges,</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:16:07.811581','2025-09-11 06:16:07.811593',142,0,0,''),
('FL-PF-001','Pennant Flags','<p>gfesrt</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:17:21.217434','2025-09-11 06:17:21.217449',143,0,0,''),
('FL-PF-002','Pole Flag 10 meter','<p>hgfo</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:31:34.713361','2025-09-11 06:31:34.713378',144,0,0,''),
('FL-PT-001','Premium Table Flags','<p>gfdsd</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:19:06.441318','2025-09-11 06:19:06.441336',145,0,0,''),
('FL-ST-001','Standard Table Flags','<p>fgfhj</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:21:40.722160','2025-09-11 06:21:40.722176',146,0,0,''),
('FL-TD-001','Tear Drop Flag','<p>ghbvcgh</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:39:46.606036','2025-09-11 06:39:46.606058',147,0,0,''),
('FL-TS-001','T Shape Table Flags','<p>gjhmn</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:23:09.815486','2025-09-11 06:37:42.480915',148,0,0,''),
('FL-VC-001','VIP Conference Flag (2.9m)','<p>gfhdgf</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:27:31.056392','2025-09-11 06:27:31.056403',149,0,0,''),
('FL-VS-001','V Shape Table Flags','<p>ghfbdc</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:26:33.943030','2025-09-11 06:26:33.943045',150,0,0,''),
('FL-YS-001','Y Shape Table Flags','<p>rrfesyhs</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-11 06:28:30.528158','2025-09-11 06:28:30.528183',151,0,0,''),
('GI-LP-001','Logo Printed Notebook & Pen Gift Combo','<p dir=\"ltr\"><span>The best high-end gift set for honoring business partners, CEOs, or guest speakers. It is aesthetically presented to leave a lasting and distinguished impression. Ideal as special pens for gift occasions, this pen gift set combines elegance with thoughtful branding.</span></p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material:</strong><span> Premium materials like metal, bamboo, or leatherette packaging for an upscale look.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong> </span><span>It\'s ideal for corporate gifts and promotions for brands with 2 working days or the same day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design:</strong> </span><span>The perfect combination of pens inside a chic box. It offers an elegant writing experience and a stunning visual.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for: </strong></span><span>Corporate gifts and awards, customer appreciation and holiday giveaways.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability:</strong> </span><span>Durable construction that lasts for a long time with top-quality branding that maintains its shine throughout time.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing): </strong><span><strong>&nbsp;</strong>UV printing applies full-color artwork directly onto each pen and its presentation box using ultraviolet light. This method allows for a visually cohesive and vibrant branding experience, making the gift set look polished, coordinated, and perfect for high-end corporate gifting.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> </span><span>Silk screen printing uses a mesh stencil to apply one or two solid ink colors to the pens. It&rsquo;s ideal for consistent branding across large quantities, offering a clean and professional finish that ensures every piece in the gift set aligns with your corporate identity.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Laser Engraving:</strong><span> Laser engraving etches logos or names permanently into the metal pens, giving them a refined and exclusive look. This technique adds a luxurious, personal touch to the gift set, making it ideal for executive gifts, awards, or commemorative occasions.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Pen Gift Set, fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:24:30.052327','2025-09-04 10:50:07.131993',60,0,0,''),
('NO-AS-001','A5 Size Milk Paper Spiral Notebooks, 70 Sheets 80 GSM','<p dir=\"ltr\"><span>The spiral &amp; wiro notebook can be used in Dubai\'s hectic work and school setting because it\'s comfortable and customizable. It is a spiral Notebook or Binder Notebook choice, its lay-flat layout and easy fold-back function makes it an ideal choice for those who are students, artists journalists and other professionals that require a practical instrument such as the book as well as a smaller notebook to use on a daily basis and for branding their company.</span></p>\n<h2 dir=\"ltr\"><span>Key Features:</span><b></b></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material:</strong><span> PU, cardboard or even plastic covers that have premium inner pages, and wire spiral binding made of metal.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong></span><span><strong> </strong>Perfect for offices, schools or events. It can also be used for branding. It takes 2-3 days for delivery or the same day.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design:</strong><span> Flip-able pages that can be easily flipped with a lay-flat layout, as well as an adjustable cover that can be customized with dividers and pen holders.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Perfect for:</strong><span><strong> </strong>Educational kits, corporate use conference giveaways, as well as promotional events.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability: </strong><span>Strong binding and tough covers that are designed to withstand regular handling as well as the long-term brand visibility.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>UV Printing (Direct Printing):</strong></span><span><strong> </strong>UV printing applies full-colour designs directly onto the cover, delivering sharp detail and high-quality visuals that wrap cleanly around the spiral or wiro binding. It&rsquo;s perfect for impactful branding on both flexible and rigid covers.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> </span><span>Silk screen printing places bold, solid-colour logos on the notebook cover, providing a clean, professional look that\'s ideal for bulk orders and long-term brand recall.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Spiral &amp; Wiro Notebook, fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:17:14.121060','2025-09-04 12:19:20.960117',25,0,0,''),
('NO-BA-001','Branded A5 Hardcover Notebooks','<p dir=\"ltr\"><span>An elegant and practical notebook that is ideal for daily planning, journaling, and meetings. This writing notebook with quality notebook paper is perfect for corporate teams, events, and branded giveaways because it is useful every day and has a lasting effect on the brand.</span></p>\n<h2 dir=\"ltr\"><span>Key Features:</span><span><b></b></span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong> </span><span>80 GSM paper on paperboard, PU leather, or cloth.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use: </strong><span>Ideal to use for stationery, corporate and gifts that take 2-3 working days, or delivery on the same day.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design</strong><span><strong>:</strong> </span><span>A sleek hardcover that has a strap closure with elastics&nbsp; ribbon bookmark and an optional pen loop.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong></span><strong> </strong><span>Office usage conference, academic, office use as well as executive gifts.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span>&nbsp;</span><strong>Durability:</strong><span>Durable cover that lasts for years and bindings with professional branding through debossing, screening, and UV print.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span> </span><span>UV printing adds vibrant, full-color designs directly onto the hardcover surface. It provides a high-quality, durable finish that protects the print while showcasing vivid detail, ideal for modern branding on notebooks used in meetings or conferences.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> </span><span>Silk screen printing applies one or two bold solid colors onto the notebook&rsquo;s cover. This method is cost-effective and well-suited for simple, impactful logos or text, giving your notebook a clean and professional appearance.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Debossing / Foil Stamping: </strong><span>Debossing presses your logo into the cover for a premium, tactile effect, while foil stamping enhances it with metallic accents like gold or silver. Together, these techniques create an upscale, executive-level notebook perfect for gifting or brand prestige.</span></p>\n</li>\n</ul>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:49:22.066650','2025-09-04 12:14:54.003587',26,0,0,''),
('NO-CB-001','Custom Branded Notebooks','gjbm','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:45:09.057081','2025-09-01 11:45:09.057097',27,5,369,''),
('NO-CC-001','Custom Corporate Diaries & Executive Notebooks Dubai & UAE','<p>hhghjnhj</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 08:05:19.026059','2025-09-04 08:05:19.026073',24,0,0,''),
('NO-LP-001','Leather Portfolio with Zipper and Calculator','yygi','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:06:56.667820','2025-09-01 12:06:56.667832',28,0,0,''),
('NO-PD-001','Premium Dorniel A5 PU notebooks with front pocket & magnetic flap','<p>Compact, convenient, and designed for quick note-taking on the move, this pocket notebook is a smart and stylish addition to any giveaway set. It is the perfect choice for professionals, students, and event attendees who require the ability to record thoughts, reminders, or sketches at any time and in any location.</p>\n<h2 dir=\"ltr\"><span>Key Features:</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material: </strong></span><span>PU that lasts a long time, PVC that bends, or cardboard that is strong with 80 GSM inner pages.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use:</strong><span> </span><span>Perfect for daily writing and giveaways that are branded which require a minimum of 2 working days, or next-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design: </strong><span>Small and pocket-sized design with an closing elastic as well as ribbon marker or pen loop.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Perfect for:</strong><span> </span><span>Corporate gifts conference, fieldwork as well as travel kits and every day plan.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability:</strong><span> Designed for mobile use with strong bindings and lasting customized branding</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing): </strong><span>UV printing applies vibrant, full-colour artwork directly onto the compact cover, ensuring long-lasting clarity and visual appeal, even on small surfaces like pocket-sized notebooks.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> Silk screen printing adds one or two solid-colour logos to the notebook&rsquo;s cover. It&rsquo;s a cost-effective way to maintain clean, consistent branding across high volumes.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Embossing: </strong><span>Embossing creates a raised impression of your logo or text on the notebook&rsquo;s surface, delivering a subtle yet premium feel, ideal for stylish and professional branding on giveaways or corporate sets</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your pocket notebook,&nbsp; fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:56:03.017745','2025-09-04 12:20:56.378378',29,0,0,''),
('NO-SN-001','Softcover Notebooks','<p>&nbsp;A softcover notebook is a stylish and practical branding tool in Dubai&rsquo;s fast-paced business scene. Lightweight and customizable, it&rsquo;s ideal for conferences, training, exhibitions, and promotional giveaways, helping brands stand out with ease.</p>\n<h2 dir=\"ltr\"><span>Key features</span><b></b></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material: </strong><span>Flexible card stock or PU cover that has high-end inside pages (lined empty, blank or with dotted).</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong> </span><span>Excellent for events as well as branding and note-taking. Available for 2 working days, or next-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design:</strong> </span><span>Portable and slim with a binding that is stitched or glued as well as a large branding space.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Perfect for: </strong><span>Conferences, training sessions, giveaways, as well as for academic purposes.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability:</strong> </span><span>It is lightweight yet durable with high-quality print that stands the test of time.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing): </strong><span>&nbsp;UV printing applies full-colour designs directly onto the softcover material, producing sharp, vibrant visuals that won&rsquo;t crack or fade&mdash;ideal for creative and professional branding on flexible notebook covers.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> This method places one or two solid-colour logos onto the notebook&rsquo;s surface, offering a clean, minimal look that&rsquo;s cost-effective and perfect for bulk giveaways or branded training materials.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Debossing and Foil Stamping:</strong><span> Debossing presses the logo into the softcover for a subtle, textured impression, while foil stamping adds a metallic finish for added elegance, great for gifting or premium branding.</span></p>\n</li>\n</ul>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:10:13.223802','2025-09-04 12:17:09.655450',30,0,0,''),
('NO-SN-002','Spiral Notebook with Sticky Note and Pen','ggfrh','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:14:18.321962','2025-09-01 12:14:18.321975',31,0,0,''),
('PL-AP-001','Affordable plastic ballpoint pens','<p>An affordable marketing tool that\'s perfect for spreading brand awareness at events, trade shows, and conferences in bulk. Whether used as a pen gift or writing pen, this plastic ballpoint pen makes a thoughtful corporate gift in Dubai and across the UAE. This option is ideal for promotional purposes, regardless of whether you\'re using a writing pen, ballpoint pen, or pen.</p>\n<h2><b id=\"docs-internal-guid-c13c299b-7fff-e8b4-d47e-fe619a5fda83\"><span>Main Features:</span></b></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material</strong>:</span><span> </span><span>The material is durable and lightweight ABS plastic that is suitable for daily use.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use</strong>:</span><span> Ideal for a large distribution that takes 2-3 working days, or for same-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design</strong>: Smooth flow of ink and a secure grip.</p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong> </span><span>&nbsp;Promotions, events as well as education and hospitality. This option is ideal for promotional purposes regardless of whether you\'re using a writing pen, ballpoint pen or pen gift writing pen or ballpen. This plastic ballpoint pen remains a versatile choice for your promotional needs and makes a thoughtful corporate gift in Dubai and across the UAE.</span></p>\n</li>\n<li><strong>Durability: </strong>Strong construction with durable, fade-resistant branding.<br>\n<h3><b><span>Branding methods<br></span></b></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span><br></span><span> UV printing uses ultraviolet light to cure ink directly onto the plastic surface of the pen, allowing for vibrant, full-color branding with a professional finish. On the Plastic Ballpoint Pen, this method delivers sharp, long-lasting designs that resist wear, making it ideal for multicolored logos and detailed artwork that stand out at promotional events.</span><span><br><br></span></p>\n</li>\n</ul>\n<b id=\"docs-internal-guid-d8f673a2-7fff-7dd1-09bb-05aeb6e48764\"><span><b id=\"docs-internal-guid-64d65fe0-7fff-e856-1bf1-ee230fc305fc\">Silk Screen Printing:<br></b></span></b>Silk screen printing applies one or two solid ink colors through a mesh stencil onto the pen&rsquo;s surface. This method is perfect for bold, simple logos or text and is highly suitable for bulk branding. On the Plastic Ballpoint Pen, it ensures clear, durable prints, making it an excellent choice for cost-effective, large-scale giveaways.<br><br></li>\n</ul>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-03 12:56:02.068149','2025-09-04 10:32:42.485293',55,0,0,''),
('PL-SM-001','Stylus Metal Pens with Textured Grip','xcfgdsdg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:27:33.353125','2025-09-01 06:27:33.353138',56,0,0,''),
('PO-BB-001','Branded Bamboo Wireless Fast Charging Pad','ttjghhg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:54:02.135110','2025-09-01 06:54:02.135127',116,0,0,''),
('PO-HC-001','High Capacity Powerbank 30,000 mAh','hgc','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:52:00.836992','2025-09-01 06:52:00.837011',117,0,0,''),
('PO-MD-001','Multi-Device Wireless Charger Power Bank','<p dir=\"ltr\"><span>A reliable and useful way to keep devices charged all day. Whether used as a power bank or wireless power bank, this standard power bank makes a thoughtful corporate gift in Dubai and across the UAE. Great for corporate giveaways, travel kits, event swag, or gifts for employees. It makes sure that the brand is seen and used consistently over time. This Power Bank is an ideal choice for modern tech needs.</span></p>\n<h2 dir=\"ltr\"><span>Main Features:</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong> </span><span>A strong plastic or aluminium case with a smooth finish.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use:</strong><span><strong> </strong>Ideal for branding on mobile devices and tech-related giveaways. It takes 2 working days of delivery or next-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design: </strong><span>Portable, slim style with USB/Type-C ports as well as a big branding surface.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong></span><strong> </strong><span>Corporate presents and events traveling kits, as well as other tech-related emergency items.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability</strong><span><strong>:</strong> </span><span>The battery\'s life is long that includes protection circuits inbuilt as well as a long-lasting logo imprint using Laser marking or UV.</span></p>\n</li>\n</ul>\n<h3><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span><strong> </strong>UV printing uses ultraviolet light to apply full-color artwork directly onto the plastic or aluminum surface of the power bank. This method offers a glossy, high-resolution finish that&rsquo;s both vibrant and durable, ideal for showcasing logos, icons, or artwork that makes your brand stand out on tech essentials.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Laser Engraving: </strong><span>Laser engraving etches your logo or design directly into the metal casing of the power bank. It creates a sleek, permanent mark that won&rsquo;t fade or scratch, perfect for professional, high-end branding that enhances the product&rsquo;s modern tech appeal.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customise your Main Features, fast delivery across Dubai and the UAE</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:56:25.380317','2025-09-04 11:51:43.613467',118,0,0,''),
('PR-CC-001','Custom Corporate Brochures & Booklets Dubai & UAE','<p>fdfdf</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:52:14.584306','2025-09-18 05:57:32.255073',5,0,0,''),
('PR-CC-002','Corporate Catalogs, Profiles & Manuals Dubai & UAE','<p>wer</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:54:34.958335','2025-09-04 07:54:34.958357',6,0,0,''),
('PR-CH-001','Custom Holographic Waterproof Stickers Dubai & UAE','dfgh','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:14:53.441538','2025-09-01 12:14:53.441549',8,0,0,''),
('PR-CO-001','Corporate Office Gift Set in Color Themed Box with Ribbon Handle','<p>gt5g</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:33:10.622430','2025-09-04 07:33:10.622444',132,0,0,''),
('PR-CP-001','Custom Promotional Flyers & Leaflets Dubai & UAE','sdfghj','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:12:10.689220','2025-09-01 12:12:10.689231',9,0,0,''),
('PR-CP-002','Custom Pull Up & Retractable Banners Dubai & UAE','<p>fgjfkh</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 07:56:17.763253','2025-09-04 07:56:17.763266',7,0,0,''),
('PR-CW-001','Custom Waterproof Gold Stickers Dubai & UAE','sdfg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:13:47.803878','2025-09-01 12:13:47.803890',10,0,0,''),
('SP-PB-001','Plastic Bottles with Straw','<p>frf4</p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-04 06:52:49.207244','2025-09-04 06:52:49.207267',76,0,0,''),
('SP-PS-001','Promotional Sports Bottles 750ml | Custom Branded Sports Water Bottles Dubai','<p>A lightweight, reusable bottle suitable for sports, fitness, outdoor events, and environmentally conscious promotions. It works to reduce single-use plastic and promote active lifestyles. This sports bottle is also an ideal water bottle for daily hydration and branding opportunities.Whether used as a bottle or water bottle, this aluminium sports bottle makes a thoughtful corporate gift in Dubai and across the UAE.</p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material: </strong></span><span>It is light and durable aluminum that has a stylish, modern look.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong></span><span><strong> </strong>It\'s ideal for branding your lifestyle with 2 working days, or even same-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design:</strong></span><span><strong> </strong>Leak-proof cap with ergonomic shape for easy carrying and use.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong></span><span><strong> </strong>Event sponsorships and fitness events, outdoors campaigns and giving.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability: </strong></span><span>Rust-resistant and built for repeated use, with long-lasting printed or engraved branding.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span><strong> </strong>UV printing uses ultraviolet light to cure full-color designs directly onto the aluminium surface. On the sports bottle, this method provides a clean, vibrant finish that resists wear and is perfect for detailed logos or colorful artwork with daily durability.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing:</strong><span> UV DTF printing applies a high-resolution, full-wrap design using a durable UV-cured transfer film. It&rsquo;s ideal for wrapping multi-color graphics around the bottle&rsquo;s body, maximizing visibility and making your brand stand out during active use or outdoor events.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> Silk screen printing transfers one solid color onto the bottle using a mesh stencil. This method is great for bold, simple branding like logos or slogans, offering a cost-effective solution for bulk orders with consistent and strong visual impact.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>Contact us today to customize your Aluminium Sport bottle, fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:55:15.544580','2025-09-04 11:31:16.543619',77,4.5,0,''),
('SP-RB-001','rPET Bottles with Cork Base & Twist-Off Lid 720ml | Eco-Friendly Water Bottles Dubai','A modern and sustainable choice, these rPET bottles with cork base, twist-off lid, and handle (720ml) are designed for eco-conscious promotions and daily use. Made from recycled PET plastic with a natural cork base, they combine durability, style, and functionality. Perfect for corporate giveaways, wellness programs, and retail branding across Dubai and the UAE, they showcase your brand while promoting sustainability.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:20:18.607119','2025-09-01 11:20:18.607137',78,5,0,''),
('SP-RT-001','rPET Transparent Bottles 800ml with Stainless Steel Lid & Carry Handle | Eco-Friendly Water Bottles Dubai','A stylish and sustainable promotional product, these rPET transparent bottles (800ml) with stainless steel lid and carry handle are perfect for eco-conscious campaigns, corporate giveaways, and wellness programs. Made from recycled PET plastic, they promote sustainability while keeping your brand visible every day. Widely used across Dubai and the UAE, these bottles combine portability, durability, and a modern look that resonates with environmentally aware audiences.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:35:38.969462','2025-09-01 11:35:38.969473',79,4,0,''),
('SP-SS-001','Stainless Steel Bamboo Flask | Eco-Friendly Custom Flask Dubai','A premium and eco-conscious promotional gift, this stainless steel bamboo flask combines durability with natural elegance. Perfect for corporate giveaways, wellness programs, and retail branding, it keeps beverages hot or cold while showcasing your brand on a sustainable bamboo finish. Popular across Dubai and the UAE, it’s a stylish and practical item that promotes both your business and eco-friendly values.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:06:03.134238','2025-09-01 11:06:03.134252',80,4,0,''),
('SP-TB-001','Travel Bottles | Custom Branded Water & Sports Bottles Dubai','Practical and portable, these travel bottles are perfect for on-the-go hydration and brand visibility. Designed for daily use, events, and corporate giveaways, they combine functionality with strong promotional impact. Whether used as water bottles, sports bottles, or branded travel bottles, they are highly popular across Dubai and the UAE, keeping your logo in hand wherever your clients or employees go.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:38:01.205239','2025-09-01 10:38:01.205252',81,4.5,0,''),
('SP-TT-001','Travel Tumbler with Cork Base 450ml Stainless Steel | Custom Branded Tumblers Dubai','A premium and practical promotional gift, this travel tumbler with cork base (450ml) stainless steel is designed for durability and style. The double-wall stainless steel keeps drinks hot or cold, while the natural cork base adds grip and insulation. Perfect for corporate giveaways, wellness programs, and retail promotions, these tumblers are widely used across Dubai and the UAE as eco-friendly and reusable drinkware.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:48:00.447948','2025-09-01 11:48:00.447961',82,0,0,''),
('SP-WB-001','Water Bottles | Custom Branded Sports & Travel Bottles Dubai','A highly popular promotional item, these water bottles are perfect for corporate giveaways, fitness campaigns, and retail branding. Lightweight, portable, and reusable, they ensure your logo stays visible in offices, gyms, schools, and outdoor events. Widely used across Dubai and the UAE, branded water bottles are a practical way to promote wellness while delivering lasting brand exposure.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 10:44:45.878986','2025-09-01 10:44:45.879002',83,5,0,''),
('SP-WB-002','Water Bottle with Fruit Infuser | Custom Infuser Sports Bottles Dubai','<p dir=\"ltr\"><span>A healthy, stylish hydration option that promotes natural flavour infusion, ideal for wellness brands, fitness campaigns, and summer promotions. Whether used as an infuser water bottle or plastic bottle, this fruit infuser bottle makes a thoughtful corporate gift in Dubai and across the UAE. This infuser water bottle is a great choice for anyone looking for a functional and visually appealing plastic bottle.</span></p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material: </strong><span>BPA-free Tritan or durable plastic integrated infuser compartment.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use:</strong><span><strong> </strong>It\'s great for health-related promotional campaigns with a minimum of 2 working days or delivery on the same day.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design:</strong><span><strong> </strong>Clear waterproof, leak-proof body that has an infuser that can be used to add fruit or even herbs.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for</strong>: </span><span>Giveaways for wellness as well as fitness and lifestyle brands and outdoor activities.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability:</strong><span> It is reusable, durable to impact and designed to provide everyday water with a long-lasting brand image.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span> UV printing uses ultraviolet light to apply full-color designs directly onto the plastic or Tritan surface of the infuser bottle. It delivers bright, long-lasting visuals that stay vibrant even with daily use, perfect for fitness brands or wellness campaigns looking to make an impact.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing: </strong><span>UV DTF printing applies multi-color artwork via a UV-cured transfer film that wraps around the bottle. This method is ideal for high-detail, full-wrap branding that emphasizes lifestyle imagery or health-conscious messaging across the bottle\'s clear surface.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Silk Screen Printing:</strong></span><span><strong> </strong>Silk screen printing applies one solid ink color to the bottle using a stencil and mesh screen. This method is excellent for clean, straightforward branding, ideal for logos or taglines that need to be bold and recognizable in health and wellness settings.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>Contact us today to customize your Fruit Infuser Bottle,&nbsp; fast delivery across Dubai and the UAE.</span><span></span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:15:09.131035','2025-09-04 11:34:05.958973',84,4.5,0,''),
('TA-EF-001','Eco-Friendly Custom Branded Coaster Printing','ghu','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-02 08:05:42.217227','2025-09-02 08:05:42.217239',87,0,0,''),
('TA-HT-001','Hardboard Tea Coasters','ghkg','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-02 08:09:44.159865','2025-09-02 08:09:44.159881',88,0,0,''),
('TA-RG-001','Round Glass Tea Coasters','gghk','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-02 08:12:46.423762','2025-09-02 08:12:46.423773',89,0,0,''),
('TA-SG-001','Square Glass Tea Coasters','tggu','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-02 08:11:13.953306','2025-09-02 08:11:13.953318',90,0,0,''),
('TR-CC-001','ChasePlus Credit Card Holder with RFID Protection GLASGOW','fucujr','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:10:42.722937','2025-09-01 08:10:42.722954',23,0,0,''),
('TR-CT-001','Custom Travel Mugs | Promotional Coffee Mug & Branded Travel Mug Dubai','A durable and practical promotional item, the custom travel mug is perfect for everyday use, corporate giveaways, and branding campaigns. Whether used as a travel coffee mug or branded travel mug, it offers consistent visibility for your brand in Dubai and across the UAE. With its sleek design and reusable build, this travel mug ensures both functionality and long-term promotional impact.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 07:50:09.462148','2025-09-01 07:50:09.462163',74,4,0,''),
('TR-CW-001','Custom White Luggage Tags Printing in Dubai','<p>A small, useful item used for business trips, or as a tourist. Whether used as a luggage tag or bag tag, this luggage tag makes a thoughtful corporate gift in Dubai and across the UAE. The luggage tag, also called a bag tag or custom suitcase accessory, is great for hotels, airlines, travel agencies, and corporate teams because it combines usefulness with marketing power to keep brand awareness high around the world.</p>\n<h2 dir=\"ltr\"><span>Key features</span><b></b></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong> </span><span>PU leather PVC or silicone, with the buckle strap secured as well as an identification window.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use:</strong><span> Excellent to promote travel and corporate gifts with 2-3 working days or delivery on the same day.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span>Design: </span><span>A sleek, flexible design with clear information slots and a strong attachment.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Best for: </strong></span><span>Campaigning for travel and hospitality branding, as well as promotional giveaways for events and even employee kits</span><span>.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability:</strong><span> Long-lasting, waterproof and durable, featuring high-quality imprints or embossed logos.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"></p>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span> </span><span>UV printing applies vibrant, full-color artwork directly onto PVC, PU leather, or silicone luggage tags. It ensures your branding remains bright and scratch-resistant, perfect for global exposure on travel accessories.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span><strong> </strong>Silk screen printing deposits one or two solid colors onto the tag&rsquo;s surface, offering clear, long-lasting branding. It\'s an excellent choice for large orders needing budget-friendly yet impactful customization.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Debossing (Leather):</strong><span> Debossing presses your logo into the leather surface, creating a recessed, tactile effect. This technique gives the luggage tag a refined, premium appearance suitable for executive gifts and upscale campaigns.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your Luggage Tag,&nbsp; fast delivery across Dubai and the UAE.</span></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:07:06.723929','2025-09-04 12:13:07.308429',105,0,0,''),
('TR-DS-001','Durable stainless steel travel mugs','<p dir=\"ltr\"><span>A long-lasting, practical gift for travellers and those who live an active lifestyle, ideal for daily use and consistent brand exposure. This </span><span>travel mug</span><span> doubles as a </span><span>travel coffee mug</span><span> and makes a great </span><span>branded travel mug</span><span> for marketing and gifting purposes.</span></p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material:</strong></span><strong> </strong><span>Double-wall stainless steel to ensure temperature retention and long-term durability.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong></span><strong> </strong><span>Perfect for portable branding and gifting, with a minimum of 3-4 working days, or even same-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design:</strong></span><strong> </strong><span>Sleek, spill-proof design with a lid that is secure with ergonomic grip.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for:</strong></span><strong> </strong><span>Corporate gifting promotional travel health and fitness programs, as well as regular commuters.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability: </strong><span>Rust-resistant, long-lasting with premium branding that can stand up to everyday usage.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding Methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span><br></span><span> UV printing uses ultraviolet light to cure full-color graphics directly onto the stainless steel surface. On the travel mug, this method provides a vibrant and durable finish that can withstand daily use, making it ideal for colorful branding that lasts.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV DTF Printing:</strong><span><br></span><span> UV DTF printing uses a UV-cured transfer film to wrap detailed, multi-color artwork around the mug&rsquo;s body. It&rsquo;s perfect for complex logos, patterns, or full-wrap designs, delivering a high-impact result without compromising the mug&rsquo;s sleek appearance.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span><br></span><span> Silk screen printing applies one or two solid colors onto the metal surface using a mesh stencil. This technique is great for bold, straightforward logos and offers a cost-effective solution for consistent branding across bulk orders.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Laser Engraving:</strong><span><br></span><span> Laser engraving permanently etches your logo or message into the stainless steel, creating a clean, premium look that won&rsquo;t fade or peel. It&rsquo;s ideal for high-end branding where a subtle, long-lasting finish is essential.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Contact us today to customize your stainless steel travel mug, fast delivery across Dubai and the UAE.</span></p>\n<p></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-03 13:08:57.645794','2025-09-04 11:25:05.725412',69,0,0,''),
('TR-DW-001','Double Wall Tumblers 473ml with Flip-Top PP Lid | Custom Travel Tumblers Dubai','A sleek and functional promotional item, these double wall tumblers with flip-top PP lid (473ml) are designed to keep beverages hot or cold while showcasing your brand in style. With their spill-proof design and durable build, they’re ideal for travel, office use, and giveaways. Popular across Dubai and the UAE, these tumblers combine practicality with branding power, making them a smart choice for corporate campaigns and retail promotions.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 11:55:58.671319','2025-09-01 11:55:58.671337',70,4.5,0,''),
('TR-DW-002','Double Wall Stainless Steel Tumblers 591ml with Slide-Lock PP Lid | Custom Travel Tumblers Dubai','Premium and practical, these double wall stainless steel tumblers with slide-lock PP lid (591ml) are designed for long-lasting temperature control and everyday convenience. With their spill-resistant slide-lock design and large capacity, they’re perfect for coffee, tea, or cold beverages on the go. Widely used across Dubai and the UAE, these tumblers make excellent corporate giveaways, wellness gifts, and retail promotional items.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:00:22.745413','2025-09-01 12:03:05.305924',71,5,0,''),
('TR-LT-001','LED Temperature Display Black Tumblers 510ml Stainless Steel | Smart Custom Tumblers Dubai','Modern and innovative, these LED temperature display black tumblers (510ml) in stainless steel are designed for smart hydration and stylish branding. Featuring a built-in LED temperature display on the lid, they let users check drink temperature instantly while showcasing your brand. Popular across Dubai and the UAE, these premium tumblers make excellent corporate gifts, tech-savvy giveaways, and promotional items for modern brands.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:06:27.299349','2025-09-01 12:06:27.299361',72,4.5,0,''),
('TR-PT-001','Promotional Travel Mugs | Custom Coffee Mug & Branded Travel Mug Dubai','A practical and stylish promotional gift, these promotional travel mugs are designed to maximize brand exposure while offering everyday convenience. Perfect for corporate giveaways, event sponsorships, and retail campaigns, these mugs function as both travel coffee mugs and branded promotional items. Widely used in Dubai and across the UAE, they combine portability, durability, and high-impact branding to keep your logo visible on the go.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 07:54:24.513904','2025-09-01 07:54:24.513917',75,4.5,0,''),
('TR-TT-001','Travel Tumbler with Cork Base 450ml Stainless Steel | Ramadan Corporate Gifts Dubai','Elegant and practical, this travel tumbler with cork base (450ml) stainless steel makes a thoughtful choice for Ramadan gifts and corporate giveaways. The stainless steel body keeps drinks hot or cold, while the natural cork base adds grip, insulation, and eco-friendly appeal. Popular across Dubai and the UAE, these tumblers combine style with function, making them ideal for Ramadan promotions, wellness campaigns, and everyday branding.','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 12:10:47.285686','2025-09-01 12:10:47.285698',73,4,0,''),
('UN-CH-001','Custom High-Visibility Safety Vests Dubai & UAE','dfghyj','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:28:05.074966','2025-09-01 08:28:05.074988',48,0,0,''),
('UN-PC-001','Personalized Cotton Aprons with Embroidery','hhhhj','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 08:04:24.993079','2025-09-01 08:04:24.993102',49,0,0,''),
('WO-BW-001','Branded Wooden Pens','<p>A stylish, eco-friendly pen that is great for green marketing, corporate gifts, and campaigns that focus on sustainability. Whether used as a stylus pen, this bamboo pen makes a thoughtful corporate gift in Dubai and across the UAE. This pen gift is perfect for making a lasting impression while supporting environmentally responsible branding.</p>\n<h2 dir=\"ltr\"><span>Key features</span></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Material: </strong></span><span>Sustainable bamboo that has an organic, natural appeal.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Use: </strong><span>It\'s perfect for eco-friendly campaigns, gifting and green advertising that take 2-3 days to deliver or next-day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Design: </strong></span><span>Smooth writing experience, with a comfy grasp and elegant look.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for</strong>:</span><span> Corporate gifts, education events and trade exhibitions.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Durability</strong><span><strong>:</strong> Durable, durable construction with a long-lasting imprint thanks to UV or laser branding.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"></p>\n<h3 dir=\"ltr\"><strong>Branding Methods:</strong></h3>\n<p dir=\"ltr\"></p>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing):</strong><span><strong> </strong>UV printing uses ultraviolet light to apply full-color artwork directly onto the bamboo barrel. This method blends vibrant visuals with the pen&rsquo;s natural wood grain, making it ideal for eco-conscious brands that want colorful, eye-catching designs without compromising sustainability.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> </span><span>Silk screen printing applies one or two solid ink colors onto the bamboo using a mesh stencil. On the Bamboo Pen, it delivers a clean, minimalistic look that highlights simplicity while offering a cost-effective branding solution for green campaigns or large-scale promotions.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Laser Engraving:</strong><span> </span><span>Laser engraving etches your logo or message directly into the bamboo surface using a precision laser beam. It creates a rustic, permanent mark that aligns perfectly with the pen&rsquo;s organic material, ideal for brands that want to emphasize authenticity and eco responsibility.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>Contact us today to customise your Bamboo Pen, fast delivery across Dubai and the UAE.</span></p>\n<p dir=\"ltr\"></p>\n<p></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:22:19.821913','2025-09-04 10:48:09.994331',58,0,0,''),
('WO-EC-001','Executive Colored Pencil Set with Wooden Box','edrftgyh','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-01 06:29:30.108662','2025-09-01 06:29:30.108676',59,0,0,''),
('WO-EF-001','Eco-friendly wooden pencil sets','<p>An eco-friendly promotional item suitable for schools, workshops, and sustainability-themed events. Great for brands that want to show they care about the environment. This wooden pencil set is a perfect choice for anyone looking to promote their brand through the best pencil options in eco-conscious stationery.</p>\n<h2 dir=\"ltr\"><strong>Key features:</strong></h2>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Material:</strong><span> </span><span>Natural wood for a classic, eco-friendly finish.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Use:</strong></span><strong> </strong><span>Ideal for offices, schools or for giveaways that take 2 to 3 working days or the same day delivery.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Design: </strong><span>A soft graphite core that has a polished finish. an easy grip.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Perfect for: </strong></span><span>Kits for education and branding, art shows and sustainability-based promotions.</span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><span><strong>Durability:</strong></span><strong> </strong><span>Built with strength, high-quality performance and long-lasting branding alternatives.</span></p>\n</li>\n</ul>\n<h3 dir=\"ltr\"><span>Branding methods</span></h3>\n<ul>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>UV Printing (Direct Printing): </strong><span>UV printing allows us to apply full-color artwork directly onto the wooden pencil using ultraviolet light to instantly cure the ink. This method retains the natural wood grain while adding vivid, high-resolution details&mdash;perfect for logos or designs that require both clarity and visual impact on eco-conscious products.</span><span><br><br></span></p>\n</li>\n<li dir=\"ltr\" aria-level=\"1\">\n<p dir=\"ltr\" role=\"presentation\"><strong>Silk Screen Printing:</strong><span> </span><span>&nbsp;Silk screen printing uses a mesh stencil to apply one or two solid colors along the length of the pencil. It&rsquo;s ideal for simple branding like bold logos or text, especially in large quantities. On the Wooden Pencil Set, this method provides consistent and durable branding that complements its natural, sustainable look.</span></p>\n</li>\n</ul>\n<p dir=\"ltr\"><span>Contact us today to customize your Wooden Pencil Set, fast delivery across Dubai and the UAE.</span></p>\n<p></p>','',0.00,0.00,0,'','','active','SuperAdmin','admin','2025-09-03 13:05:04.512238','2025-09-04 10:43:03.218618',57,0,0,'');
/*!40000 ALTER TABLE `admin_backend_final_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_productimage`
--

DROP TABLE IF EXISTS `admin_backend_final_productimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_productimage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `image_id` varchar(100) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  `caption` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_backend_final__image_id_50100b2e_fk_admin_bac` (`image_id`),
  KEY `admin_backend_final__product_id_4fd00f52_fk_admin_bac` (`product_id`),
  CONSTRAINT `admin_backend_final__image_id_50100b2e_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`),
  CONSTRAINT `admin_backend_final__product_id_4fd00f52_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1168 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_productimage`
--

LOCK TABLES `admin_backend_final_productimage` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_productimage` DISABLE KEYS */;
INSERT INTO `admin_backend_final_productimage` VALUES
(437,'2025-09-01 06:14:41.100802',0,'IMG-1cd04b7d','BA-BA-001',''),
(438,'2025-09-01 06:14:41.103026',0,'IMG-41eed264','BA-BA-001',''),
(439,'2025-09-01 06:14:41.105712',0,'IMG-2ebfef2b','BA-BA-001',''),
(440,'2025-09-01 06:14:41.107927',0,'IMG-500a553f','BA-BA-001',''),
(441,'2025-09-01 06:14:41.110661',0,'IMG-dcc3ff2c','BA-BA-001',''),
(442,'2025-09-01 06:14:41.112846',0,'IMG-efe4de17','BA-BA-001',''),
(443,'2025-09-01 06:22:17.263237',0,'IMG-d64bff64','BA-MC-001',''),
(444,'2025-09-01 06:22:17.265306',0,'IMG-b4e2bc85','BA-MC-001',''),
(445,'2025-09-01 06:22:17.267476',0,'IMG-7f14cfee','BA-MC-001',''),
(446,'2025-09-01 06:22:17.269477',0,'IMG-bc15618a','BA-MC-001',''),
(447,'2025-09-01 06:22:17.271414',0,'IMG-369f26d9','BA-MC-001',''),
(448,'2025-09-01 06:22:17.273413',0,'IMG-3c52bb72','BA-MC-001',''),
(449,'2025-09-01 06:22:19.835000',0,'IMG-89bfe62e','WO-BW-001',''),
(450,'2025-09-01 06:22:19.837576',0,'IMG-ac78a314','WO-BW-001',''),
(451,'2025-09-01 06:22:19.840168',0,'IMG-6802c018','WO-BW-001',''),
(452,'2025-09-01 06:22:19.842737',0,'IMG-e972c837','WO-BW-001',''),
(453,'2025-09-01 06:22:19.845337',0,'IMG-df357fa5','WO-BW-001',''),
(454,'2025-09-01 06:22:19.847960',0,'IMG-e1931548','WO-BW-001',''),
(455,'2025-09-01 06:24:30.070457',0,'IMG-98879c49','GI-LP-001',''),
(456,'2025-09-01 06:24:30.079958',0,'IMG-69fcb131','GI-LP-001',''),
(457,'2025-09-01 06:24:30.086555',0,'IMG-3bc78bd4','GI-LP-001',''),
(458,'2025-09-01 06:24:30.092251',0,'IMG-c85a56ba','GI-LP-001',''),
(459,'2025-09-01 06:24:30.098090',0,'IMG-18a079b8','GI-LP-001',''),
(460,'2025-09-01 06:24:30.103115',0,'IMG-d5ec4353','GI-LP-001',''),
(461,'2025-09-01 06:24:50.900859',0,'IMG-358d9b82','BA-EC-001',''),
(462,'2025-09-01 06:24:50.903671',0,'IMG-8a9e908c','BA-EC-001',''),
(463,'2025-09-01 06:24:50.907324',0,'IMG-8a6b07a1','BA-EC-001',''),
(464,'2025-09-01 06:24:50.909182',0,'IMG-c367948d','BA-EC-001',''),
(465,'2025-09-01 06:24:50.912188',0,'IMG-f355d515','BA-EC-001',''),
(466,'2025-09-01 06:24:50.914372',0,'IMG-97e03640','BA-EC-001',''),
(467,'2025-09-01 06:27:33.388305',0,'IMG-7c498fc2','PL-SM-001',''),
(468,'2025-09-01 06:27:33.390936',0,'IMG-53b05885','PL-SM-001',''),
(469,'2025-09-01 06:27:33.392763',0,'IMG-3f7aac6d','PL-SM-001',''),
(470,'2025-09-01 06:27:33.394589',0,'IMG-b61ccc41','PL-SM-001',''),
(471,'2025-09-01 06:27:33.397022',0,'IMG-7538c760','PL-SM-001',''),
(472,'2025-09-01 06:27:33.403469',0,'IMG-babaedf9','PL-SM-001',''),
(473,'2025-09-01 06:29:30.119238',0,'IMG-4dadea86','WO-EC-001',''),
(474,'2025-09-01 06:29:30.121303',0,'IMG-654a20fb','WO-EC-001',''),
(475,'2025-09-01 06:29:30.123490',0,'IMG-e783811f','WO-EC-001',''),
(476,'2025-09-01 06:29:30.125500',0,'IMG-e27d60be','WO-EC-001',''),
(477,'2025-09-01 06:31:13.160255',0,'IMG-a189fe32','BA-EC-002',''),
(478,'2025-09-01 06:31:13.163315',0,'IMG-a699a20c','BA-EC-002',''),
(479,'2025-09-01 06:31:13.165543',0,'IMG-2997f25c','BA-EC-002',''),
(480,'2025-09-01 06:31:13.167613',0,'IMG-8d1b9a64','BA-EC-002',''),
(481,'2025-09-01 06:31:13.169614',0,'IMG-6614dce2','BA-EC-002',''),
(482,'2025-09-01 06:31:13.171711',0,'IMG-bd03fa83','BA-EC-002',''),
(483,'2025-09-01 06:32:55.777428',0,'IMG-dbd55727','EV-SC-001',''),
(484,'2025-09-01 06:32:55.784785',0,'IMG-83f98cfb','EV-SC-001',''),
(485,'2025-09-01 06:32:55.787901',0,'IMG-ad2561f7','EV-SC-001',''),
(486,'2025-09-01 06:32:55.790990',0,'IMG-4d31882b','EV-SC-001',''),
(487,'2025-09-01 06:38:34.676907',0,'IMG-08549a12','CO-BE-001',''),
(488,'2025-09-01 06:38:34.679104',0,'IMG-8fe5c707','CO-BE-001',''),
(489,'2025-09-01 06:38:34.680973',0,'IMG-16ca3651','CO-BE-001',''),
(490,'2025-09-01 06:38:34.682775',0,'IMG-ce43d0d6','CO-BE-001',''),
(491,'2025-09-01 06:38:34.684563',0,'IMG-6d77c983','CO-BE-001',''),
(492,'2025-09-01 06:38:34.687423',0,'IMG-be808af9','CO-BE-001',''),
(493,'2025-09-01 06:44:22.466565',0,'IMG-68c4468c','CO-CL-001',''),
(494,'2025-09-01 06:44:22.468359',0,'IMG-bc851705','CO-CL-001',''),
(495,'2025-09-01 06:44:22.470830',0,'IMG-b5dd9d85','CO-CL-001',''),
(496,'2025-09-01 06:44:22.472620',0,'IMG-fd195f64','CO-CL-001',''),
(497,'2025-09-01 06:44:22.474373',0,'IMG-ebffc30c','CO-CL-001',''),
(498,'2025-09-01 06:44:22.476113',0,'IMG-f844ef78','CO-CL-001',''),
(499,'2025-09-01 06:50:01.394161',0,'IMG-fd561462','CO-CC-001',''),
(500,'2025-09-01 06:50:01.397147',0,'IMG-667a30ef','CO-CC-001',''),
(501,'2025-09-01 06:50:01.400222',0,'IMG-2bdd130b','CO-CC-001',''),
(502,'2025-09-01 06:50:01.402658',0,'IMG-7c325476','CO-CC-001',''),
(503,'2025-09-01 06:50:01.404934',0,'IMG-c1d81296','CO-CC-001',''),
(504,'2025-09-01 06:50:01.407147',0,'IMG-9a1a2d60','CO-CC-001',''),
(505,'2025-09-01 06:52:00.851383',0,'IMG-6ddf0d9a','PO-HC-001',''),
(506,'2025-09-01 06:52:00.853622',0,'IMG-8f3eff4b','PO-HC-001',''),
(507,'2025-09-01 06:52:00.856709',0,'IMG-f5670c89','PO-HC-001',''),
(508,'2025-09-01 06:52:00.859311',0,'IMG-9deb33c4','PO-HC-001',''),
(509,'2025-09-01 06:52:00.861632',0,'IMG-7645a4bc','PO-HC-001',''),
(510,'2025-09-01 06:52:00.864109',0,'IMG-b48ff8e8','PO-HC-001',''),
(511,'2025-09-01 06:54:02.147577',0,'IMG-3c01d8a1','PO-BB-001',''),
(512,'2025-09-01 06:54:02.149872',0,'IMG-828a05b5','PO-BB-001',''),
(513,'2025-09-01 06:54:02.151748',0,'IMG-74a0dd0a','PO-BB-001',''),
(514,'2025-09-01 06:54:02.153579',0,'IMG-3e06507b','PO-BB-001',''),
(515,'2025-09-01 06:54:02.155579',0,'IMG-d7c50560','PO-BB-001',''),
(516,'2025-09-01 06:54:02.158146',0,'IMG-5f41d42c','PO-BB-001',''),
(517,'2025-09-01 06:56:25.390236',0,'IMG-7ce74dd1','PO-MD-001',''),
(518,'2025-09-01 06:56:25.392300',0,'IMG-bdd5c5a2','PO-MD-001',''),
(519,'2025-09-01 06:56:25.394894',0,'IMG-71c7cfdf','PO-MD-001',''),
(520,'2025-09-01 06:56:25.396947',0,'IMG-0fb58b53','PO-MD-001',''),
(521,'2025-09-01 06:56:25.399229',0,'IMG-6b29b145','PO-MD-001',''),
(522,'2025-09-01 06:56:25.401257',0,'IMG-48558fe5','PO-MD-001',''),
(528,'2025-09-01 07:04:51.892995',0,'IMG-ea14febd','EV-RJ-001',''),
(529,'2025-09-01 07:04:51.895126',0,'IMG-ef5cb0de','EV-RJ-001',''),
(530,'2025-09-01 07:04:51.897190',0,'IMG-f0a16988','EV-RJ-001',''),
(531,'2025-09-01 07:04:51.899331',0,'IMG-659ef9f1','EV-RJ-001',''),
(532,'2025-09-01 07:19:05.011838',0,'IMG-4471d1cc','EV-CJ-001',''),
(533,'2025-09-01 07:19:05.014219',0,'IMG-159565aa','EV-CJ-001',''),
(534,'2025-09-01 07:19:05.016336',0,'IMG-8cc8296d','EV-CJ-001',''),
(535,'2025-09-01 07:19:05.019009',0,'IMG-b8940c7e','EV-CJ-001',''),
(536,'2025-09-01 07:19:05.021115',0,'IMG-fcd19ce1','EV-CJ-001',''),
(537,'2025-09-01 07:19:05.023129',0,'IMG-e45abb16','EV-CJ-001',''),
(538,'2025-09-01 07:31:27.153150',0,'IMG-e52fbc38','EV-CJ-002',''),
(539,'2025-09-01 07:31:27.155329',0,'IMG-2b33afa9','EV-CJ-002',''),
(540,'2025-09-01 07:50:09.477032',0,'IMG-3ddb71cd','TR-CT-001',''),
(541,'2025-09-01 07:50:09.479042',0,'IMG-84e5a747','TR-CT-001',''),
(542,'2025-09-01 07:50:09.480828',0,'IMG-4f221bd1','TR-CT-001',''),
(543,'2025-09-01 07:50:09.482596',0,'IMG-5219a9aa','TR-CT-001',''),
(544,'2025-09-01 07:52:59.448843',0,'IMG-f619dc9c','EV-CJ-003',''),
(545,'2025-09-01 07:52:59.450916',0,'IMG-d33ffa7b','EV-CJ-003',''),
(546,'2025-09-01 07:52:59.452749',0,'IMG-8e8a12b3','EV-CJ-003',''),
(547,'2025-09-01 07:54:24.526287',0,'IMG-cd289b90','TR-PT-001',''),
(548,'2025-09-01 07:54:24.528325',0,'IMG-94829de1','TR-PT-001',''),
(549,'2025-09-01 07:54:24.530674',0,'IMG-b1a23b0e','TR-PT-001',''),
(550,'2025-09-01 07:54:24.532599',0,'IMG-9d0cd24d','TR-PT-001',''),
(551,'2025-09-01 07:54:24.534479',0,'IMG-fcd78f5d','TR-PT-001',''),
(552,'2025-09-01 07:59:30.663944',0,'IMG-8e28d2ef','CE-MC-001',''),
(553,'2025-09-01 07:59:30.665879',0,'IMG-baee5290','CE-MC-001',''),
(554,'2025-09-01 07:59:30.667655',0,'IMG-7f2278b4','CE-MC-001',''),
(555,'2025-09-01 07:59:30.669418',0,'IMG-c5a566a2','CE-MC-001',''),
(556,'2025-09-01 08:01:45.617991',0,'IMG-d1a4ea45','EV-VN-001',''),
(557,'2025-09-01 08:01:45.619984',0,'IMG-3664f11d','EV-VN-001',''),
(558,'2025-09-01 08:01:45.621908',0,'IMG-6a0e10fa','EV-VN-001',''),
(559,'2025-09-01 08:01:45.623773',0,'IMG-1918c9ce','EV-VN-001',''),
(560,'2025-09-01 08:01:45.625694',0,'IMG-199cb2a3','EV-VN-001',''),
(561,'2025-09-01 08:01:45.627627',0,'IMG-679aa922','EV-VN-001',''),
(562,'2025-09-01 08:04:25.006284',0,'IMG-ae636d4b','UN-PC-001',''),
(563,'2025-09-01 08:04:25.008768',0,'IMG-48298749','UN-PC-001',''),
(564,'2025-09-01 08:04:25.012421',0,'IMG-16b44dda','UN-PC-001',''),
(565,'2025-09-01 08:04:31.883747',0,'IMG-4319fcf9','EV-RV-001',''),
(566,'2025-09-01 08:04:31.885728',0,'IMG-17407275','EV-RV-001',''),
(573,'2025-09-01 08:07:06.737609',0,'IMG-d98123ca','TR-CW-001',''),
(574,'2025-09-01 08:07:06.739898',0,'IMG-6a6d3891','TR-CW-001',''),
(575,'2025-09-01 08:07:35.352006',0,'IMG-3337e230','CE-CG-001',''),
(576,'2025-09-01 08:07:35.353874',0,'IMG-575d2f43','CE-CG-001',''),
(577,'2025-09-01 08:07:35.355665',0,'IMG-6838e974','CE-CG-001',''),
(578,'2025-09-01 08:07:35.357521',0,'IMG-0d9f4c4b','CE-CG-001',''),
(579,'2025-09-01 08:08:19.100616',0,'IMG-d9c66a32','AC-CC-001',''),
(580,'2025-09-01 08:08:19.102577',0,'IMG-ea73bfd9','AC-CC-001',''),
(581,'2025-09-01 08:08:19.104975',0,'IMG-99862e54','AC-CC-001',''),
(582,'2025-09-01 08:08:19.106909',0,'IMG-0d389188','AC-CC-001',''),
(583,'2025-09-01 08:08:19.108741',0,'IMG-6b749965','AC-CC-001',''),
(584,'2025-09-01 08:09:50.077078',0,'IMG-35c206e9','AC-EU-001',''),
(585,'2025-09-01 08:09:50.079286',0,'IMG-4bb94150','AC-EU-001',''),
(586,'2025-09-01 08:10:42.737728',0,'IMG-4672ac1d','TR-CC-001',''),
(587,'2025-09-01 08:10:42.743419',0,'IMG-1aa9d885','TR-CC-001',''),
(588,'2025-09-01 08:10:42.748738',0,'IMG-c5dc32c0','TR-CC-001',''),
(589,'2025-09-01 08:10:42.754176',0,'IMG-75f1f9a7','TR-CC-001',''),
(590,'2025-09-01 08:10:42.759160',0,'IMG-c530670a','TR-CC-001',''),
(603,'2025-09-01 08:13:41.690943',0,'IMG-246f53e9','BR-CP-001',''),
(604,'2025-09-01 08:13:41.692924',0,'IMG-7e382c65','BR-CP-001',''),
(605,'2025-09-01 08:13:41.694910',0,'IMG-bc41f433','BR-CP-001',''),
(606,'2025-09-01 08:14:06.500314',0,'IMG-461245fb','CE-WC-001',''),
(607,'2025-09-01 08:14:06.502696',0,'IMG-d800f7e3','CE-WC-001',''),
(608,'2025-09-01 08:14:06.505427',0,'IMG-4af10ebd','CE-WC-001',''),
(609,'2025-09-01 08:14:06.507892',0,'IMG-466857fc','CE-WC-001',''),
(610,'2025-09-01 08:14:06.510283',0,'IMG-17e568db','CE-WC-001',''),
(611,'2025-09-01 08:14:06.512515',0,'IMG-5061fa9d','CE-WC-001',''),
(612,'2025-09-01 08:14:06.514434',0,'IMG-cd9e1ee7','CE-WC-001',''),
(613,'2025-09-01 08:14:06.516490',0,'IMG-64395d03','CE-WC-001',''),
(614,'2025-09-01 08:14:06.518644',0,'IMG-4491b2b6','CE-WC-001',''),
(624,'2025-09-01 08:18:56.296267',0,'IMG-f77966a0','CE-BS-001',''),
(625,'2025-09-01 08:18:56.298290',0,'IMG-1557d4e9','CE-BS-001',''),
(626,'2025-09-01 08:18:56.300634',0,'IMG-9b8dcf07','CE-BS-001',''),
(627,'2025-09-01 08:18:56.302568',0,'IMG-e99efd16','CE-BS-001',''),
(628,'2025-09-01 08:18:56.304648',0,'IMG-1498ba93','CE-BS-001',''),
(629,'2025-09-01 08:18:56.306589',0,'IMG-ad8c60df','CE-BS-001',''),
(630,'2025-09-01 08:18:56.308604',0,'IMG-3f218c43','CE-BS-001',''),
(631,'2025-09-01 08:20:03.123118',0,'IMG-3d2264ab','BR-CM-001',''),
(632,'2025-09-01 08:20:03.125104',0,'IMG-11e169da','BR-CM-001',''),
(633,'2025-09-01 08:20:03.127007',0,'IMG-b6cfd82b','BR-CM-001',''),
(634,'2025-09-01 08:20:03.128835',0,'IMG-c03eb01d','BR-CM-001',''),
(635,'2025-09-01 08:20:03.130700',0,'IMG-f802f2fc','BR-CM-001',''),
(636,'2025-09-01 08:21:39.589912',0,'IMG-5d1d3732','AC-CP-001',''),
(637,'2025-09-01 08:21:39.591873',0,'IMG-364f36f6','AC-CP-001',''),
(638,'2025-09-01 08:21:39.593636',0,'IMG-faa59694','AC-CP-001',''),
(639,'2025-09-01 08:21:39.595696',0,'IMG-0c616e3d','AC-CP-001',''),
(640,'2025-09-01 08:21:39.597875',0,'IMG-ec10886f','AC-CP-001',''),
(641,'2025-09-01 08:21:39.600895',0,'IMG-7761582f','AC-CP-001',''),
(645,'2025-09-01 08:23:31.499839',0,'IMG-3a7dba1c','AC-WA-001',''),
(646,'2025-09-01 08:23:31.501578',0,'IMG-13f7b170','AC-WA-001',''),
(647,'2025-09-01 08:23:31.503376',0,'IMG-67545d12','AC-WA-001',''),
(648,'2025-09-01 08:23:31.505206',0,'IMG-1790e8c6','AC-WA-001',''),
(649,'2025-09-01 08:23:31.507073',0,'IMG-70bc8e44','AC-WA-001',''),
(650,'2025-09-01 08:23:31.508843',0,'IMG-d9adb4c5','AC-WA-001',''),
(651,'2025-09-01 08:23:54.309066',0,'IMG-89b74a01','CE-CE-001',''),
(652,'2025-09-01 08:23:54.310767',0,'IMG-553b12d9','CE-CE-001',''),
(653,'2025-09-01 08:23:54.312400',0,'IMG-721ceacf','CE-CE-001',''),
(654,'2025-09-01 08:24:54.976009',0,'IMG-b1523439','BR-PG-001',''),
(655,'2025-09-01 08:24:54.984828',0,'IMG-35bb3c10','BR-PG-001',''),
(656,'2025-09-01 08:24:54.988600',0,'IMG-62b5e27a','BR-PG-001',''),
(658,'2025-09-01 08:28:05.085458',0,'IMG-e5b5fe4e','UN-CH-001',''),
(659,'2025-09-01 08:28:05.087496',0,'IMG-cb405a1c','UN-CH-001',''),
(660,'2025-09-01 08:28:05.089404',0,'IMG-39068fca','UN-CH-001',''),
(661,'2025-09-01 08:29:05.903885',0,'IMG-fb22c7e3','BR-PE-001',''),
(662,'2025-09-01 08:29:05.906859',0,'IMG-f79ab9c9','BR-PE-001',''),
(663,'2025-09-01 08:29:05.913359',0,'IMG-34a4a948','BR-PE-001',''),
(664,'2025-09-01 08:34:20.724649',0,'IMG-fb065cbe','CE-PM-001',''),
(665,'2025-09-01 08:34:20.726754',0,'IMG-c29428fc','CE-PM-001',''),
(666,'2025-09-01 08:34:20.728888',0,'IMG-f61d3086','CE-PM-001',''),
(667,'2025-09-01 08:34:53.201067',0,'IMG-7ab332e8','BR-CR-001',''),
(668,'2025-09-01 08:34:53.203271',0,'IMG-1afac751','BR-CR-001',''),
(669,'2025-09-01 08:34:53.205477',0,'IMG-d21e63ff','BR-CR-001',''),
(670,'2025-09-01 08:34:53.207477',0,'IMG-2b630fd5','BR-CR-001',''),
(671,'2025-09-01 08:34:53.209301',0,'IMG-a4958986','BR-CR-001',''),
(672,'2025-09-01 08:38:07.654858',0,'IMG-a836833d','BR-CA-001',''),
(673,'2025-09-01 08:38:07.657009',0,'IMG-e91d5a1b','BR-CA-001',''),
(674,'2025-09-01 08:38:07.658891',0,'IMG-148c3f94','BR-CA-001',''),
(675,'2025-09-01 08:38:07.660663',0,'IMG-0c1dccb5','BR-CA-001',''),
(676,'2025-09-01 08:38:07.662509',0,'IMG-8cd146bb','BR-CA-001',''),
(677,'2025-09-01 08:38:07.664389',0,'IMG-bfc216f5','BR-CA-001',''),
(678,'2025-09-01 08:41:07.077148',0,'IMG-bc983ddb','CE-WC-002',''),
(679,'2025-09-01 08:41:07.078988',0,'IMG-1f29c190','CE-WC-002',''),
(680,'2025-09-01 08:41:07.081024',0,'IMG-928b28ce','CE-WC-002',''),
(681,'2025-09-01 08:41:07.082925',0,'IMG-22b943a3','CE-WC-002',''),
(692,'2025-09-01 08:47:14.771546',0,'IMG-1f88b890','CE-TT-001',''),
(693,'2025-09-01 08:47:14.773556',0,'IMG-c97a3e4c','CE-TT-001',''),
(694,'2025-09-01 08:47:14.775587',0,'IMG-354ff69f','CE-TT-001',''),
(695,'2025-09-01 08:47:14.777598',0,'IMG-4a1544af','CE-TT-001',''),
(696,'2025-09-01 08:47:14.779701',0,'IMG-c91a529a','CE-TT-001',''),
(697,'2025-09-01 08:47:14.781712',0,'IMG-c4a99238','CE-TT-001',''),
(708,'2025-09-01 08:55:48.145996',0,'IMG-a186b8cf','CE-CC-001',''),
(709,'2025-09-01 08:55:48.148587',0,'IMG-98329af8','CE-CC-001',''),
(710,'2025-09-01 08:55:48.150459',0,'IMG-4c4b4a3f','CE-CC-001',''),
(711,'2025-09-01 08:55:48.152299',0,'IMG-c63feac7','CE-CC-001',''),
(712,'2025-09-01 08:55:48.154119',0,'IMG-7ff3975c','CE-CC-001',''),
(713,'2025-09-01 08:55:48.156110',0,'IMG-6d142d84','CE-CC-001',''),
(714,'2025-09-01 08:55:48.158020',0,'IMG-68d44310','CE-CC-001',''),
(715,'2025-09-01 08:55:48.159835',0,'IMG-6e5adecb','CE-CC-001',''),
(716,'2025-09-01 08:55:48.162007',0,'IMG-f34d7616','CE-CC-001',''),
(731,'2025-09-01 09:04:01.016618',0,'IMG-bf8671c9','CE-GB-001',''),
(732,'2025-09-01 09:04:01.018646',0,'IMG-4267efed','CE-GB-001',''),
(733,'2025-09-01 09:04:01.020642',0,'IMG-831826fc','CE-GB-001',''),
(734,'2025-09-01 09:09:17.539794',0,'IMG-ce5b425a','CE-WS-001',''),
(735,'2025-09-01 09:09:17.541633',0,'IMG-9d244602','CE-WS-001',''),
(736,'2025-09-01 09:09:17.543304',0,'IMG-885c5232','CE-WS-001',''),
(737,'2025-09-01 09:09:17.544992',0,'IMG-7323ea7e','CE-WS-001',''),
(738,'2025-09-01 09:09:17.546768',0,'IMG-1f7eb1f3','CE-WS-001',''),
(739,'2025-09-01 09:12:16.140069',0,'IMG-8c9d6f93','CE-GC-001',''),
(740,'2025-09-01 09:12:16.142122',0,'IMG-5f2c2964','CE-GC-001',''),
(741,'2025-09-01 09:12:16.143906',0,'IMG-b16081be','CE-GC-001',''),
(742,'2025-09-01 09:19:55.170745',0,'IMG-d16033af','CE-TT-002',''),
(743,'2025-09-01 09:19:55.172565',0,'IMG-078aa2bf','CE-TT-002',''),
(744,'2025-09-01 09:19:55.174484',0,'IMG-8bb0daf5','CE-TT-002',''),
(745,'2025-09-01 09:19:55.176305',0,'IMG-e5970917','CE-TT-002',''),
(746,'2025-09-01 09:19:55.178240',0,'IMG-85f2c99d','CE-TT-002',''),
(747,'2025-09-01 09:19:55.180083',0,'IMG-f5cf819c','CE-TT-002',''),
(748,'2025-09-01 09:19:55.182998',0,'IMG-6a5a85a4','CE-TT-002',''),
(749,'2025-09-01 09:19:55.184807',0,'IMG-bd2b0a51','CE-TT-002',''),
(750,'2025-09-01 09:24:05.823265',0,'IMG-d4653943','CE-PC-001',''),
(751,'2025-09-01 09:24:05.825004',0,'IMG-71ef152d','CE-PC-001',''),
(752,'2025-09-01 09:24:05.826751',0,'IMG-34a0b93a','CE-PC-001',''),
(753,'2025-09-01 09:32:14.759856',0,'IMG-34280d49','CE-CM-001',''),
(754,'2025-09-01 09:32:14.768152',0,'IMG-cbbfa155','CE-CM-001',''),
(755,'2025-09-01 09:32:14.772351',0,'IMG-ce7655df','CE-CM-001',''),
(756,'2025-09-01 09:32:14.776185',0,'IMG-8aa6f019','CE-CM-001',''),
(757,'2025-09-01 09:41:51.586532',0,'IMG-c601ccc7','CE-TT-003',''),
(758,'2025-09-01 09:41:51.588770',0,'IMG-5c419ff2','CE-TT-003',''),
(759,'2025-09-01 09:41:51.592382',0,'IMG-82107623','CE-TT-003',''),
(760,'2025-09-01 09:41:51.595579',0,'IMG-2a6d22a0','CE-TT-003',''),
(761,'2025-09-01 09:41:51.597424',0,'IMG-21bbb569','CE-TT-003',''),
(762,'2025-09-01 10:02:44.940376',0,'IMG-04f465d8','CE-BC-001',''),
(763,'2025-09-01 10:02:44.942282',0,'IMG-008d33de','CE-BC-001',''),
(764,'2025-09-01 10:08:07.437669',0,'IMG-b84cbb46','EV-LW-001',''),
(765,'2025-09-01 10:08:07.439770',0,'IMG-3b135005','EV-LW-001',''),
(766,'2025-09-01 10:08:07.441634',0,'IMG-8476f5ae','EV-LW-001',''),
(767,'2025-09-01 10:09:15.171904',0,'IMG-d153cd43','CE-WC-003',''),
(768,'2025-09-01 10:09:15.173681',0,'IMG-9d826841','CE-WC-003',''),
(769,'2025-09-01 10:09:15.175318',0,'IMG-fc7d4da0','CE-WC-003',''),
(770,'2025-09-01 10:10:07.073978',0,'IMG-04335be7','EV-CL-001',''),
(771,'2025-09-01 10:10:07.076307',0,'IMG-d6d970c8','EV-CL-001',''),
(772,'2025-09-01 10:10:07.078407',0,'IMG-f86c11e7','EV-CL-001',''),
(773,'2025-09-01 10:10:07.080466',0,'IMG-99eb4f8e','EV-CL-001',''),
(774,'2025-09-01 10:10:07.082468',0,'IMG-5f72ff19','EV-CL-001',''),
(775,'2025-09-01 10:10:07.084519',0,'IMG-78d1256d','EV-CL-001',''),
(776,'2025-09-01 10:11:31.284923',0,'IMG-4d4f4247','EV-DP-001',''),
(777,'2025-09-01 10:11:31.286938',0,'IMG-2cc81568','EV-DP-001',''),
(778,'2025-09-01 10:11:31.288820',0,'IMG-b70381cf','EV-DP-001',''),
(779,'2025-09-01 10:11:31.290700',0,'IMG-f9f9c44e','EV-DP-001',''),
(780,'2025-09-01 10:11:31.292749',0,'IMG-b6ffb142','EV-DP-001',''),
(781,'2025-09-01 10:13:10.530222',0,'IMG-7b5f8d9f','EV-TW-001',''),
(782,'2025-09-01 10:13:10.532000',0,'IMG-3f3ea6f7','EV-TW-001',''),
(783,'2025-09-01 10:13:10.533771',0,'IMG-a522fb04','EV-TW-001',''),
(784,'2025-09-01 10:13:10.535548',0,'IMG-00bf4ed2','EV-TW-001',''),
(785,'2025-09-01 10:13:10.537624',0,'IMG-1f606dfa','EV-TW-001',''),
(786,'2025-09-01 10:13:10.539670',0,'IMG-d861dac5','EV-TW-001',''),
(787,'2025-09-01 10:13:38.514740',0,'IMG-955072d4','CE-LM-001',''),
(788,'2025-09-01 10:13:38.516737',0,'IMG-c33d73cc','CE-LM-001',''),
(789,'2025-09-01 10:13:38.518575',0,'IMG-ed26f117','CE-LM-001',''),
(790,'2025-09-01 10:20:26.372241',0,'IMG-ef829147','CE-WS-002',''),
(791,'2025-09-01 10:20:26.374151',0,'IMG-fc597b89','CE-WS-002',''),
(792,'2025-09-01 10:20:26.375903',0,'IMG-2fe06a97','CE-WS-002',''),
(793,'2025-09-01 10:22:47.029437',0,'IMG-875034b4','DE-BF-001',''),
(794,'2025-09-01 10:22:47.038281',0,'IMG-3de67620','DE-BF-001',''),
(795,'2025-09-01 10:22:47.040783',0,'IMG-a5c0449c','DE-BF-001',''),
(796,'2025-09-01 10:22:47.042879',0,'IMG-00f08103','DE-BF-001',''),
(797,'2025-09-01 10:22:47.045340',0,'IMG-03c622ff','DE-BF-001',''),
(798,'2025-09-01 10:22:47.047402',0,'IMG-313428fd','DE-BF-001',''),
(799,'2025-09-01 10:26:26.200171',0,'IMG-ed4badac','DE-SF-001',''),
(800,'2025-09-01 10:26:26.202157',0,'IMG-13ccf61b','DE-SF-001',''),
(801,'2025-09-01 10:26:26.203916',0,'IMG-2a8ef7d0','DE-SF-001',''),
(802,'2025-09-01 10:26:26.205707',0,'IMG-dd50389b','DE-SF-001',''),
(803,'2025-09-01 10:26:26.207493',0,'IMG-c1db34d3','DE-SF-001',''),
(810,'2025-09-01 10:38:01.214680',0,'IMG-05e0edd6','SP-TB-001',''),
(811,'2025-09-01 10:38:01.216520',0,'IMG-e5f768e6','SP-TB-001',''),
(812,'2025-09-01 10:38:01.218408',0,'IMG-34eb3b15','SP-TB-001',''),
(813,'2025-09-01 10:38:01.220117',0,'IMG-89ab784e','SP-TB-001',''),
(814,'2025-09-01 10:38:01.221887',0,'IMG-611e83b8','SP-TB-001',''),
(815,'2025-09-01 10:44:45.888372',0,'IMG-91512092','SP-WB-001',''),
(816,'2025-09-01 10:44:45.890409',0,'IMG-39d8dd2e','SP-WB-001',''),
(817,'2025-09-01 10:44:45.892497',0,'IMG-bbd21882','SP-WB-001',''),
(818,'2025-09-01 10:44:45.894342',0,'IMG-a4e6352a','SP-WB-001',''),
(828,'2025-09-01 10:57:46.926513',0,'IMG-23a2f1c5','SP-PS-001',''),
(829,'2025-09-01 10:57:46.928561',0,'IMG-13063ec3','SP-PS-001',''),
(830,'2025-09-01 10:57:46.930508',0,'IMG-55569b5c','SP-PS-001',''),
(831,'2025-09-01 10:57:46.932774',0,'IMG-1c8930e0','SP-PS-001',''),
(832,'2025-09-01 10:57:46.935233',0,'IMG-c3431cdb','SP-PS-001',''),
(833,'2025-09-01 11:01:10.797210',0,'IMG-230422a4','CA-BC-001',''),
(834,'2025-09-01 11:01:10.799185',0,'IMG-4000a29d','CA-BC-001',''),
(835,'2025-09-01 11:01:10.801218',0,'IMG-365e8ff8','CA-BC-001',''),
(836,'2025-09-01 11:01:10.803211',0,'IMG-728ff72e','CA-BC-001',''),
(837,'2025-09-01 11:01:10.805136',0,'IMG-3065b02c','CA-BC-001',''),
(838,'2025-09-01 11:03:33.075369',0,'IMG-c47a8cb4','CA-SB-001',''),
(839,'2025-09-01 11:03:33.077329',0,'IMG-abe3d81b','CA-SB-001',''),
(840,'2025-09-01 11:03:33.079341',0,'IMG-c79095ac','CA-SB-001',''),
(841,'2025-09-01 11:03:33.081261',0,'IMG-f30263bf','CA-SB-001',''),
(842,'2025-09-01 11:05:36.362134',0,'IMG-cddb1a49','CA-2T-001',''),
(843,'2025-09-01 11:05:36.364083',0,'IMG-a8772df1','CA-2T-001',''),
(844,'2025-09-01 11:05:36.366007',0,'IMG-d7881dff','CA-2T-001',''),
(845,'2025-09-01 11:05:36.367982',0,'IMG-6e501b3b','CA-2T-001',''),
(846,'2025-09-01 11:05:36.369937',0,'IMG-13371bdd','CA-2T-001',''),
(847,'2025-09-01 11:05:36.371870',0,'IMG-bfb42902','CA-2T-001',''),
(848,'2025-09-01 11:06:03.143782',0,'IMG-0b9ef7cd','SP-SS-001',''),
(849,'2025-09-01 11:06:03.145510',0,'IMG-a16bc0c2','SP-SS-001',''),
(850,'2025-09-01 11:06:03.147190',0,'IMG-3a0dde5f','SP-SS-001',''),
(851,'2025-09-01 11:06:03.150069',0,'IMG-616e763c','SP-SS-001',''),
(852,'2025-09-01 11:06:03.151798',0,'IMG-ce363763','SP-SS-001',''),
(853,'2025-09-01 11:08:15.418177',0,'IMG-ebd32a9f','CA-FW-001',''),
(854,'2025-09-01 11:08:15.433332',0,'IMG-345e4196','CA-FW-001',''),
(855,'2025-09-01 11:08:15.435976',0,'IMG-b9019475','CA-FW-001',''),
(856,'2025-09-01 11:08:15.438052',0,'IMG-66b7ad6c','CA-FW-001',''),
(857,'2025-09-01 11:13:10.362976',0,'IMG-a9e4fb62','CA-FC-001',''),
(858,'2025-09-01 11:13:10.365338',0,'IMG-fe4cbbc1','CA-FC-001',''),
(859,'2025-09-01 11:13:10.367431',0,'IMG-eb823f14','CA-FC-001',''),
(860,'2025-09-01 11:13:10.369512',0,'IMG-1df38173','CA-FC-001',''),
(861,'2025-09-01 11:13:10.371583',0,'IMG-cec0f6b8','CA-FC-001',''),
(862,'2025-09-01 11:15:09.141970',0,'IMG-c91da05a','SP-WB-002',''),
(863,'2025-09-01 11:15:09.143914',0,'IMG-9aa926df','SP-WB-002',''),
(864,'2025-09-01 11:15:09.145688',0,'IMG-08e65b34','SP-WB-002',''),
(865,'2025-09-01 11:15:09.147401',0,'IMG-bdbb38df','SP-WB-002',''),
(872,'2025-09-01 11:20:18.620116',0,'IMG-a65c1b25','SP-RB-001',''),
(873,'2025-09-01 11:20:18.621935',0,'IMG-8b40b12a','SP-RB-001',''),
(874,'2025-09-01 11:20:18.623829',0,'IMG-4d12d2d7','SP-RB-001',''),
(875,'2025-09-01 11:20:18.625764',0,'IMG-039b10ff','SP-RB-001',''),
(876,'2025-09-01 11:20:18.627556',0,'IMG-0a70aaa1','SP-RB-001',''),
(877,'2025-09-01 11:20:26.651224',0,'IMG-9b20e839','CA-MN-001',''),
(878,'2025-09-01 11:20:26.653151',0,'IMG-13cf4853','CA-MN-001',''),
(879,'2025-09-01 11:20:26.655082',0,'IMG-6d3a0ac3','CA-MN-001',''),
(880,'2025-09-01 11:20:26.656945',0,'IMG-668cf9a1','CA-MN-001',''),
(881,'2025-09-01 11:20:26.658750',0,'IMG-d432a836','CA-MN-001',''),
(882,'2025-09-01 11:20:26.665241',0,'IMG-888834ff','CA-MN-001',''),
(883,'2025-09-01 11:24:13.357916',0,'IMG-bc658e57','CA-RA-001',''),
(884,'2025-09-01 11:24:13.360647',0,'IMG-9a6001cc','CA-RA-001',''),
(885,'2025-09-01 11:26:58.732284',0,'IMG-9e4b8fe2','CA-AN-001',''),
(886,'2025-09-01 11:26:58.735104',0,'IMG-5f11373e','CA-AN-001',''),
(887,'2025-09-01 11:26:58.737262',0,'IMG-157ce22f','CA-AN-001',''),
(888,'2025-09-01 11:26:58.739288',0,'IMG-deec7112','CA-AN-001',''),
(889,'2025-09-01 11:34:30.757888',0,'IMG-53618f0d','CA-IC-001',''),
(890,'2025-09-01 11:34:30.761333',0,'IMG-7fe22d24','CA-IC-001',''),
(891,'2025-09-01 11:35:38.981928',0,'IMG-277c0367','SP-RT-001',''),
(892,'2025-09-01 11:35:38.984186',0,'IMG-014758bb','SP-RT-001',''),
(893,'2025-09-01 11:35:38.986140',0,'IMG-2beb5efe','SP-RT-001',''),
(894,'2025-09-01 11:35:38.988088',0,'IMG-698d63a5','SP-RT-001',''),
(895,'2025-09-01 11:35:38.990550',0,'IMG-7a4c3e2b','SP-RT-001',''),
(896,'2025-09-01 11:36:48.048361',0,'IMG-d39ace7e','CA-PR-001',''),
(897,'2025-09-01 11:36:48.050537',0,'IMG-e8798d0c','CA-PR-001',''),
(898,'2025-09-01 11:36:48.053083',0,'IMG-b8140e0e','CA-PR-001',''),
(899,'2025-09-01 11:36:48.055212',0,'IMG-7e679969','CA-PR-001',''),
(905,'2025-09-01 11:45:09.068082',0,'IMG-34dd79d6','NO-CB-001',''),
(906,'2025-09-01 11:45:09.069827',0,'IMG-f9952801','NO-CB-001',''),
(907,'2025-09-01 11:45:09.071716',0,'IMG-9f445a64','NO-CB-001',''),
(908,'2025-09-01 11:45:09.073661',0,'IMG-657e5683','NO-CB-001',''),
(909,'2025-09-01 11:45:09.075501',0,'IMG-ab5b668b','NO-CB-001',''),
(910,'2025-09-01 11:48:00.459845',0,'IMG-b4303324','SP-TT-001',''),
(911,'2025-09-01 11:48:00.461958',0,'IMG-a76ac0e3','SP-TT-001',''),
(912,'2025-09-01 11:48:00.463908',0,'IMG-3c3ca2e1','SP-TT-001',''),
(913,'2025-09-01 11:48:00.465807',0,'IMG-cbcbb5b8','SP-TT-001',''),
(914,'2025-09-01 11:49:22.076032',0,'IMG-847b4963','NO-BA-001',''),
(915,'2025-09-01 11:49:22.077827',0,'IMG-313f8278','NO-BA-001',''),
(916,'2025-09-01 11:49:22.079574',0,'IMG-85fe45aa','NO-BA-001',''),
(917,'2025-09-01 11:49:22.081358',0,'IMG-e7296d10','NO-BA-001',''),
(918,'2025-09-01 11:49:22.083081',0,'IMG-f930ea4a','NO-BA-001',''),
(919,'2025-09-01 11:49:22.084904',0,'IMG-703739c0','NO-BA-001',''),
(920,'2025-09-01 11:49:22.087000',0,'IMG-78e0bfdf','NO-BA-001',''),
(921,'2025-09-01 11:55:58.681441',0,'IMG-f1221aed','TR-DW-001',''),
(922,'2025-09-01 11:55:58.683337',0,'IMG-5e2582bf','TR-DW-001',''),
(923,'2025-09-01 11:55:58.685144',0,'IMG-81dde5a6','TR-DW-001',''),
(924,'2025-09-01 11:55:58.687145',0,'IMG-f3fe1f83','TR-DW-001',''),
(925,'2025-09-01 11:56:03.028143',0,'IMG-8d91f595','NO-PD-001',''),
(926,'2025-09-01 11:56:03.030955',0,'IMG-091a18a7','NO-PD-001',''),
(927,'2025-09-01 11:56:03.033102',0,'IMG-aaccf612','NO-PD-001',''),
(928,'2025-09-01 11:56:03.035079',0,'IMG-26e7613c','NO-PD-001',''),
(929,'2025-09-01 11:56:03.037255',0,'IMG-60265f8a','NO-PD-001',''),
(930,'2025-09-01 11:56:03.039257',0,'IMG-ce10a2d2','NO-PD-001',''),
(931,'2025-09-01 11:56:03.041137',0,'IMG-0c46e145','NO-PD-001',''),
(937,'2025-09-01 12:03:05.320703',0,'IMG-fb6380af','TR-DW-002',''),
(938,'2025-09-01 12:03:05.322653',0,'IMG-52b11f67','TR-DW-002',''),
(939,'2025-09-01 12:03:05.324576',0,'IMG-e6356e5d','TR-DW-002',''),
(940,'2025-09-01 12:03:05.326357',0,'IMG-a0037312','TR-DW-002',''),
(948,'2025-09-01 12:06:27.311216',0,'IMG-56f89ba8','TR-LT-001',''),
(949,'2025-09-01 12:06:27.319582',0,'IMG-f984f02b','TR-LT-001',''),
(950,'2025-09-01 12:06:27.321863',0,'IMG-2e42ad6e','TR-LT-001',''),
(951,'2025-09-01 12:06:27.324008',0,'IMG-953874b3','TR-LT-001',''),
(952,'2025-09-01 12:06:56.679125',0,'IMG-b7faec87','NO-LP-001',''),
(953,'2025-09-01 12:06:56.681101',0,'IMG-6f2ebc42','NO-LP-001',''),
(954,'2025-09-01 12:06:56.683074',0,'IMG-39453d68','NO-LP-001',''),
(956,'2025-09-01 12:10:13.233695',0,'IMG-f7896a7b','NO-SN-001',''),
(957,'2025-09-01 12:10:13.235518',0,'IMG-d77536bf','NO-SN-001',''),
(958,'2025-09-01 12:10:13.237343',0,'IMG-66bb8f21','NO-SN-001',''),
(964,'2025-09-01 12:10:47.294636',0,'IMG-4f6bae05','TR-TT-001',''),
(965,'2025-09-01 12:10:47.296370',0,'IMG-547229ed','TR-TT-001',''),
(966,'2025-09-01 12:10:47.298148',0,'IMG-68bc4912','TR-TT-001',''),
(967,'2025-09-01 12:10:47.299879',0,'IMG-ea1e1ec0','TR-TT-001',''),
(968,'2025-09-01 12:12:10.700707',0,'IMG-720e2398','PR-CP-001',''),
(969,'2025-09-01 12:13:47.814466',0,'IMG-a725c48d','PR-CW-001',''),
(970,'2025-09-01 12:13:47.816550',0,'IMG-fb357ec6','PR-CW-001',''),
(971,'2025-09-01 12:13:47.818566',0,'IMG-a9673b22','PR-CW-001',''),
(972,'2025-09-01 12:14:18.331291',0,'IMG-b634ffe7','NO-SN-002',''),
(973,'2025-09-01 12:14:18.333175',0,'IMG-02c7cf35','NO-SN-002',''),
(974,'2025-09-01 12:14:18.335005',0,'IMG-7dd06ebd','NO-SN-002',''),
(975,'2025-09-01 12:14:53.450976',0,'IMG-dd74cb3e','PR-CH-001',''),
(976,'2025-09-01 12:14:53.452774',0,'IMG-c0f93105','PR-CH-001',''),
(977,'2025-09-01 12:14:53.455691',0,'IMG-b3dd5f50','PR-CH-001',''),
(978,'2025-09-01 12:17:14.134156',0,'IMG-c7ebca1d','NO-AS-001',''),
(979,'2025-09-01 12:17:14.136715',0,'IMG-4918456e','NO-AS-001',''),
(980,'2025-09-01 12:17:14.139098',0,'IMG-edf2c28c','NO-AS-001',''),
(983,'2025-09-01 12:28:37.697836',0,'IMG-cd3e933d','EX-WP-001',''),
(984,'2025-09-01 12:28:37.699606',0,'IMG-cfcd1cb5','EX-WP-001',''),
(985,'2025-09-01 12:28:37.701390',0,'IMG-6301f369','EX-WP-001',''),
(986,'2025-09-01 12:28:37.703224',0,'IMG-77bbf26f','EX-WP-001',''),
(987,'2025-09-01 12:28:37.704913',0,'IMG-89a1519e','EX-WP-001',''),
(988,'2025-09-01 12:28:37.706613',0,'IMG-02445113','EX-WP-001',''),
(989,'2025-09-02 07:54:11.372946',0,'IMG-c5057079','CA-PS-001',''),
(990,'2025-09-02 07:54:11.375928',0,'IMG-a820c2e2','CA-PS-001',''),
(991,'2025-09-02 07:54:11.378782',0,'IMG-a12f42ce','CA-PS-001',''),
(992,'2025-09-02 07:54:11.382038',0,'IMG-7a73e3ea','CA-PS-001',''),
(993,'2025-09-02 07:54:11.384383',0,'IMG-e29544b2','CA-PS-001',''),
(994,'2025-09-02 07:54:11.386323',0,'IMG-a27dee20','CA-PS-001',''),
(995,'2025-09-02 08:05:42.228680',0,'IMG-632f38d4','TA-EF-001',''),
(996,'2025-09-02 08:05:42.230557',0,'IMG-7a6bbc91','TA-EF-001',''),
(997,'2025-09-02 08:05:42.232531',0,'IMG-e5ea3a7e','TA-EF-001',''),
(998,'2025-09-02 08:05:42.234519',0,'IMG-f9f07b76','TA-EF-001',''),
(999,'2025-09-02 08:09:44.173287',0,'IMG-32ae0bf8','TA-HT-001',''),
(1000,'2025-09-02 08:09:44.175226',0,'IMG-05e0a404','TA-HT-001',''),
(1001,'2025-09-02 08:09:44.176963',0,'IMG-1ac605fa','TA-HT-001',''),
(1002,'2025-09-02 08:09:44.178733',0,'IMG-93cd23f4','TA-HT-001',''),
(1003,'2025-09-02 08:11:13.963313',0,'IMG-aaabf99b','TA-SG-001',''),
(1004,'2025-09-02 08:11:13.965135',0,'IMG-90d14e5a','TA-SG-001',''),
(1005,'2025-09-02 08:11:13.966963',0,'IMG-43635dfe','TA-SG-001',''),
(1006,'2025-09-02 08:12:46.433476',0,'IMG-9ef164eb','TA-RG-001',''),
(1007,'2025-09-02 08:12:46.435340',0,'IMG-b36679aa','TA-RG-001',''),
(1008,'2025-09-02 08:12:46.437298',0,'IMG-96bf55dc','TA-RG-001',''),
(1009,'2025-09-03 12:56:02.080406',0,'IMG-bb7b46e5','PL-AP-001',''),
(1010,'2025-09-03 12:56:02.082596',0,'IMG-8b13e30c','PL-AP-001',''),
(1011,'2025-09-03 12:56:02.084605',0,'IMG-978efc93','PL-AP-001',''),
(1012,'2025-09-03 12:56:02.086522',0,'IMG-fd5ac9a8','PL-AP-001',''),
(1013,'2025-09-03 12:56:02.088586',0,'IMG-c595dd3e','PL-AP-001',''),
(1014,'2025-09-03 12:56:02.090742',0,'IMG-d9dfcc10','PL-AP-001',''),
(1015,'2025-09-03 13:05:04.527249',0,'IMG-73004b4b','WO-EF-001',''),
(1016,'2025-09-03 13:08:57.657465',0,'IMG-d55935d2','TR-DS-001',''),
(1017,'2025-09-03 13:08:57.659460',0,'IMG-65519455','TR-DS-001',''),
(1018,'2025-09-03 13:08:57.661382',0,'IMG-e1f75197','TR-DS-001',''),
(1019,'2025-09-03 13:08:57.663113',0,'IMG-04c3d7d6','TR-DS-001',''),
(1020,'2025-09-04 06:52:49.239563',0,'IMG-1c52f3d3','SP-PB-001',''),
(1021,'2025-09-04 06:52:49.242420',0,'IMG-d4a85de9','SP-PB-001',''),
(1022,'2025-09-04 06:52:49.245009',0,'IMG-21da0231','SP-PB-001',''),
(1023,'2025-09-04 06:52:49.247191',0,'IMG-9cf43281','SP-PB-001',''),
(1024,'2025-09-04 06:52:49.249518',0,'IMG-e41277bf','SP-PB-001',''),
(1025,'2025-09-04 07:01:28.062315',0,'IMG-5312cb0c','EC-EF-001',''),
(1026,'2025-09-04 07:01:28.064217',0,'IMG-98e3e26b','EC-EF-001',''),
(1027,'2025-09-04 07:01:28.066959',0,'IMG-fbbfae6d','EC-EF-001',''),
(1028,'2025-09-04 07:01:28.068743',0,'IMG-a03d1936','EC-EF-001',''),
(1029,'2025-09-04 07:10:08.129520',0,'IMG-1ccf3047','EC-BF-001',''),
(1030,'2025-09-04 07:10:08.132012',0,'IMG-d38427f4','EC-BF-001',''),
(1031,'2025-09-04 07:10:08.134425',0,'IMG-6a29db2c','EC-BF-001',''),
(1032,'2025-09-04 07:10:08.136817',0,'IMG-d32a9bb9','EC-BF-001',''),
(1033,'2025-09-04 07:10:08.138971',0,'IMG-8e21f431','EC-BF-001',''),
(1034,'2025-09-04 07:10:08.140978',0,'IMG-4a256a0c','EC-BF-001',''),
(1035,'2025-09-04 07:33:10.671958',0,'IMG-68eaa16a','PR-CO-001',''),
(1036,'2025-09-04 07:33:10.674553',0,'IMG-8e5b8105','PR-CO-001',''),
(1037,'2025-09-04 07:33:10.684006',0,'IMG-632e17ba','PR-CO-001',''),
(1038,'2025-09-04 07:33:10.688555',0,'IMG-466e40e2','PR-CO-001',''),
(1039,'2025-09-04 07:33:10.693388',0,'IMG-112e730a','PR-CO-001',''),
(1040,'2025-09-04 07:33:10.698029',0,'IMG-45ef33a6','PR-CO-001',''),
(1041,'2025-09-04 07:39:52.248600',0,'IMG-71a00eff','EX-PL-001',''),
(1042,'2025-09-04 07:39:52.250427',0,'IMG-dfa5fc8e','EX-PL-001',''),
(1043,'2025-09-04 07:39:52.252253',0,'IMG-26822b81','EX-PL-001',''),
(1044,'2025-09-04 07:39:52.254309',0,'IMG-19c9d494','EX-PL-001',''),
(1045,'2025-09-04 07:39:52.256297',0,'IMG-9bd7e6bb','EX-PL-001',''),
(1046,'2025-09-04 07:52:14.605688',0,'IMG-95ed8196','PR-CC-001',''),
(1047,'2025-09-04 07:52:14.607626',0,'IMG-b4e2e4fc','PR-CC-001',''),
(1048,'2025-09-04 07:52:14.609651',0,'IMG-f6cf4e7b','PR-CC-001',''),
(1049,'2025-09-04 07:52:14.611448',0,'IMG-8670d875','PR-CC-001',''),
(1050,'2025-09-04 07:52:14.613306',0,'IMG-2ac93dc5','PR-CC-001',''),
(1051,'2025-09-04 07:54:01.442285',0,'IMG-ffb0688b','CO-WU-001',''),
(1052,'2025-09-04 07:54:01.444471',0,'IMG-06b66025','CO-WU-001',''),
(1053,'2025-09-04 07:54:01.447275',0,'IMG-2fb0946b','CO-WU-001',''),
(1054,'2025-09-04 07:54:34.983905',0,'IMG-c4364a98','PR-CC-002',''),
(1055,'2025-09-04 07:54:34.986106',0,'IMG-6731ec59','PR-CC-002',''),
(1056,'2025-09-04 07:54:34.988115',0,'IMG-f08eabd7','PR-CC-002',''),
(1057,'2025-09-04 07:54:34.990172',0,'IMG-b9e3a773','PR-CC-002',''),
(1058,'2025-09-04 07:54:34.992220',0,'IMG-0120f4f8','PR-CC-002',''),
(1059,'2025-09-04 07:56:17.775044',0,'IMG-a4f96415','PR-CP-002',''),
(1060,'2025-09-04 07:56:17.776887',0,'IMG-9abe2491','PR-CP-002',''),
(1061,'2025-09-04 07:56:17.778785',0,'IMG-3e538203','PR-CP-002',''),
(1062,'2025-09-04 07:56:17.780636',0,'IMG-013cc75d','PR-CP-002',''),
(1063,'2025-09-04 07:56:17.782561',0,'IMG-9d1ad4d1','PR-CP-002',''),
(1064,'2025-09-04 07:59:19.775577',0,'IMG-7291ea57','BR-PP-001',''),
(1065,'2025-09-04 07:59:19.777533',0,'IMG-4b1a2d9f','BR-PP-001',''),
(1066,'2025-09-04 07:59:19.779446',0,'IMG-267e51ee','BR-PP-001',''),
(1067,'2025-09-04 07:59:19.781345',0,'IMG-bc9eccd4','BR-PP-001',''),
(1068,'2025-09-04 07:59:19.783518',0,'IMG-172d77d5','BR-PP-001',''),
(1074,'2025-09-04 08:05:19.040314',0,'IMG-52b960ed','NO-CC-001',''),
(1075,'2025-09-04 08:05:19.042425',0,'IMG-8b5a9108','NO-CC-001',''),
(1076,'2025-09-04 08:05:19.044508',0,'IMG-b507881e','NO-CC-001',''),
(1077,'2025-09-04 08:05:19.046403',0,'IMG-81f01c37','NO-CC-001',''),
(1078,'2025-09-04 08:05:19.048343',0,'IMG-89396cbe','NO-CC-001',''),
(1079,'2025-09-04 08:07:29.829857',0,'IMG-9b36a5fc','EX-CB-001',''),
(1080,'2025-09-04 08:07:29.831654',0,'IMG-2cc15757','EX-CB-001',''),
(1081,'2025-09-04 08:07:29.833422',0,'IMG-71ad1748','EX-CB-001',''),
(1082,'2025-09-04 08:07:29.835075',0,'IMG-98e02991','EX-CB-001',''),
(1083,'2025-09-04 08:07:29.836917',0,'IMG-db1ad6ec','EX-CB-001',''),
(1084,'2025-09-04 08:09:59.943229',0,'IMG-14cf3f40','EX-CC-001',''),
(1085,'2025-09-04 08:09:59.945190',0,'IMG-91e5db93','EX-CC-001',''),
(1086,'2025-09-04 08:09:59.947117',0,'IMG-ce1c1ab0','EX-CC-001',''),
(1087,'2025-09-04 08:09:59.948888',0,'IMG-62111a90','EX-CC-001',''),
(1088,'2025-09-04 08:09:59.950643',0,'IMG-b9617570','EX-CC-001',''),
(1089,'2025-09-04 08:11:46.930046',0,'IMG-68393e7e','EX-CC-002',''),
(1090,'2025-09-04 08:11:46.932064',0,'IMG-88f2bbd9','EX-CC-002',''),
(1091,'2025-09-04 08:11:46.933946',0,'IMG-162f6a84','EX-CC-002',''),
(1092,'2025-09-04 08:11:46.935733',0,'IMG-995af78f','EX-CC-002',''),
(1093,'2025-09-04 08:11:46.937769',0,'IMG-2582d1aa','EX-CC-002',''),
(1094,'2025-09-04 08:13:38.306849',0,'IMG-9832cb2d','CA-CO-001',''),
(1095,'2025-09-04 08:13:38.309244',0,'IMG-3cee1d2e','CA-CO-001',''),
(1096,'2025-09-04 08:13:38.311582',0,'IMG-8b1fa8cf','CA-CO-001',''),
(1097,'2025-09-04 08:13:38.313982',0,'IMG-44a4fdc4','CA-CO-001',''),
(1098,'2025-09-04 08:13:38.316320',0,'IMG-db937163','CA-CO-001',''),
(1099,'2025-09-04 08:16:40.241050',0,'IMG-dabc4cb8','EV-CE-001',''),
(1100,'2025-09-04 08:16:40.242802',0,'IMG-754806e8','EV-CE-001',''),
(1101,'2025-09-04 08:16:40.244547',0,'IMG-4e7d6313','EV-CE-001',''),
(1102,'2025-09-04 08:16:40.246259',0,'IMG-0e94d4ba','EV-CE-001',''),
(1103,'2025-09-04 08:16:40.248099',0,'IMG-95303739','EV-CE-001',''),
(1104,'2025-09-04 08:18:38.170382',0,'IMG-3815eb6a','EV-CR-001',''),
(1105,'2025-09-04 08:18:38.172628',0,'IMG-3c2e178b','EV-CR-001',''),
(1106,'2025-09-04 08:18:38.174581',0,'IMG-9be8a6cd','EV-CR-001',''),
(1107,'2025-09-04 08:18:38.176664',0,'IMG-2ef5fbd1','EV-CR-001',''),
(1108,'2025-09-04 08:18:38.178483',0,'IMG-663e2f00','EV-CR-001',''),
(1109,'2025-09-04 08:21:03.957399',0,'IMG-3af523c9','EV-CR-002',''),
(1110,'2025-09-04 08:21:03.959175',0,'IMG-96244a00','EV-CR-002',''),
(1111,'2025-09-04 08:21:03.960916',0,'IMG-d5fccc38','EV-CR-002',''),
(1112,'2025-09-04 08:21:03.962662',0,'IMG-0fcde3c8','EV-CR-002',''),
(1113,'2025-09-04 08:21:03.964427',0,'IMG-2b4f9016','EV-CR-002',''),
(1114,'2025-09-04 08:23:28.445182',0,'IMG-22b1d3f7','CO-EF-001',''),
(1115,'2025-09-04 08:23:28.446958',0,'IMG-9c2bc050','CO-EF-001',''),
(1116,'2025-09-04 08:23:28.450023',0,'IMG-a067fe27','CO-EF-001',''),
(1117,'2025-09-04 08:23:28.451956',0,'IMG-f0796806','CO-EF-001',''),
(1118,'2025-09-04 08:23:28.453931',0,'IMG-770fbc43','CO-EF-001',''),
(1119,'2025-09-04 08:26:58.039517',0,'IMG-d7144707','CO-SC-001',''),
(1120,'2025-09-04 08:26:58.041357',0,'IMG-f5e1bef9','CO-SC-001',''),
(1121,'2025-09-04 08:26:58.043095',0,'IMG-2a759109','CO-SC-001',''),
(1122,'2025-09-04 08:26:58.044836',0,'IMG-352d1723','CO-SC-001',''),
(1123,'2025-09-04 08:28:56.003693',0,'IMG-d97f352e','CO-DU-001',''),
(1124,'2025-09-04 08:28:56.005917',0,'IMG-992b1460','CO-DU-001',''),
(1125,'2025-09-04 08:28:56.007957',0,'IMG-03db3b6d','CO-DU-001',''),
(1126,'2025-09-04 08:28:56.010000',0,'IMG-581fecf0','CO-DU-001',''),
(1127,'2025-09-04 08:28:56.011874',0,'IMG-16bfc789','CO-DU-001',''),
(1128,'2025-09-04 08:30:04.880120',0,'IMG-e398a0e3','CO-CB-001',''),
(1129,'2025-09-04 08:30:04.881908',0,'IMG-ec1f279f','CO-CB-001',''),
(1130,'2025-09-04 08:30:04.883773',0,'IMG-f522ab8d','CO-CB-001',''),
(1131,'2025-09-04 08:30:04.886219',0,'IMG-d209e3e8','CO-CB-001',''),
(1132,'2025-09-04 08:30:04.888308',0,'IMG-f1ad9fbf','CO-CB-001',''),
(1133,'2025-09-04 08:31:25.932806',0,'IMG-0bc8a510','CO-CU-001',''),
(1134,'2025-09-04 08:33:25.911219',0,'IMG-74b2dc03','CO-UM-001',''),
(1135,'2025-09-04 08:33:25.913621',0,'IMG-2e63454c','CO-UM-001',''),
(1136,'2025-09-04 08:33:25.916367',0,'IMG-58114c8d','CO-UM-001',''),
(1137,'2025-09-04 08:33:25.918870',0,'IMG-2de523f2','CO-UM-001',''),
(1138,'2025-09-04 08:33:25.921275',0,'IMG-3b16c02e','CO-UM-001',''),
(1139,'2025-09-11 06:08:39.770599',0,'IMG-7504d57b','FL-CF-001',''),
(1140,'2025-09-11 06:10:06.901043',0,'IMG-e95fab36','FL-CF-002',''),
(1141,'2025-09-11 06:11:57.661398',0,'IMG-e59c27db','FL-HT-001',''),
(1142,'2025-09-11 06:13:31.007044',0,'IMG-7702a4ac','FL-HD-001',''),
(1143,'2025-09-11 06:14:38.849664',0,'IMG-5eb80941','FL-HT-002',''),
(1144,'2025-09-11 06:16:07.823296',0,'IMG-0394efdd','FL-LS-001',''),
(1145,'2025-09-11 06:17:21.250842',0,'IMG-e9013275','FL-PF-001',''),
(1146,'2025-09-11 06:19:06.458479',0,'IMG-2055ddd2','FL-PT-001',''),
(1147,'2025-09-11 06:21:40.736045',0,'IMG-e502e048','FL-ST-001',''),
(1149,'2025-09-11 06:24:47.289219',0,'IMG-7ec1f3f3','FL-HB-001',''),
(1150,'2025-09-11 06:26:33.958641',0,'IMG-f6ef068e','FL-VS-001',''),
(1151,'2025-09-11 06:27:31.069384',0,'IMG-81c7034d','FL-VC-001',''),
(1152,'2025-09-11 06:28:30.541885',0,'IMG-8176b50f','FL-YS-001',''),
(1153,'2025-09-11 06:31:34.727065',0,'IMG-8321a94b','FL-PF-002',''),
(1154,'2025-09-11 06:35:12.923699',0,'IMG-acc76146','FL-CT-001',''),
(1155,'2025-09-11 06:37:42.496761',0,'IMG-f0c0b43f','FL-TS-001',''),
(1156,'2025-09-11 06:39:46.618119',0,'IMG-b6f43385','FL-TD-001',''),
(1157,'2025-09-11 07:23:36.139815',0,'IMG-c02c0a34','BA-FB-001',''),
(1158,'2025-09-11 07:23:36.144131',0,'IMG-7915fee0','BA-FB-001',''),
(1159,'2025-09-11 07:23:36.148312',0,'IMG-fa24368d','BA-FB-001',''),
(1160,'2025-09-11 07:23:36.151732',0,'IMG-29b92b35','BA-FB-001',''),
(1161,'2025-09-11 07:34:28.068869',0,'IMG-031667ed','BA-FB-002',''),
(1162,'2025-09-11 07:34:28.075548',0,'IMG-fab760e2','BA-FB-002',''),
(1163,'2025-09-11 07:34:28.079377',0,'IMG-b9357941','BA-FB-002','');
/*!40000 ALTER TABLE `admin_backend_final_productimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_productinventory`
--

DROP TABLE IF EXISTS `admin_backend_final_productinventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_productinventory` (
  `inventory_id` varchar(100) NOT NULL,
  `stock_quantity` int(11) NOT NULL,
  `low_stock_alert` int(11) NOT NULL,
  `stock_status` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`inventory_id`),
  UNIQUE KEY `product_id` (`product_id`),
  KEY `admin_backend_final_productinventory_stock_status_e6fb9fe5` (`stock_status`),
  CONSTRAINT `admin_backend_final__product_id_8378b28f_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_productinventory`
--

LOCK TABLES `admin_backend_final_productinventory` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_productinventory` DISABLE KEYS */;
INSERT INTO `admin_backend_final_productinventory` VALUES
('INV-AC-CC-001',0,0,'In Stock','2025-09-01 08:08:19.090268','2025-09-01 08:08:19.090281','AC-CC-001'),
('INV-AC-CP-001',0,0,'In Stock','2025-09-01 08:21:39.579887','2025-09-01 08:21:39.579906','AC-CP-001'),
('INV-AC-EU-001',0,0,'In Stock','2025-09-01 08:09:50.066973','2025-09-01 08:09:50.066988','AC-EU-001'),
('INV-AC-WA-001',0,0,'In Stock','2025-09-01 08:23:31.491950','2025-09-01 08:23:31.491964','AC-WA-001'),
('INV-BA-BA-001',0,0,'Out Of Stock','2025-09-01 06:14:41.089646','2025-09-04 12:07:59.606602','BA-BA-001'),
('INV-BA-EC-001',0,0,'Out Of Stock','2025-09-01 06:24:50.889504','2025-09-04 12:09:47.090311','BA-EC-001'),
('INV-BA-EC-002',0,0,'In Stock','2025-09-01 06:31:13.143628','2025-09-01 06:31:13.143642','BA-EC-002'),
('INV-BA-FB-001',0,0,'In Stock','2025-09-11 07:23:36.085280','2025-09-11 07:23:36.085296','BA-FB-001'),
('INV-BA-FB-002',0,0,'In Stock','2025-09-11 07:34:27.992336','2025-09-11 07:34:27.992350','BA-FB-002'),
('INV-BA-MC-001',0,0,'In Stock','2025-09-01 06:22:17.252897','2025-09-01 06:22:17.252912','BA-MC-001'),
('INV-BR-CA-001',0,0,'In Stock','2025-09-01 08:38:07.645547','2025-09-01 08:38:07.645559','BR-CA-001'),
('INV-BR-CM-001',0,0,'In Stock','2025-09-01 08:20:03.113832','2025-09-01 08:20:03.113844','BR-CM-001'),
('INV-BR-CP-001',0,0,'In Stock','2025-09-01 08:13:41.681223','2025-09-01 08:13:41.681237','BR-CP-001'),
('INV-BR-CR-001',0,0,'Out Of Stock','2025-09-01 08:34:53.190117','2025-09-01 09:04:32.051113','BR-CR-001'),
('INV-BR-PE-001',0,0,'In Stock','2025-09-01 08:29:05.872489','2025-09-01 08:29:05.872502','BR-PE-001'),
('INV-BR-PG-001',0,0,'In Stock','2025-09-01 08:24:54.965640','2025-09-01 08:24:54.965654','BR-PG-001'),
('INV-BR-PP-001',0,0,'In Stock','2025-09-04 07:59:19.767279','2025-09-04 07:59:19.767292','BR-PP-001'),
('INV-CA-2T-001',0,0,'In Stock','2025-09-01 11:05:36.354087','2025-09-01 11:05:36.354099','CA-2T-001'),
('INV-CA-AN-001',0,0,'In Stock','2025-09-01 11:26:58.723234','2025-09-01 11:26:58.723249','CA-AN-001'),
('INV-CA-BC-001',0,0,'In Stock','2025-09-01 10:37:38.755045','2025-09-01 11:01:10.784136','CA-BC-001'),
('INV-CA-CO-001',0,0,'In Stock','2025-09-04 08:13:38.296306','2025-09-04 08:13:38.296327','CA-CO-001'),
('INV-CA-FC-001',0,0,'In Stock','2025-09-01 11:13:10.351235','2025-09-01 11:13:10.351255','CA-FC-001'),
('INV-CA-FW-001',0,0,'Out Of Stock','2025-09-01 11:08:15.408852','2025-09-04 11:53:58.368441','CA-FW-001'),
('INV-CA-IC-001',0,0,'In Stock','2025-09-01 11:34:30.748087','2025-09-01 11:34:30.748100','CA-IC-001'),
('INV-CA-MN-001',0,0,'In Stock','2025-09-01 11:18:35.742010','2025-09-01 11:20:26.640044','CA-MN-001'),
('INV-CA-PR-001',0,0,'In Stock','2025-09-01 11:36:48.039624','2025-09-01 11:36:48.039638','CA-PR-001'),
('INV-CA-PS-001',0,0,'In Stock','2025-09-02 07:54:11.357941','2025-09-02 07:54:11.357960','CA-PS-001'),
('INV-CA-RA-001',0,0,'In Stock','2025-09-01 11:24:13.347552','2025-09-01 11:24:13.347570','CA-RA-001'),
('INV-CA-SB-001',0,0,'In Stock','2025-09-01 11:03:33.065931','2025-09-01 11:03:33.065949','CA-SB-001'),
('INV-CE-BC-001',1000,1,'In Stock','2025-09-01 10:02:44.929803','2025-09-01 10:02:44.929817','CE-BC-001'),
('INV-CE-BS-001',1000,-1,'In Stock','2025-09-01 08:18:56.286829','2025-09-01 08:18:56.286845','CE-BS-001'),
('INV-CE-CC-001',1000,-2,'In Stock','2025-09-01 08:55:48.134487','2025-09-04 10:56:31.469622','CE-CC-001'),
('INV-CE-CE-001',1000,1,'In Stock','2025-09-01 08:22:50.534545','2025-09-01 08:23:54.297409','CE-CE-001'),
('INV-CE-CG-001',1000,-2,'In Stock','2025-09-01 08:07:35.342038','2025-09-01 08:07:35.342052','CE-CG-001'),
('INV-CE-CM-001',1000,1,'In Stock','2025-09-01 09:32:14.748114','2025-09-04 10:53:19.073442','CE-CM-001'),
('INV-CE-GB-001',1000,1,'In Stock','2025-09-01 09:04:00.891537','2025-09-01 09:04:01.001032','CE-GB-001'),
('INV-CE-GC-001',1000,1,'In Stock','2025-09-01 09:12:16.131473','2025-09-01 09:12:16.131486','CE-GC-001'),
('INV-CE-LM-001',1000,-1,'In Stock','2025-09-01 10:13:38.506483','2025-09-01 10:13:38.506496','CE-LM-001'),
('INV-CE-MC-001',1000,1,'In Stock','2025-09-01 07:59:30.653666','2025-09-01 07:59:30.653685','CE-MC-001'),
('INV-CE-PC-001',1000,1,'In Stock','2025-09-01 09:24:05.814857','2025-09-01 09:24:05.814870','CE-PC-001'),
('INV-CE-PM-001',1000,1,'In Stock','2025-09-01 08:34:20.716115','2025-09-01 08:34:20.716128','CE-PM-001'),
('INV-CE-TT-001',1000,1,'In Stock','2025-09-01 08:47:14.761843','2025-09-01 09:33:17.768259','CE-TT-001'),
('INV-CE-TT-002',1000,1,'In Stock','2025-09-01 09:19:55.162326','2025-09-01 09:33:45.707508','CE-TT-002'),
('INV-CE-TT-003',1000,1,'In Stock','2025-09-01 09:41:51.565185','2025-09-01 09:41:51.565217','CE-TT-003'),
('INV-CE-WC-001',1000,1,'In Stock','2025-09-01 08:14:06.489232','2025-09-04 11:37:35.931298','CE-WC-001'),
('INV-CE-WC-002',1000,-1,'In Stock','2025-09-01 08:41:07.068228','2025-09-01 08:41:07.068243','CE-WC-002'),
('INV-CE-WC-003',1000,1,'In Stock','2025-09-01 10:09:15.161848','2025-09-01 10:09:15.161863','CE-WC-003'),
('INV-CE-WS-001',1000,1,'In Stock','2025-09-01 09:09:17.530823','2025-09-01 09:09:17.530837','CE-WS-001'),
('INV-CE-WS-002',1000,-2,'In Stock','2025-09-01 10:20:26.364612','2025-09-01 10:20:26.364628','CE-WS-002'),
('INV-CO-BE-001',0,0,'Out Of Stock','2025-09-01 06:38:34.663293','2025-09-04 11:49:49.802254','CO-BE-001'),
('INV-CO-CB-001',0,0,'In Stock','2025-09-04 08:30:04.871120','2025-09-04 08:30:04.871135','CO-CB-001'),
('INV-CO-CC-001',0,0,'In Stock','2025-09-01 06:50:01.373584','2025-09-01 06:50:01.373597','CO-CC-001'),
('INV-CO-CL-001',0,0,'Out Of Stock','2025-09-01 06:44:22.456726','2025-09-04 11:47:12.710291','CO-CL-001'),
('INV-CO-CU-001',0,0,'In Stock','2025-09-04 08:31:25.921708','2025-09-04 08:31:25.921728','CO-CU-001'),
('INV-CO-DU-001',0,0,'Out Of Stock','2025-09-04 08:28:55.994760','2025-09-04 11:41:53.287622','CO-DU-001'),
('INV-CO-EF-001',0,0,'In Stock','2025-09-04 08:23:28.437053','2025-09-04 08:23:28.437066','CO-EF-001'),
('INV-CO-SC-001',0,0,'In Stock','2025-09-04 08:26:58.019781','2025-09-04 08:26:58.019796','CO-SC-001'),
('INV-CO-UM-001',0,0,'In Stock','2025-09-04 08:33:25.900513','2025-09-04 08:33:25.900533','CO-UM-001'),
('INV-CO-WU-001',0,0,'Out Of Stock','2025-09-04 07:54:01.432938','2025-09-04 11:43:50.632341','CO-WU-001'),
('INV-DE-BF-001',0,0,'In Stock','2025-09-01 10:22:47.020087','2025-09-01 10:22:47.020101','DE-BF-001'),
('INV-DE-SF-001',0,0,'In Stock','2025-09-01 10:26:26.190140','2025-09-01 10:26:26.190154','DE-SF-001'),
('INV-EC-BF-001',0,0,'In Stock','2025-09-04 07:10:08.105244','2025-09-04 07:10:08.105261','EC-BF-001'),
('INV-EC-EF-001',0,0,'In Stock','2025-09-04 07:01:28.040974','2025-09-04 07:01:28.040989','EC-EF-001'),
('INV-EV-CE-001',0,0,'In Stock','2025-09-04 08:16:40.232721','2025-09-04 08:16:40.232735','EV-CE-001'),
('INV-EV-CJ-001',0,0,'Out Of Stock','2025-09-01 07:19:05.000950','2025-09-04 12:11:23.944304','EV-CJ-001'),
('INV-EV-CJ-002',1000,1,'In Stock','2025-09-01 07:31:27.144549','2025-09-04 11:58:30.310712','EV-CJ-002'),
('INV-EV-CJ-003',0,0,'In Stock','2025-09-01 07:52:59.439961','2025-09-01 07:52:59.439975','EV-CJ-003'),
('INV-EV-CL-001',0,0,'In Stock','2025-09-01 10:10:07.061701','2025-09-01 10:10:07.061715','EV-CL-001'),
('INV-EV-CR-001',0,0,'In Stock','2025-09-04 08:18:38.160803','2025-09-04 08:18:38.160818','EV-CR-001'),
('INV-EV-CR-002',0,0,'Out Of Stock','2025-09-04 08:21:03.937896','2025-09-04 12:00:55.866067','EV-CR-002'),
('INV-EV-DP-001',0,0,'In Stock','2025-09-01 10:11:31.276135','2025-09-01 10:11:31.276148','EV-DP-001'),
('INV-EV-LW-001',0,0,'In Stock','2025-09-01 10:08:07.426295','2025-09-01 10:08:07.426314','EV-LW-001'),
('INV-EV-RJ-001',0,0,'In Stock','2025-09-01 06:59:40.561541','2025-09-01 07:04:51.876029','EV-RJ-001'),
('INV-EV-RV-001',0,0,'In Stock','2025-09-01 08:04:31.873612','2025-09-01 08:04:31.873624','EV-RV-001'),
('INV-EV-SC-001',0,0,'Out Of Stock','2025-09-01 06:32:55.744628','2025-09-04 11:55:39.711147','EV-SC-001'),
('INV-EV-TW-001',0,0,'In Stock','2025-09-01 10:13:10.522737','2025-09-01 10:13:10.522751','EV-TW-001'),
('INV-EV-VN-001',0,0,'Out Of Stock','2025-09-01 08:01:45.609249','2025-09-04 12:03:12.221364','EV-VN-001'),
('INV-EX-CB-001',0,0,'In Stock','2025-09-04 08:07:29.821226','2025-09-04 08:07:29.821241','EX-CB-001'),
('INV-EX-CC-001',0,0,'In Stock','2025-09-04 08:09:59.935246','2025-09-04 08:09:59.935265','EX-CC-001'),
('INV-EX-CC-002',0,0,'In Stock','2025-09-04 08:11:46.921138','2025-09-04 08:11:46.921153','EX-CC-002'),
('INV-EX-PL-001',0,0,'In Stock','2025-09-04 07:39:52.240245','2025-09-04 07:39:52.240258','EX-PL-001'),
('INV-EX-WP-001',0,0,'In Stock','2025-09-01 12:28:37.689275','2025-09-01 12:28:37.689287','EX-WP-001'),
('INV-FL-CF-001',0,0,'In Stock','2025-09-11 06:08:39.744172','2025-09-11 06:08:39.744187','FL-CF-001'),
('INV-FL-CF-002',0,0,'In Stock','2025-09-11 06:10:06.891476','2025-09-11 06:10:06.891494','FL-CF-002'),
('INV-FL-CT-001',0,0,'In Stock','2025-09-11 06:35:12.912852','2025-09-11 06:35:12.912884','FL-CT-001'),
('INV-FL-HB-001',0,0,'In Stock','2025-09-11 06:24:47.274083','2025-09-11 06:24:47.274103','FL-HB-001'),
('INV-FL-HD-001',0,0,'In Stock','2025-09-11 06:13:30.996162','2025-09-11 06:13:30.996189','FL-HD-001'),
('INV-FL-HT-001',0,0,'In Stock','2025-09-11 06:11:57.652814','2025-09-11 06:11:57.652844','FL-HT-001'),
('INV-FL-HT-002',0,0,'In Stock','2025-09-11 06:14:38.839095','2025-09-11 06:14:38.839111','FL-HT-002'),
('INV-FL-LS-001',0,0,'In Stock','2025-09-11 06:16:07.813579','2025-09-11 06:16:07.813594','FL-LS-001'),
('INV-FL-PF-001',0,0,'In Stock','2025-09-11 06:17:21.220777','2025-09-11 06:17:21.220792','FL-PF-001'),
('INV-FL-PF-002',0,0,'In Stock','2025-09-11 06:31:34.715407','2025-09-11 06:31:34.715423','FL-PF-002'),
('INV-FL-PT-001',0,0,'In Stock','2025-09-11 06:19:06.444061','2025-09-11 06:19:06.444079','FL-PT-001'),
('INV-FL-ST-001',0,0,'In Stock','2025-09-11 06:21:40.724117','2025-09-11 06:21:40.724137','FL-ST-001'),
('INV-FL-TD-001',0,0,'In Stock','2025-09-11 06:39:46.608912','2025-09-11 06:39:46.608932','FL-TD-001'),
('INV-FL-TS-001',0,0,'In Stock','2025-09-11 06:23:09.817170','2025-09-11 06:37:42.482890','FL-TS-001'),
('INV-FL-VC-001',0,0,'In Stock','2025-09-11 06:27:31.059742','2025-09-11 06:27:31.059756','FL-VC-001'),
('INV-FL-VS-001',0,0,'In Stock','2025-09-11 06:26:33.945905','2025-09-11 06:26:33.945919','FL-VS-001'),
('INV-FL-YS-001',0,0,'In Stock','2025-09-11 06:28:30.530584','2025-09-11 06:28:30.530606','FL-YS-001'),
('INV-GI-LP-001',0,0,'Out Of Stock','2025-09-01 06:24:30.055572','2025-09-04 10:50:07.133738','GI-LP-001'),
('INV-NO-AS-001',0,0,'Out Of Stock','2025-09-01 12:17:14.123721','2025-09-04 12:19:20.961805','NO-AS-001'),
('INV-NO-BA-001',0,0,'Out Of Stock','2025-09-01 11:49:22.068158','2025-09-04 12:14:54.005422','NO-BA-001'),
('INV-NO-CB-001',0,0,'In Stock','2025-09-01 11:45:09.058937','2025-09-01 11:45:09.058954','NO-CB-001'),
('INV-NO-CC-001',0,0,'In Stock','2025-09-04 08:05:19.029085','2025-09-04 08:05:19.029102','NO-CC-001'),
('INV-NO-LP-001',0,0,'In Stock','2025-09-01 12:06:56.669324','2025-09-01 12:06:56.669337','NO-LP-001'),
('INV-NO-PD-001',0,0,'Out Of Stock','2025-09-01 11:56:03.019458','2025-09-04 12:20:56.379857','NO-PD-001'),
('INV-NO-SN-001',0,0,'Out Of Stock','2025-09-01 12:10:13.225472','2025-09-04 12:17:09.658093','NO-SN-001'),
('INV-NO-SN-002',0,0,'In Stock','2025-09-01 12:14:18.323323','2025-09-01 12:14:18.323336','NO-SN-002'),
('INV-PL-AP-001',0,0,'Out Of Stock','2025-09-03 12:56:02.070885','2025-09-04 10:32:42.487771','PL-AP-001'),
('INV-PL-SM-001',0,0,'In Stock','2025-09-01 06:27:33.355551','2025-09-01 06:27:33.355565','PL-SM-001'),
('INV-PO-BB-001',0,0,'In Stock','2025-09-01 06:54:02.137790','2025-09-01 06:54:02.137810','PO-BB-001'),
('INV-PO-HC-001',0,0,'In Stock','2025-09-01 06:52:00.839065','2025-09-01 06:52:00.839082','PO-HC-001'),
('INV-PO-MD-001',0,0,'Out Of Stock','2025-09-01 06:56:25.381726','2025-09-04 11:51:43.615077','PO-MD-001'),
('INV-PR-CC-001',0,0,'Out Of Stock','2025-09-04 07:52:14.586634','2025-09-18 05:57:32.257951','PR-CC-001'),
('INV-PR-CC-002',0,0,'In Stock','2025-09-04 07:54:34.961879','2025-09-04 07:54:34.961902','PR-CC-002'),
('INV-PR-CH-001',0,0,'In Stock','2025-09-01 12:14:53.442936','2025-09-01 12:14:53.442948','PR-CH-001'),
('INV-PR-CO-001',0,0,'In Stock','2025-09-04 07:33:10.626183','2025-09-04 07:33:10.626229','PR-CO-001'),
('INV-PR-CP-001',0,0,'In Stock','2025-09-01 12:12:10.690644','2025-09-01 12:12:10.690657','PR-CP-001'),
('INV-PR-CP-002',0,0,'In Stock','2025-09-04 07:56:17.765085','2025-09-04 07:56:17.765099','PR-CP-002'),
('INV-PR-CW-001',0,0,'In Stock','2025-09-01 12:13:47.805469','2025-09-01 12:13:47.805483','PR-CW-001'),
('INV-SP-PB-001',0,0,'In Stock','2025-09-04 06:52:49.211471','2025-09-04 06:52:49.211487','SP-PB-001'),
('INV-SP-PS-001',1000,0,'In Stock','2025-09-01 10:55:15.546012','2025-09-04 11:31:16.545605','SP-PS-001'),
('INV-SP-RB-001',1000,1,'In Stock','2025-09-01 11:20:18.608965','2025-09-01 11:20:18.608983','SP-RB-001'),
('INV-SP-RT-001',1000,1,'In Stock','2025-09-01 11:35:38.970912','2025-09-01 11:35:38.970924','SP-RT-001'),
('INV-SP-SS-001',1000,1,'In Stock','2025-09-01 11:06:03.135833','2025-09-01 11:06:03.135847','SP-SS-001'),
('INV-SP-TB-001',1000,1,'In Stock','2025-09-01 10:38:01.206706','2025-09-01 10:38:01.206719','SP-TB-001'),
('INV-SP-TT-001',1000,-2,'In Stock','2025-09-01 11:48:00.449295','2025-09-01 11:48:00.449308','SP-TT-001'),
('INV-SP-WB-001',1000,1,'In Stock','2025-09-01 10:44:45.880505','2025-09-01 10:44:45.880520','SP-WB-001'),
('INV-SP-WB-002',1000,1,'In Stock','2025-09-01 11:15:09.133333','2025-09-04 11:34:05.962453','SP-WB-002'),
('INV-TA-EF-001',0,0,'In Stock','2025-09-02 08:05:42.218947','2025-09-02 08:05:42.218962','TA-EF-001'),
('INV-TA-HT-001',0,0,'In Stock','2025-09-02 08:09:44.161962','2025-09-02 08:09:44.161977','TA-HT-001'),
('INV-TA-RG-001',0,0,'In Stock','2025-09-02 08:12:46.425139','2025-09-02 08:12:46.425152','TA-RG-001'),
('INV-TA-SG-001',0,0,'In Stock','2025-09-02 08:11:13.954810','2025-09-02 08:11:13.954824','TA-SG-001'),
('INV-TR-CC-001',0,0,'In Stock','2025-09-01 08:10:42.724543','2025-09-01 08:10:42.724566','TR-CC-001'),
('INV-TR-CT-001',1000,1,'In Stock','2025-09-01 07:50:09.464889','2025-09-01 07:50:09.464905','TR-CT-001'),
('INV-TR-CW-001',0,0,'Out Of Stock','2025-09-01 08:07:06.726890','2025-09-04 12:13:07.310582','TR-CW-001'),
('INV-TR-DS-001',0,0,'Out Of Stock','2025-09-03 13:08:57.647525','2025-09-04 11:25:05.727663','TR-DS-001'),
('INV-TR-DW-001',1000,1,'In Stock','2025-09-01 11:55:58.673019','2025-09-01 11:55:58.673033','TR-DW-001'),
('INV-TR-DW-002',1000,1,'In Stock','2025-09-01 12:00:22.747627','2025-09-01 12:03:05.307925','TR-DW-002'),
('INV-TR-LT-001',1000,1,'In Stock','2025-09-01 12:06:27.300799','2025-09-01 12:06:27.300812','TR-LT-001'),
('INV-TR-PT-001',1000,1,'In Stock','2025-09-01 07:54:24.515542','2025-09-01 07:54:24.515556','TR-PT-001'),
('INV-TR-TT-001',1000,1,'In Stock','2025-09-01 12:10:47.287103','2025-09-01 12:10:47.287117','TR-TT-001'),
('INV-UN-CH-001',0,0,'In Stock','2025-09-01 08:28:05.076679','2025-09-01 08:28:05.076697','UN-CH-001'),
('INV-UN-PC-001',0,0,'In Stock','2025-09-01 08:04:24.995174','2025-09-01 08:04:24.995210','UN-PC-001'),
('INV-WO-BW-001',0,0,'Out Of Stock','2025-09-01 06:22:19.823788','2025-09-04 10:48:09.996090','WO-BW-001'),
('INV-WO-EC-001',0,0,'In Stock','2025-09-01 06:29:30.110062','2025-09-01 06:29:30.110076','WO-EC-001'),
('INV-WO-EF-001',0,0,'Out Of Stock','2025-09-03 13:05:04.514702','2025-09-04 10:43:03.220285','WO-EF-001');
/*!40000 ALTER TABLE `admin_backend_final_productinventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_productseo`
--

DROP TABLE IF EXISTS `admin_backend_final_productseo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_productseo` (
  `seo_id` varchar(100) NOT NULL,
  `image_alt_text` varchar(255) NOT NULL,
  `meta_title` varchar(255) NOT NULL,
  `meta_description` longtext NOT NULL,
  `meta_keywords` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`meta_keywords`)),
  `open_graph_title` varchar(255) NOT NULL,
  `open_graph_desc` longtext NOT NULL,
  `open_graph_image_url` varchar(200) NOT NULL,
  `canonical_url` varchar(200) NOT NULL,
  `json_ld` longtext NOT NULL,
  `custom_tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`custom_tags`)),
  `grouped_filters` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`grouped_filters`)),
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`seo_id`),
  UNIQUE KEY `product_id` (`product_id`),
  CONSTRAINT `admin_backend_final__product_id_0b98d163_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_productseo`
--

LOCK TABLES `admin_backend_final_productseo` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_productseo` DISABLE KEYS */;
INSERT INTO `admin_backend_final_productseo` VALUES
('SEO-AC-CC-001','','','','[]','','','','','','[]','[]','2025-09-01 08:08:19.091814','2025-09-01 08:08:19.092158','AC-CC-001'),
('SEO-AC-CP-001','','','','[]','','','','','','[]','[]','2025-09-01 08:21:39.582415','2025-09-01 08:21:39.582817','AC-CP-001'),
('SEO-AC-EU-001','','','','[]','','','','','','[]','[]','2025-09-01 08:09:50.068559','2025-09-01 08:09:50.068893','AC-EU-001'),
('SEO-AC-WA-001','','','','[]','','','','','','[]','[]','2025-09-01 08:23:31.493429','2025-09-01 08:23:31.493748','AC-WA-001'),
('SEO-BA-BA-001','','','','[]','','','','','','[]','[]','2025-09-01 06:14:41.091326','2025-09-04 12:07:59.608247','BA-BA-001'),
('SEO-BA-EC-001','','','','[]','','','','','','[]','[]','2025-09-01 06:24:50.890947','2025-09-04 12:09:47.091874','BA-EC-001'),
('SEO-BA-EC-002','','','','[]','','','','','','[]','[]','2025-09-01 06:31:13.145127','2025-09-01 06:31:13.145466','BA-EC-002'),
('SEO-BA-FB-001','','','','[]','','','','','','[]','[]','2025-09-11 07:23:36.087167','2025-09-11 07:23:36.087625','BA-FB-001'),
('SEO-BA-FB-002','','','','[]','','','','','','[]','[]','2025-09-11 07:34:27.994254','2025-09-11 07:34:27.995476','BA-FB-002'),
('SEO-BA-MC-001','','','','[]','','','','','','[]','[]','2025-09-01 06:22:17.254472','2025-09-01 06:22:17.254856','BA-MC-001'),
('SEO-BR-CA-001','','','','[]','','','','','','[]','[]','2025-09-01 08:38:07.647085','2025-09-01 08:38:07.647528','BR-CA-001'),
('SEO-BR-CM-001','','','','[]','','','','','','[]','[]','2025-09-01 08:20:03.115265','2025-09-01 08:20:03.115626','BR-CM-001'),
('SEO-BR-CP-001','','','','[]','','','','','','[]','[]','2025-09-01 08:13:41.682704','2025-09-01 08:13:41.683073','BR-CP-001'),
('SEO-BR-CR-001','','','','[]','','','','','','[]','[]','2025-09-01 08:34:53.191840','2025-09-01 09:04:32.053124','BR-CR-001'),
('SEO-BR-PE-001','','','','[]','','','','','','[]','[]','2025-09-01 08:29:05.874056','2025-09-01 08:29:05.874460','BR-PE-001'),
('SEO-BR-PG-001','','','','[]','','','','','','[]','[]','2025-09-01 08:24:54.967326','2025-09-01 08:24:54.967796','BR-PG-001'),
('SEO-BR-PP-001','','','','[]','','','','','','[]','[]','2025-09-04 07:59:19.768821','2025-09-04 07:59:19.769163','BR-PP-001'),
('SEO-CA-2T-001','','','','[]','','','','','','[]','[]','2025-09-01 11:05:36.355492','2025-09-01 11:05:36.355808','CA-2T-001'),
('SEO-CA-AN-001','','','','[]','','','','','','[]','[]','2025-09-01 11:26:58.724745','2025-09-01 11:26:58.725079','CA-AN-001'),
('SEO-CA-BC-001','','','','[]','','','','','','[]','[]','2025-09-01 10:37:38.756395','2025-09-01 11:01:10.785707','CA-BC-001'),
('SEO-CA-CO-001','','','','[]','','','','','','[]','[]','2025-09-04 08:13:38.298265','2025-09-04 08:13:38.298776','CA-CO-001'),
('SEO-CA-FC-001','','','','[]','','','','','','[]','[]','2025-09-01 11:13:10.353284','2025-09-01 11:13:10.353758','CA-FC-001'),
('SEO-CA-FW-001','','','','[]','','','','','','[]','[]','2025-09-01 11:08:15.410546','2025-09-04 11:53:58.370578','CA-FW-001'),
('SEO-CA-IC-001','','','','[]','','','','','','[]','[]','2025-09-01 11:34:30.749797','2025-09-01 11:34:30.750207','CA-IC-001'),
('SEO-CA-MN-001','','','','[]','','','','','','[]','[]','2025-09-01 11:18:35.743662','2025-09-01 11:20:26.641755','CA-MN-001'),
('SEO-CA-PR-001','','','','[]','','','','','','[]','[]','2025-09-01 11:36:48.041189','2025-09-01 11:36:48.041620','CA-PR-001'),
('SEO-CA-PS-001','','','','[]','','','','','','[]','[]','2025-09-02 07:54:11.360445','2025-09-02 07:54:11.361373','CA-PS-001'),
('SEO-CA-RA-001','','','','[]','','','','','','[]','[]','2025-09-01 11:24:13.349464','2025-09-01 11:24:13.349891','CA-RA-001'),
('SEO-CA-SB-001','','','','[]','','','','','','[]','[]','2025-09-01 11:03:33.067637','2025-09-01 11:03:33.068082','CA-SB-001'),
('SEO-CE-BC-001','','','','[]','','','','','','[]','[]','2025-09-01 10:02:44.931685','2025-09-01 10:02:44.932479','CE-BC-001'),
('SEO-CE-BS-001','','','','[]','','','','','','[]','[]','2025-09-01 08:18:56.288259','2025-09-01 08:18:56.288984','CE-BS-001'),
('SEO-CE-CC-001','','','','[]','','','','','','[]','[]','2025-09-01 08:55:48.135946','2025-09-04 10:56:31.471551','CE-CC-001'),
('SEO-CE-CE-001','','','','[]','','','','','','[]','[]','2025-09-01 08:22:50.535933','2025-09-01 08:23:54.298830','CE-CE-001'),
('SEO-CE-CG-001','','','','[]','','','','','','[]','[]','2025-09-01 08:07:35.343927','2025-09-01 08:07:35.344339','CE-CG-001'),
('SEO-CE-CM-001','','','','[]','','','','','','[]','[]','2025-09-01 09:32:14.750787','2025-09-04 10:53:19.075464','CE-CM-001'),
('SEO-CE-GB-001','','','','[]','','','','','','[]','[]','2025-09-01 09:04:00.893188','2025-09-01 09:04:01.003095','CE-GB-001'),
('SEO-CE-GC-001','','','','[]','','','','','','[]','[]','2025-09-01 09:12:16.132916','2025-09-01 09:12:16.133242','CE-GC-001'),
('SEO-CE-LM-001','','','','[]','','','','','','[]','[]','2025-09-01 10:13:38.507969','2025-09-01 10:13:38.508361','CE-LM-001'),
('SEO-CE-MC-001','','','','[]','','','','','','[]','[]','2025-09-01 07:59:30.656015','2025-09-01 07:59:30.656510','CE-MC-001'),
('SEO-CE-PC-001','','','','[]','','','','','','[]','[]','2025-09-01 09:24:05.816557','2025-09-01 09:24:05.816990','CE-PC-001'),
('SEO-CE-PM-001','','','','[]','','','','','','[]','[]','2025-09-01 08:34:20.717567','2025-09-01 08:34:20.717904','CE-PM-001'),
('SEO-CE-TT-001','','','','[]','','','','','','[]','[]','2025-09-01 08:47:14.763548','2025-09-01 09:33:17.770022','CE-TT-001'),
('SEO-CE-TT-002','','','','[]','','','','','','[]','[]','2025-09-01 09:19:55.163839','2025-09-01 09:33:45.709280','CE-TT-002'),
('SEO-CE-TT-003','','','','[]','','','','','','[]','[]','2025-09-01 09:41:51.566814','2025-09-01 09:41:51.567142','CE-TT-003'),
('SEO-CE-WC-001','','','','[]','','','','','','[]','[]','2025-09-01 08:14:06.490930','2025-09-04 11:37:35.932843','CE-WC-001'),
('SEO-CE-WC-002','','','','[]','','','','','','[]','[]','2025-09-01 08:41:07.070248','2025-09-01 08:41:07.070667','CE-WC-002'),
('SEO-CE-WC-003','','','','[]','','','','','','[]','[]','2025-09-01 10:09:15.163481','2025-09-01 10:09:15.163831','CE-WC-003'),
('SEO-CE-WS-001','','','','[]','','','','','','[]','[]','2025-09-01 09:09:17.532240','2025-09-01 09:09:17.532610','CE-WS-001'),
('SEO-CE-WS-002','','','','[]','','','','','','[]','[]','2025-09-01 10:20:26.366104','2025-09-01 10:20:26.366426','CE-WS-002'),
('SEO-CO-BE-001','','','','[]','','','','','','[]','[]','2025-09-01 06:38:34.665468','2025-09-04 11:49:49.804407','CO-BE-001'),
('SEO-CO-CB-001','','','','[]','','','','','','[]','[]','2025-09-04 08:30:04.872890','2025-09-04 08:30:04.873314','CO-CB-001'),
('SEO-CO-CC-001','','','','[]','','','','','','[]','[]','2025-09-01 06:50:01.375043','2025-09-01 06:50:01.375419','CO-CC-001'),
('SEO-CO-CL-001','','','','[]','','','','','','[]','[]','2025-09-01 06:44:22.458517','2025-09-04 11:47:12.711864','CO-CL-001'),
('SEO-CO-CU-001','','','','[]','','','','','','[]','[]','2025-09-04 08:31:25.923846','2025-09-04 08:31:25.924287','CO-CU-001'),
('SEO-CO-DU-001','','','','[]','','','','','','[]','[]','2025-09-04 08:28:55.996281','2025-09-04 11:41:53.289329','CO-DU-001'),
('SEO-CO-EF-001','','','','[]','','','','','','[]','[]','2025-09-04 08:23:28.438540','2025-09-04 08:23:28.439009','CO-EF-001'),
('SEO-CO-SC-001','','','','[]','','','','','','[]','[]','2025-09-04 08:26:58.022058','2025-09-04 08:26:58.022555','CO-SC-001'),
('SEO-CO-UM-001','','','','[]','','','','','','[]','[]','2025-09-04 08:33:25.902385','2025-09-04 08:33:25.902858','CO-UM-001'),
('SEO-CO-WU-001','','','','[]','','','','','','[]','[]','2025-09-04 07:54:01.434689','2025-09-04 11:43:50.634092','CO-WU-001'),
('SEO-DE-BF-001','','','','[]','','','','','','[]','[]','2025-09-01 10:22:47.021838','2025-09-01 10:22:47.022257','DE-BF-001'),
('SEO-DE-SF-001','','','','[]','','','','','','[]','[]','2025-09-01 10:26:26.191622','2025-09-01 10:26:26.192056','DE-SF-001'),
('SEO-EC-BF-001','','','','[]','','','','','','[]','[]','2025-09-04 07:10:08.107747','2025-09-04 07:10:08.108174','EC-BF-001'),
('SEO-EC-EF-001','','','','[]','','','','','','[]','[]','2025-09-04 07:01:28.043125','2025-09-04 07:01:28.043557','EC-EF-001'),
('SEO-EV-CE-001','','','','[]','','','','','','[]','[]','2025-09-04 08:16:40.234176','2025-09-04 08:16:40.234563','EV-CE-001'),
('SEO-EV-CJ-001','','','','[]','','','','','','[]','[]','2025-09-01 07:19:05.002735','2025-09-04 12:11:23.946978','EV-CJ-001'),
('SEO-EV-CJ-002','','','','[]','','','','','','[]','[]','2025-09-01 07:31:27.146041','2025-09-04 11:58:30.312702','EV-CJ-002'),
('SEO-EV-CJ-003','','','','[]','','','','','','[]','[]','2025-09-01 07:52:59.441621','2025-09-01 07:52:59.441921','EV-CJ-003'),
('SEO-EV-CL-001','','','','[]','','','','','','[]','[]','2025-09-01 10:10:07.063573','2025-09-01 10:10:07.063956','EV-CL-001'),
('SEO-EV-CR-001','','','','[]','','','','','','[]','[]','2025-09-04 08:18:38.162593','2025-09-04 08:18:38.163024','EV-CR-001'),
('SEO-EV-CR-002','','','','[]','','','','','','[]','[]','2025-09-04 08:21:03.939909','2025-09-04 12:00:55.867782','EV-CR-002'),
('SEO-EV-DP-001','','','','[]','','','','','','[]','[]','2025-09-01 10:11:31.277603','2025-09-01 10:11:31.277918','EV-DP-001'),
('SEO-EV-LW-001','','','','[]','','','','','','[]','[]','2025-09-01 10:08:07.428517','2025-09-01 10:08:07.428987','EV-LW-001'),
('SEO-EV-RJ-001','','','','[]','','','','','','[]','[]','2025-09-01 06:59:40.563265','2025-09-01 07:04:51.877888','EV-RJ-001'),
('SEO-EV-RV-001','','','','[]','','','','','','[]','[]','2025-09-01 08:04:31.874901','2025-09-01 08:04:31.875293','EV-RV-001'),
('SEO-EV-SC-001','','','','[]','','','','','','[]','[]','2025-09-01 06:32:55.746565','2025-09-04 11:55:39.712867','EV-SC-001'),
('SEO-EV-TW-001','','','','[]','','','','','','[]','[]','2025-09-01 10:13:10.524082','2025-09-01 10:13:10.524401','EV-TW-001'),
('SEO-EV-VN-001','','','','[]','','','','','','[]','[]','2025-09-01 08:01:45.610735','2025-09-04 12:03:12.223111','EV-VN-001'),
('SEO-EX-CB-001','','','','[]','','','','','','[]','[]','2025-09-04 08:07:29.822802','2025-09-04 08:07:29.823117','EX-CB-001'),
('SEO-EX-CC-001','','','','[]','','','','','','[]','[]','2025-09-04 08:09:59.936785','2025-09-04 08:09:59.937087','EX-CC-001'),
('SEO-EX-CC-002','','','','[]','','','','','','[]','[]','2025-09-04 08:11:46.922935','2025-09-04 08:11:46.923351','EX-CC-002'),
('SEO-EX-PL-001','','','','[]','','','','','','[]','[]','2025-09-04 07:39:52.241756','2025-09-04 07:39:52.242119','EX-PL-001'),
('SEO-EX-WP-001','','','','[]','','','','','','[]','[]','2025-09-01 12:28:37.690848','2025-09-01 12:28:37.691193','EX-WP-001'),
('SEO-FL-CF-001','','','','[]','','','','','','[]','[]','2025-09-11 06:08:39.747571','2025-09-11 06:08:39.748135','FL-CF-001'),
('SEO-FL-CF-002','','','','[]','','','','','','[]','[]','2025-09-11 06:10:06.893103','2025-09-11 06:10:06.893462','FL-CF-002'),
('SEO-FL-CT-001','','','','[]','','','','','','[]','[]','2025-09-11 06:35:12.915002','2025-09-11 06:35:12.915402','FL-CT-001'),
('SEO-FL-HB-001','','','','[]','','','','','','[]','[]','2025-09-11 06:24:47.276549','2025-09-11 06:24:47.277048','FL-HB-001'),
('SEO-FL-HD-001','','','','[]','','','','','','[]','[]','2025-09-11 06:13:30.998143','2025-09-11 06:13:30.998553','FL-HD-001'),
('SEO-FL-HT-001','','','','[]','','','','','','[]','[]','2025-09-11 06:11:57.654799','2025-09-11 06:11:57.655164','FL-HT-001'),
('SEO-FL-HT-002','','','','[]','','','','','','[]','[]','2025-09-11 06:14:38.841492','2025-09-11 06:14:38.841910','FL-HT-002'),
('SEO-FL-LS-001','','','','[]','','','','','','[]','[]','2025-09-11 06:16:07.815520','2025-09-11 06:16:07.815877','FL-LS-001'),
('SEO-FL-PF-001','','','','[]','','','','','','[]','[]','2025-09-11 06:17:21.223988','2025-09-11 06:17:21.224515','FL-PF-001'),
('SEO-FL-PF-002','','','','[]','','','','','','[]','[]','2025-09-11 06:31:34.717372','2025-09-11 06:31:34.717871','FL-PF-002'),
('SEO-FL-PT-001','','','','[]','','','','','','[]','[]','2025-09-11 06:19:06.446412','2025-09-11 06:19:06.446908','FL-PT-001'),
('SEO-FL-ST-001','','','','[]','','','','','','[]','[]','2025-09-11 06:21:40.726085','2025-09-11 06:21:40.726557','FL-ST-001'),
('SEO-FL-TD-001','','','','[]','','','','','','[]','[]','2025-09-11 06:39:46.610602','2025-09-11 06:39:46.611089','FL-TD-001'),
('SEO-FL-TS-001','','','','[]','','','','','','[]','[]','2025-09-11 06:23:09.818864','2025-09-11 06:37:42.484558','FL-TS-001'),
('SEO-FL-VC-001','','','','[]','','','','','','[]','[]','2025-09-11 06:27:31.061571','2025-09-11 06:27:31.061952','FL-VC-001'),
('SEO-FL-VS-001','','','','[]','','','','','','[]','[]','2025-09-11 06:26:33.947858','2025-09-11 06:26:33.948330','FL-VS-001'),
('SEO-FL-YS-001','','','','[]','','','','','','[]','[]','2025-09-11 06:28:30.532830','2025-09-11 06:28:30.533299','FL-YS-001'),
('SEO-GI-LP-001','','','','[]','','','','','','[]','[]','2025-09-01 06:24:30.058224','2025-09-04 10:50:07.135417','GI-LP-001'),
('SEO-NO-AS-001','','','','[]','','','','','','[]','[]','2025-09-01 12:17:14.125686','2025-09-04 12:19:20.963488','NO-AS-001'),
('SEO-NO-BA-001','','','','[]','','','','','','[]','[]','2025-09-01 11:49:22.069671','2025-09-04 12:14:54.007048','NO-BA-001'),
('SEO-NO-CB-001','','','','[]','','','','','','[]','[]','2025-09-01 11:45:09.061346','2025-09-01 11:45:09.061761','NO-CB-001'),
('SEO-NO-CC-001','','','','[]','','','','','','[]','[]','2025-09-04 08:05:19.031082','2025-09-04 08:05:19.031529','NO-CC-001'),
('SEO-NO-LP-001','','','','[]','','','','','','[]','[]','2025-09-01 12:06:56.671571','2025-09-01 12:06:56.671995','NO-LP-001'),
('SEO-NO-PD-001','','','','[]','','','','','','[]','[]','2025-09-01 11:56:03.021191','2025-09-04 12:20:56.381359','NO-PD-001'),
('SEO-NO-SN-001','','','','[]','','','','','','[]','[]','2025-09-01 12:10:13.227048','2025-09-04 12:17:09.659828','NO-SN-001'),
('SEO-NO-SN-002','','','','[]','','','','','','[]','[]','2025-09-01 12:14:18.324901','2025-09-01 12:14:18.325271','NO-SN-002'),
('SEO-PL-AP-001','','','','[]','','','','','','[]','[]','2025-09-03 12:56:02.072520','2025-09-04 10:32:42.489507','PL-AP-001'),
('SEO-PL-SM-001','','','','[]','','','','','','[]','[]','2025-09-01 06:27:33.357189','2025-09-01 06:27:33.357553','PL-SM-001'),
('SEO-PO-BB-001','','','','[]','','','','','','[]','[]','2025-09-01 06:54:02.139522','2025-09-01 06:54:02.139957','PO-BB-001'),
('SEO-PO-HC-001','','','','[]','','','','','','[]','[]','2025-09-01 06:52:00.841147','2025-09-01 06:52:00.841665','PO-HC-001'),
('SEO-PO-MD-001','','','','[]','','','','','','[]','[]','2025-09-01 06:56:25.383167','2025-09-04 11:51:43.616716','PO-MD-001'),
('SEO-PR-CC-001','','','','[]','','','','','','[]','[]','2025-09-04 07:52:14.588963','2025-09-18 05:57:32.259856','PR-CC-001'),
('SEO-PR-CC-002','','','','[]','','','','','','[]','[]','2025-09-04 07:54:34.965120','2025-09-04 07:54:34.965611','PR-CC-002'),
('SEO-PR-CH-001','','','','[]','','','','','','[]','[]','2025-09-01 12:14:53.444344','2025-09-01 12:14:53.444663','PR-CH-001'),
('SEO-PR-CO-001','','','','[]','','','','','','[]','[]','2025-09-04 07:33:10.628961','2025-09-04 07:33:10.629449','PR-CO-001'),
('SEO-PR-CP-001','','','','[]','','','','','','[]','[]','2025-09-01 12:12:10.692071','2025-09-01 12:12:10.692397','PR-CP-001'),
('SEO-PR-CP-002','','','','[]','','','','','','[]','[]','2025-09-04 07:56:17.767017','2025-09-04 07:56:17.767420','PR-CP-002'),
('SEO-PR-CW-001','','','','[]','','','','','','[]','[]','2025-09-01 12:13:47.807026','2025-09-01 12:13:47.807772','PR-CW-001'),
('SEO-SP-PB-001','','','','[]','','','','','','[]','[]','2025-09-04 06:52:49.214639','2025-09-04 06:52:49.215139','SP-PB-001'),
('SEO-SP-PS-001','','','','[]','','','','','','[]','[]','2025-09-01 10:55:15.547630','2025-09-04 11:31:16.547260','SP-PS-001'),
('SEO-SP-RB-001','','','','[]','','','','','','[]','[]','2025-09-01 11:20:18.611006','2025-09-01 11:20:18.611528','SP-RB-001'),
('SEO-SP-RT-001','','','','[]','','','','','','[]','[]','2025-09-01 11:35:38.972412','2025-09-01 11:35:38.972813','SP-RT-001'),
('SEO-SP-SS-001','','','','[]','','','','','','[]','[]','2025-09-01 11:06:03.137271','2025-09-01 11:06:03.137601','SP-SS-001'),
('SEO-SP-TB-001','','','','[]','','','','','','[]','[]','2025-09-01 10:38:01.208266','2025-09-01 10:38:01.208625','SP-TB-001'),
('SEO-SP-TT-001','','','','[]','','','','','','[]','[]','2025-09-01 11:48:00.450643','2025-09-01 11:48:00.450950','SP-TT-001'),
('SEO-SP-WB-001','','','','[]','','','','','','[]','[]','2025-09-01 10:44:45.881971','2025-09-01 10:44:45.882298','SP-WB-001'),
('SEO-SP-WB-002','','','','[]','','','','','','[]','[]','2025-09-01 11:15:09.135109','2025-09-04 11:34:05.964172','SP-WB-002'),
('SEO-TA-EF-001','','','','[]','','','','','','[]','[]','2025-09-02 08:05:42.220759','2025-09-02 08:05:42.221152','TA-EF-001'),
('SEO-TA-HT-001','','','','[]','','','','','','[]','[]','2025-09-02 08:09:44.163880','2025-09-02 08:09:44.164287','TA-HT-001'),
('SEO-TA-RG-001','','','','[]','','','','','','[]','[]','2025-09-02 08:12:46.426715','2025-09-02 08:12:46.427083','TA-RG-001'),
('SEO-TA-SG-001','','','','[]','','','','','','[]','[]','2025-09-02 08:11:13.956374','2025-09-02 08:11:13.956712','TA-SG-001'),
('SEO-TR-CC-001','','','','[]','','','','','','[]','[]','2025-09-01 08:10:42.726897','2025-09-01 08:10:42.727318','TR-CC-001'),
('SEO-TR-CT-001','','','','[]','','','','','','[]','[]','2025-09-01 07:50:09.466574','2025-09-01 07:50:09.466925','TR-CT-001'),
('SEO-TR-CW-001','','','','[]','','','','','','[]','[]','2025-09-01 08:07:06.728701','2025-09-04 12:13:07.312689','TR-CW-001'),
('SEO-TR-DS-001','','','','[]','','','','','','[]','[]','2025-09-03 13:08:57.649181','2025-09-04 11:25:05.729408','TR-DS-001'),
('SEO-TR-DW-001','','','','[]','','','','','','[]','[]','2025-09-01 11:55:58.674579','2025-09-01 11:55:58.674939','TR-DW-001'),
('SEO-TR-DW-002','','','','[]','','','','','','[]','[]','2025-09-01 12:00:22.749414','2025-09-01 12:03:05.309830','TR-DW-002'),
('SEO-TR-LT-001','','','','[]','','','','','','[]','[]','2025-09-01 12:06:27.302316','2025-09-01 12:06:27.302655','TR-LT-001'),
('SEO-TR-PT-001','','','','[]','','','','','','[]','[]','2025-09-01 07:54:24.517219','2025-09-01 07:54:24.517598','TR-PT-001'),
('SEO-TR-TT-001','','','','[]','','','','','','[]','[]','2025-09-01 12:10:47.288545','2025-09-01 12:10:47.288862','TR-TT-001'),
('SEO-UN-CH-001','','','','[]','','','','','','[]','[]','2025-09-01 08:28:05.078517','2025-09-01 08:28:05.078903','UN-CH-001'),
('SEO-UN-PC-001','','','','[]','','','','','','[]','[]','2025-09-01 08:04:24.997122','2025-09-01 08:04:24.997622','UN-PC-001'),
('SEO-WO-BW-001','','','','[]','','','','','','[]','[]','2025-09-01 06:22:19.825767','2025-09-04 10:48:09.997711','WO-BW-001'),
('SEO-WO-EC-001','','','','[]','','','','','','[]','[]','2025-09-01 06:29:30.111554','2025-09-01 06:29:30.111955','WO-EC-001'),
('SEO-WO-EF-001','','','','[]','','','','','','[]','[]','2025-09-03 13:05:04.517310','2025-09-04 10:43:03.222126','WO-EF-001');
/*!40000 ALTER TABLE `admin_backend_final_productseo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_productsubcategorymap`
--

DROP TABLE IF EXISTS `admin_backend_final_productsubcategorymap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_productsubcategorymap` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `product_id` varchar(100) NOT NULL,
  `subcategory_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_backend_final_prod_product_id_subcategory_i_d170acfe_uniq` (`product_id`,`subcategory_id`),
  KEY `admin_backe_product_b23fc6_idx` (`product_id`),
  KEY `admin_backe_subcate_c8e19f_idx` (`subcategory_id`),
  CONSTRAINT `admin_backend_final__product_id_1c0bff6c_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`),
  CONSTRAINT `admin_backend_final__subcategory_id_3a94323e_fk_admin_bac` FOREIGN KEY (`subcategory_id`) REFERENCES `admin_backend_final_subcategory` (`subcategory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=349 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_productsubcategorymap`
--

LOCK TABLES `admin_backend_final_productsubcategorymap` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_productsubcategorymap` DISABLE KEYS */;
INSERT INTO `admin_backend_final_productsubcategorymap` VALUES
(136,'AC-CC-001','CAA-ACCESSORIES-001'),
(147,'AC-CP-001','CAA-ACCESSORIES-001'),
(137,'AC-EU-001','CAA-ACCESSORIES-001'),
(149,'AC-WA-001','CAA-ACCESSORIES-001'),
(315,'BA-BA-001','B&T-BACKPACKS-001'),
(316,'BA-EC-001','B&T-BACKPACKS-001'),
(109,'BA-EC-002','B&T-BACKPACKS-001'),
(341,'BA-FB-001','BD&F-BANNERS-001'),
(342,'BA-FB-002','BD&F-BANNERS-001'),
(103,'BA-MC-001','B&T-BACKPACKS-001'),
(157,'BR-CA-001','EG&S-BRANDED-001'),
(146,'BR-CM-001','EG&S-BRANDED-001'),
(141,'BR-CP-001','EG&S-BRANDED-001'),
(169,'BR-CR-001','EG&S-BRANDED-001'),
(154,'BR-PE-001','EG&S-BRANDED-001'),
(151,'BR-PG-001','EG&S-BRANDED-001'),
(268,'BR-PP-001','EG&S-BRANDED-001'),
(198,'CA-2T-001','O&S-CALENDARS-001'),
(207,'CA-AN-001','O&S-CALENDARS-001'),
(196,'CA-BC-001','O&S-CALENDARS-001'),
(274,'CA-CO-001','O&S-CALENDARS-001'),
(201,'CA-FC-001','O&S-CALENDARS-001'),
(309,'CA-FW-001','O&S-CALENDARS-001'),
(208,'CA-IC-001','O&S-CALENDARS-001'),
(205,'CA-MN-001','O&S-CALENDARS-001'),
(210,'CA-PR-001','O&S-CALENDARS-001'),
(249,'CA-PS-001','CAA-CAPS-001'),
(206,'CA-RA-001','O&S-CALENDARS-001'),
(197,'CA-SB-001','O&S-CALENDARS-001'),
(180,'CE-BC-001','D-CERAMIC-001'),
(145,'CE-BS-001','D-CERAMIC-001'),
(297,'CE-CC-001','D-CERAMIC-001'),
(298,'CE-CC-001','P&MM-CERAMIC-001'),
(150,'CE-CE-001','D-CERAMIC-001'),
(240,'CE-CE-001','P&MM-CERAMIC-001'),
(135,'CE-CG-001','D-CERAMIC-001'),
(239,'CE-CG-001','P&MM-CERAMIC-001'),
(295,'CE-CM-001','D-CERAMIC-001'),
(296,'CE-CM-001','P&MM-CERAMIC-001'),
(168,'CE-GB-001','D-CERAMIC-001'),
(171,'CE-GC-001','D-CERAMIC-001'),
(241,'CE-GC-001','P&MM-CERAMIC-001'),
(186,'CE-LM-001','D-CERAMIC-001'),
(129,'CE-MC-001','D-CERAMIC-001'),
(173,'CE-PC-001','D-CERAMIC-001'),
(155,'CE-PM-001','D-CERAMIC-001'),
(176,'CE-TT-001','D-CERAMIC-001'),
(244,'CE-TT-001','P&MM-CERAMIC-001'),
(177,'CE-TT-002','D-CERAMIC-001'),
(242,'CE-TT-002','P&MM-CERAMIC-001'),
(178,'CE-TT-003','D-CERAMIC-001'),
(243,'CE-TT-003','P&MM-CERAMIC-001'),
(302,'CE-WC-001','D-CERAMIC-001'),
(303,'CE-WC-001','P&MM-CERAMIC-001'),
(158,'CE-WC-002','D-CERAMIC-001'),
(182,'CE-WC-003','D-CERAMIC-001'),
(245,'CE-WC-003','P&MM-CERAMIC-001'),
(170,'CE-WS-001','D-CERAMIC-001'),
(248,'CE-WS-001','P&MM-CERAMIC-001'),
(187,'CE-WS-002','D-CERAMIC-001'),
(247,'CE-WS-002','P&MM-CERAMIC-001'),
(307,'CO-BE-001','T-COMPUTER-001'),
(283,'CO-CB-001','T-COMPUTER-001'),
(278,'CO-CC-001','T-CUSTOM-001'),
(306,'CO-CL-001','T-COMPUTER-001'),
(284,'CO-CU-001','T-COMPUTER-001'),
(304,'CO-DU-001','T-CUSTOM-001'),
(287,'CO-EF-001','T-CUSTOM-001'),
(288,'CO-SC-001','T-CUSTOM-001'),
(285,'CO-UM-001','T-COMPUTER-001'),
(305,'CO-WU-001','T-CUSTOM-001'),
(188,'DE-BF-001','EG&S-DECORATIVE-001'),
(189,'DE-SF-001','EG&S-DECORATIVE-001'),
(261,'EC-BF-001','D-ECO-FRIENDLY-001'),
(260,'EC-EF-001','D-ECO-FRIENDLY-001'),
(275,'EV-CE-001','B&T-EVERYDAY-001'),
(317,'EV-CJ-001','B&T-EVERYDAY-001'),
(311,'EV-CJ-002','B&T-EVERYDAY-001'),
(127,'EV-CJ-003','B&T-EVERYDAY-001'),
(183,'EV-CL-001','EG&S-EVENT-001'),
(276,'EV-CR-001','B&T-EVERYDAY-001'),
(312,'EV-CR-002','B&T-EVERYDAY-001'),
(184,'EV-DP-001','EG&S-EVENT-001'),
(181,'EV-LW-001','EG&S-EVENT-001'),
(119,'EV-RJ-001','B&T-EVERYDAY-001'),
(132,'EV-RV-001','B&T-EVERYDAY-001'),
(310,'EV-SC-001','B&T-EVERYDAY-001'),
(185,'EV-TW-001','EG&S-EVENT-001'),
(313,'EV-VN-001','B&T-EVERYDAY-001'),
(271,'EX-CB-001','O&S-EXECUTIVE-001'),
(272,'EX-CC-001','O&S-EXECUTIVE-001'),
(273,'EX-CC-002','O&S-EXECUTIVE-001'),
(263,'EX-PL-001','O&S-EXECUTIVE-001'),
(235,'EX-WP-001','O&S-EXECUTIVE-001'),
(323,'FL-CF-001','BD&F-FLAGS-001'),
(324,'FL-CF-002','BD&F-FLAGS-001'),
(338,'FL-CT-001','BD&F-FLAGS-001'),
(333,'FL-HB-001','BD&F-FLAGS-001'),
(326,'FL-HD-001','BD&F-FLAGS-001'),
(325,'FL-HT-001','BD&F-FLAGS-001'),
(327,'FL-HT-002','BD&F-FLAGS-001'),
(328,'FL-LS-001','BD&F-FLAGS-001'),
(329,'FL-PF-001','BD&F-FLAGS-001'),
(337,'FL-PF-002','BD&F-FLAGS-001'),
(330,'FL-PT-001','BD&F-FLAGS-001'),
(331,'FL-ST-001','BD&F-FLAGS-001'),
(340,'FL-TD-001','BD&F-FLAGS-001'),
(339,'FL-TS-001','BD&F-FLAGS-001'),
(335,'FL-VC-001','BD&F-FLAGS-001'),
(334,'FL-VS-001','BD&F-FLAGS-001'),
(336,'FL-YS-001','BD&F-FLAGS-001'),
(294,'GI-LP-001','WI-GIFT-001'),
(321,'NO-AS-001','O&S-NOTEBOOKS-001'),
(319,'NO-BA-001','O&S-NOTEBOOKS-001'),
(212,'NO-CB-001','O&S-NOTEBOOKS-001'),
(270,'NO-CC-001','O&S-NOTEBOOKS-001'),
(223,'NO-LP-001','O&S-NOTEBOOKS-001'),
(322,'NO-PD-001','O&S-NOTEBOOKS-001'),
(320,'NO-SN-001','O&S-NOTEBOOKS-001'),
(230,'NO-SN-002','O&S-NOTEBOOKS-001'),
(290,'PL-AP-001','WI-PLASTIC-001'),
(107,'PL-SM-001','WI-PLASTIC-001'),
(115,'PO-BB-001','T-POWER-001'),
(114,'PO-HC-001','T-POWER-001'),
(308,'PO-MD-001','T-POWER-001'),
(346,'PR-CC-001','P&MM-PROMOTIONAL-001'),
(266,'PR-CC-002','P&MM-PROMOTIONAL-001'),
(231,'PR-CH-001','P&MM-PROMOTIONAL-001'),
(262,'PR-CO-001','EG&S-PREMIUM-001'),
(228,'PR-CP-001','P&MM-PROMOTIONAL-001'),
(267,'PR-CP-002','P&MM-PROMOTIONAL-001'),
(229,'PR-CW-001','P&MM-PROMOTIONAL-001'),
(259,'SP-PB-001','D-SPORTS-001'),
(300,'SP-PS-001','D-SPORTS-001'),
(204,'SP-RB-001','D-SPORTS-001'),
(209,'SP-RT-001','D-SPORTS-001'),
(199,'SP-SS-001','D-SPORTS-001'),
(191,'SP-TB-001','D-SPORTS-001'),
(213,'SP-TT-001','D-SPORTS-001'),
(192,'SP-WB-001','D-SPORTS-001'),
(301,'SP-WB-002','D-SPORTS-001'),
(250,'TA-EF-001','D-TABLE-001'),
(251,'TA-HT-001','D-TABLE-001'),
(253,'TA-RG-001','D-TABLE-001'),
(252,'TA-SG-001','D-TABLE-001'),
(138,'TR-CC-001','B&T-TRAVEL-001'),
(238,'TR-CC-001','P&MM-CERAMIC-001'),
(126,'TR-CT-001','D-TRAVEL-001'),
(318,'TR-CW-001','B&T-TRAVEL-001'),
(299,'TR-DS-001','D-TRAVEL-001'),
(215,'TR-DW-001','D-TRAVEL-001'),
(219,'TR-DW-002','D-TRAVEL-001'),
(222,'TR-LT-001','D-TRAVEL-001'),
(128,'TR-PT-001','D-TRAVEL-001'),
(227,'TR-TT-001','D-TRAVEL-001'),
(153,'UN-CH-001','CAA-UNIFORMS-001'),
(131,'UN-PC-001','CAA-UNIFORMS-001'),
(293,'WO-BW-001','WI-WOODEN-001'),
(108,'WO-EC-001','WI-WOODEN-001'),
(292,'WO-EF-001','WI-WOODEN-001');
/*!40000 ALTER TABLE `admin_backend_final_productsubcategorymap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_productvariant`
--

DROP TABLE IF EXISTS `admin_backend_final_productvariant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_productvariant` (
  `variant_id` varchar(100) NOT NULL,
  `size` varchar(50) NOT NULL,
  `color` varchar(50) NOT NULL,
  `material_type` varchar(50) NOT NULL,
  `fabric_finish` varchar(50) NOT NULL,
  `printing_methods` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`printing_methods`)),
  `add_on_options` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`add_on_options`)),
  `created_at` datetime(6) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`variant_id`),
  KEY `admin_backend_final__product_id_adee4ffc_fk_admin_bac` (`product_id`),
  CONSTRAINT `admin_backend_final__product_id_adee4ffc_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_productvariant`
--

LOCK TABLES `admin_backend_final_productvariant` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_productvariant` DISABLE KEYS */;
INSERT INTO `admin_backend_final_productvariant` VALUES
('VAR-00DFE823','','','','','[]','[]','2025-09-04 12:14:54.009896','NO-BA-001'),
('VAR-012884EF','','','','','[]','[]','2025-09-11 06:28:30.536169','FL-YS-001'),
('VAR-0200AC6B','','','','','[]','[]','2025-09-01 11:13:10.356495','CA-FC-001'),
('VAR-0391E8E0','','','','','[]','[]','2025-09-11 06:19:06.449986','FL-PT-001'),
('VAR-047FA617','','','','','[]','[]','2025-09-01 08:07:35.346844','CE-CG-001'),
('VAR-05281F09','','','','','[]','[]','2025-09-11 06:16:07.818548','FL-LS-001'),
('VAR-06E055B3','','','','','[]','[]','2025-09-02 08:09:44.167565','TA-HT-001'),
('VAR-07403190','','','','','[]','[]','2025-09-01 12:28:37.693403','EX-WP-001'),
('VAR-07C63211','','','','','[]','[]','2025-09-01 11:20:18.614373','SP-RB-001'),
('VAR-09941A32','','','','','[]','[]','2025-09-01 08:41:07.072809','CE-WC-002'),
('VAR-0ADADA27','','','','','[]','[]','2025-09-11 06:31:34.720401','FL-PF-002'),
('VAR-0BB0AEEA','','','','','[]','[]','2025-09-11 06:10:06.895745','FL-CF-002'),
('VAR-0E26097F','','','','','[]','[]','2025-09-04 10:53:19.079057','CE-CM-001'),
('VAR-0E6FF39D','','','','','[]','[]','2025-09-01 10:20:26.368311','CE-WS-002'),
('VAR-106CE217','','','','','[]','[]','2025-09-01 10:08:07.431895','EV-LW-001'),
('VAR-14E3A97E','','','','','[]','[]','2025-09-01 08:10:42.729507','TR-CC-001'),
('VAR-16F247C3','','','','','[]','[]','2025-09-04 12:19:20.966276','NO-AS-001'),
('VAR-189B31C2','','','','','[]','[]','2025-09-01 11:01:10.788717','CA-BC-001'),
('VAR-1920CAED','','','','','[]','[]','2025-09-01 08:13:41.685073','BR-CP-001'),
('VAR-1A7021C3','','','','','[]','[]','2025-09-01 06:31:13.147816','BA-EC-002'),
('VAR-1D1EB90A','','','','','[]','[]','2025-09-04 07:54:34.969254','PR-CC-002'),
('VAR-1E540F05','','','','','[]','[]','2025-09-04 06:52:49.218411','SP-PB-001'),
('VAR-1F261567','','','','','[]','[]','2025-09-04 11:41:53.292576','CO-DU-001'),
('VAR-1F3EA263','','','','','[]','[]','2025-09-04 11:47:12.714502','CO-CL-001'),
('VAR-21541817','','','','','[]','[]','2025-09-01 08:04:31.878111','EV-RV-001'),
('VAR-22F3ACE3','','','','','[]','[]','2025-09-01 11:26:58.727165','CA-AN-001'),
('VAR-230D8F43','','','','','[]','[]','2025-09-01 12:10:47.290724','TR-TT-001'),
('VAR-2381262F','','','','','[]','[]','2025-09-01 12:14:18.327284','NO-SN-002'),
('VAR-24FA418A','','','','','[]','[]','2025-09-04 12:20:56.383994','NO-PD-001'),
('VAR-26AD3953','','','','','[]','[]','2025-09-04 08:30:04.875640','CO-CB-001'),
('VAR-2C14DEB8','','','','','[]','[]','2025-09-01 08:24:54.970762','BR-PG-001'),
('VAR-2D1537FF','','','','','[]','[]','2025-09-01 08:08:19.094779','AC-CC-001'),
('VAR-2D72FF0B','','','','','[]','[]','2025-09-11 06:27:31.064429','FL-VC-001'),
('VAR-2DCD0856','','','','','[]','[]','2025-09-01 07:54:24.520288','TR-PT-001'),
('VAR-31FCFFA6','','','','','[]','[]','2025-09-01 06:29:30.114604','WO-EC-001'),
('VAR-336C171F','','','','','[]','[]','2025-09-04 12:17:09.662970','NO-SN-001'),
('VAR-344B586E','','','','','[]','[]','2025-09-01 11:34:30.753165','CA-IC-001'),
('VAR-347827F9','','','','','[]','[]','2025-09-04 11:37:35.935592','CE-WC-001'),
('VAR-35EE42B4','','','','','[]','[]','2025-09-04 08:26:58.025971','CO-SC-001'),
('VAR-364B7E9E','','','','','[]','[]','2025-09-11 06:17:21.229738','FL-PF-001'),
('VAR-3C86116F','','','','','[]','[]','2025-09-11 06:21:40.730339','FL-ST-001'),
('VAR-3E230F12','','','','','[]','[]','2025-09-01 07:50:09.470041','TR-CT-001'),
('VAR-3F270F8B','','','','','[]','[]','2025-09-01 10:26:26.194647','DE-SF-001'),
('VAR-404B4DD7','','','','','[]','[]','2025-09-01 12:12:10.694335','PR-CP-001'),
('VAR-41AB9ABB','','','','','[]','[]','2025-09-01 08:34:20.720427','CE-PM-001'),
('VAR-4506961A','','','','','[]','[]','2025-09-01 06:22:17.257421','BA-MC-001'),
('VAR-46C7C899','','','','','[]','[]','2025-09-01 10:10:07.066127','EV-CL-001'),
('VAR-4AE6C044','','','','','[]','[]','2025-09-01 10:22:47.024470','DE-BF-001'),
('VAR-4B61D313','','','','','[]','[]','2025-09-04 08:09:59.939168','EX-CC-001'),
('VAR-4E8DCC69','','','','','[]','[]','2025-09-02 07:54:11.365067','CA-PS-001'),
('VAR-4FD8938D','','','','','[]','[]','2025-09-01 06:27:33.360071','PL-SM-001'),
('VAR-5479B653','','','','','[]','[]','2025-09-01 12:06:56.674162','NO-LP-001'),
('VAR-55631594','','','','','[]','[]','2025-09-01 10:02:44.935291','CE-BC-001'),
('VAR-56DC5E50','','','','','[]','[]','2025-09-11 06:24:47.280158','FL-HB-001'),
('VAR-585CDCBF','','','','','[]','[]','2025-09-01 08:09:50.070986','AC-EU-001'),
('VAR-5A297842','','','','','[]','[]','2025-09-04 10:48:10.000692','WO-BW-001'),
('VAR-5CC4EA80','','','','','[]','[]','2025-09-04 12:13:07.316584','TR-CW-001'),
('VAR-5DEAF19A','','','','','[]','[]','2025-09-01 12:13:47.809780','PR-CW-001'),
('VAR-5F6C0B2C','','','','','[]','[]','2025-09-01 07:04:51.881029','EV-RJ-001'),
('VAR-644387A2','','','','','[]','[]','2025-09-04 10:43:03.224938','WO-EF-001'),
('VAR-6763C196','','','','','[]','[]','2025-09-01 07:59:30.658822','CE-MC-001'),
('VAR-6A49DC70','','','','','[]','[]','2025-09-04 12:00:55.870334','EV-CR-002'),
('VAR-6B075F5E','','','','','[]','[]','2025-09-11 06:14:38.844710','FL-HT-002'),
('VAR-6B08F433','','','','','[]','[]','2025-09-11 06:37:42.487545','FL-TS-001'),
('VAR-6CF38A02','','','','','[]','[]','2025-09-04 12:07:59.610816','BA-BA-001'),
('VAR-6DC0E541','','','','','[]','[]','2025-09-04 11:55:39.716087','EV-SC-001'),
('VAR-728D1CDE','','','','','[]','[]','2025-09-01 11:45:09.063856','NO-CB-001'),
('VAR-7300B973','','','','','[]','[]','2025-09-04 11:31:16.550362','SP-PS-001'),
('VAR-73B8B0CC','','','','','[]','[]','2025-09-04 08:23:28.441124','CO-EF-001'),
('VAR-754A40C2','','','','','[]','[]','2025-09-04 11:34:05.967333','SP-WB-002'),
('VAR-763BCA83','','','','','[]','[]','2025-09-04 08:05:19.034228','NO-CC-001'),
('VAR-77D7CB29','','','','','[]','[]','2025-09-01 11:36:48.043770','CA-PR-001'),
('VAR-786C1C7D','','','','','[]','[]','2025-09-01 09:24:05.819035','CE-PC-001'),
('VAR-7AD139A1','','','','','[]','[]','2025-09-01 09:04:32.056535','BR-CR-001'),
('VAR-7D49BE91','','','','','[]','[]','2025-09-04 07:59:19.771095','BR-PP-001'),
('VAR-7D581519','','','','','[]','[]','2025-09-01 11:24:13.352481','CA-RA-001'),
('VAR-80B12E24','','','','','[]','[]','2025-09-01 11:55:58.677121','TR-DW-001'),
('VAR-84F8D14B','','','','','[]','[]','2025-09-02 08:12:46.429272','TA-RG-001'),
('VAR-8A8CE31B','','','','','[]','[]','2025-09-01 09:41:51.569409','CE-TT-003'),
('VAR-8B5D3173','','','','','[]','[]','2025-09-01 11:20:26.644370','CA-MN-001'),
('VAR-8CC9C9DE','','','','','[]','[]','2025-09-01 09:12:16.135155','CE-GC-001'),
('VAR-8D0314F4','','','','','[]','[]','2025-09-11 07:34:27.997967','BA-FB-002'),
('VAR-8E093245','','','','','[]','[]','2025-09-01 11:35:38.975017','SP-RT-001'),
('VAR-8E41F967','','','','','[]','[]','2025-09-04 07:39:52.244249','EX-PL-001'),
('VAR-97490433','','','','','[]','[]','2025-09-01 10:38:01.210667','SP-TB-001'),
('VAR-979EC677','','','','','[]','[]','2025-09-18 05:57:32.263617','PR-CC-001'),
('VAR-9BD9F72F','','','','','[]','[]','2025-09-01 08:23:54.301372','CE-CE-001'),
('VAR-9DF044C7','','','','','[]','[]','2025-09-01 08:20:03.117597','BR-CM-001'),
('VAR-9ECD9FCF','','','','','[]','[]','2025-09-01 11:03:33.070613','CA-SB-001'),
('VAR-9EF7198B','','','','','[]','[]','2025-09-04 08:18:38.165407','EV-CR-001'),
('VAR-9F2417A9','','','','','[]','[]','2025-09-11 06:35:12.917750','FL-CT-001'),
('VAR-A1DE2736','','','','','[]','[]','2025-09-04 12:09:47.094620','BA-EC-001'),
('VAR-A52C9E25','','','','','[]','[]','2025-09-01 12:14:53.446602','PR-CH-001'),
('VAR-A558D664','','','','','[]','[]','2025-09-04 12:11:23.950968','EV-CJ-001'),
('VAR-A59C0418','','','','','[]','[]','2025-09-01 08:04:25.000490','UN-PC-001'),
('VAR-A9CF0C1C','','','','','[]','[]','2025-09-04 08:33:25.905648','CO-UM-001'),
('VAR-A9EB5A23','','','','','[]','[]','2025-09-01 09:33:45.712295','CE-TT-002'),
('VAR-ADA60B87','','','','','[]','[]','2025-09-01 08:18:56.291851','CE-BS-001'),
('VAR-B1DE1B90','','','','','[]','[]','2025-09-04 07:01:28.046355','EC-EF-001'),
('VAR-B42FD460','','','','','[]','[]','2025-09-01 10:13:38.510644','CE-LM-001'),
('VAR-B4D6C3CC','','','','','[]','[]','2025-09-04 11:25:05.732479','TR-DS-001'),
('VAR-B59FC4C2','','','','','[]','[]','2025-09-01 08:38:07.650310','BR-CA-001'),
('VAR-B5D34D27','','','','','[]','[]','2025-09-01 08:21:39.585515','AC-CP-001'),
('VAR-B6396C28','','','','','[]','[]','2025-09-01 10:11:31.280039','EV-DP-001'),
('VAR-B66EDA74','','','','','[]','[]','2025-09-04 11:53:58.374238','CA-FW-001'),
('VAR-B874E158','','','','','[]','[]','2025-09-04 07:56:17.769634','PR-CP-002'),
('VAR-B94137F6','','','','','[]','[]','2025-09-01 11:48:00.453792','SP-TT-001'),
('VAR-B9E18364','','','','','[]','[]','2025-09-11 06:13:31.001293','FL-HD-001'),
('VAR-BA166700','','','','','[]','[]','2025-09-01 10:13:10.526263','EV-TW-001'),
('VAR-BB4AF5B3','','','','','[]','[]','2025-09-01 09:04:01.005893','CE-GB-001'),
('VAR-BC45583C','','','','','[]','[]','2025-09-04 07:33:10.632823','PR-CO-001'),
('VAR-BCE3EF48','','','','','[]','[]','2025-09-01 09:33:17.773033','CE-TT-001'),
('VAR-BEF4C712','','','','','[]','[]','2025-09-04 08:31:25.927058','CO-CU-001'),
('VAR-C0A3EEE4','','','','','[]','[]','2025-09-04 11:49:49.807862','CO-BE-001'),
('VAR-C0EF4E83','','','','','[]','[]','2025-09-01 12:03:05.313009','TR-DW-002'),
('VAR-C146CD25','','','','','[]','[]','2025-09-04 07:10:08.111608','EC-BF-001'),
('VAR-C333B7DA','','','','','[]','[]','2025-09-01 09:09:17.535457','CE-WS-001'),
('VAR-C36D4F8B','','','','','[]','[]','2025-09-01 06:54:02.142306','PO-BB-001'),
('VAR-C3CDD807','','','','','[]','[]','2025-09-01 11:05:36.357693','CA-2T-001'),
('VAR-C830C321','','','','','[]','[]','2025-09-11 06:39:46.613824','FL-TD-001'),
('VAR-C8928FE1','','','','','[]','[]','2025-09-04 11:58:30.315437','EV-CJ-002'),
('VAR-C8AC390E','','','','','[]','[]','2025-09-01 06:50:01.377376','CO-CC-001'),
('VAR-CC90F66E','','','','','[]','[]','2025-09-01 08:29:05.877318','BR-PE-001'),
('VAR-D0D75871','','','','','[]','[]','2025-09-02 08:11:13.958883','TA-SG-001'),
('VAR-D19E962A','','','','','[]','[]','2025-09-11 07:23:36.090126','BA-FB-001'),
('VAR-D30D4688','','','','','[]','[]','2025-09-02 08:05:42.223340','TA-EF-001'),
('VAR-D492E4DD','','','','','[]','[]','2025-09-01 08:28:05.081074','UN-CH-001'),
('VAR-D9260A7C','','','','','[]','[]','2025-09-11 06:26:33.951027','FL-VS-001'),
('VAR-DC7F695A','','','','','[]','[]','2025-09-01 10:44:45.884275','SP-WB-001'),
('VAR-DCC8954A','','','','','[]','[]','2025-09-04 08:11:46.925519','EX-CC-002'),
('VAR-E8077294','','','','','[]','[]','2025-09-04 12:03:12.226130','EV-VN-001'),
('VAR-E89A014E','','','','','[]','[]','2025-09-01 07:52:59.443761','EV-CJ-003'),
('VAR-E911AF0E','','','','','[]','[]','2025-09-01 08:23:31.495817','AC-WA-001'),
('VAR-EC654FB5','','','','','[]','[]','2025-09-04 10:50:07.138301','GI-LP-001'),
('VAR-EEAA55E3','','','','','[]','[]','2025-09-11 06:08:39.752376','FL-CF-001'),
('VAR-EEFCDBBA','','','','','[]','[]','2025-09-01 10:09:15.166676','CE-WC-003'),
('VAR-EF55F8A6','','','','','[]','[]','2025-09-04 11:51:43.619511','PO-MD-001'),
('VAR-F00A16F7','','','','','[]','[]','2025-09-04 08:16:40.236661','EV-CE-001'),
('VAR-F0D2140E','','','','','[]','[]','2025-09-01 12:06:27.304911','TR-LT-001'),
('VAR-F170FADA','','','','','[]','[]','2025-09-04 08:13:38.301560','CA-CO-001'),
('VAR-F1DE9923','','','','','[]','[]','2025-09-01 11:06:03.139635','SP-SS-001'),
('VAR-F2449F2F','','','','','[]','[]','2025-09-11 06:11:57.657226','FL-HT-001'),
('VAR-F51536C5','','','','','[]','[]','2025-09-04 11:43:50.637019','CO-WU-001'),
('VAR-F79B0A4A','','','','','[]','[]','2025-09-01 06:52:00.844836','PO-HC-001'),
('VAR-F8900B81','','','','','[]','[]','2025-09-04 10:32:42.492822','PL-AP-001'),
('VAR-FC094BED','','','','','[]','[]','2025-09-04 08:07:29.825838','EX-CB-001'),
('VAR-FCF0D9B3','','','','','[]','[]','2025-09-04 10:56:31.475256','CE-CC-001');
/*!40000 ALTER TABLE `admin_backend_final_productvariant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_secondcarousel`
--

DROP TABLE IF EXISTS `admin_backend_final_secondcarousel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_secondcarousel` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_secondcarousel`
--

LOCK TABLES `admin_backend_final_secondcarousel` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_secondcarousel` DISABLE KEYS */;
INSERT INTO `admin_backend_final_secondcarousel` VALUES
(1,'Default Second Carousel Title','Default Second Carousel Description');
/*!40000 ALTER TABLE `admin_backend_final_secondcarousel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_secondcarouselimage`
--

DROP TABLE IF EXISTS `admin_backend_final_secondcarouselimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_secondcarouselimage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `caption` varchar(255) NOT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  `created_at` datetime(6) NOT NULL,
  `carousel_id` bigint(20) NOT NULL,
  `image_id` varchar(100) NOT NULL,
  `subcategory_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_backend_final__carousel_id_8182be3c_fk_admin_bac` (`carousel_id`),
  KEY `admin_backend_final__image_id_ff3c593c_fk_admin_bac` (`image_id`),
  KEY `admin_backend_final__subcategory_id_d29a39e2_fk_admin_bac` (`subcategory_id`),
  CONSTRAINT `admin_backend_final__carousel_id_8182be3c_fk_admin_bac` FOREIGN KEY (`carousel_id`) REFERENCES `admin_backend_final_secondcarousel` (`id`),
  CONSTRAINT `admin_backend_final__image_id_ff3c593c_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`),
  CONSTRAINT `admin_backend_final__subcategory_id_d29a39e2_fk_admin_bac` FOREIGN KEY (`subcategory_id`) REFERENCES `admin_backend_final_subcategory` (`subcategory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_secondcarouselimage`
--

LOCK TABLES `admin_backend_final_secondcarouselimage` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_secondcarouselimage` DISABLE KEYS */;
INSERT INTO `admin_backend_final_secondcarouselimage` VALUES
(1,'100 feesad','',0,'2025-08-29 05:45:51.068699',1,'IMG-ebab6fc4',NULL);
/*!40000 ALTER TABLE `admin_backend_final_secondcarouselimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_shippinginfo`
--

DROP TABLE IF EXISTS `admin_backend_final_shippinginfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_shippinginfo` (
  `shipping_id` varchar(100) NOT NULL,
  `shipping_class` varchar(100) NOT NULL,
  `processing_time` varchar(100) NOT NULL,
  `entered_by_id` varchar(100) NOT NULL,
  `entered_by_type` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`shipping_id`),
  UNIQUE KEY `product_id` (`product_id`),
  CONSTRAINT `admin_backend_final__product_id_b67aac7d_fk_admin_bac` FOREIGN KEY (`product_id`) REFERENCES `admin_backend_final_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_shippinginfo`
--

LOCK TABLES `admin_backend_final_shippinginfo` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_shippinginfo` DISABLE KEYS */;
INSERT INTO `admin_backend_final_shippinginfo` VALUES
('SHIP-AC-CC-001','','','SuperAdmin','admin','2025-09-01 08:08:19.093858','AC-CC-001'),
('SHIP-AC-CP-001','','','SuperAdmin','admin','2025-09-01 08:21:39.584423','AC-CP-001'),
('SHIP-AC-EU-001','','','SuperAdmin','admin','2025-09-01 08:09:50.069935','AC-EU-001'),
('SHIP-AC-WA-001','','','SuperAdmin','admin','2025-09-01 08:23:31.494790','AC-WA-001'),
('SHIP-BA-BA-001','','','SuperAdmin','admin','2025-09-04 12:07:59.608602','BA-BA-001'),
('SHIP-BA-EC-001','','','SuperAdmin','admin','2025-09-04 12:09:47.092316','BA-EC-001'),
('SHIP-BA-EC-002','','','SuperAdmin','admin','2025-09-01 06:31:13.146845','BA-EC-002'),
('SHIP-BA-FB-001','','','SuperAdmin','admin','2025-09-11 07:23:36.088893','BA-FB-001'),
('SHIP-BA-FB-002','','','SuperAdmin','admin','2025-09-11 07:34:27.996790','BA-FB-002'),
('SHIP-BA-MC-001','','','SuperAdmin','admin','2025-09-01 06:22:17.256181','BA-MC-001'),
('SHIP-BR-CA-001','','','SuperAdmin','admin','2025-09-01 08:38:07.649352','BR-CA-001'),
('SHIP-BR-CM-001','','','SuperAdmin','admin','2025-09-01 08:20:03.116688','BR-CM-001'),
('SHIP-BR-CP-001','','','SuperAdmin','admin','2025-09-01 08:13:41.684130','BR-CP-001'),
('SHIP-BR-CR-001','','','SuperAdmin','admin','2025-09-01 09:04:32.053597','BR-CR-001'),
('SHIP-BR-PE-001','','','SuperAdmin','admin','2025-09-01 08:29:05.876265','BR-PE-001'),
('SHIP-BR-PG-001','','','SuperAdmin','admin','2025-09-01 08:24:54.969648','BR-PG-001'),
('SHIP-BR-PP-001','','','SuperAdmin','admin','2025-09-04 07:59:19.770214','BR-PP-001'),
('SHIP-CA-2T-001','','','SuperAdmin','admin','2025-09-01 11:05:36.356801','CA-2T-001'),
('SHIP-CA-AN-001','','','SuperAdmin','admin','2025-09-01 11:26:58.726122','CA-AN-001'),
('SHIP-CA-BC-001','','','SuperAdmin','admin','2025-09-01 11:01:10.786056','CA-BC-001'),
('SHIP-CA-CO-001','','','SuperAdmin','admin','2025-09-04 08:13:38.300268','CA-CO-001'),
('SHIP-CA-FC-001','','','SuperAdmin','admin','2025-09-01 11:13:10.355152','CA-FC-001'),
('SHIP-CA-FW-001','','','SuperAdmin','admin','2025-09-04 11:53:58.371053','CA-FW-001'),
('SHIP-CA-IC-001','','','SuperAdmin','admin','2025-09-01 11:34:30.751830','CA-IC-001'),
('SHIP-CA-MN-001','','','SuperAdmin','admin','2025-09-01 11:20:26.642105','CA-MN-001'),
('SHIP-CA-PR-001','','','SuperAdmin','admin','2025-09-01 11:36:48.042716','CA-PR-001'),
('SHIP-CA-PS-001','','','SuperAdmin','admin','2025-09-02 07:54:11.363595','CA-PS-001'),
('SHIP-CA-RA-001','','','SuperAdmin','admin','2025-09-01 11:24:13.351245','CA-RA-001'),
('SHIP-CA-SB-001','','','SuperAdmin','admin','2025-09-01 11:03:33.069535','CA-SB-001'),
('SHIP-CE-BC-001','','','SuperAdmin','admin','2025-09-01 10:02:44.934131','CE-BC-001'),
('SHIP-CE-BS-001','','','SuperAdmin','admin','2025-09-01 08:18:56.290682','CE-BS-001'),
('SHIP-CE-CC-001','','','SuperAdmin','admin','2025-09-04 10:56:31.472026','CE-CC-001'),
('SHIP-CE-CE-001','','','SuperAdmin','admin','2025-09-01 08:23:54.299159','CE-CE-001'),
('SHIP-CE-CG-001','','','SuperAdmin','admin','2025-09-01 08:07:35.345566','CE-CG-001'),
('SHIP-CE-CM-001','','','SuperAdmin','admin','2025-09-04 10:53:19.075986','CE-CM-001'),
('SHIP-CE-GB-001','','','SuperAdmin','admin','2025-09-01 09:04:01.003530','CE-GB-001'),
('SHIP-CE-GC-001','','','SuperAdmin','admin','2025-09-01 09:12:16.134258','CE-GC-001'),
('SHIP-CE-LM-001','','','SuperAdmin','admin','2025-09-01 10:13:38.509694','CE-LM-001'),
('SHIP-CE-MC-001','','','SuperAdmin','admin','2025-09-01 07:59:30.657708','CE-MC-001'),
('SHIP-CE-PC-001','','','SuperAdmin','admin','2025-09-01 09:24:05.818055','CE-PC-001'),
('SHIP-CE-PM-001','','','SuperAdmin','admin','2025-09-01 08:34:20.719216','CE-PM-001'),
('SHIP-CE-TT-001','','','SuperAdmin','admin','2025-09-01 09:33:17.770404','CE-TT-001'),
('SHIP-CE-TT-002','','','SuperAdmin','admin','2025-09-01 09:33:45.709679','CE-TT-002'),
('SHIP-CE-TT-003','','','SuperAdmin','admin','2025-09-01 09:41:51.568279','CE-TT-003'),
('SHIP-CE-WC-001','','','SuperAdmin','admin','2025-09-04 11:37:35.933260','CE-WC-001'),
('SHIP-CE-WC-002','','','SuperAdmin','admin','2025-09-01 08:41:07.071835','CE-WC-002'),
('SHIP-CE-WC-003','','','SuperAdmin','admin','2025-09-01 10:09:15.165160','CE-WC-003'),
('SHIP-CE-WS-001','','','SuperAdmin','admin','2025-09-01 09:09:17.533761','CE-WS-001'),
('SHIP-CE-WS-002','','','SuperAdmin','admin','2025-09-01 10:20:26.367424','CE-WS-002'),
('SHIP-CO-BE-001','','','SuperAdmin','admin','2025-09-04 11:49:49.804930','CO-BE-001'),
('SHIP-CO-CB-001','','','SuperAdmin','admin','2025-09-04 08:30:04.874497','CO-CB-001'),
('SHIP-CO-CC-001','','','SuperAdmin','admin','2025-09-01 06:50:01.376463','CO-CC-001'),
('SHIP-CO-CL-001','','','SuperAdmin','admin','2025-09-04 11:47:12.712255','CO-CL-001'),
('SHIP-CO-CU-001','','','SuperAdmin','admin','2025-09-04 08:31:25.925763','CO-CU-001'),
('SHIP-CO-DU-001','','','SuperAdmin','admin','2025-09-04 11:41:53.289727','CO-DU-001'),
('SHIP-CO-EF-001','','','SuperAdmin','admin','2025-09-04 08:23:28.440143','CO-EF-001'),
('SHIP-CO-SC-001','','','SuperAdmin','admin','2025-09-04 08:26:58.024787','CO-SC-001'),
('SHIP-CO-UM-001','','','SuperAdmin','admin','2025-09-04 08:33:25.904281','CO-UM-001'),
('SHIP-CO-WU-001','','','SuperAdmin','admin','2025-09-04 11:43:50.634503','CO-WU-001'),
('SHIP-DE-BF-001','','','SuperAdmin','admin','2025-09-01 10:22:47.023440','DE-BF-001'),
('SHIP-DE-SF-001','','','SuperAdmin','admin','2025-09-01 10:26:26.193574','DE-SF-001'),
('SHIP-EC-BF-001','','','SuperAdmin','admin','2025-09-04 07:10:08.110089','EC-BF-001'),
('SHIP-EC-EF-001','','','SuperAdmin','admin','2025-09-04 07:01:28.045083','EC-EF-001'),
('SHIP-EV-CE-001','','','SuperAdmin','admin','2025-09-04 08:16:40.235617','EV-CE-001'),
('SHIP-EV-CJ-001','','','SuperAdmin','admin','2025-09-04 12:11:23.947525','EV-CJ-001'),
('SHIP-EV-CJ-002','','','SuperAdmin','admin','2025-09-04 11:58:30.313071','EV-CJ-002'),
('SHIP-EV-CJ-003','','','SuperAdmin','admin','2025-09-01 07:52:59.442889','EV-CJ-003'),
('SHIP-EV-CL-001','','','SuperAdmin','admin','2025-09-01 10:10:07.065120','EV-CL-001'),
('SHIP-EV-CR-001','','','SuperAdmin','admin','2025-09-04 08:18:38.164286','EV-CR-001'),
('SHIP-EV-CR-002','','','SuperAdmin','admin','2025-09-04 12:00:55.868174','EV-CR-002'),
('SHIP-EV-DP-001','','','SuperAdmin','admin','2025-09-01 10:11:31.279069','EV-DP-001'),
('SHIP-EV-LW-001','','','SuperAdmin','admin','2025-09-01 10:08:07.430425','EV-LW-001'),
('SHIP-EV-RJ-001','','','SuperAdmin','admin','2025-09-01 07:04:51.878350','EV-RJ-001'),
('SHIP-EV-RV-001','','','SuperAdmin','admin','2025-09-01 08:04:31.877063','EV-RV-001'),
('SHIP-EV-SC-001','','','SuperAdmin','admin','2025-09-04 11:55:39.713290','EV-SC-001'),
('SHIP-EV-TW-001','','','SuperAdmin','admin','2025-09-01 10:13:10.525372','EV-TW-001'),
('SHIP-EV-VN-001','','','SuperAdmin','admin','2025-09-04 12:03:12.223538','EV-VN-001'),
('SHIP-EX-CB-001','','','SuperAdmin','admin','2025-09-04 08:07:29.824931','EX-CB-001'),
('SHIP-EX-CC-001','','','SuperAdmin','admin','2025-09-04 08:09:59.938258','EX-CC-001'),
('SHIP-EX-CC-002','','','SuperAdmin','admin','2025-09-04 08:11:46.924445','EX-CC-002'),
('SHIP-EX-PL-001','','','SuperAdmin','admin','2025-09-04 07:39:52.243242','EX-PL-001'),
('SHIP-EX-WP-001','','','SuperAdmin','admin','2025-09-01 12:28:37.692398','EX-WP-001'),
('SHIP-FL-CF-001','','','SuperAdmin','admin','2025-09-11 06:08:39.750663','FL-CF-001'),
('SHIP-FL-CF-002','','','SuperAdmin','admin','2025-09-11 06:10:06.894643','FL-CF-002'),
('SHIP-FL-CT-001','','','SuperAdmin','admin','2025-09-11 06:35:12.916569','FL-CT-001'),
('SHIP-FL-HB-001','','','SuperAdmin','admin','2025-09-11 06:24:47.278599','FL-HB-001'),
('SHIP-FL-HD-001','','','SuperAdmin','admin','2025-09-11 06:13:30.999786','FL-HD-001'),
('SHIP-FL-HT-001','','','SuperAdmin','admin','2025-09-11 06:11:57.656261','FL-HT-001'),
('SHIP-FL-HT-002','','','SuperAdmin','admin','2025-09-11 06:14:38.843503','FL-HT-002'),
('SHIP-FL-LS-001','','','SuperAdmin','admin','2025-09-11 06:16:07.817412','FL-LS-001'),
('SHIP-FL-PF-001','','','SuperAdmin','admin','2025-09-11 06:17:21.227946','FL-PF-001'),
('SHIP-FL-PF-002','','','SuperAdmin','admin','2025-09-11 06:31:34.719216','FL-PF-002'),
('SHIP-FL-PT-001','','','SuperAdmin','admin','2025-09-11 06:19:06.448487','FL-PT-001'),
('SHIP-FL-ST-001','','','SuperAdmin','admin','2025-09-11 06:21:40.728965','FL-ST-001'),
('SHIP-FL-TD-001','','','SuperAdmin','admin','2025-09-11 06:39:46.612718','FL-TD-001'),
('SHIP-FL-TS-001','','','SuperAdmin','admin','2025-09-11 06:37:42.484924','FL-TS-001'),
('SHIP-FL-VC-001','','','SuperAdmin','admin','2025-09-11 06:27:31.063389','FL-VC-001'),
('SHIP-FL-VS-001','','','SuperAdmin','admin','2025-09-11 06:26:33.949637','FL-VS-001'),
('SHIP-FL-YS-001','','','SuperAdmin','admin','2025-09-11 06:28:30.534819','FL-YS-001'),
('SHIP-GI-LP-001','','','SuperAdmin','admin','2025-09-04 10:50:07.135823','GI-LP-001'),
('SHIP-NO-AS-001','','','SuperAdmin','admin','2025-09-04 12:19:20.963877','NO-AS-001'),
('SHIP-NO-BA-001','','','SuperAdmin','admin','2025-09-04 12:14:54.007428','NO-BA-001'),
('SHIP-NO-CB-001','','','SuperAdmin','admin','2025-09-01 11:45:09.062866','NO-CB-001'),
('SHIP-NO-CC-001','','','SuperAdmin','admin','2025-09-04 08:05:19.032961','NO-CC-001'),
('SHIP-NO-LP-001','','','SuperAdmin','admin','2025-09-01 12:06:56.673168','NO-LP-001'),
('SHIP-NO-PD-001','','','SuperAdmin','admin','2025-09-04 12:20:56.381766','NO-PD-001'),
('SHIP-NO-SN-001','','','SuperAdmin','admin','2025-09-04 12:17:09.660250','NO-SN-001'),
('SHIP-NO-SN-002','','','SuperAdmin','admin','2025-09-01 12:14:18.326333','NO-SN-002'),
('SHIP-PL-AP-001','','','SuperAdmin','admin','2025-09-04 10:32:42.489951','PL-AP-001'),
('SHIP-PL-SM-001','','','SuperAdmin','admin','2025-09-01 06:27:33.358894','PL-SM-001'),
('SHIP-PO-BB-001','','','SuperAdmin','admin','2025-09-01 06:54:02.141110','PO-BB-001'),
('SHIP-PO-HC-001','','','SuperAdmin','admin','2025-09-01 06:52:00.843597','PO-HC-001'),
('SHIP-PO-MD-001','','','SuperAdmin','admin','2025-09-04 11:51:43.617107','PO-MD-001'),
('SHIP-PR-CC-001','','','SuperAdmin','admin','2025-09-18 05:57:32.260372','PR-CC-001'),
('SHIP-PR-CC-002','','','SuperAdmin','admin','2025-09-04 07:54:34.967849','PR-CC-002'),
('SHIP-PR-CH-001','','','SuperAdmin','admin','2025-09-01 12:14:53.445683','PR-CH-001'),
('SHIP-PR-CO-001','','','SuperAdmin','admin','2025-09-04 07:33:10.631429','PR-CO-001'),
('SHIP-PR-CP-001','','','SuperAdmin','admin','2025-09-01 12:12:10.693407','PR-CP-001'),
('SHIP-PR-CP-002','','','SuperAdmin','admin','2025-09-04 07:56:17.768527','PR-CP-002'),
('SHIP-PR-CW-001','','','SuperAdmin','admin','2025-09-01 12:13:47.808835','PR-CW-001'),
('SHIP-SP-PB-001','','','SuperAdmin','admin','2025-09-04 06:52:49.217007','SP-PB-001'),
('SHIP-SP-PS-001','','','SuperAdmin','admin','2025-09-04 11:31:16.547677','SP-PS-001'),
('SHIP-SP-RB-001','','','SuperAdmin','admin','2025-09-01 11:20:18.613020','SP-RB-001'),
('SHIP-SP-RT-001','','','SuperAdmin','admin','2025-09-01 11:35:38.973984','SP-RT-001'),
('SHIP-SP-SS-001','','','SuperAdmin','admin','2025-09-01 11:06:03.138712','SP-SS-001'),
('SHIP-SP-TB-001','','','SuperAdmin','admin','2025-09-01 10:38:01.209693','SP-TB-001'),
('SHIP-SP-TT-001','','','SuperAdmin','admin','2025-09-01 11:48:00.452946','SP-TT-001'),
('SHIP-SP-WB-001','','','SuperAdmin','admin','2025-09-01 10:44:45.883322','SP-WB-001'),
('SHIP-SP-WB-002','','','SuperAdmin','admin','2025-09-04 11:34:05.964628','SP-WB-002'),
('SHIP-TA-EF-001','','','SuperAdmin','admin','2025-09-02 08:05:42.222348','TA-EF-001'),
('SHIP-TA-HT-001','','','SuperAdmin','admin','2025-09-02 08:09:44.166295','TA-HT-001'),
('SHIP-TA-RG-001','','','SuperAdmin','admin','2025-09-02 08:12:46.428103','TA-RG-001'),
('SHIP-TA-SG-001','','','SuperAdmin','admin','2025-09-02 08:11:13.957875','TA-SG-001'),
('SHIP-TR-CC-001','','','SuperAdmin','admin','2025-09-01 08:10:42.728466','TR-CC-001'),
('SHIP-TR-CT-001','','','SuperAdmin','admin','2025-09-01 07:50:09.468519','TR-CT-001'),
('SHIP-TR-CW-001','','','SuperAdmin','admin','2025-09-04 12:13:07.313212','TR-CW-001'),
('SHIP-TR-DS-001','','','SuperAdmin','admin','2025-09-04 11:25:05.729877','TR-DS-001'),
('SHIP-TR-DW-001','','','SuperAdmin','admin','2025-09-01 11:55:58.676108','TR-DW-001'),
('SHIP-TR-DW-002','','','SuperAdmin','admin','2025-09-01 12:03:05.310240','TR-DW-002'),
('SHIP-TR-LT-001','','','SuperAdmin','admin','2025-09-01 12:06:27.303859','TR-LT-001'),
('SHIP-TR-PT-001','','','SuperAdmin','admin','2025-09-01 07:54:24.519237','TR-PT-001'),
('SHIP-TR-TT-001','','','SuperAdmin','admin','2025-09-01 12:10:47.289851','TR-TT-001'),
('SHIP-UN-CH-001','','','SuperAdmin','admin','2025-09-01 08:28:05.080115','UN-CH-001'),
('SHIP-UN-PC-001','','','SuperAdmin','admin','2025-09-01 08:04:24.999177','UN-PC-001'),
('SHIP-WO-BW-001','','','SuperAdmin','admin','2025-09-04 10:48:09.998088','WO-BW-001'),
('SHIP-WO-EC-001','','','SuperAdmin','admin','2025-09-01 06:29:30.113653','WO-EC-001'),
('SHIP-WO-EF-001','','','SuperAdmin','admin','2025-09-04 10:43:03.222514','WO-EF-001');
/*!40000 ALTER TABLE `admin_backend_final_shippinginfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_sitesettings`
--

DROP TABLE IF EXISTS `admin_backend_final_sitesettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_sitesettings` (
  `setting_id` varchar(100) NOT NULL,
  `site_title` varchar(100) NOT NULL,
  `logo_url` varchar(200) NOT NULL,
  `language` varchar(20) NOT NULL,
  `currency` varchar(10) NOT NULL,
  `timezone` varchar(50) NOT NULL,
  `tax_rate` double NOT NULL,
  `payment_modes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`payment_modes`)),
  `shipping_zones` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`shipping_zones`)),
  `social_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`social_links`)),
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`setting_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_sitesettings`
--

LOCK TABLES `admin_backend_final_sitesettings` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_sitesettings` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_sitesettings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_subcategory`
--

DROP TABLE IF EXISTS `admin_backend_final_subcategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_subcategory` (
  `subcategory_id` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `caption` varchar(255) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  PRIMARY KEY (`subcategory_id`),
  KEY `admin_backend_final_subcategory_name_ca49f92c` (`name`),
  KEY `admin_backend_final_subcategory_status_4d9a99f7` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_subcategory`
--

LOCK TABLES `admin_backend_final_subcategory` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_subcategory` DISABLE KEYS */;
INSERT INTO `admin_backend_final_subcategory` VALUES
('B&T-BACKPACKS-001','Backpacks & Laptop Bags','visible','SuperAdmin','2025-08-29 06:53:28.322316','2025-09-09 11:20:03.592932','Laptop Bags, Travel Pouches & Printing Services.','<p>Discover laptop, shoulder, document &amp; travel bags. Custom printed bags near you from a trusted Dubai print shop.</p>',6),
('B&T-EVERYDAY-001','Everyday & Tote Bags','visible','SuperAdmin','2025-08-29 06:52:07.368096','2025-09-09 10:35:42.771143','Canvas, Jute & Branded Tote Bags with Printing Dubai.','<p>Shop tote bags for women, canvas &amp; jute totes, with eco-friendly designs and custom printing in Dubai.</p>',5),
('B&T-TRAVEL-001','Travel Accessories','visible','SuperAdmin','2025-08-29 06:55:27.338076','2025-09-09 11:14:27.931801','Printed Passport Covers & Travel Bag Tags in Dubai.','<p>Discover personalized passport covers, leather holders &amp; custom luggage tags with stylish printing in Dubai.</p>',7),
('BD&F-BANNERS-001','Banners','visible','SuperAdmin','2025-09-03 07:09:32.768964','2025-09-10 16:14:27.342404','Custom Banners Printing in Dubai','<p>ghjbj</p>',33),
('BD&F-DISPLAY-001','Display','visible','SuperAdmin','2025-09-10 11:17:56.105737','2025-09-10 16:21:31.085240','Exhibition Display Stands Dubai',NULL,34),
('BD&F-FLAGS-001','Flags','visible','SuperAdmin','2025-09-10 11:20:54.207035','2025-09-10 16:49:58.772364','Custom Flags Printing Dubai',NULL,35),
('CAA-ACCESSORIES-001','Accessories','visible','SuperAdmin','2025-08-29 07:06:12.615578','2025-09-09 09:48:49.347794','Sashes, Wristbands, Caps & Fashion Accessories Dubai.','<p>Discover sashes, wristbands, caps, hats, masks &amp; bandanas with personalized printing services in Dubai.</p>',16),
('CAA-CAPS-001','Caps & Hats','visible','SuperAdmin','2025-09-02 07:51:14.353776','2025-09-09 10:19:59.799986','Custom Cap Printing Dubai | Caps, Hats & Graduation Caps','<p>Order custom cap printing in Dubai stylish caps for men, bucket hats, beach hats &amp; graduation caps with personalized name printing.</p>',15),
('CAA-HOODIES-001','Hoodies & Jackets','visible','SuperAdmin','2025-08-29 07:03:53.753227','2025-09-09 08:23:46.652229','Branded Hoodies, Dubai Jackets & Custom Printing.','<p>Explore men&rsquo;s hoodies, Dubai hoodies &amp; windbreaker jackets with personalized designs from trusted Dubai print shops.</p>',13),
('CAA-KIDS\'-001','Kids\' Apparel','visible','SuperAdmin','2025-08-29 07:02:59.678958','2025-09-09 08:08:14.664559','Branded Kids’ T-Shirts & Polo Printing in Dubai.','<p>Discover cotton t-shirts, polos &amp; UAE kids&rsquo; shirts with high-quality custom printing from expert Dubai print shops.</p>',12),
('CAA-T-SHIRTS-001','T-Shirts & Polo Shirts','visible','SuperAdmin','2025-08-29 07:01:59.242745','2025-09-09 07:59:03.192512','Custom Men’s T-Shirts & Polo Printing Services Dubai.','<p>Shop v-neck, crew neck &amp; polo t-shirts with premium printing near you. Trusted branded t-shirt shops in Dubai.</p>',11),
('CAA-UNIFORMS-001','Uniforms & Workwear','visible','SuperAdmin','2025-08-29 07:04:49.909400','2025-09-09 08:46:17.847689','Branded Workwear, Aprons & Safety Jackets Dubai.','<p>High-quality workwear in Dubai: safety vests, jackets, aprons &amp; scrubs with custom printing from local print shops.</p>',14),
('D-CERAMIC-001','Ceramic Mugs','visible','SuperAdmin','2025-09-01 06:44:08.560930','2025-09-09 11:28:27.818261','Custom Ceramic & Coffee Mugs Dubai.','<p>Ceramic mugs, magic cups &amp; coffee mugs with logo printing in Dubai ideal for events &amp; corporate giveaways.</p>',22),
('D-ECO-FRIENDLY-001','Eco-Friendly Drinkware','visible','SuperAdmin','2025-08-29 07:15:31.411552','2025-09-09 12:54:31.245890','Eco-Friendly Glass & Coffee Drinkware Printing Dubai.','<p>Eco-friendly drinkware: glass bottles, infusers &amp; coffee mugs with stylish custom logo branding in Dubai.</p>',25),
('D-SPORTS-001','Sports Bottles','visible','SuperAdmin','2025-08-29 07:14:13.995816','2025-09-09 12:42:35.537385','Branded Sports & Plastic Water Bottles Dubai.','<p>Custom sports, plastic &amp; branded water bottles with logo printing in Dubai. Perfect for events, giveaways &amp; branding.</p>',24),
('D-TABLE-001','Table Accessories','visible','SuperAdmin','2025-08-29 07:16:55.561688','2025-09-09 11:27:40.709179','Custom Coaster Sets & Cup Coaster Printing Dubai.','<p>Premium table accessories: coasters, sets &amp; tea coasters with custom logo branding from trusted Dubai print shops.</p>',26),
('D-TRAVEL-001','Travel & Insulated Mugs','visible','SuperAdmin','2025-08-29 07:12:28.318589','2025-09-09 11:40:59.144498','Insulated & Travel Mugs Dubai.','<p>Discover personalized travel mugs and insulated flasks with custom printing. Ideal for promotions and daily use in Dubai.</p>',23),
('EG&S-BRANDED-001','Branded Giveaway Items','visible','SuperAdmin','2025-08-29 07:21:08.517494','2025-09-09 14:13:17.240717','Custom Keychains & Stress Balls in Dubai.','<p>Discover custom keychains in Dubai, UAE name, family, Lego &amp; men&rsquo;s designs plus stress balls &amp; giveaways.</p>',29),
('EG&S-DECORATIVE-001','Decorative & Promotional','visible','SuperAdmin','2025-08-29 07:19:39.805530','2025-09-09 14:05:51.008313','Custom Balloons, Umbrellas & Car Sun Shades Printing in Dubai.','<p>Get custom balloons, beach umbrellas, car umbrellas &amp; sun shade printing in Dubai&mdash;perfect for events &amp; promotions.</p>',28),
('EG&S-EVENT-001','Event Essentials','visible','SuperAdmin','2025-08-29 07:18:20.166608','2025-09-09 13:33:58.143598','Custom Wristbands & Lanyards Printing in Dubai, UAE','<p>Custom Tyvek &amp; silicone wristbands in Dubai, UAE. Branded lanyards &amp; online lanyard printing for events &amp; promos.</p>',27),
('EG&S-PET-001','Pet & Specialty Item','visible','SuperAdmin','2025-08-29 07:24:01.470130','2025-09-10 05:55:16.861456','Custom Pet Accessories & Promotional Products in Dubai.','<p>Shop custom pet accessories &amp; promo items in Dubai, UAE from branded collars to unique giveaways for events.</p>',31),
('EG&S-PREMIUM-001','Premium & Corporate Gifts','visible','SuperAdmin','2025-08-29 07:22:39.961796','2025-09-10 05:51:12.710183','Customized Luxury Gifts in Dubai for Men & Women.','<p>Explore customized gifts in Dubai luxury corporate gifts, unique men&rsquo;s &amp; women&rsquo;s gifts, and premium giveaways.</p>',30),
('EG&S-SIGNAGE-001','Signage','visible','SuperAdmin','2025-08-29 07:25:17.458342','2025-09-10 05:55:46.079855','Signage and Custom Sign Boards in Dubai for Businesses and Events.','<p>Explore professional signage &amp; custom sign boards in Dubai shop signs, event displays &amp; branding solutions</p>',32),
('O&S-CALENDARS-001','Calendars & Miscellaneous Items','visible','SuperAdmin','2025-08-29 07:00:36.225575','2025-09-04 14:19:46.770133','Custom Calendars, Stamps & Card Holders Dubai.','<p>Shop Islamic calendars, badges, stamps &amp; card holders with reliable printing services in Dubai for offices &amp; events.</p>',10),
('O&S-EXECUTIVE-001','Executive Diaries & Planners','visible','SuperAdmin','2025-08-29 06:59:19.862635','2025-09-04 14:08:36.335710','Executive Diaries, Planners & Office Stationery Dubai.','<p>Explore executive diaries, planners &amp; promotional diaries with branded document holders &amp; office printing.</p>',9),
('O&S-INVOICE-001','Invoice Book','visible','SuperAdmin','2025-09-18 11:47:46.933301','2025-09-18 11:47:46.933331','fghbk g',NULL,41),
('O&S-NOTEBOOKS-001','Notebooks & Writing Pads','visible','SuperAdmin','2025-08-29 06:57:55.765001','2025-09-04 12:39:34.063082','Custom Notebooks, Spiral Pads & Office Stationery Dubai.','<p>Custom notebooks, spiral pads &amp; writing journals with branded covers, leather portfolios &amp; document holders.</p>',8),
('P&MM-BUSINESS-001','Standard Business Cards','visible','SuperAdmin','2025-08-29 07:07:27.772646','2025-09-03 15:26:41.900709','Professional Business Card Printing Near Me.','Get custom business card printing in Dubai, incl. metal & NFC cards. Expert print shops near you for premium services.',17),
('P&MM-CERAMIC-001','Ceramic Mugs','visible','SuperAdmin','2025-08-29 07:11:00.046968','2025-09-04 11:39:10.547547','Ceramic Mugs, Magic Cups & Coffee Mug Printing UAE.','<p>Explore ceramic mugs, magic cups, tea &amp; coffee mugs with logo printing. Order branded Dubai mug sets in UAE.</p>',21),
('P&MM-ENVELOPE-001','Envelope','visible','SuperAdmin','2025-09-18 10:24:52.132252','2025-09-18 10:24:52.132301','Custom Envelopes Printing in Dubai',NULL,39),
('P&MM-LETTERHEADS-001','Letterheads','visible','SuperAdmin','2025-09-18 10:27:55.153445','2025-09-18 10:27:55.153483','Premium Letterheads for Business Communication & Branding.',NULL,40),
('P&MM-OFFICE-001','Office Stationery','visible','SuperAdmin','2025-08-29 07:09:54.407866','2025-09-04 12:02:45.089572','Envelopes, Folders & Table Tent Printing UAE.','<p>Get custom white envelopes, A4/A5 folders with pockets &amp; table tents. Reliable office stationery printing UAE.</p>',20),
('P&MM-PREMIUM-001','Premium Business Card','visible','SuperAdmin','2025-09-04 11:35:27.325295','2025-09-04 11:35:27.325319',NULL,NULL,18),
('P&MM-PROMOTIONAL-001','Promotional & Corporate Print','visible','SuperAdmin','2025-08-29 07:08:44.674290','2025-09-03 15:27:53.270013','Brochures, Stickers & Roll-Up Banner Printing UAE.','Professional flyer, leaflet & brochure printing in Dubai. Custom booklets, stickers, posters & roll-up banners UAE.',19),
('S-CHANNEL-001','Channel Letters','visible','SuperAdmin','2025-09-20 09:33:07.677871','2025-09-20 09:33:07.677940','Channel Letters Dubai & UAE | Custom Front-Lit, Back-Lit & 3D Signage',NULL,42),
('T-COMPUTER-001','Computer & Office Gadgets','visible','SuperAdmin','2025-08-29 06:29:23.420828','2025-09-04 10:23:19.091576','USB Drives, Desk Accessories & Printing Dubai.','<p>Discover custom USB drives, wireless chargers, and desk accessories with logo printing. Premium printing services in Dubai and local print shops.</p>',37),
('T-CUSTOM-001','Custom USB Drives','visible','SuperAdmin','2025-09-03 15:22:56.142959','2025-09-11 13:27:09.067506',NULL,NULL,36),
('T-POWER-001','Power & Charging Accessories','visible','SuperAdmin','2025-09-01 06:42:08.413838','2025-09-04 08:44:04.754815','Wireless Chargers & Power Banks in Dubai','<p>Custom power banks &amp; wireless chargers with logo printing in Dubai perfect for corporate giveaways.</p>',38),
('WI-GIFT-001','Gift Sets','visible','SuperAdmin','2025-08-30 07:50:05.564363','2025-09-09 10:24:15.904648','Custom Gift Sets & Special Pens for Corporate Gifting Dubai','<p>Premium pen gift sets &amp; logo-printed boxes in Dubai ideal for corporate gifts &amp; giveaways.</p>',4),
('WI-METAL-001','Metal Ballpoint Pen','visible','SuperAdmin','2025-08-29 06:47:54.697376','2025-09-09 10:23:27.431919','Custom Metal Pens & Ballpoint Pen Boxes Dubai','<p>Premium metal &amp; ballpoint pens with custom logo printing in Dubai. Elegant boxes for gifts &amp; promotions.</p>',2),
('WI-PLASTIC-001','Plastic Pens','visible','SuperAdmin','2025-08-29 06:45:48.544323','2025-09-09 10:23:39.681578','Custom Plastic & Ballpoint Writing Pens Dubai','<p>Affordable branded plastic &amp; ballpoint pens with custom logo printing in Dubai for events, offices &amp; giveaways.</p>',1),
('WI-WOODEN-001','Wooden & Eco Pens','visible','SuperAdmin','2025-08-29 06:51:21.404035','2025-09-09 10:23:55.943261',': Custom Wooden Pencils & Eco-Friendly Writing Pens Dubai','<p>Eco-friendly wooden pencils &amp; pens with custom logo printing in Dubai. Ideal for schools, offices &amp; events.</p>',3);
/*!40000 ALTER TABLE `admin_backend_final_subcategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_subcategoryimage`
--

DROP TABLE IF EXISTS `admin_backend_final_subcategoryimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_subcategoryimage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `image_id` varchar(100) NOT NULL,
  `subcategory_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_backend_final__image_id_52d44544_fk_admin_bac` (`image_id`),
  KEY `admin_backend_final__subcategory_id_171ce9bc_fk_admin_bac` (`subcategory_id`),
  CONSTRAINT `admin_backend_final__image_id_52d44544_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`),
  CONSTRAINT `admin_backend_final__subcategory_id_171ce9bc_fk_admin_bac` FOREIGN KEY (`subcategory_id`) REFERENCES `admin_backend_final_subcategory` (`subcategory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_subcategoryimage`
--

LOCK TABLES `admin_backend_final_subcategoryimage` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_subcategoryimage` DISABLE KEYS */;
INSERT INTO `admin_backend_final_subcategoryimage` VALUES
(5,'2025-09-03 15:26:41.918047','IMG-76be8052','P&MM-BUSINESS-001'),
(6,'2025-09-03 15:27:53.277355','IMG-fcc5b88e','P&MM-PROMOTIONAL-001'),
(7,'2025-09-04 08:44:04.761813','IMG-d4937651','T-POWER-001'),
(8,'2025-09-04 10:23:19.105155','IMG-b84a7c06','T-COMPUTER-001'),
(9,'2025-09-04 11:35:27.336074','IMG-5148c283','P&MM-PREMIUM-001'),
(11,'2025-09-04 11:39:10.553801','IMG-5d45c1d7','P&MM-CERAMIC-001'),
(12,'2025-09-04 12:02:45.096717','IMG-3b4ca488','P&MM-OFFICE-001'),
(13,'2025-09-04 12:39:34.069288','IMG-cb1b9e3e','O&S-NOTEBOOKS-001'),
(14,'2025-09-04 14:08:36.347875','IMG-958f5197','O&S-EXECUTIVE-001'),
(15,'2025-09-04 14:19:46.777187','IMG-ef9cfa50','O&S-CALENDARS-001'),
(16,'2025-09-09 07:59:03.205022','IMG-754b9060','CAA-T-SHIRTS-001'),
(17,'2025-09-09 08:08:14.675131','IMG-67701935','CAA-KIDS\'-001'),
(18,'2025-09-09 08:23:46.660776','IMG-2aab538f','CAA-HOODIES-001'),
(19,'2025-09-09 08:46:17.857473','IMG-b3669b2d','CAA-UNIFORMS-001'),
(20,'2025-09-09 09:48:49.364504','IMG-c075f19c','CAA-ACCESSORIES-001'),
(21,'2025-09-09 10:19:59.811153','IMG-cda91a3d','CAA-CAPS-001'),
(22,'2025-09-09 10:23:27.439732','IMG-009d7870','WI-METAL-001'),
(23,'2025-09-09 10:23:39.702140','IMG-3d6c2f60','WI-PLASTIC-001'),
(24,'2025-09-09 10:23:55.948612','IMG-e21bdb4b','WI-WOODEN-001'),
(25,'2025-09-09 10:24:15.917874','IMG-8a2614da','WI-GIFT-001'),
(27,'2025-09-09 10:35:42.784260','IMG-1893485a','B&T-EVERYDAY-001'),
(29,'2025-09-09 11:14:27.939651','IMG-09053827','B&T-TRAVEL-001'),
(30,'2025-09-09 11:20:03.604900','IMG-2749e1fe','B&T-BACKPACKS-001'),
(34,'2025-09-09 11:27:40.721416','IMG-f34b6617','D-TABLE-001'),
(35,'2025-09-09 11:28:27.830163','IMG-a4b70fb2','D-CERAMIC-001'),
(36,'2025-09-09 11:40:59.154916','IMG-8383d894','D-TRAVEL-001'),
(37,'2025-09-09 12:42:35.559223','IMG-b75b200e','D-SPORTS-001'),
(38,'2025-09-09 12:54:31.287055','IMG-c246e58d','D-ECO-FRIENDLY-001'),
(39,'2025-09-09 13:33:58.155358','IMG-e704e69d','EG&S-EVENT-001'),
(40,'2025-09-09 14:05:51.019838','IMG-66262117','EG&S-DECORATIVE-001'),
(41,'2025-09-09 14:13:17.249512','IMG-f070b115','EG&S-BRANDED-001'),
(42,'2025-09-10 05:51:12.721387','IMG-8085ea97','EG&S-PREMIUM-001'),
(43,'2025-09-10 05:55:16.869773','IMG-a4a9356d','EG&S-PET-001'),
(45,'2025-09-10 05:55:46.095089','IMG-ab276ed5','EG&S-SIGNAGE-001'),
(46,'2025-09-10 16:14:27.380054','IMG-2ed292c2','BD&F-BANNERS-001'),
(47,'2025-09-10 16:21:31.095187','IMG-5d328142','BD&F-DISPLAY-001'),
(49,'2025-09-10 16:49:58.786383','IMG-4c9ea229','BD&F-FLAGS-001'),
(50,'2025-09-11 13:27:09.088351','IMG-384ce930','T-CUSTOM-001'),
(51,'2025-09-20 09:33:07.706034','IMG-c4b6a33c','S-CHANNEL-001');
/*!40000 ALTER TABLE `admin_backend_final_subcategoryimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_testimonial`
--

DROP TABLE IF EXISTS `admin_backend_final_testimonial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_testimonial` (
  `testimonial_id` varchar(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `content` longtext NOT NULL,
  `image_url` varchar(200) NOT NULL,
  `rating` smallint(5) unsigned NOT NULL CHECK (`rating` >= 0),
  `status` varchar(20) NOT NULL,
  `created_by` varchar(100) NOT NULL,
  `created_by_type` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `order` int(10) unsigned NOT NULL CHECK (`order` >= 0),
  `image_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`testimonial_id`),
  KEY `admin_backend_final__image_id_a60831d9_fk_admin_bac` (`image_id`),
  KEY `admin_backend_final_testimonial_name_1fbb63c5` (`name`),
  KEY `admin_backend_final_testimonial_rating_9cff88f9` (`rating`),
  KEY `admin_backend_final_testimonial_status_3fd0a8a3` (`status`),
  KEY `admin_backend_final_testimonial_created_at_6fe7c914` (`created_at`),
  KEY `admin_backend_final_testimonial_order_dd78e9f2` (`order`),
  KEY `admin_backe_status_f2c13d_idx` (`status`),
  KEY `admin_backe_rating_5cb428_idx` (`rating`),
  KEY `admin_backe_created_0b93d4_idx` (`created_at`),
  CONSTRAINT `admin_backend_final__image_id_a60831d9_fk_admin_bac` FOREIGN KEY (`image_id`) REFERENCES `admin_backend_final_image` (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_testimonial`
--

LOCK TABLES `admin_backend_final_testimonial` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_testimonial` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_testimonial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_user`
--

DROP TABLE IF EXISTS `admin_backend_final_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_user` (
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `user_id` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `address` longtext NOT NULL,
  `emirates_id` varchar(50) DEFAULT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `emirates_id` (`emirates_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_user`
--

LOCK TABLES `admin_backend_final_user` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_user` DISABLE KEYS */;
INSERT INTO `admin_backend_final_user` VALUES
('pbkdf2_sha256$600000$fDMe84ib4AdjzcOk58omzK$9qAbUy2mpEvBxmGYZvfxDO0+HshOcQSmLr6eA5ujqZg=','2025-09-01 11:41:06.711697',1,'abdullah','','',1,1,'2025-08-29 06:07:16.437688','','abd04@gmail.com','','2025-08-29 06:07:16.573727','2025-08-29 06:07:16.573736','',NULL,0,''),
('',NULL,0,'saboortahir453@gmail.com','Saboor Tahir','',0,1,'2025-09-01 06:24:45.860041','jcfu5XNX4cc3R0NmYqZl9nizWPo2','saboortahir453@gmail.com','','2025-09-01 06:24:45.860500','2025-09-01 06:24:45.860508','',NULL,0,''),
('',NULL,0,'overpowered120minecraft@gmail.com','Minecraft Player','',0,1,'2025-08-29 13:37:51.841591','KPTL9F1r8CXb9tjwG1jPE8B8LnR2','overpowered120minecraft@gmail.com','','2025-08-29 13:37:51.841739','2025-08-29 13:40:35.937559','',NULL,0,''),
('',NULL,0,'gptccaddxb@gmail.com','Chat GPT','',0,1,'2025-08-29 13:34:32.389663','Lirtv3dCFgcnSMDYPVAzGMAbMtR2','gptccaddxb@gmail.com','','2025-08-29 13:34:32.390257','2025-08-29 14:45:18.163224','',NULL,0,''),
('',NULL,0,'saimameer094@gmail.com','','',0,1,'2025-08-29 12:47:24.179173','local-1756471642616','saimameer094@gmail.com','pbkdf2_sha256$600000$V0S4IniRBD9V0p5iL1Up8m$9zMsUrrOi+cYikwgG1IhvxhRtoVwhtALNkEH6hR9uik=','2025-08-29 12:47:24.179595','2025-08-29 12:47:24.179604','',NULL,0,''),
('',NULL,0,'xyzmrop56@gmail.com','Ikrash','',0,1,'2025-09-02 15:53:20.020844','SAYxBYB1EWTHwKCG1Evkrqhkx9k1','xyzmrop56@gmail.com','pbkdf2_sha256$600000$fQCRwYgfAe95oj88jJn3oQ$wdhQ2v+0c2daqbkj4MsiPRVv9SH3slhUL5Ky0oaZQ+o=','2025-09-02 15:53:20.021235','2025-09-02 15:53:20.021243','',NULL,0,''),
('',NULL,0,'ccaddxb@gmail.com','Yasir Mehrban','',0,1,'2025-09-01 17:06:57.449113','XGKazNWNVEYjggmz86gJMVz5uww2','ccaddxb@gmail.com','','2025-09-01 17:06:57.449452','2025-09-02 19:01:39.631095','',NULL,0,'');
/*!40000 ALTER TABLE `admin_backend_final_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_user_groups`
--

DROP TABLE IF EXISTS `admin_backend_final_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(100) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_backend_final_user_groups_user_id_group_id_6abc6f7b_uniq` (`user_id`,`group_id`),
  KEY `admin_backend_final__group_id_3fc65fd4_fk_auth_grou` (`group_id`),
  CONSTRAINT `admin_backend_final__group_id_3fc65fd4_fk_auth_grou` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `admin_backend_final__user_id_c814c4d7_fk_admin_bac` FOREIGN KEY (`user_id`) REFERENCES `admin_backend_final_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_user_groups`
--

LOCK TABLES `admin_backend_final_user_groups` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_user_user_permissions`
--

DROP TABLE IF EXISTS `admin_backend_final_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(100) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_backend_final_user_user_id_permission_id_233a31c5_uniq` (`user_id`,`permission_id`),
  KEY `admin_backend_final__permission_id_e7c98d3e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `admin_backend_final__permission_id_e7c98d3e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `admin_backend_final__user_id_d22959f6_fk_admin_bac` FOREIGN KEY (`user_id`) REFERENCES `admin_backend_final_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_user_user_permissions`
--

LOCK TABLES `admin_backend_final_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_backend_final_variantcombination`
--

DROP TABLE IF EXISTS `admin_backend_final_variantcombination`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_backend_final_variantcombination` (
  `combo_id` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `price_override` decimal(10,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `variant_id` varchar(100) NOT NULL,
  PRIMARY KEY (`combo_id`),
  KEY `admin_backend_final__variant_id_79cd121b_fk_admin_bac` (`variant_id`),
  CONSTRAINT `admin_backend_final__variant_id_79cd121b_fk_admin_bac` FOREIGN KEY (`variant_id`) REFERENCES `admin_backend_final_productvariant` (`variant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_backend_final_variantcombination`
--

LOCK TABLES `admin_backend_final_variantcombination` WRITE;
/*!40000 ALTER TABLE `admin_backend_final_variantcombination` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_backend_final_variantcombination` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add content type',4,'add_contenttype'),
(14,'Can change content type',4,'change_contenttype'),
(15,'Can delete content type',4,'delete_contenttype'),
(16,'Can view content type',4,'view_contenttype'),
(17,'Can add session',5,'add_session'),
(18,'Can change session',5,'change_session'),
(19,'Can delete session',5,'delete_session'),
(20,'Can view session',5,'view_session'),
(21,'Can add Blacklisted Token',6,'add_blacklistedtoken'),
(22,'Can change Blacklisted Token',6,'change_blacklistedtoken'),
(23,'Can delete Blacklisted Token',6,'delete_blacklistedtoken'),
(24,'Can view Blacklisted Token',6,'view_blacklistedtoken'),
(25,'Can add Outstanding Token',7,'add_outstandingtoken'),
(26,'Can change Outstanding Token',7,'change_outstandingtoken'),
(27,'Can delete Outstanding Token',7,'delete_outstandingtoken'),
(28,'Can view Outstanding Token',7,'view_outstandingtoken'),
(29,'Can add user',8,'add_user'),
(30,'Can change user',8,'change_user'),
(31,'Can delete user',8,'delete_user'),
(32,'Can view user',8,'view_user'),
(33,'Can add admin',9,'add_admin'),
(34,'Can change admin',9,'change_admin'),
(35,'Can delete admin',9,'delete_admin'),
(36,'Can view admin',9,'view_admin'),
(37,'Can add admin role',10,'add_adminrole'),
(38,'Can change admin role',10,'change_adminrole'),
(39,'Can delete admin role',10,'delete_adminrole'),
(40,'Can view admin role',10,'view_adminrole'),
(41,'Can add blog',11,'add_blog'),
(42,'Can change blog',11,'change_blog'),
(43,'Can delete blog',11,'delete_blog'),
(44,'Can view blog',11,'view_blog'),
(45,'Can add blog category',12,'add_blogcategory'),
(46,'Can change blog category',12,'change_blogcategory'),
(47,'Can delete blog category',12,'delete_blogcategory'),
(48,'Can view blog category',12,'view_blogcategory'),
(49,'Can add callback request',13,'add_callbackrequest'),
(50,'Can change callback request',13,'change_callbackrequest'),
(51,'Can delete callback request',13,'delete_callbackrequest'),
(52,'Can view callback request',13,'view_callbackrequest'),
(53,'Can add cart',14,'add_cart'),
(54,'Can change cart',14,'change_cart'),
(55,'Can delete cart',14,'delete_cart'),
(56,'Can view cart',14,'view_cart'),
(57,'Can add category',15,'add_category'),
(58,'Can change category',15,'change_category'),
(59,'Can delete category',15,'delete_category'),
(60,'Can view category',15,'view_category'),
(61,'Can add deleted items cache',16,'add_deleteditemscache'),
(62,'Can change deleted items cache',16,'change_deleteditemscache'),
(63,'Can delete deleted items cache',16,'delete_deleteditemscache'),
(64,'Can view deleted items cache',16,'view_deleteditemscache'),
(65,'Can add first carousel',17,'add_firstcarousel'),
(66,'Can change first carousel',17,'change_firstcarousel'),
(67,'Can delete first carousel',17,'delete_firstcarousel'),
(68,'Can view first carousel',17,'view_firstcarousel'),
(69,'Can add hero banner',18,'add_herobanner'),
(70,'Can change hero banner',18,'change_herobanner'),
(71,'Can delete hero banner',18,'delete_herobanner'),
(72,'Can view hero banner',18,'view_herobanner'),
(73,'Can add image',19,'add_image'),
(74,'Can change image',19,'change_image'),
(75,'Can delete image',19,'delete_image'),
(76,'Can view image',19,'view_image'),
(77,'Can add notification',20,'add_notification'),
(78,'Can change notification',20,'change_notification'),
(79,'Can delete notification',20,'delete_notification'),
(80,'Can view notification',20,'view_notification'),
(81,'Can add orders',21,'add_orders'),
(82,'Can change orders',21,'change_orders'),
(83,'Can delete orders',21,'delete_orders'),
(84,'Can view orders',21,'view_orders'),
(85,'Can add product',22,'add_product'),
(86,'Can change product',22,'change_product'),
(87,'Can delete product',22,'delete_product'),
(88,'Can view product',22,'view_product'),
(89,'Can add product variant',23,'add_productvariant'),
(90,'Can change product variant',23,'change_productvariant'),
(91,'Can delete product variant',23,'delete_productvariant'),
(92,'Can view product variant',23,'view_productvariant'),
(93,'Can add second carousel',24,'add_secondcarousel'),
(94,'Can change second carousel',24,'change_secondcarousel'),
(95,'Can delete second carousel',24,'delete_secondcarousel'),
(96,'Can view second carousel',24,'view_secondcarousel'),
(97,'Can add site settings',25,'add_sitesettings'),
(98,'Can change site settings',25,'change_sitesettings'),
(99,'Can delete site settings',25,'delete_sitesettings'),
(100,'Can view site settings',25,'view_sitesettings'),
(101,'Can add sub category',26,'add_subcategory'),
(102,'Can change sub category',26,'change_subcategory'),
(103,'Can delete sub category',26,'delete_subcategory'),
(104,'Can view sub category',26,'view_subcategory'),
(105,'Can add variant combination',27,'add_variantcombination'),
(106,'Can change variant combination',27,'change_variantcombination'),
(107,'Can delete variant combination',27,'delete_variantcombination'),
(108,'Can view variant combination',27,'view_variantcombination'),
(109,'Can add sub category image',28,'add_subcategoryimage'),
(110,'Can change sub category image',28,'change_subcategoryimage'),
(111,'Can delete sub category image',28,'delete_subcategoryimage'),
(112,'Can view sub category image',28,'view_subcategoryimage'),
(113,'Can add shipping info',29,'add_shippinginfo'),
(114,'Can change shipping info',29,'change_shippinginfo'),
(115,'Can delete shipping info',29,'delete_shippinginfo'),
(116,'Can view shipping info',29,'view_shippinginfo'),
(117,'Can add second carousel image',30,'add_secondcarouselimage'),
(118,'Can change second carousel image',30,'change_secondcarouselimage'),
(119,'Can delete second carousel image',30,'delete_secondcarouselimage'),
(120,'Can view second carousel image',30,'view_secondcarouselimage'),
(121,'Can add product seo',31,'add_productseo'),
(122,'Can change product seo',31,'change_productseo'),
(123,'Can delete product seo',31,'delete_productseo'),
(124,'Can view product seo',31,'view_productseo'),
(125,'Can add product inventory',32,'add_productinventory'),
(126,'Can change product inventory',32,'change_productinventory'),
(127,'Can delete product inventory',32,'delete_productinventory'),
(128,'Can view product inventory',32,'view_productinventory'),
(129,'Can add product image',33,'add_productimage'),
(130,'Can change product image',33,'change_productimage'),
(131,'Can delete product image',33,'delete_productimage'),
(132,'Can view product image',33,'view_productimage'),
(133,'Can add order item',34,'add_orderitem'),
(134,'Can change order item',34,'change_orderitem'),
(135,'Can delete order item',34,'delete_orderitem'),
(136,'Can view order item',34,'view_orderitem'),
(137,'Can add order delivery',35,'add_orderdelivery'),
(138,'Can change order delivery',35,'change_orderdelivery'),
(139,'Can delete order delivery',35,'delete_orderdelivery'),
(140,'Can view order delivery',35,'view_orderdelivery'),
(141,'Can add hero banner image',36,'add_herobannerimage'),
(142,'Can change hero banner image',36,'change_herobannerimage'),
(143,'Can delete hero banner image',36,'delete_herobannerimage'),
(144,'Can view hero banner image',36,'view_herobannerimage'),
(145,'Can add first carousel image',37,'add_firstcarouselimage'),
(146,'Can change first carousel image',37,'change_firstcarouselimage'),
(147,'Can delete first carousel image',37,'delete_firstcarouselimage'),
(148,'Can view first carousel image',37,'view_firstcarouselimage'),
(149,'Can add dashboard snapshot',38,'add_dashboardsnapshot'),
(150,'Can change dashboard snapshot',38,'change_dashboardsnapshot'),
(151,'Can delete dashboard snapshot',38,'delete_dashboardsnapshot'),
(152,'Can view dashboard snapshot',38,'view_dashboardsnapshot'),
(153,'Can add category image',39,'add_categoryimage'),
(154,'Can change category image',39,'change_categoryimage'),
(155,'Can delete category image',39,'delete_categoryimage'),
(156,'Can view category image',39,'view_categoryimage'),
(157,'Can add cart item',40,'add_cartitem'),
(158,'Can change cart item',40,'change_cartitem'),
(159,'Can delete cart item',40,'delete_cartitem'),
(160,'Can view cart item',40,'view_cartitem'),
(161,'Can add blog seo',41,'add_blogseo'),
(162,'Can change blog seo',41,'change_blogseo'),
(163,'Can delete blog seo',41,'delete_blogseo'),
(164,'Can view blog seo',41,'view_blogseo'),
(165,'Can add product sub category map',42,'add_productsubcategorymap'),
(166,'Can change product sub category map',42,'change_productsubcategorymap'),
(167,'Can delete product sub category map',42,'delete_productsubcategorymap'),
(168,'Can view product sub category map',42,'view_productsubcategorymap'),
(169,'Can add category sub category map',43,'add_categorysubcategorymap'),
(170,'Can change category sub category map',43,'change_categorysubcategorymap'),
(171,'Can delete category sub category map',43,'delete_categorysubcategorymap'),
(172,'Can view category sub category map',43,'view_categorysubcategorymap'),
(173,'Can add blog category map',44,'add_blogcategorymap'),
(174,'Can change blog category map',44,'change_blogcategorymap'),
(175,'Can delete blog category map',44,'delete_blogcategorymap'),
(176,'Can view blog category map',44,'view_blogcategorymap'),
(177,'Can add attribute',45,'add_attribute'),
(178,'Can change attribute',45,'change_attribute'),
(179,'Can delete attribute',45,'delete_attribute'),
(180,'Can view attribute',45,'view_attribute'),
(181,'Can add admin role map',46,'add_adminrolemap'),
(182,'Can change admin role map',46,'change_adminrolemap'),
(183,'Can delete admin role map',46,'delete_adminrolemap'),
(184,'Can view admin role map',46,'view_adminrolemap'),
(185,'Can add blog post',47,'add_blogpost'),
(186,'Can change blog post',47,'change_blogpost'),
(187,'Can delete blog post',47,'delete_blogpost'),
(188,'Can view blog post',47,'view_blogpost'),
(189,'Can add testimonial',48,'add_testimonial'),
(190,'Can change testimonial',48,'change_testimonial'),
(191,'Can delete testimonial',48,'delete_testimonial'),
(192,'Can view testimonial',48,'view_testimonial'),
(193,'Can add blog image',49,'add_blogimage'),
(194,'Can change blog image',49,'change_blogimage'),
(195,'Can delete blog image',49,'delete_blogimage'),
(196,'Can view blog image',49,'view_blogimage'),
(197,'Can add blog comment',50,'add_blogcomment'),
(198,'Can change blog comment',50,'change_blogcomment'),
(199,'Can delete blog comment',50,'delete_blogcomment'),
(200,'Can view blog comment',50,'view_blogcomment');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_admin_bac` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_admin_bac` FOREIGN KEY (`user_id`) REFERENCES `admin_backend_final_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES
(1,'2025-08-29 06:07:37.112077','1','admin',1,'[{\"added\": {}}]',9,''),
(2,'2025-08-29 06:55:22.782084','1','admin',3,'',9,'');
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES
(1,'admin','logentry'),
(9,'admin_backend_final','admin'),
(10,'admin_backend_final','adminrole'),
(46,'admin_backend_final','adminrolemap'),
(45,'admin_backend_final','attribute'),
(11,'admin_backend_final','blog'),
(12,'admin_backend_final','blogcategory'),
(44,'admin_backend_final','blogcategorymap'),
(50,'admin_backend_final','blogcomment'),
(49,'admin_backend_final','blogimage'),
(47,'admin_backend_final','blogpost'),
(41,'admin_backend_final','blogseo'),
(13,'admin_backend_final','callbackrequest'),
(14,'admin_backend_final','cart'),
(40,'admin_backend_final','cartitem'),
(15,'admin_backend_final','category'),
(39,'admin_backend_final','categoryimage'),
(43,'admin_backend_final','categorysubcategorymap'),
(38,'admin_backend_final','dashboardsnapshot'),
(16,'admin_backend_final','deleteditemscache'),
(17,'admin_backend_final','firstcarousel'),
(37,'admin_backend_final','firstcarouselimage'),
(18,'admin_backend_final','herobanner'),
(36,'admin_backend_final','herobannerimage'),
(19,'admin_backend_final','image'),
(20,'admin_backend_final','notification'),
(35,'admin_backend_final','orderdelivery'),
(34,'admin_backend_final','orderitem'),
(21,'admin_backend_final','orders'),
(22,'admin_backend_final','product'),
(33,'admin_backend_final','productimage'),
(32,'admin_backend_final','productinventory'),
(31,'admin_backend_final','productseo'),
(42,'admin_backend_final','productsubcategorymap'),
(23,'admin_backend_final','productvariant'),
(24,'admin_backend_final','secondcarousel'),
(30,'admin_backend_final','secondcarouselimage'),
(29,'admin_backend_final','shippinginfo'),
(25,'admin_backend_final','sitesettings'),
(26,'admin_backend_final','subcategory'),
(28,'admin_backend_final','subcategoryimage'),
(48,'admin_backend_final','testimonial'),
(8,'admin_backend_final','user'),
(27,'admin_backend_final','variantcombination'),
(3,'auth','group'),
(2,'auth','permission'),
(4,'contenttypes','contenttype'),
(5,'sessions','session'),
(6,'token_blacklist','blacklistedtoken'),
(7,'token_blacklist','outstandingtoken');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES
(1,'contenttypes','0001_initial','2025-08-28 16:30:23.523052'),
(2,'contenttypes','0002_remove_content_type_name','2025-08-28 16:30:23.536721'),
(3,'auth','0001_initial','2025-08-28 16:30:23.578700'),
(4,'auth','0002_alter_permission_name_max_length','2025-08-28 16:30:23.587102'),
(5,'auth','0003_alter_user_email_max_length','2025-08-28 16:30:23.589885'),
(6,'auth','0004_alter_user_username_opts','2025-08-28 16:30:23.593209'),
(7,'auth','0005_alter_user_last_login_null','2025-08-28 16:30:23.595776'),
(8,'auth','0006_require_contenttypes_0002','2025-08-28 16:30:23.596643'),
(9,'auth','0007_alter_validators_add_error_messages','2025-08-28 16:30:23.599182'),
(10,'auth','0008_alter_user_username_max_length','2025-08-28 16:30:23.601921'),
(11,'auth','0009_alter_user_last_name_max_length','2025-08-28 16:30:23.604539'),
(12,'auth','0010_alter_group_name_max_length','2025-08-28 16:30:23.610560'),
(13,'auth','0011_update_proxy_permissions','2025-08-28 16:30:23.613556'),
(14,'auth','0012_alter_user_first_name_max_length','2025-08-28 16:30:23.616041'),
(15,'admin_backend_final','0001_initial','2025-08-28 16:30:24.315942'),
(16,'admin','0001_initial','2025-08-28 16:30:24.344795'),
(17,'admin','0002_logentry_remove_auto_add','2025-08-28 16:30:24.349892'),
(18,'admin','0003_logentry_add_action_flag_choices','2025-08-28 16:30:24.355068'),
(19,'sessions','0001_initial','2025-08-28 16:30:24.362948'),
(20,'token_blacklist','0001_initial','2025-08-28 16:30:24.405589'),
(21,'token_blacklist','0002_outstandingtoken_jti_hex','2025-08-28 16:30:24.414148'),
(22,'token_blacklist','0003_auto_20171017_2007','2025-08-28 16:30:24.431849'),
(23,'token_blacklist','0004_auto_20171017_2013','2025-08-28 16:30:24.447254'),
(24,'token_blacklist','0005_remove_outstandingtoken_jti','2025-08-28 16:30:24.457494'),
(25,'token_blacklist','0006_auto_20171017_2113','2025-08-28 16:30:24.466328'),
(26,'token_blacklist','0007_auto_20171017_2214','2025-08-28 16:30:24.514318'),
(27,'token_blacklist','0008_migrate_to_bigautofield','2025-08-28 16:30:24.561163'),
(28,'token_blacklist','0010_fix_migrate_to_bigautofield','2025-08-28 16:30:24.577107'),
(29,'token_blacklist','0011_linearizes_history','2025-08-28 16:30:24.578272'),
(30,'token_blacklist','0012_alter_outstandingtoken_user','2025-08-28 16:30:24.591309'),
(31,'token_blacklist','0013_alter_blacklistedtoken_options_and_more','2025-08-28 16:30:24.598390'),
(32,'admin_backend_final','0002_remove_productseo_slug_alter_product_title','2025-08-29 17:58:29.131047'),
(33,'admin_backend_final','0003_orders_device_uuid_user_address_user_emirates_id_and_more','2025-09-03 16:44:37.045725'),
(34,'admin_backend_final','0004_delete_blogseo','2025-09-17 18:15:34.308838'),
(35,'admin_backend_final','0005_delete_blogcategorymap','2025-09-17 18:19:09.059514'),
(36,'admin_backend_final','0006_delete_blogcategory','2025-09-17 18:19:58.774700'),
(37,'admin_backend_final','0007_delete_blog','2025-09-17 18:20:43.485520'),
(38,'admin_backend_final','0008_blogpost_product_long_description_and_more','2025-09-17 18:29:09.784870');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES
('4l64sqjo9fkesblpffhd0r5f1r7ams9s','.eJxVjDsOwjAQRO_iGln4H1PS5wzW2rvGAWRLcVIh7g6WUkAzxZs382IB9q2EvdMaFmQXxk6_KEJ6UB0c71BvjadWt3WJfCj8aDufG9Lzerh_BwV6GeuzTwAes0EjLGJyEqVWhKSdSIhWZvqGV2hd1tqAMmQFRanFRHFS7P0B6uU4aA:1ut2uI:kNy3IOxHFVsXs_hTWAXKTa26LscLN0iuiBaaXbyfH98','2025-09-15 11:41:06.714561');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_blacklistedtoken`
--

LOCK TABLES `token_blacklist_blacklistedtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` varchar(100) DEFAULT NULL,
  `jti` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outs_user_id_83bc629a_fk_admin_bac` (`user_id`),
  CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_admin_bac` FOREIGN KEY (`user_id`) REFERENCES `admin_backend_final_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_outstandingtoken`
--

LOCK TABLES `token_blacklist_outstandingtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'api_creative'
--

--
-- Dumping routines for database 'api_creative'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-20 21:20:56
