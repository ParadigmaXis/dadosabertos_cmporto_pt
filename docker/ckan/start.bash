#!/bin/bash

export PGPASSWORD=$DB_ENV_POSTGRES_PASSWORD

function wait_for_service {
  while : ; do
    exec 6<>/dev/tcp/$1/$2
    if [[ $? -eq 0 ]]; then
      break
    fi
    sleep 1
  done

  exec 6>&- # close output connection
  exec 6<&- # close input connection
}

# Wait for dependencies
wait_for_service db 5432
wait_for_service solr 8983 

# Check if database already exist or create a new one
count=$(psql -lqt -U postgres -h db | cut -d \| -f 1 | grep -w ckan | wc -l)

if [[ $count -eq 0 ]]; then
  echo 'Creating database...'
  createuser -h db -U postgres -S -D -R -w $CKAN_DB_USER
  createdb -h db -U postgres -O $CKAN_DB_USER $CKAN_DB_NAME -E utf-8 
  psql -h db -U postgres -c "ALTER ROLE $CKAN_DB_USER WITH ENCRYPTED PASSWORD '123456';"
fi

# Configure filestore
mkdir -p $STORE_PATH
chown apache $STORE_PATH
chmod u+rwx $STORE_PATH

# Initialize db
"$APP_HOME"/bin/paster --plugin=ckan db init -c "${CKAN_CONFIG}/ckan.ini"

exec httpd-foreground
