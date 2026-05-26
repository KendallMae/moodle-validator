#!/bin/bash
set -e

MOODLE_DIR="/var/www/moodle"
MOODLE_DATA="/var/www/moodledata"
LOCK_FILE="$MOODLE_DATA/.installed"

# Wait for the database to be fully ready
echo "Waiting for database..."
until php -r "new PDO('mysql:host=db;dbname=moodle', 'moodleuser', 'moodlepass');" 2>/dev/null; do
    sleep 2
done
echo "Database is ready."

# Always generate config.php (it lives in the container layer and gets lost on restart)
echo "Writing config.php..."
cat > "$MOODLE_DIR/config.php" <<'PHPEOF'
<?php
unset($CFG);
global $CFG;
$CFG = new stdClass();

$CFG->dbtype    = 'mariadb';
$CFG->dbhost    = 'db';
$CFG->dbname    = 'moodle';
$CFG->dbuser    = 'moodleuser';
$CFG->dbpass    = 'moodlepass';
$CFG->prefix    = 'mdl_';
$CFG->dboptions = ['dbcollation' => 'utf8mb4_unicode_ci'];

$CFG->wwwroot   = 'http://localhost:8080';
$CFG->dataroot  = '/var/www/moodledata';
$CFG->admin     = 'admin';

$CFG->directorypermissions = 0777;

require_once(__DIR__ . '/lib/setup.php');
PHPEOF

# Run the Moodle CLI installer if not already installed
if [ ! -f "$LOCK_FILE" ]; then
    echo "Running Moodle install..."
    php "$MOODLE_DIR/admin/cli/install_database.php" \
        --agree-license \
        --adminuser=user \
        --adminpass="AdminPass123!" \
        --adminemail="admin@example.com" \
        --fullname="New Site" \
        --shortname="moodle"

    touch "$LOCK_FILE"
    echo "Moodle install complete."
else
    echo "Moodle already installed, skipping database setup."
fi

# Ensure correct permissions for Apache (www-data)
chown -R www-data:www-data "$MOODLE_DATA"
chown www-data:www-data "$MOODLE_DIR/config.php"

# Start Apache in the foreground
echo "Starting Apache..."
exec apache2-foreground
