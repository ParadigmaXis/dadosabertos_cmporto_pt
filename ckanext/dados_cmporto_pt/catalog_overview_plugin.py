# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.model as model
import ckan.logic as logic

from pylons import c
import copy
import logging
log = logging.getLogger(__name__)

class CatalogOverviewPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.ITemplateHelpers)
    
    def get_helpers(self):
        return {'get_recent_datasets' : get_recent_datasets,
                'get_most_pop_datasets' : get_most_pop_datasets,
                'get_top_tags' : get_top_tags,
        }

def get_recent_datasets():
    _ctx = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    result = logic.get_action('package_search')(_ctx, { 'rows': 5, 'sort' : 'metadata_modified desc', 'q':'type:(dataset OR simples OR composto)' })
    return result['results']

def get_most_pop_datasets():
    _ctx = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    result = logic.get_action('package_search')(_ctx, { 'sort' : 'views_recent desc', 'rows': 5, 'q':'type:(dataset OR simples OR composto)' })
    return result['results']

def get_top_tags():
    _ctx = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    if not c.facets or not c.facets.get('tags'):
        return []
    tags_list = [(_tag,_val) for _tag,_val in c.facets.get('tags').iteritems()]
    return sorted(tags_list, key=lambda x:x[1], reverse=True)[0:min(20,len(tags_list))]


