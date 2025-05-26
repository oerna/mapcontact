<?php
// Set the path to the Python application
$python_app = '/home/ddiemeo9zafc/mapcontacts/app.py';

// Set environment variables
putenv('PYTHONPATH=/home/ddiemeo9zafc/mapcontacts');
putenv('FLASK_APP=app.py');
putenv('FLASK_ENV=production');

// Get the request method and URI
$method = $_SERVER['REQUEST_METHOD'];
$uri = $_SERVER['REQUEST_URI'];

// Forward the request to the Python application
$command = "python3 $python_app";
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin
   1 => array("pipe", "w"),  // stdout
   2 => array("pipe", "w")   // stderr
);

$process = proc_open($command, $descriptorspec, $pipes);

if (is_resource($process)) {
    // Write the request to stdin
    fwrite($pipes[0], json_encode([
        'method' => $method,
        'uri' => $uri,
        'headers' => getallheaders(),
        'body' => file_get_contents('php://input')
    ]));
    fclose($pipes[0]);

    // Read the response
    $output = stream_get_contents($pipes[1]);
    $errors = stream_get_contents($pipes[2]);

    // Close pipes
    fclose($pipes[1]);
    fclose($pipes[2]);

    // Close process
    $return_value = proc_close($process);

    if ($return_value === 0) {
        // Parse the response
        $response = json_decode($output, true);
        if ($response) {
            // Set headers
            foreach ($response['headers'] as $header) {
                header($header);
            }
            // Output the body
            echo $response['body'];
        } else {
            // If response is not JSON, output as is
            echo $output;
        }
    } else {
        // Handle error
        header('HTTP/1.1 500 Internal Server Error');
        echo "Error executing Python application: $errors";
    }
} else {
    header('HTTP/1.1 500 Internal Server Error');
    echo "Could not execute Python application";
}
?> 