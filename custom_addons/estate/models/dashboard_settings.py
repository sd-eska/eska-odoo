# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json


class DashboardSettings(models.Model):
    _name = 'estate.dashboard.settings'
    _description = 'Dashboard Settings'

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade', index=True)
    enabled_items = fields.Text(string='Enabled Items', default='[]')

    _sql_constraints = [
        ('user_unique', 'unique(user_id)', 'Each user can only have one dashboard settings record!')
    ]

    def get_enabled_items(self):
        """Get enabled dashboard items for current user"""
        self.ensure_one()
        try:
            return json.loads(self.enabled_items or '[]')
        except:
            return []

    def set_enabled_items(self, items):
        """Set enabled dashboard items for current user"""
        self.ensure_one()
        self.enabled_items = json.dumps(items)
