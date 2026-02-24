from datetime import timedelta
from odoo import api, fields, models, exceptions

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Emlak Mülk Teklifi"

    _sql_constraints = [
        ("check_price", "CHECK(price > 0)", "The offer price must be strictly positive."),
    ]

    price = fields.Float(string="Fiyat", required=True)
    status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        string="Durum",
        copy=False,
        default='pending',
        help="Teklifin şu anki durumu."
    )
    partner_id = fields.Many2one("res.partner", string="İş Ortağı", required=True)
    property_id = fields.Many2one("estate.property", string="Mülk", required=True)
    property_type_id = fields.Many2one(
        "estate.property.type", 
        related="property_id.property_type_id", 
        string="Mülk Tipi", 
        store=True
    )

    validity = fields.Integer(string="Geçerlilik (Gün)", default=7)
    date_deadline = fields.Date(string="Son Tarih", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            # create_date is only available after record creation. Use today() if not yet set.
            start_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = start_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            start_date = record.create_date.date() if record.create_date else fields.Date.today()
            # Calculate days between deadline and start_date
            record.validity = (record.date_deadline - start_date).days

    @api.model
    def create(self, vals):
        property_id = self.env['estate.property'].browse(vals['property_id'])
        
        # Fiyat kontrolü: Mevcut tekliflerden düşük olamaz
        if property_id.offer_ids:
            max_offer_price = max(property_id.offer_ids.mapped('price'))
            if vals.get('price', 0) < max_offer_price:
                raise exceptions.UserError("Teklif fiyatı mevcut en yüksek tekliften (%.2f) düşük olamaz!" % max_offer_price)
        
        property_id.state = 'offer_received'
        return super().create(vals)

    def unlink(self):
        # Store properties affected by deletion to check them later
        properties = self.mapped('property_id')
        
        for record in self:
            if record.status == "accepted":
                raise exceptions.UserError("Kabul edilmiş bir teklif silinemez!")
        
        # Perform deletion
        res = super().unlink()
        
        # After deletion, if a property has no offers left, reset its state to 'new'
        for prop in properties:
            if not prop.offer_ids:
                prop.state = 'new'
        
        return res

    def action_accept(self):
        for record in self:
            # Check if an offer is already accepted for this property
            if "accepted" in record.property_id.offer_ids.mapped("status"):
                raise exceptions.UserError("Zaten kabul edilmiş bir teklif var!")
            
            record.status = "accepted"
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = "offer_accepted"
        return True

    def action_refuse(self):
        for record in self:
            record.status = "refused"
            # Eğer mülkün tüm teklifleri reddedilmişse ve hiç bekleyen yoksa
            other_offers = record.property_id.offer_ids
            if all(o.status == 'refused' for o in other_offers):
                record.property_id.state = "offer_refused"
        return True

