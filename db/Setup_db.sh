#!/bin/bash

DB_USER="root"
DB_HOST="51.75.25.241"
DB_NAME="TicketsSupport"


mysql -u $DB_USER -p -h $DB_HOST -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME;"


mysql -u $DB_USER -p -h $DB_HOST $DB_NAME < ~/Desktop/Projet/AppTicket/db/init.sql


mysql -u $DB_USER -p -h $DB_HOST $DB_NAME < ~/Desktop/Projet/AppTicket/db/insert_test.sql

echo "Base de données setup avec Succès"
