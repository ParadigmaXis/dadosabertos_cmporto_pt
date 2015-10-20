# -*- coding: utf-8 -*-

from ckan import plugins
from ckan.plugins import toolkit
from ckan.lib import helpers
from ckan.common import g
import json
import utils

from geoserver_integration import upload_shapefile_resource

import logging
log = logging.getLogger(__name__)


class CMPortoPlugin(plugins.SingletonPlugin):
    '''Theme for the dados.cmporto.pt portal
    '''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public', 'dados_cmporto_pt')
        

    # IRoutes

    def before_map(self, map):
        """This IRoutes implementation overrides the standard
        ``/ckan-admin/config`` behaviour with a custom controller.
        """
        map.connect('/ckan-admin/config', controller='ckanext.dados_cmporto_pt.controller:AdminController', action='config')
        map.connect('/terms-of-use', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='terms_of_use')
        map.connect('/privacy-policy', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='privacy_policy')
        map.connect('/moderation-policy', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='moderation_policy')
        map.connect('/license', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='list_license')
        map.connect('linked_data', '/linked-data', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='linked_data')
        return map

    # IConfigurable

    def configure(self, config):
        self.is_dcat_plugin_active = 'dcat' in config.get('ckan.plugins', '')


    #ITemplateHelpers

    def get_helpers(self):
        return {
            'is_dcat_plugin_active' : lambda: self.is_dcat_plugin_active,
            'format_non_duplicate_resource_items' : format_non_duplicate_resource_items,
            'sorted_guia_extras' : sorted_guia_extras,
        }


def format_non_duplicate_resource_items(resource_dict, extra_black_list=None):
    if not resource_dict: return []
    res_dict = resource_dict.copy()
    # From resource_read.html:
    used_fields = ['last_modified', 'revision_timestamp', 'created', 'mimetype_inner', 'mimetype', 'format']
    black_list = [ f for f in used_fields if f in res_dict.keys() and res_dict.get(f) ]
    black_list.append('input_Diag_Store_OK_MSG')

    if extra_black_list:
        black_list.extend(extra_black_list)

    for f in black_list:
        if f in res_dict.keys(): del res_dict[f]
    return helpers.format_resource_items(res_dict.items())


def sorted_guia_extras(package_extras):
    ''' Used for outputting package extras

    :param package_extras: the package extras
    :type package_extras: dict
    '''

    guia_extras = utils.get_ordered_package_extras()

    def guia_sort_key(value):
        try:
            return guia_extras.index(value)
        except ValueError:
            return len(guia_extras)+1

    def to_value(key, value):
        if key in ['h_manutencao_recurso', 'h_idioma', 'h_tipo_representacao_espacial', 'h_extensao_geografica']:
            parsed = json.loads(value)
            value = ", ".join(map(unicode, parsed))
        if key == 'consulta_online':
            parsed = json.loads(value)
            value = parsed
            return (key, value, 'package/snippets/read_table_consulta_online.html')
        if key == 'resolucao_espacial':
            parsed = json.loads(value)
            value = parsed
            return (key, value, 'package/snippets/read_table_resolucao_espacial.html')
        return (key, value, None)

    exclude = g.package_hide_extras
    output = []
    for extra in sorted(package_extras, key=lambda x: guia_sort_key(x['key'])):
        if extra.get('state') == 'deleted':
            continue
        k, v = extra['key'], extra['value']
        if k in exclude:
            continue
        if isinstance(v, (list, tuple)):
            v = ", ".join(map(unicode, v))
        output.append(to_value(k, v))
    return output

class ShapefilePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IConfigurable, inherit=True)

    def get_resource_storage_path(self, resource_id):
        return '{0}/resources/{1}/{2}/{3}'.format(self.storage_path, resource_id[0:3], resource_id[3:6], resource_id[6:])

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
        self.storage_path = config.get('ckan.storage_path', None)
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
