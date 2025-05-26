<?php
echo "<h1>Apache Configuration Check</h1>";

// Check if mod_wsgi is loaded
echo "<h2>Loaded Apache Modules:</h2>";
echo "<pre>";
print_r(apache_get_modules());
echo "</pre>";

// Check PHP version
echo "<h2>PHP Version:</h2>";
echo phpversion();

// Check server software
echo "<h2>Server Software:</h2>";
echo $_SERVER['SERVER_SOFTWARE'];

// Check document root
echo "<h2>Document Root:</h2>";
echo $_SERVER['DOCUMENT_ROOT'];
?> 