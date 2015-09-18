# -*- coding: utf-8 -*-

import ckan.lib.base as base
from ckan.controllers import admin
import json
from ckan.model import Package

class AdminController(admin.AdminController):
    def _get_config_form_items(self):
        items = super(AdminController, self)._get_config_form_items()
        items[7]['options'].append({'value': '4', 'text': 'dados.cm-porto.pt'})
        return items

class StaticPagesController(base.BaseController):
    def linked_data(self):
        return base.render('home/cmp/px-linked-data.html')

    def terms_of_use(self):
        return base.render('home/cmp/px-terms-of-use.html')

    def privacy_policy(self):
        return base.render('home/cmp/px-privacy-policy.html')

    def moderation_policy(self):
        return base.render('home/cmp/px-moderation-policy.html')

    def list_license(self):
        return base.render('home/cmp/px-license-list.html', extra_vars = {'licenses': Package.get_license_register().items()})

