# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.model as model
import ckan.logic as logic

from pylons import c

import logging
log = logging.getLogger(__name__)

class OpenDataUIPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.ITemplateHelpers)
    
    def get_helpers(self):
        return {'get_recent_datasets' : get_recent_datasets
        }

def get_recent_datasets():
    _ctx = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    return logic.get_action('current_package_list_with_resources')(_ctx, {'limit' : 5 })

