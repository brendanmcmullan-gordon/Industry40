<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
 
// database connection will be here
// include database and object files
include_once '../config/database.php';
include_once '../objects/roomData.php';
 
// instantiate database and roomData object
$database = new Database();
$db = $database->getConnection();
 
// initialize object
$roomData = new RoomData($db);
 
// read roomData will be here
// query roomData
$stmt = $roomData->read();
$num = $stmt->rowCount();
 
// check if more than 0 record found
if($num>0){
 
    // products array
    $roomData_arr=array();
    $roomData_arr["records"]=array();
 
    // retrieve our table contents
    // fetch() is faster than fetchAll()
    // http://stackoverflow.com/questions/2770630/pdofetchall-vs-pdofetch-in-a-loop
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)){
        // extract row
        // this will make $row['name'] to
        // just $name only
        extract($row);

        $roomData_item=array(
            "id" => $id,
            "roomName" => $roomName,
            "humidity" => $humidity,
            "temperature" => $temperature,
            "outsideTemp" => $outsideTemp,
            "CO2" => $CO2
        );
 
        array_push($roomData_arr["records"], $roomData_item);
    }
    
 
    // set response code - 200 OK
    http_response_code(200);
 
    // show roomData data in json format
    echo json_encode($roomData_arr);
}
 
// no roomData found will be here


// ref below
//        public $id;
//        public $roomName;
//        public $humidity;
//        public $temperature;
//        public $outsideTemp;
//        public $CO2;
//        public $readDate;
//  CREATE TABLE roomData (
//      id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
//      roomName VARCHAR(20) NOT NULL,
//      humidity VARCHAR(8),
//      temperature VARCHAR(8),
//      outsideTemp VARCHAR(4),
//      CO2 VARCHAR(8),
//      readDate TIMESTAMP
//  )