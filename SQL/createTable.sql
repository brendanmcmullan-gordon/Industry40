CREATE TABLE MAINTABLE
(
	ID INT AUTO_INCREMENT PRIMARY KEY,
	ROOMNUM VARCHAR(10),
	ROOMTEMP VARCHAR(4),
	OUTSIDETEMP VARCHAR(4),
	HUMIDITY VARCHAR(4),
	CO2 VARCHAR(8),
	TIMESTAMP DATETIME
);
