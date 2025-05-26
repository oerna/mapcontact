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

// Function to log messages
function log_message($message) {
    error_log(date('[Y-m-d H:i:s] ') . $message . "\n", 3, '/home/ddiemeo9zafc/mapcontacts/public/php_error.log');
}

// Set environment variables
putenv('PYTHONPATH=/home/ddiemeo9zafc/mapcontacts');
putenv('FLASK_APP=app.py');
putenv('FLASK_ENV=production');

// Function to check if a process is running
function is_process_running($pid) {
    if (!$pid) return false;
    return file_exists("/proc/$pid");
}

// Function to start the Flask application
function start_flask_app() {
    global $python_app, $pid_file, $log_file;
    
    // Kill any existing process
    if (file_exists($pid_file)) {
        $old_pid = file_get_contents($pid_file);
        if (is_process_running($old_pid)) {
            exec("kill $old_pid");
            sleep(1);
        }
        unlink($pid_file);
    }
    
    // Start the application with Gunicorn
    $command = "cd /home/ddiemeo9zafc/mapcontacts && nohup gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 120 --access-logfile $log_file --error-logfile $log_file app:app > $log_file 2>&1 & echo $! > $pid_file";
    exec($command);
    log_message("Started Flask application with command: $command");
    
    // Wait for the application to start
    $max_attempts = 10;
    $attempt = 0;
    while ($attempt < $max_attempts) {
        if (file_exists($pid_file)) {
            $pid = file_get_contents($pid_file);
            if (is_process_running($pid)) {
                // Check if the application is responding
                $ch = curl_init("http://127.0.0.1:8000/");
                curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($ch, CURLOPT_TIMEOUT, 2);
                $response = curl_exec($ch);
                $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                curl_close($ch);
                
                if ($http_code > 0) {
                    log_message("Flask application started successfully with PID: $pid");
                    return true;
                }
            }
        }
        sleep(1);
        $attempt++;
    }
    
    log_message("Failed to start Flask application after $max_attempts attempts");
    return false;
}

// Start or restart the Flask application if needed
if (!file_exists($pid_file) || !is_process_running(file_get_contents($pid_file))) {
    log_message("Flask application not running, starting it...");
    if (!start_flask_app()) {
        header('HTTP/1.1 500 Internal Server Error');
        echo "Failed to start the application. Please check the error logs.";
        exit;
    }
}

// Forward the request to the Python application
$ch = curl_init();
$url = "http://localhost:$port" . $_SERVER['REQUEST_URI'];
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);

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
    $error = curl_error($ch);
    log_message("Curl error: $error");
    
    // If connection failed, try restarting the Flask application
    if (strpos($error, 'Connection refused') !== false) {
        log_message("Connection refused, attempting to restart Flask application...");
        if (start_flask_app()) {
            // Retry the request
            $response = curl_exec($ch);
            $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
            $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        }
    }
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