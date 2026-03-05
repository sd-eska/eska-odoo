from odoo import models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'uts.sync.mixin']

    def action_uts_uretim_bildirimi(self):
        self.ensure_one()
        if not self.product_id.is_uts_tracked:
            raise UserError(_("Bu ürün ÜTS takibine tabi değil."))
        if self.state != 'done':
            raise UserError(_("Üretim bildirimi için üretim emri 'Bitti' olmalıdır."))
        self._send_to_uts('uretim_bildirimi_ekle')
        return True

    def _prepare_uts_payloads(self):
        return self.env['uts.client']._build_uretim_payloads_from_production(self)
