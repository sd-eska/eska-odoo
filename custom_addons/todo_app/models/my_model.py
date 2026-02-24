from odoo import fields, models
from datetime import timedelta

class TestModel(models.Model):
    _name = "test.model"  # Nokta ile yazılır!
    _description = "Test Model"
    _log_access = False

    name = fields.Char(required=True, string="İsim")
    expected_price = fields.Float(required=True, string="Beklenen Fiyat")
    
    # Exercise: Default values
    bedrooms = fields.Integer(
        string="Yatak Odası Sayısı",
        default=2,  # Default: 2 bedrooms
        help="Yatak odası sayısı"
    )
    
    availability_date = fields.Date(
        string="Müsaitlik Tarihi",
        default=lambda self: fields.Date.today() + timedelta(days=90),  # 3 months from today
        help="Bu tarihten itibaren müsait"
    )