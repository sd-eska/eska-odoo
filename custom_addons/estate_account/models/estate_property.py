from odoo import models, Command

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        for record in self:
            # Fatura oluşturma
            self.env["account.move"].create({
                "partner_id": record.buyer_id.id,
                "move_type": "out_invoice", # Müşteri Faturası
                "invoice_line_ids": [
                    Command.create({
                        "name": record.name + " - Satış Komisyonu (%6)",
                        "quantity": 1.0,
                        "price_unit": record.selling_price * 0.06,
                    }),
                    Command.create({
                        "name": "İdari Masraflar",
                        "quantity": 1.0,
                        "price_unit": 100.0,
                    }),
                ],
            })
        return super().super_action_sold() if hasattr(super(), 'super_action_sold') else super().action_sold()
