# -*- coding: utf-8 -*-
from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Mülk Étiketi"
    _order = "name"

    name = fields.Char(string="Etiket", required=True)
    color = fields.Integer(string="Renk")

    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name must be unique."),
    ]
