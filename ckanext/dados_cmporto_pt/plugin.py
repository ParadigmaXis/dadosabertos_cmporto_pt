# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.harvest.harvesters import CKANHarvester

import logging
log = logging.getLogger(__name__)


class CMPortoPlugin(plugins.SingletonPlugin):
    '''Theme for the dados.cmporto.pt portal
    '''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dados_cmporto_pt')

    # IRoutes

    def before_map(self, map):
        """This IRoutes implementation overrides the standard
        ``/ckan-admin/config`` behaviour with a custom controller.
        """
        map.connect('/ckan-admin/config', controller='ckanext.dados_cmporto_pt.controller:AdminController', action='config')
        map.connect('/terms-of-use', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='terms_of_use')
        map.connect('/privacy-policy', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='privacy_policy')
        map.connect('/moderation-policy', controller='ckanext.dados_cmporto_pt.controller:StaticPagesController', action='moderation_policy')
        return map

class GuiaHarvesterPlugin(CKANHarvester):
    '''Harvester for CMPorto's GUIA
    '''
    def info(self):
        return {
            'name': 'guia',
            'title': 'GUIA',
            'description': 'Harvests remote GUIA CKAN instances',
            'form_config_interface':'Text'
        }

    def _should_import(self,package_dict):
        extras = package_dict.get('extras', [])
        is_public_package = extras.get('fornecimento_externo', '') == u'Não'
        if not is_public_package:
            log.warn('Remote dataset is not published ({0}), not importing...'.format(package_dict.get('id', '')))
            return False
        return True
