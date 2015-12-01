#!/bin/bash

source /etc/envvars
source $(dirname "$0")/utils.bash

# Wait for dependencies
wait_for_lock /root/start.lock

"$APP_HOME"/bin/paster --plugin=ckan search-index rebuild -r -c "$CKAN_CONFIG/$CONFIG_FILE"
