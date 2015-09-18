# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.model as model
import ckan.new_authz as new_authz
import ckan.lib.dictization.model_dictize as model_dictize

from pylons import c

import logging
log = logging.getLogger(__name__)

class RelationshipsPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.ITemplateHelpers)
    
    def get_helpers(self):
        return {'get_relationships_as_Subj_dependsOn_Obj' : get_relationships_as_Subj_dependsOn_Obj,
                'get_relationships_as_Obj_isDependencyOf_Subj' : get_relationships_as_Obj_isDependencyOf_Subj,
                'get_relationships_as_Subj_derives_from_Obj' : get_relationships_as_Subj_derives_from_Obj,
                'get_relationships_as_Obj_has_derivation_Subj' : get_relationships_as_Obj_has_derivation_Subj,
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

