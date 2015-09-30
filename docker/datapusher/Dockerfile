FROM centos:7

RUN yum -y update; \
    yum -y install epel-release; \
    yum -y install python-pip git gcc libffi-devel openssl-devel python-devel libxslt-devel libxml2-devel; \
    yum clean all

ENV DATAPUSHER_HOME /usr/lib/ckan/datapusher

#create a source directory and switch to it
RUN mkdir -p $DATAPUSHER_HOME/src; \
    cd $DATAPUSHER_HOME/src; \
    git clone https://github.com/ckan/datapusher.git; \
    cd datapusher; \
    git checkout 847f4bb; \
    pip install requests[security]; \
    pip install -r requirements.txt; \
    python setup.py develop

WORKDIR $DATAPUSHER_HOME/src/datapusher/
EXPOSE 8800

CMD ["start.bash"]
