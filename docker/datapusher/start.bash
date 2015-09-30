#!/bin/bash

source $(dirname "$0")/utils.bash

# Wait for dependencies
wait_for_service ckan 80

python datapusher/main.py deployment/datapusher_settings.py