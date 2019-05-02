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
}