<?php
// Enable error logging
ini_set('display_errors', 1);
ini_set('log_errors', 1);
ini_set('error_log', '/home/ddiemeo9zafc/mapcontacts/public/php_error.log');

// Set the path to the Python application
$python_app = '/home/ddiemeo9zafc/mapcontacts/app.py';
$port = 8000;
$pid_file = '/home/ddiemeo9zafc/mapcontacts/app.pid';
$log_file = '/home/ddiemeo9zafc/mapcontacts/public/app.log';

// Set environment variables
putenv('PYTHONPATH=/home/ddiemeo9zafc/mapcontacts');
putenv('FLASK_APP=app.py');
putenv('FLASK_ENV=production');

// Start the Python application if it's not running
if (!file_exists($pid_file)) {
    // Start the application with logging
    $command = "cd /home/ddiemeo9zafc/mapcontacts && python3 app.py > $log_file 2>&1 & echo $! > $pid_file";
    exec($command);
    // Wait a moment for the application to start
    sleep(2);
}

// Check if the application is running
$pid = file_exists($pid_file) ? file_get_contents($pid_file) : null;
if ($pid && !file_exists("/proc/$pid")) {
    // Process is not running, remove PID file and try to start again
    unlink($pid_file);
    $command = "cd /home/ddiemeo9zafc/mapcontacts && python3 app.py > $log_file 2>&1 & echo $! > $pid_file";
    exec($command);
    sleep(2);
}

// Forward the request to the Python application
$ch = curl_init();
$url = "http://localhost:$port" . $_SERVER['REQUEST_URI'];
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10); // Add timeout

// Forward the request method
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']);

// Forward headers
$headers = getallheaders();
$curl_headers = [];
foreach ($headers as $key => $value) {
    if ($key != 'Host') {
        $curl_headers[] = "$key: $value";
    }
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $curl_headers);

// Forward POST data
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input'));
}

// Get the response
$response = curl_exec($ch);
$header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

// Log any curl errors
if ($response === false) {
    error_log("Curl error: " . curl_error($ch));
}

// Close the connection
curl_close($ch);

// Split response into headers and body
$header = substr($response, 0, $header_size);
$body = substr($response, $header_size);

// Forward headers
$header_lines = explode("\n", $header);
foreach ($header_lines as $line) {
    if (trim($line) != '') {
        header($line);
    }
}

// Set the status code
http_response_code($http_code);

// Output the body
echo $body;
?> 