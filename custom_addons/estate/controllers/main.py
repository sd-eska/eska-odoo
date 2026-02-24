# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class AwesomeDashboard(http.Controller):
    @http.route('/awesome_dashboard/statistics', type='json', auth='user')
    def get_statistics(self):
        return {
            "new_orders_this_month": 150,
            "total_amount_new_orders": 45000,
            "average_tshirts_per_order": 3.5,
            "cancelled_orders_this_month": 12,
            "average_time_to_process": 4.2,
            "tshirt_sizes": {
                "S": 45,
                "M": 120,
                "L": 85,
                "XL": 30
            }
        }

    @http.route('/estate/dashboard/settings/get', type='json', auth='user')
    def get_dashboard_settings(self):
        """Get dashboard settings for current user"""
        user = request.env.user
        settings = request.env['estate.dashboard.settings'].search([('user_id', '=', user.id)], limit=1)
        
        if settings:
            return settings.get_enabled_items()
        return None  # Return None to indicate no saved settings

    @http.route('/estate/dashboard/settings/set', type='json', auth='user')
    def set_dashboard_settings(self, enabled_items):
        """Save dashboard settings for current user"""
        user = request.env.user
        settings = request.env['estate.dashboard.settings'].search([('user_id', '=', user.id)], limit=1)
        
        if settings:
            settings.set_enabled_items(enabled_items)
        else:
            request.env['estate.dashboard.settings'].create({
                'user_id': user.id,
                'enabled_items': json.dumps(enabled_items)
            })
        
        return {'success': True}
