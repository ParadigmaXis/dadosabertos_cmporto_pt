#!/bin/bash

source $(dirname "$0")/utils.bash

# Wait for dependencies
wait_for_service db 5432

"$APP_HOME"/bin/paster --plugin=ckanext-harvest harvester gather_consumer -c "$CKAN_CONFIG/$CONFIG_FILE"
