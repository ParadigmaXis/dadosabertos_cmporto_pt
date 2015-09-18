# -*- coding: utf-8 -*-

from ckan import plugins
from ckan.plugins import toolkit
from ckan.lib import helpers

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
        }


def format_non_duplicate_resource_items(resource_dict):
    if not resource_dict: return []
    res_dict = resource_dict.copy()
    # From resource_read.html:
    used_fields = ['last_modified', 'revision_timestamp', 'created', 'mimetype_inner', 'mimetype', 'format']
    black_list = [ f for f in used_fields if f in res_dict.keys() and res_dict.get(f) ]

    black_list += ['id', 'resource_type', 'package_id', 'state', 'revision_id', 'position']

    for f in black_list:
        if f in res_dict.keys(): del res_dict[f]
    return helpers.format_resource_items(res_dict.items())

