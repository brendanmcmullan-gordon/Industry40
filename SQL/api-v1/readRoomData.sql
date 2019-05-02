"SELECT
    roomName, humidity, temperature, outsideTemp, CO2, readDate 
FROM
    " . $this->table_name . "
ORDER BY
    readDate DESC"