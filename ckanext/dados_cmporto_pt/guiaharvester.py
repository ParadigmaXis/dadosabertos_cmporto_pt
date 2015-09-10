# -*- coding: utf-8 -*-
from ckan import model, new_authz, logic
from ckan.model import Session
from ckan.model.license import LicenseCreativeCommonsAttribution
from ckan.lib.helpers import json
from ckanext.harvest.harvesters import CKANHarvester
import utils

import logging
log = logging.getLogger(__name__)

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

    def import_stage(self, harvest_object):
        package_dict = json.loads(harvest_object.content)
        if not self._should_import_local(package_dict):
            package_dict['state'] = 'deleted'
        else:
            package_dict = self._apply_package_extras_white_list(package_dict)
            package_dict = self._apply_package_resource_extras_black_list(package_dict)
            package_dict = self._fix_date_in_fields(package_dict)
            package_dict = self._set_license(package_dict)
        harvest_object.content = json.dumps(package_dict)

        import_stage_result = super(GuiaHarvesterPlugin, self).import_stage(harvest_object)

        if import_stage_result:
            package_dict = json.loads(harvest_object.content)
            harvested_rels = package_dict.get('relationships', [])
            try:
                this_package = model.Package.get(package_dict['name'])
                if not this_package: raise logic.NotFound
            except logic.NotFound as nf:
                log.info('import_stage(): relationships not replaced; could not find package {0}: {1}'.format(package_dict['name'], nf))
                return import_stage_result

            existing_rels = this_package.get_relationships()
            log.info('import_stage() : this package: {0}'.format(this_package))
            self._replace_relationships(existing_rels, harvested_rels)
        return import_stage_result

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

    def _set_license(self, package_dict):
        lic = LicenseCreativeCommonsAttribution()
        package_dict['license_id'] = lic.id
        return package_dict

    def _replace_relationships(self, existing_rels, havested_rels):
        _ctx = {'model': model, 'session': Session, 'user': self._get_user_name()}
        try:
            log.info('import_stage() : existing relationships: {0}'.format(existing_rels))
            for _existing in existing_rels:
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

        for _rel in havested_rels:
            try:
                _can_create = new_authz.is_authorized('package_relationship_create', _ctx, _rel)
                if _can_create['success']:
                    ## TODO: should use toolkit.get_action(...)
                    # _r_dicts = toolkit.get_action('package_relationship_create')(_ctx, _rel)
                    _r_dicts = logic.action.create.package_relationship_create(_ctx, _rel)
                    log.info('import_stage() .  created relationship : {0}'.format(_r_dicts))
            except logic.NotFound as nf:
                log.info('import_stage().relationship : not found package: {0}'.format(nf))
            except logic.ValidationError as ve:
                log.info('import_stage().relationship : validation error : {0}'.format(ve))


