# -*- coding: utf-8 -*-

from ckan import plugins
from ckan.plugins import toolkit
from ckan.lib import helpers
from ckan.common import g
import json
import utils

import logging
log = logging.getLogger(__name__)


class CMPortoPlugin(plugins.SingletonPlugin):
    '''Theme for the dados.cmporto.pt portal
    '''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IPackageController, inherit=True)

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
        map.connect('data_cubes', '/data-cubes', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='data_cubes')
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
            'group_list_all_fields' : lambda: toolkit.get_action('group_list')(data_dict = {'all_fields' : True}),
        }

    # IPackageController
    def before_search(self, search_params):
        # Este query parser aceita pesquisa com wildcards:
        search_params['defType'] = 'edismax'
        return search_params

def format_non_duplicate_resource_items(resource_dict, extra_black_list=None):
    if not resource_dict: return []
    res_dict = resource_dict.copy()
    # From resource_read.html:
    used_fields = ['last_modified', 'revision_timestamp', 'created', 'mimetype_inner', 'mimetype', 'format']
    black_list = [ f for f in used_fields if f in res_dict.keys() and res_dict.get(f) ]
    black_list.append('input_Diag_Store_OK_MSG')

    if extra_black_list: black_list.extend(extra_black_list)

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
        try: return guia_extras.index(value)
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
