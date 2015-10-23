# -*- coding: utf-8 -*-

from ckan.lib.uploader import get_storage_path
from ckan import plugins
from ckan.plugins import toolkit
from ckan.lib import helpers
from ckan.common import g
import json
from os.path import join
from geoserver_integration import upload_shapefile_resource

import logging
log = logging.getLogger(__name__)

class ShapefilePlugin(plugins.SingletonPlugin):
    """
    This class requires the following redirect on the apache virtual server for ckan:
    RewriteRule ^/dataset/[^/]*/resource/([^/]*)/wms$ http://${OPENDATA_GEOSERVER_1_PORT_8080_TCP_ADDR}:${OPENDATA_GEOSERVER_1_PORT_8080_TCP_PORT}/geoserver/shp-$1/wms [P]
    """
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IConfigurable, inherit=True)

    def get_resource_storage_path(self, resource_id):
        return join(self.storage_path, 'resources', resource_id[0:3], resource_id[3:6], resource_id[6:])

    def before_create(self, context, resource):
        pass
    def after_create(self, context, resource):
        try:
            if self.can_view_resource(resource):
                resource_id = resource['id']
                upload_shapefile_resource(self.geoserver_url, self.geoserver_user, self.geoserver_password, resource_id, self.get_resource_storage_path(resource_id))
        except Exception as e:
            log.exception(e)
    def before_update(self, context, current, resource):
        pass
    def after_update(self, context, resource):
        try:
            if self.can_view_resource(resource):
                resource_id = resource['id']
                upload_shapefile_resource(self.geoserver_url, self.geoserver_user, self.geoserver_password, resource_id, self.get_resource_storage_path(resource_id))
        except Exception as e:
            log.exception(e)
    def before_delete(self, context, resource, resources):
        pass
    def after_delete(self, context, resources):
        pass
    def before_show(self, resource):
        pass

    def configure(self, config):
        self.gapi_key = config.get('ckanext.geoview.gapi_key', None)
        self.storage_path = get_storage_path()
        self.geoserver_url = config.get('dadosabertos.geoserver.url', None)
        self.geoserver_user = config.get('dadosabertos.geoserver.user', None)
        self.geoserver_password = config.get('dadosabertos.geoserver.password', None)

    def info(self):
        return {'name': 'shapefile_view',
                'title': plugins.toolkit._('Shapefile Viewer (GeoStore)'),
                'icon': 'globe',
                'iframed': True,
                'default_title': plugins.toolkit._('Shapefile Viewer (GeoStore)')
                }

    def can_view(self, data_dict):
        resource = data_dict.get('resource', None)
        return self.can_view_resource(resource)

    def can_view_resource(self, resource):
        if resource:
            url_type = resource.get('url_type', '')
            format_lower = resource.get('format', '').lower()
            if url_type == 'upload' and format_lower == 'shp':
                return True
        return False

    def view_template(self, context, data_dict):
        return 'dataviewer/openlayers2.html'

    def _get_wms_url(self, resource):
        return '/dataset/{0}/resource/{1}/wms'.format(resource.get('package_id', None), resource.get('id', None))

    def setup_template_variables(self, context, data_dict):
        resource = data_dict.get('resource', None)
        resource['original_format'] = resource.get('format', None)
        resource['format'] = 'wms'
        resource['original_url'] = resource.get('url', None)
        resource['url'] = self._get_wms_url(resource)
        return {'proxy_service_url': self._get_wms_url(resource),
            'proxy_url': self._get_wms_url(resource),
            'gapi_key': self.gapi_key}
