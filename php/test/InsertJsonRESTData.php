<?php
// Author : Steve Gale 29/03/9
// Modified : SG - 29/03/19 -
// Copyright 2019 Steve Gale - seek permission and terms of use before you copy or modify this code
$servername = "localhost";
$username = "I40";
$password = "Password1";
$dbname = "Industry40db";

// Create connection
$conn = mysqli_connect($servername, $username, $password, $dbname);
// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}
// POST data 
$response = array();
$res=array();

//$json = json_decode($_POST[]);
$json = _json_decode(file_get_contents('php://input'));

if($json!=null){
   
    $RoomName=$json["RoomName"];
    $Humidity=$json["Humidity"];
    $Temperature=$json["Temperature"];
 //   $SampleDate=$json["date"];
    
$sql = "INSERT INTO TestData (roomName, humidity, temperature)
VALUES ('$RoomName', '$Humidity', '$Temperature')";

    if (mysqli_query($conn, $sql)) {
        // successfully inserted into database
        $response["code"] = "1";
        $response["message"] = "successfully stored";
        // echoing JSON response
        echo json_encode($response);
    } else {
            // failed to insert row
        $response["code"] = "2";
        $response["message"] = mysqli_error($conn);
        // echoing JSON response
        echo json_encode($response);
    }
} else {
   echo "json data error";
}
mysqli_close($conn);


// fixes magic quotes issue in json post data
function _json_decode($string) {
    if (get_magic_quotes_gpc()) {
        $string = stripslashes($string);
    }
    return json_decode($string,true);
    }
?>

