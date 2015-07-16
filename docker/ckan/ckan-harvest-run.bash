#!/bin/bash

source /etc/envvars
source $(dirname "$0")/utils.bash

# Wait for dependencies
wait_for_service db 5432
wait_for_service solr 8983 

"$APP_HOME"/bin/paster --plugin=ckanext-harvest harvester run -c "$CKAN_CONFIG/$CONFIG_FILE"
