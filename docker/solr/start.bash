#!/bin/bash

if [ ! "$(ls -A $SOLR_HOME/ckan/)" ]; then
  cp -R $SOLR_HOME/collection1/* $SOLR_HOME/ckan/
  echo name=ckan > $SOLR_HOME/ckan/core.properties
  curl -L -o $SOLR_HOME/ckan/conf/schema.xml https://github.com/ckan/ckan/raw/ckan-$CKAN_VERSION/ckan/config/solr/schema.xml
fi

cd $SOLR_HOME/../
java -jar start.jar
