from odoo import api, fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Mülk Tipi"
    _order = "sequence, name"
    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name must be unique."),
    ]

    name = fields.Char(string="Tür", required=True)
    sequence = fields.Integer("Sıralama", default=1, help="Elle sıralama için kullanılır.")
    
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(string="Teklif Sayısı", compute="_compute_offer_count")
    property_ids = fields.One2many("estate.property", "property_type_id")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

