# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.harvest.harvesters import CKANHarvester

from ckan.lib.helpers import json

from ckan import model
from ckan.model import PackageRelationship, Session
import ckan.logic as logic

import ckan.new_authz as new_authz
import utils
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
        return True

    def _should_import_local(self, package_dict):
        if package_dict.get('type', '') == u'app': 
            return False 
        extras = package_dict.get('extras', {})
        is_public_package = extras.get('fornecimento_externo', '') == u'Não'
        if not is_public_package:
            log.warn('Remote dataset is not published ({0}), not importing...'.format(package_dict.get('id', '')))
            return False
        return True

    def _apply_package_extras_white_list(self, package_dict):
        EXTRAS = 'extras'
        extras = package_dict.get(EXTRAS, {})
        white_list = utils.get_white_listed_package_extras()
        clean_extras = {}
        for k, v in extras.iteritems():
            if k in white_list:
                clean_extras[k] = v
            else:
                log.info('package.extras: blacklisted field {0} discarded'.format(k))
        package_dict[EXTRAS] = clean_extras
        #log.debug('==package.extras==\nBEFORE{0}\n====\nAFTER{1}\n==end=='.format(json.dumps(extras), json.dumps(clean_extras)))
        return package_dict

    def _apply_package_resource_extras_black_list(self, package_dict):
        RESOURCES = 'resources'
        resources = package_dict.get(RESOURCES, [])
        black_list = utils.get_black_listed_package_resource_extras()
        clean_resources = []
        for resource in resources:
            clean_resource = {}
            for k, v in resource.iteritems():
                if k not in black_list:
                    clean_resource[k] = v
                else:
                    log.info('package.resources: blacklisted field {0} discarded'.format(k))
            clean_resources.append(clean_resource)
        package_dict[RESOURCES] = clean_resources
        #log.debug('==package.resources==\nBEFORE{0}\n====\nAFTER{1}\n==end=='.format(json.dumps(resources), json.dumps(clean_resources)))
        return package_dict

    def _fix_date_in_fields(self, package_dict):
        """
        This method appends a white space to avoid recognition of year as integer, that will be formatted as '#,###'.
        """
        RESOURCES = 'resources'
        resources = package_dict.get(RESOURCES, [])
        fields = ['data_actualizacao', 'data_criacao', 'data_referencia_final', 'data_referencia_inicial']
        def is_number(value):
            import re
            # regex copied from ckan/lib/helpers.py, function format_resource_items(items)
            reg_ex_int = '^-?\d{1,}$'
            return re.search(reg_ex_int, value) != None

        for resource in resources:
            for field in fields:
                value = resource.get(field, '')
                if field in resource and is_number(value):
                    resource[field] = '{0} '.format(value)
        return package_dict

    def import_stage(self, harvest_object):
        #log.info('import_stage().harvest_object.content : {0}'.format(harvest_object.content) )

        package_dict = json.loads(harvest_object.content)
        if not self._should_import_local(package_dict):
            package_dict['state'] = 'deleted'
        else:
            package_dict = self._apply_package_extras_white_list(package_dict)
            package_dict = self._apply_package_resource_extras_black_list(package_dict)
            package_dict = self._fix_date_in_fields(package_dict)
            harvest_object.content = json.dumps(package_dict)

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
    
        
