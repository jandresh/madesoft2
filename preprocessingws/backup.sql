-- MySQL dump 10.13  Distrib 5.7.35, for Linux (x86_64)
--
-- Host: localhost    Database: adccali
-- ------------------------------------------------------
-- Server version	5.7.35

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
-- Table structure for table `patterns`
--

DROP TABLE IF EXISTS `patterns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `patterns` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `pattern` text NOT NULL,
  `db` text NOT NULL,
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=116 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patterns`
--

LOCK TABLES `patterns` WRITE;
/*!40000 ALTER TABLE `patterns` DISABLE KEYS */;
INSERT INTO `patterns` VALUES (1,'abstract:(cáncer AND pulmón)','CORE','Corpus 1'),(2,'abstract:(cáncer AND prostata)','CORE','Corpus 1'),(3,'abstract:(cáncer AND mama)','CORE','Corpus 1'),(4,'abstract:(cáncer AND ovario)','CORE','Corpus 1'),(5,'abstract:(cáncer AND cervix)','CORE','Corpus 1'),(6,'abstract:(cáncer AND pelvis)','CORE','Corpus 1'),(7,'abstract:(cáncer AND vejiga)','CORE','Corpus 1'),(8,'abstract:(cáncer AND metástasis)','CORE','Corpus 1'),(9,'abstract:(cáncer AND estómago)','CORE','Corpus 1'),(10,'abstract:(cáncer AND huesos)','CORE','Corpus 1'),(11,'abstract:(cáncer AND tiroides)','CORE','Corpus 1'),(12,'abstract:(cáncer AND colon)','CORE','Corpus 1'),(13,'abstract:(cáncer AND cuello AND uterino)','CORE','Corpus 1'),(14,'abstract:(cáncer AND quimioterapia)','CORE','Corpus 1'),(15,'abstract:(cáncer AND radioterapia)','CORE','Corpus 1'),(16,'abstract:(cáncer AND tratamiento)','CORE','Corpus 1'),(17,'abstract:(tumores AND cerebrales)','CORE','Corpus 1'),(18,'abstract:(cáncer AND piel)','CORE','Corpus 1'),(19,'abstract:(cáncer AND triple AND negativo)','CORE','Corpus 1'),(20,'abstract:(Cáncer AND fumador)','CORE','Corpus 1'),(21,'abstract:(Cáncer AND mutación)','CORE','Corpus 1'),(22,'abstract:(Leucemia)','CORE','Corpus 1'),(23,'abstract:(neoplasia AND pulmonar)','CORE','Corpus 1'),(24,'abstract:(neoplasia AND maligna)','CORE','Corpus 1'),(25,'abstract:(carcinoma AND pulmonar)','CORE','Corpus 1'),(26,'abstract:(carcinoma AND escamoso AND pulmón)','CORE','Corpus 1'),(27,'abstract:(adenocarcinoma AND pulmón)','CORE','Corpus 1'),(28,'abstract:(carcinoma AND celulas AND grandes)','CORE','Corpus 1'),(29,'abstract:(carcinoma AND celulas AND pequeñas)','CORE','Corpus 1'),(30,'abstract:(carcinoma AND quimioterapia)','CORE','Corpus 1'),(31,'abstract:(carcinoma AND radioterapia)','CORE','Corpus 1'),(32,'abstract:(células AND malignas)','CORE','Corpus 1'),(33,'abstract:(células AND cancerosas)','CORE','Corpus 1'),(34,'abstract:(células AND cancerígenas)','CORE','Corpus 1'),(35,'abstract:(carcinoma AND infiltrante)','CORE','Corpus 1'),(36,'abstract:(carcinoma AND mamario)','CORE','Corpus 1'),(37,'abstract:(carcinoma AND in AND situ)','CORE','Corpus 1'),(38,'abstract:(Carcinoma AND lobulillar)','CORE','Corpus 1'),(39,'abstract:(Carcinoma AND ductal)','CORE','Corpus 1'),(40,'abstract:(Carcinoma AND invasivo)','CORE','Corpus 1'),(41,'abstract:(Melanoma)','CORE','Corpus 1'),(42,'abstract:(Linfoma)','CORE','Corpus 1'),(43,'abstract:(paciente AND oncológico)','CORE','Corpus 1'),(44,'abstract:(efectos AND adversos AND medicamentos)','CORE','Corpus 1'),(45,'abstract:(efectos AND secundarios AND medicamentos)','CORE','Corpus 1'),(46,'abstract:(Terapia AND reemplazo AND hormonal)','CORE','Corpus 1'),(47,'abstract:(Carboplatino)','CORE','Corpus 1'),(48,'abstract:(Pemetrexed)','CORE','Corpus 1'),(49,'abstract:(Cisplatino)','CORE','Corpus 1'),(50,'abstract:(Vinorelbina)','CORE','Corpus 1'),(51,'abstract:(Gemcitabina)','CORE','Corpus 1'),(52,'abstract:(Metoclopramida)','CORE','Corpus 1'),(53,'abstract:(Doxetacel)','CORE','Corpus 1'),(54,'abstract:(bevacizumab)','CORE','Corpus 1'),(55,'abstract:(Taxol)','CORE','Corpus 1'),(56,'abstract:(Ciclofosfamida)','CORE','Corpus 1'),(57,'abstract:(Doxorrubicina)','CORE','Corpus 1'),(58,'abstract:(Metotrexato)','CORE','Corpus 1'),(59,'abstract:(Cabazitaxel)','CORE','Corpus 1'),(60,'abstract:(Capecitabina)','CORE','Corpus 1'),(61,'abstract:(tratamiento AND hormonal)','CORE','Corpus 1'),(62,'abstract:(Ciclofosfamida)','CORE','Corpus 1'),(63,'abstract:(Etopósido)','CORE','Corpus 1'),(64,'abstract:(Oxaliplatino)','CORE','Corpus 1'),(65,'abstract:(Taxotere)','CORE','Corpus 1'),(66,'abstract:(Trifluridina)','CORE','Corpus 1'),(67,'abstract:(Temozolomida)','CORE','Corpus 1'),(68,'abstract:(Dacarbazina)','CORE','Corpus 1'),(69,'abstract:(Amoxicilina)','CORE','Corpus 1'),(70,'abstract:(Penicilina)','CORE','Corpus 1'),(71,'abstract:(Tetraciclina)','CORE','Corpus 1'),(72,'abstract:(Ticarcilina)','CORE','Corpus 1'),(73,'abstract:(Azitromicina)','CORE','Corpus 1'),(74,'abstract:(Gentamicina)','CORE','Corpus 1'),(75,'abstract:(Dexametasona)','CORE','Corpus 1'),(76,'abstract:(Ivermectina)','CORE','Corpus 1'),(77,'abstract:(Hidroxicloroquina)','CORE','Corpus 1'),(78,'abstract:(Inmunoterapia)','CORE','Corpus 1'),(79,'abstract:(diabetes)','CORE','Corpus 1'),(80,'abstract:(enfermedad AND cardiovascular)','CORE','Corpus 1'),(81,'abstract:(hipertensión AND arterial)','CORE','Corpus 1'),(82,'abstract:(presión AND arterial)','CORE','Corpus 1'),(83,'abstract:(dislipidemia)','CORE','Corpus 1'),(84,'abstract:(hipotiroidismo)','CORE','Corpus 1'),(85,'abstract:(trombopenia)','CORE','Corpus 1'),(86,'abstract:(neuropatia)','CORE','Corpus 1'),(87,'abstract:(dislipemia)','CORE','Corpus 1'),(88,'abstract:(enfisema)','CORE','Corpus 1'),(89,'abstract:(Trombosis AND venosa AND profunda)','CORE','Corpus 1'),(90,'abstract:(Adenopatías)','CORE','Corpus 1'),(91,'abstract:(Adenopatía)','CORE','Corpus 1'),(92,'abstract:(sistema AND inmunológico)','CORE','Corpus 1'),(93,'abstract:(Osteoporosis)','CORE','Corpus 1'),(94,'abstract:(insuficiencia AND respiratoria)','CORE','Corpus 1'),(95,'abstract:(insuficiencia AND cardiaca)','CORE','Corpus 1'),(96,'abstract:(deterioro AND cognitivo)','CORE','Corpus 1'),(97,'abstract:(esclerosis AND múltiple)','CORE','Corpus 1'),(98,'abstract:(úlcera AND gastroduodenal)','CORE','Corpus 1'),(99,'abstract:(ictus AND isquémico)','CORE','Corpus 1'),(100,'abstract:(Accidente AND cerebrovascular)','CORE','Corpus 1'),(101,'abstract:(epilepsia)','CORE','Corpus 1'),(102,'abstract:(Uropatias)','CORE','Corpus 1'),(103,'abstract:(Hipercolesterolemia)','CORE','Corpus 1'),(104,'abstract:(reacciones AND alérgicas)','CORE','Corpus 1'),(105,'abstract:(murmullo AND vesicular)','CORE','Corpus 1'),(106,'abstract:(obstrucción AND pulmonar AND crónica)','CORE','Corpus 1'),(107,'abstract:(Anemia)','CORE','Corpus 1'),(108,'abstract:(Mastectomía)','CORE','Corpus 1'),(109,'abstract:(Linfadenectomía)','CORE','Corpus 1'),(110,'abstract:(Tumorectomía)','CORE','Corpus 1'),(111,'abstract:(Lobectomía)','CORE','Corpus 1'),(112,'abstract:(oncología AND médica)','CORE','Corpus 1'),(113,'abstract:(Cirugía AND coronaria)','CORE','Corpus 1'),(114,'abstract:(Cirugía AND valvular)','CORE','Corpus 1'),(115,'abstract:(Neumonectomía)','CORE','Corpus 1');
/*!40000 ALTER TABLE `patterns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `searches`
--

DROP TABLE IF EXISTS `searches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `searches` (
  `patid` int(10) NOT NULL,
  `docid` int(10) NOT NULL,
  `title` text,
  `abs` text,
  `ftext` mediumtext,
  PRIMARY KEY (`patid`,`docid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `searches`
--

LOCK TABLES `searches` WRITE;
/*!40000 ALTER TABLE `searches` DISABLE KEYS */;
/*!40000 ALTER TABLE `searches` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-12-13 22:46:02
