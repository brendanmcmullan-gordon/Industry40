<?php
class RoomData{
 
    // database connection and table name
    private $conn;
    private $table_name = "roomData";
 
    // object properties
    public $id;
    public $roomName;
    public $humidity;
    public $temperature;
    public $outsideTemp;
    public $CO2;
    public $readDate;
 
    // constructor with $db as database connection
    public function __construct($db){
        $this->conn = $db;
    }

    // read roomData
    function read(){
 
        // select all query
        $query = "SELECT
                roomName, humidity, temperature, outsideTemp, CO2, readDate 
            FROM
                " . $this->table_name . "
            ORDER BY
                readDate DESC";
 
    // prepare query statement
        $stmt = $this->conn->prepare($query);
 
    // execute query
        $stmt->execute();
 
        return $stmt;
    }
}

//  CREATE TABLE roomData (
//      id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
//      roomName VARCHAR(20) NOT NULL,
//      humidity VARCHAR(8),
//      temperature VARCHAR(8),
//      outsideTemp VARCHAR(4),
//      CO2 VARCHAR(8),
//      readDate TIMESTAMP
//  )