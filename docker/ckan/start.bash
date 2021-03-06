#!/bin/bash

source $(dirname "$0")/utils.bash

export PGPASSWORD=$POSTGRES_PASSWORD

# Wait for dependencies
wait_for_service db 5432
wait_for_service solr 8983 

# Check if database already exist or create a new one
count=$(psql -lqt -U postgres -h db | cut -d \| -f 1 | grep -w ckan | wc -l)

if [[ $count -eq 0 ]]; then
  echo 'Creating database...'
  createuser -h db -U postgres -S -D -R -w $CKAN_DB_USER
  createdb -h db -U postgres -O $CKAN_DB_USER $CKAN_DB_NAME -E utf-8 
  psql -h db -U postgres -c "ALTER ROLE $CKAN_DB_USER WITH ENCRYPTED PASSWORD '$CKAN_DB_PASS';"
fi

# Check if datastore database already exist or create a new one
count=$(psql -lqt -U postgres -h db | cut -d \| -f 1 | grep -w datastore | wc -l)

if [[ $count -eq 0 ]]; then
  echo 'Creating datastore database...'
  createuser -h db -U postgres -S -D -R -w $DATASTORE_DB_USER
  createdb -h db -U postgres -O $CKAN_DB_USER $DATASTORE_DB_NAME -E utf-8
  psql -h db -U postgres -c "ALTER ROLE $DATASTORE_DB_USER WITH ENCRYPTED PASSWORD '$DATASTORE_DB_PASS';"
fi

# Configure filestore
mkdir -p $STORE_PATH
chown apache $STORE_PATH
chmod u+rwx $STORE_PATH

# Add CKAN settings
if [ ! -f /srv/app/conf/app.ini ]; then
    cp -n "$APP_CONFIG_FILE" /srv/app/conf/
else
    cp -f /srv/app/conf/app.ini "$APP_CONFIG"
fi
"$APP_HOME"/bin/paster --plugin=ckan config-tool -f "$APP_CONFIG_FILE" "$CKAN_CONFIG/$CONFIG_FILE" -e
"$APP_HOME"/bin/paster --plugin=ckan config-tool "$CKAN_CONFIG/$CONFIG_FILE" -e sqlalchemy.url=postgresql://$CKAN_DB_USER:$CKAN_DB_PASS@db/$CKAN_DB_NAME
"$APP_HOME"/bin/paster --plugin=ckan config-tool "$CKAN_CONFIG/$CONFIG_FILE" -e ckan.datastore.write_url=postgresql://$CKAN_DB_USER:$CKAN_DB_PASS@db/$DATASTORE_DB_NAME
"$APP_HOME"/bin/paster --plugin=ckan config-tool "$CKAN_CONFIG/$CONFIG_FILE" -e ckan.datastore.read_url=postgresql://$DATASTORE_DB_USER:$DATASTORE_DB_PASS@db/$DATASTORE_DB_NAME

# Initialize db
"$APP_HOME"/bin/paster --plugin=ckan db init -c "${CKAN_CONFIG}/$CONFIG_FILE"

# Set permissions for datastore db
"$APP_HOME"/bin/paster --plugin=ckan datastore set-permissions -c "${CKAN_CONFIG}/$CONFIG_FILE" | psql -h db -U postgres --set ON_ERROR_STOP=1

# Release lock
rm -rf /root/start.lock

# Generate rewrites file for apache
if [ ! -f /srv/app/conf/rewrites.conf ]; then
    cp -n "$APACHE_REWRITES_FILE" /srv/app/conf/
else
    cp -f /srv/app/conf/rewrites.conf "$APP_CONFIG"
fi

# Start Apache
exec httpd-foreground
