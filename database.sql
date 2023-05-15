-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.27-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.5.0.6677
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for installations_db
CREATE DATABASE IF NOT EXISTS `installations_db` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci */;
USE `installations_db`;

-- Dumping structure for table installations_db.nodes_tbl
CREATE TABLE IF NOT EXISTS `nodes_tbl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `latitude` text DEFAULT NULL,
  `longitude` text DEFAULT NULL,
  `popup` text DEFAULT NULL,
  `image_filename` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Dumping data for table installations_db.nodes_tbl: ~2 rows (approximately)
INSERT INTO `nodes_tbl` (`id`, `latitude`, `longitude`, `popup`, `image_filename`) VALUES
	(1, '37.90838', '23.72531', 'HEADQUARTERS', 'unixfor.png'),
	(2, '40.640064', '22.944420', 'ΘΕΣΣΑΛΟΝΙΚΗΣ', 'unixfor.png');

-- Dumping structure for table installations_db.settings_tbl
CREATE TABLE IF NOT EXISTS `settings_tbl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_latitude` text NOT NULL,
  `map_longitude` text NOT NULL,
  `zoom_level` text NOT NULL,
  `x_image` int(11) NOT NULL,
  `y_image` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- Dumping data for table installations_db.settings_tbl: ~1 rows (approximately)
INSERT INTO `settings_tbl` (`id`, `map_latitude`, `map_longitude`, `zoom_level`, `x_image`, `y_image`) VALUES
	(1, '37.90838', '23.72531', '6', 25, 25);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
