// Author : Steve Gale
// Modified : SG - 27/03/19 -
// Copyright 2019 Steve Gale - seek permission and terms of use before you copy or modify this code
<?php
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

$sql = "INSERT INTO TestData (roomName, humidity, temperature)
VALUES ('E223', '10.1', '22.2')";

if (mysqli_query($conn, $sql)) {
    echo "New record created successfully";
} else {
    echo "Error: " . $sql . "<br>" . mysqli_error($conn);
}

mysqli_close($conn);
?>

