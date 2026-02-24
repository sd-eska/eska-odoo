from odoo import api, fields, models, exceptions
from odoo.tools.float_utils import float_compare, float_is_zero
from datetime import timedelta


class EstateProperty(models.Model):
    """Emlak Mülkü Modeli"""
    _name = "estate.property"
    _description = "Emlak Mülkü"
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Chatter miras alındı
    _order = "id desc"
    
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "The expected price must be strictly positive."),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The selling price must be positive."),
    ]

    # Temel Bilgiler
    name = fields.Char(
        string="Mülk Adı",
        required=True,
        help="Mülkün adı veya açıklaması"
    )

    property_type_id = fields.Many2one("estate.property.type", string="Mülk Tipi")
    tag_ids = fields.Many2many("estate.property.tag", string="Etiketler")

    # Fiyat Bilgileri
    expected_price = fields.Float(
        string="Beklenen Fiyat",
        required=True,
        tracking=True,
        help="Satış için beklenen fiyat"
    )
    
    selling_price = fields.Float(
        string="Satış Fiyatı",
        readonly=True,
        copy=False,
        tracking=True,
        help="Gerçekleşen satış fiyatı (otomatik doldurulur)"
    )

    best_price = fields.Float(
        string="En İyi Teklif",
        compute="_compute_best_price",
        help="Bu mülk için verilmiş en yüksek teklif"
    )

    # Özellikler
    bedrooms = fields.Integer(
        string="Yatak Odası",
        default=2,
        help="Yatak odası sayısı"
    )
    living_area = fields.Integer(string="Yaşam Alanı (m2)")
    garden = fields.Boolean(string="Bahçeli")
    garden_area = fields.Integer(string="Bahçe Alanı (m2)")
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'Kuzey'),
            ('south', 'Güney'),
            ('east', 'Doğu'),
            ('west', 'Batı'),
        ],
        string="Bahçe Cephesi"
    )

    # Tarihler
    availability_date = fields.Date(
        string="Müsaitlik Tarihi",
        default=lambda self: fields.Date.today() + timedelta(days=90),
        help="Bu tarihten itibaren müsait"
    )
    
    # State (Durum)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_refused', 'Offer Refused'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Cancelled'),
        ],
        string="Status",
        required=True,
        copy=False,
        default='new',
        tracking=True,
        help="Current status of the property"
    )

    # İlişkiler
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Teklifler")
    salesperson_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user, tracking=True)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, 
        default=lambda self: self.env.company
    )

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            if prices:
                record.best_price = max(prices)
            else:
                record.best_price = 0.0

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise exceptions.UserError("Sadece 'Yeni' veya 'İptal Edilmiş' mülkleri silebilirsiniz.")

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if record.state == "canceled":
                raise exceptions.UserError("Cancelled properties cannot be sold.")
            record.state = "sold"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise exceptions.UserError("Sold properties cannot be cancelled.")
            record.state = "canceled"
        return True

    @api.constrains("expected_price", "selling_price")
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_digits=2):
                if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) == -1:
                    raise exceptions.ValidationError("The selling price cannot be lower than 90% of the expected price!")
