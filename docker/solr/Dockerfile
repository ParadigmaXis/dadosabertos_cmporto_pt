FROM centos:7

# Update and install dependencies
RUN yum -y update
RUN yum -y install java tar

# Install Solr
ENV SOLR_HOME /opt/solr/example/solr
ENV SOLR_VERSION 4.10.2
ENV SOLR solr-$SOLR_VERSION
ENV CKAN_VERSION 2.3

RUN mkdir -p /opt/solr
ADD http://archive.apache.org/dist/lucene/solr/$SOLR_VERSION/$SOLR.tgz /opt/$SOLR.tgz
RUN tar zxf /opt/$SOLR.tgz -C /opt/solr --strip-components 1

# Install CKAN Solr core
ADD ./start.bash /usr/local/bin/
RUN chmod +x /usr/local/bin/start.bash

# Startup configurations
EXPOSE 8983
WORKDIR /opt/solr/example
CMD ["start.bash"]
