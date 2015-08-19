# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.harvest.harvesters import CKANHarvester

from ckan.lib.helpers import json

from ckan import model
from ckan.model import PackageRelationship, Session
import ckan.logic as logic

import ckan.new_authz as new_authz

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

    def import_stage(self, harvest_object):
        #log.info('import_stage().harvest_object.content : {0}'.format(harvest_object.content) )
        _super_import = super(GuiaHarvesterPlugin, self).import_stage(harvest_object)
        
        if _super_import:
            _ctx = {'model': model, 'session': Session, 'user': self._get_user_name()}
            package_dict = json.loads(harvest_object.content)
            _havested_rels = package_dict.get('relationships', [])
            
            try:
                this_package = model.Package.get(package_dict['name'])
                log.info('import_stage() : this package: {0}'.format(this_package))
                _existing_rels = this_package.get_relationships()
                log.info('import_stage() : existing relationships: {0}'.format(_existing_rels))
                for _existing in _existing_rels:
                    try:
                        ## TODO: should use toolkit.get_action(...)
                        logic.action.delete.package_relationship_delete(_ctx, _existing.as_dict())
                        log.info('import_stage() .  deleted relationship : {0}'.format(_existing.as_dict()))
                    except Exception as e:
                        log.info('import_stage().relationship : could not delete: {0}'.format(e))
            
            except logic.NotFound as nf:
                # The package was not created:
                log.info('import_stage().relationship : could not find package: {0}'.format(nf))
            except Exception as e: 
                log.info('import_stage().relationship : exception {0}'.format(e))
                   
            # Debug only:
            _fwd_types = PackageRelationship.get_forward_types()
            
            for _rel in _havested_rels:
                # Debug only:
                if _rel['type'] in _fwd_types:
                    log.debug('import_stage() . relationship : {0}'.format(_rel))
                    _subj = _rel['subject']
                    log.debug('import_stage() . relationship.SUBJECT : {0}'.format(_subj))
                    _type = _rel['type']
                    log.debug('import_stage() . relationship.TYPE : {0}'.format(_type))
                    _obj = _rel['object']
                    log.debug('import_stage() . relationship.OBJECT : {0}'.format(_obj))
                    _comment = _rel['comment']
                    log.debug('import_stage() . relationship.COMMENT : {0}'.format(_comment))
                try:
                    _can_create = new_authz.is_authorized('package_relationship_create', _ctx, _rel)
                    if _can_create['success']:
                        ## TODO: should use toolkit.get_action(...)
                        #_r_dicts = toolkit.get_action('package_relationship_create')(_ctx, _rel)
                        _r_dicts = logic.action.create.package_relationship_create(_ctx, _rel)
                        log.info('import_stage() .  created relationship : {0}'.format(_r_dicts))
                except logic.NotFound as nf:
                    log.info('import_stage().relationship : not found package: {0}'.format(nf))
                except logic.ValidationError as ve:
                    log.info('import_stage().relationship : validation error : {0}'.format(ve))
                    
        return _super_import
    
        