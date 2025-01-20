<?php
// file used in server to save data from the study
// this path should point to your configuration file.
include('database_config.php');

$data_array = json_decode(file_get_contents('php://input'), true);

try {
  $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
  $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  // First stage is to get all column names from the table and store
  // them in $col_names array.
  $stmt = $conn->prepare("SHOW COLUMNS FROM `$table`");
  $stmt->execute();
  $col_names = array();
  while($row = $stmt->fetchColumn()) {
    $col_names[] = $row;
  }

  // Second stage is to create prepared SQL statement using the column
  // names as a guide to what values might be in the JSON.
  // If a value is missing from a particular trial, then NULL is inserted
  $sql = "INSERT INTO $table VALUES(";
  for($i = 0; $i < count($col_names); $i++){
    $name = $col_names[$i];
    $sql .= ":$name";
    if($i != count($col_names)-1){
      $sql .= ", ";
    }
  }
  $sql .= ");";
  //create unique id for participant
  $id = uniqid("");
  $insertstmt = $conn->prepare($sql);
  for($i=0; $i < count($data_array)-2; $i++){
    for($j = 0; $j < count($col_names); $j++){
      $colname = $col_names[$j];
      if ($colname == "participant_id"){
        $insertstmt->bindValue(":$colname", $id);
      } else if ($colname == "response"){
        $insertstmt->bindValue(":$colname", json_encode($data_array[$i][$colname]));
      } else if ($colname == "statements"){
        $insertstmt->bindValue(":$colname", json_encode($data_array[$i][$colname]));
      } else if ($colname == "final_statements"){
        $insertstmt->bindValue(":$colname", json_encode($data_array[$i][$colname]));
      } else if(!isset($data_array[$i][$colname])){
        $insertstmt->bindValue(":$colname", null, PDO::PARAM_NULL);
      } else {
        $insertstmt->bindValue(":$colname", $data_array[$i][$colname]);
      }
    }
    $insertstmt->execute();
  }
  //prepare statement to insert prolific meta data into table
  // If a value is missing from a particular trial, then NULL is inserted
  $stmt = $conn->prepare("SHOW COLUMNS FROM `$table_meta`");
  $stmt->execute();
  $col_names = array();
  while($row = $stmt->fetchColumn()) {
    $col_names[] = $row;
  }

  $sql_meta = "INSERT INTO $table_meta VALUES(";
  for($i = 0; $i < count($col_names); $i++){
    $name = $col_names[$i];
    if ($name == "date_of_completion"){
      $sql_meta .= "CURRENT_TIMESTAMP";
    } else {
      $sql_meta .= ":$name";
    }
    if($i != count($col_names)-1){
      $sql_meta .= ", ";
    }
  }
  $sql_meta .= ");";
  $insertstmt_meta = $conn->prepare($sql_meta);
  $i = count($data_array)-2;
  for($j = 0; $j < count($col_names); $j++){
      $colname = $col_names[$j];
      if ($colname == "participant_id"){
        $insertstmt_meta->bindValue(":$colname", $id);
      } else if ($colname == "date_of_completion"){
        // ignore column
      } else if(!isset($data_array[$i][$colname])){
        $insertstmt_meta->bindValue(":$colname", null, PDO::PARAM_NULL);
      } else {
        $insertstmt_meta->bindValue(":$colname", $data_array[$i][$colname]);
      }
  }
  $insertstmt_meta->execute();

  echo '{"success": true}';
} catch(PDOException $e) {
  echo '{"success": false, "message": ' . $e->getMessage();
}
$conn = null;
?>
