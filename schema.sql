 CREATE TABLE `user_rates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_email` varchar(255) NOT NULL,
  `origin` varchar(255) NOT NULL,
  `destination` varchar(255) NOT NULL,
  `effective_date` date NOT NULL,
  `expiry_date` date NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `annual_volume` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`)
)

 CREATE TABLE `market_rates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `origin` varchar(255) NOT NULL,
  `destination` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`)
)

CREATE TABLE `aggregated_market_prices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `origin` varchar(255) NOT NULL,
  `destination` varchar(255) NOT NULL,
  `min_price` decimal(10,2) DEFAULT NULL,
  `percentile_10_price` decimal(10,2) DEFAULT NULL,
  `median_price` decimal(10,2) DEFAULT NULL,
  `percentile_90_price` decimal(10,2) DEFAULT NULL,
  `max_price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
)
