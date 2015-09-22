from tomcat:8-jre7

RUN mkdir /tmp/geoserver ; cd /tmp/geoserver ; wget http://downloads.sourceforge.net/project/geoserver/GeoServer/2.7.2/geoserver-2.7.2-war.zip
RUN cd /tmp/geoserver ;  unzip geoserver-2.7.2-war.zip
RUN cd ${CATALINA_HOME}/webapps/ ; mkdir geoserver ; cd geoserver ; unzip /tmp/geoserver/geoserver.war * ; rm -rf /tmp/geoserver
RUN mkdir ${CATALINA_HOME}/webapps/geoserver/data/shapefiles
