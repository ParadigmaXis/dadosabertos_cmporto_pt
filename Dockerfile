FROM centos:7

ENV APP_NAME ckan
ENV APP_HOME /srv/app/$APP_NAME
ENV CKAN_CONFIG /etc/ckan
ENV CKAN_DB_USER ckan
ENV CKAN_DB_PASS 123456
ENV CKAN_DB_NAME ckan
ENV CONFIG_FILE ckan.ini
ENV STORE_PATH /srv/app/store

RUN yum -y update; \
    yum -y install epel-release; \
    yum -y install http://yum.postgresql.org/9.4/redhat/rhel-7-x86_64/pgdg-centos94-9.4-1.noarch.rpm; \
    yum -y install httpd python-virtualenv mod_wsgi git postgresql94 postgresql94-devel gcc; \
    yum clean all

# Should be $APP_NAME
ADD ./docker/apache/app.conf /etc/httpd/conf.d/
ADD ./docker/apache/app.wsgi $CKAN_CONFIG/

# Install requirements
RUN ln -s /usr/pgsql-9.4/bin/* /usr/local/bin/; \
    mkdir -p $APP_HOME; \
    virtualenv --no-site-packages $APP_HOME; \
    $APP_HOME/bin/pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.3#egg=ckan'; \
    $APP_HOME/bin/pip install -r $APP_HOME/src/ckan/requirements.txt; \
    $APP_HOME/bin/paster make-config ckan ${CKAN_CONFIG}/${CONFIG_FILE}; \
    $APP_HOME/bin/pip install ckanext-pdfview

# Set configurations
RUN mkdir -p $CKAN_CONFIG; \
    "$APP_HOME"/bin/paster --plugin=ckan config-tool "$CKAN_CONFIG/$CONFIG_FILE" -e \
      "ckan.site_url                                   = http://opendata.cm-porto.net" \
      "sqlalchemy.url                                  = postgresql://$CKAN_DB_USER:$CKAN_DB_PASS@db/$CKAN_DB_NAME" \
      "solr_url                                        = http://solr:8983/solr/ckan" \
      "ckan.auth.create_unowned_dataset                = false" \
      "ckan.auth.create_dataset_if_not_in_organization = false" \
      "ckan.auth.user_create_groups                    = false" \
      "ckan.auth.user_create_organizations             = false" \
      "ckan.auth.user_delete_groups                    = false" \
      "ckan.auth.user_delete_organizations             = false" \
      "ckan.plugins                                    = resource_proxy text_view image_view recline_view pdf_view stats" \
      "package_edit_return_url                         = /dataset/edit/<NAME>" \
      "ckan.locale_default                             = pt_PT" \
      "ckan.locale_order                               = pt_PT" \
      "ckan.locales_offered                            = pt_PT" \
      "ckan.locales_filtered_out                       = pt_PT" \
      "ckan.max_resource_size                          = 100" \
      "ckan.views.default_views                        = webpage_view pdf_view text_view image_view recline_view"; \
    "$APP_HOME"/bin/paster --plugin=ckan config-tool "$CKAN_CONFIG/$CONFIG_FILE" \
      "ckan.storage_path                               = $STORE_PATH" \
      "ckan.datasets_per_page                          = 1000" \
      "search.facets.default                           = 1000" \
      "search.facets.limit                             = 1000" \
      "guia.admin.verf_vocabs                          = false" \
      "guia.admin.verf_cats                            = false" \
      "ckan.search.show_all_types                      = true"; \
    ln -s $APP_HOME/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini
    
# Copy start script
COPY ./docker/ckan/start.bash /usr/local/bin/
RUN chmod +x /usr/local/bin/start.bash

# Copy apache start script
COPY ./docker/apache/httpd-foreground /usr/local/bin/
RUN chmod +x /usr/local/bin/httpd-foreground

# Port, command and Shared data
EXPOSE 80
CMD ["start.bash"]
