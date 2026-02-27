from odoo import models
from .uretim_builder import UretimBuilderMixin
from .verme_builder import VermeBuilderMixin
from .alim_builder import AlimBuilderMixin
from .hek_builder import HekBuilderMixin
from .ihracat_builder import IhracatBuilderMixin
from .kozmetik_builder import KozmetikBuilderMixin
from .iade_builder import IadeBuilderMixin


class UtsPayloadMixin(
    UretimBuilderMixin,
    VermeBuilderMixin,
    AlimBuilderMixin,
    HekBuilderMixin,
    IhracatBuilderMixin,
    KozmetikBuilderMixin,
    IadeBuilderMixin,
    models.AbstractModel,
):
    """
    Katman 3: ÜTS Payload Orchestrator.

    Python çoklu kalıtım ile tüm builder mixin'lerini birleştirir.
    Her mixin saf Python sınıfıdır, `self` runtime'da Odoo instance'ına
    bağlı olduğu için `self.env`, `self._get_uno()` vb. tam çalışır.

    Miras zinciri (Odoo):
        uts.config.mixin → uts.transport → uts.base.builder → uts.payload.mixin

    Builder mixin'leri (Python MRO):
        UretimBuilderMixin     — Üretim Bildirimi
        VermeBuilderMixin      — Standart/Tanımsız/Tüketici Verme
        AlimBuilderMixin       — Alım Bildirimi
        HekBuilderMixin        — HEK/Zayiat
        IhracatBuilderMixin    — İhracat Bildirimi
        KozmetikBuilderMixin   — Kozmetik Firmaya Verme
        IadeBuilderMixin       — Tüketiciden/Tanımsız Yerden İade Alma
    """
    _name = 'uts.payload.mixin'
    _inherit = 'uts.base.builder'
    _description = 'ÜTS Payload Orchestrator'
