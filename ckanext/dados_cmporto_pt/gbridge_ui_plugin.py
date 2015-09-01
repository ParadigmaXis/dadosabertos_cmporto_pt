# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize
from ckan.common import g
import json

from pylons import c

import logging
log = logging.getLogger(__name__)

class GBridgeUIPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.ITemplateHelpers)
    
    def get_helpers(self):
        return {'get_relationships_as_Subj_dependsOn_Obj' : get_relationships_as_Subj_dependsOn_Obj,
                'get_relationships_as_Obj_isDependencyOf_Subj' : get_relationships_as_Obj_isDependencyOf_Subj,
                'get_relationships_as_Subj_derives_from_Obj' : get_relationships_as_Subj_derives_from_Obj,
                'get_relationships_as_Obj_has_derivation_Subj' : get_relationships_as_Obj_has_derivation_Subj,
                'sorted_guia_extras' : sorted_guia_extras,
        }


def get_relationships_as_Subj_dependsOn_Obj(pkg_id):
    try:
        package = model.Package.get(pkg_id)
        forward_rels = package.get_relationships(direction='forward', active=True)
        list_forward = [_rel.object.id for _rel in forward_rels if _rel.type == u'depends_on']
        return _get_relationships_Packages(list_forward)
    except Exception as e:
        log.warn('get_relationships_as_Subj_dependsOn_Obj() : exception {0}'.format(e))
        return[]
        
def get_relationships_as_Obj_isDependencyOf_Subj(pkg_id):
    try:
        package = model.Package.get(pkg_id)
        rev_rels = package.get_relationships(direction='reverse', active=True)
        list_rev = [_rel.subject.id for _rel in rev_rels if _rel.type == u'depends_on']
        return _get_relationships_Packages(list_rev)
    except Exception as e:
        log.warn('get_relationships_as_Obj_isDependencyOf_Subj() : exception {0}'.format(e))
        return[]


def get_relationships_as_Subj_derives_from_Obj(pkg_id):
    try:
        package = model.Package.get(pkg_id)
        forward_rels = package.get_relationships(direction='forward', active=True)
        list_forward = [_r.object.id for _r in forward_rels if _r.type == u'derives_from']
        return _get_relationships_Packages(list_forward)
    except Exception as e:
        log.warn('get_relationships_as_Subj_derives_from_Obj() : exception {0}'.format(e))
        return[]

def get_relationships_as_Obj_has_derivation_Subj(pkg_id):
    try:
        package = model.Package.get(pkg_id)        
        rev_rels = package.get_relationships(direction='reverse', active=True)
        list_rev = [_r.subject.id for _r in rev_rels if _r.type == u'derives_from']
        return _get_relationships_Packages(list_rev)
    except Exception as e:
        log.warn('get_relationships_as_Subj_derives_from_Obj() : exception {0}'.format(e))
        return[]


def _get_relationships_Packages(pkg_ids):
    query = model.Session.query(model.Package)\
            .filter(model.Package.id.in_(pkg_ids))\
            .filter(model.Package.state == u'active')
    pkg_list = query.all()
    ret = []
    context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    for pkg in pkg_list:
        # Filtrar os packages privados sem acesso de edicao:
        if (not pkg.private): ret.append(model_dictize.package_dictize(pkg,context))
        else:
            if new_authz.is_authorized_boolean('package_update', context, { 'id' : pkg.id}):
                ret.append(model_dictize.package_dictize(pkg,context))
    return ret

def sorted_guia_extras(package_extras):
    ''' Used for outputting package extras

    :param package_extras: the package extras
    :type package_extras: dict
    '''

    guia_extras = [
        'objectivo',
        'h_manutencao_recurso',
        'consulta_online',
        'h_idioma',
        'codificacao_caracteres',
        'dataset_data_criacao',
        'dataset_data_atualizacao',
        'vigencia_inicio',
        'anotacoes',
        'responsavel_produtor_und_organica',
        'responsavel_produtor_nome',
        'responsavel_produtor_email',
        'responsavel_produtor_telefone',
        'georreferenciado',
        'h_tipo_representacao_espacial',
        'resolucao_espacial',
        'sistema_referencia',
        'h_extensao_geografica',
        'totalidade_area',
        'metameta_norma',
    ]

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