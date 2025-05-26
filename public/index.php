<?php
// Enable error logging
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Set up logging
$log_file = __DIR__ . '/php_error.log';
function log_message($message) {
    global $log_file;
    $timestamp = date('Y-m-d H:i:s');
    file_put_contents($log_file, "[$timestamp] $message\n", FILE_APPEND);
}

// Set up environment
$app_dir = '/home/ddiemeo9zafc/mapcontacts';
$port = 8000;
$pid_file = $app_dir . '/app.pid';
$app_log = __DIR__ . '/app.log';
$gunicorn_path = '/home/ddiemeo9zafc/.local/bin/gunicorn';

// Function to check if a process is running
function is_process_running($pid) {
    if (!$pid) return false;
    return file_exists("/proc/$pid");
}

// Function to check if Gunicorn is available
function check_gunicorn() {
    global $gunicorn_path;
    if (file_exists($gunicorn_path)) {
        exec("$gunicorn_path --version", $version);
        log_message("Gunicorn found: " . implode("\n", $version));
        return true;
    }
    log_message("Gunicorn not found at $gunicorn_path");
    return false;
}

// Function to start the Flask application
function start_flask_app() {
    global $app_dir, $pid_file, $app_log;
    
    // Check if Gunicorn is available
    if (!check_gunicorn()) {
        log_message("Cannot start Flask application: Gunicorn not found");
        return false;
    }
    
    // Make sure the start script is executable
    $start_script = __DIR__ . '/start_app.sh';
    chmod($start_script, 0755);
    
    // Start the application
    $command = "nohup $start_script > $app_log 2>&1 & echo $! > $pid_file";
    log_message("Started Flask application with command: $command");
    
    exec($command, $output, $return_var);
    log_message("Command output: " . implode("\n", $output));
    log_message("Return value: $return_var");
    
    if ($return_var !== 0) {
        log_message("Failed to start Flask application");
        return false;
    }
    
    // Wait for the application to start
    $max_attempts = 10;
    $attempt = 0;
    $started = false;
    
    while ($attempt < $max_attempts) {
        $pid = file_exists($pid_file) ? file_get_contents($pid_file) : null;
        log_message("Checking process with PID: $pid");
        
        if ($pid && is_process_running($pid)) {
            // Check if the application is responding
            $ch = curl_init("http://127.0.0.1:$port/");
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, 2);
            $response = curl_exec($ch);
            $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            if ($http_code > 0) {
                $started = true;
                break;
            }
        }
        
        log_message("Process $pid is not running or not responding");
        if (file_exists($app_log)) {
            log_message("Application log contents after crash:");
            log_message(file_get_contents($app_log));
        }
        
        $attempt++;
        sleep(1);
    }
    
    if (!$started) {
        log_message("Failed to start Flask application after $max_attempts attempts");
        if (file_exists($app_log)) {
            log_message("Application log contents:");
            log_message(file_get_contents($app_log));
        }
        return false;
    }
    
    return true;
}

// Check if the application is running
$pid = file_exists($pid_file) ? file_get_contents($pid_file) : null;
if (!$pid || !is_process_running($pid)) {
    log_message("Flask application not running, starting it...");
    if (!start_flask_app()) {
        header("HTTP/1.1 500 Internal Server Error");
        echo "Failed to start the application. Please check the logs for details.";
        exit;
    }
}

// Forward the request to the Flask application
$ch = curl_init();
$url = "http://127.0.0.1:$port" . $_SERVER['REQUEST_URI'];
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

// Forward the request method
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']);

// Forward headers
$headers = [];
foreach (getallheaders() as $name => $value) {
    if (strtolower($name) !== 'host') {
        $headers[] = "$name: $value";
    }
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

// Forward request body
if ($_SERVER['REQUEST_METHOD'] === 'POST' || $_SERVER['REQUEST_METHOD'] === 'PUT') {
    $input = file_get_contents('php://input');
    curl_setopt($ch, CURLOPT_POSTFIELDS, $input);
}

// Execute the request
$response = curl_exec($ch);
$header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if ($response === false) {
    log_message("Curl error: " . curl_error($ch));
    header("HTTP/1.1 500 Internal Server Error");
    echo "Failed to forward request to the application.";
    exit;
}

// Forward the response
$headers = substr($response, 0, $header_size);
$body = substr($response, $header_size);

// Parse and forward headers
$header_lines = explode("\n", $headers);
foreach ($header_lines as $line) {
    if (trim($line) !== '') {
        header($line);
    }
}

// Set the response code
http_response_code($http_code);

// Output the response body
echo $body;

curl_close($ch);
?> 