source .env
sqlcmd -S $DB_HOST,$DB_PORT -U $DB_USERNAME -P $DB_PASSWORD -d $DB_NAME