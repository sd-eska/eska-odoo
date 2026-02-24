from odoo import models, fields, api, _

class UtsLog(models.Model):
    _name = 'uts.log'
    _description = 'ÜTS Logs'
    _order = 'create_date desc'

    name = fields.Char("İşlem Tipi")
    res_model = fields.Char("Model")
    res_id = fields.Integer("Kayıt ID")
    
    request_data = fields.Text("İstek Verisi")
    response_data = fields.Text("Yanıt Verisi")
    status_code = fields.Integer("Durum Kodu")
    
    summary = fields.Text("İşlem Özeti", compute="_compute_summary", store=True)
    state = fields.Selection([
        ('success', 'Başarılı'),
        ('failed', 'Hata Alındı')
    ], string="Durum", compute="_compute_state", store=True)

    @api.depends('status_code', 'response_data')
    def _compute_summary(self):
        for rec in self:
            if rec.status_code == 200:
                rec.summary = "Başarılı"
            elif rec.status_code == 403:
                rec.summary = "Bakanlık Güvenlik Duvarı Engeli"
            elif rec.status_code == 0:
                rec.summary = "Bağlantı Hatası"
            else:
                if "Request Rejected" in (rec.response_data or ""):
                    rec.summary = "Sunucu tarafından bloklandı."
                else:
                    rec.summary = f"ÜTS hata döndürdü (Kod: {rec.status_code})."

    @api.depends('status_code')
    def _compute_state(self):
        for rec in self:
            if rec.status_code == 200:
                rec.state = 'success'
            else:
                rec.state = 'failed'
