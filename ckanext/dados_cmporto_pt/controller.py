# -*- coding: utf-8 -*-

from ckan.controllers import admin

class AdminController(admin.AdminController):
    def _get_config_form_items(self):
        items = super(AdminController, self)._get_config_form_items()
        items[7]['options'].append({'value': '4', 'text': 'dados.cm-porto.pt'})
        return items