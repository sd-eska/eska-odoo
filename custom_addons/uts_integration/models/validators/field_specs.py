"""
ÜTS Doküman Alan Tanımları (Rev. 99, 31.05.2022)

Bu dosya ÜTS web servis dokümanındaki tüm alan kurallarını
tek merkezde tanımlar. Builder'lar ve validator'lar bu spec'leri kullanır.

Her alan tanımı:
  - required: True / False / 'conditional'
  - type: 'str' / 'int' / 'date' / 'list'
  - max: Maksimum karakter uzunluğu
  - condition: Koşullu alanlar için açıklama (opsiyonel)
"""

URETIM = {
    'UNO': {'required': True,  'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası',
            'condition': 'Lot takip edilen ürünler için zorunlu'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası',
            'condition': 'Tekil takip edilen ürünler için zorunlu'},
    'URT': {'required': True,  'type': 'date', 'max': 10, 'label': 'Üretim Tarihi'},
    'SKT': {'required': False, 'type': 'date', 'max': 13, 'label': 'Son Kullanma Tarihi'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet',
            'condition': 'Lot bazında takip edilen ürünler için zorunlu'},
    'UDI': {'required': 'conditional', 'type': 'str', 'label': 'Eşsiz Kimlik'},
    'SIP': {'required': 'conditional', 'type': 'list', 'label': 'Sistem İşlem Paketi'},
    'GTK': {'required': False, 'type': 'str', 'max': 5, 'label': 'Gönüllü Takip Kapsamı'},
}

VERME = {
    'UNO': {'required': True,  'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
    'KUN': {'required': True,  'type': 'int', 'label': 'Alıcı Kurum Numarası'},
    'BEN': {'required': False, 'type': 'str', 'max': 5, 'label': 'Bedelsiz Numune'},
    'BNO': {'required': True,  'type': 'str', 'max': 50, 'label': 'Belge Numarası'},
}

TANIMSIZ_YERE_VERME = {
    'UNO': {'required': True,  'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
    'VKN': {'required': True,  'type': 'int', 'label': 'Vergi Kimlik No'},
    'BNO': {'required': True,  'type': 'str', 'max': 50, 'label': 'Belge Numarası'},
    'BEN': {'required': False, 'type': 'str', 'max': 5, 'label': 'Bedelsiz Numune'},
}

TUKETICIYE_VERME = {
    'UNO': {'required': True,  'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
    'BEN': {'required': False, 'type': 'str', 'max': 5, 'label': 'Bedelsiz Numune'},
    'TUA': {'required': 'conditional', 'type': 'str', 'max': 50, 'label': 'Tüketici Adı'},
    'TUS': {'required': 'conditional', 'type': 'str', 'max': 50, 'label': 'Tüketici Soyadı'},
    'TKN': {'required': 'conditional', 'type': 'int', 'label': 'T.C. Kimlik No'},
    'GIT': {'required': True,  'type': 'date', 'max': 10, 'label': 'Tüketiciye Verme Tarihi'},
    'TUR': {'required': 'conditional', 'type': 'str', 'label': 'Kişi Kimlik Bilgisi Açıklama Türü'},
    'DTA': {'required': 'conditional', 'type': 'str', 'max': 50, 'label': 'Diğer Tür Açıklaması',
            'condition': "TUR == 'DIGER' ise zorunlu"},
}

ALIM = {
    'UNO': {'required': True,  'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
}

HEK_ZAYIAT = {
    'UNO': {'required': True,  'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
    'TUR': {'required': True,  'type': 'str', 'max': 20, 'label': 'Zayiat Türü'},
    'DTA': {'required': 'conditional', 'type': 'str', 'max': 50, 'label': 'Diğer Açıklaması',
            'condition': "TUR == 'DIGER' ise zorunlu"},
}

IHRACAT = {
    'UNO': {'required': True,  'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
    'BEN': {'required': False, 'type': 'str', 'max': 5, 'label': 'Bedelsiz Numune'},
    'GBN': {'required': True,  'type': 'str', 'max': 16, 'label': 'Gümrük Beyanname Numarası'},
}

KOZMETIK_VERME = {
    'UNO': {'required': True,  'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
    'KUN': {'required': True,  'type': 'int', 'label': 'Alıcı Kurum Numarası'},
    'BNO': {'required': True,  'type': 'str', 'max': 50, 'label': 'Belge Numarası'},
    'GIT': {'required': False, 'type': 'date', 'max': 10, 'label': 'Gerçek İşlem Tarihi'},
}

TUKETICIDEN_IADE = {
    'TID': {'required': 'conditional', 'type': 'str', 'label': 'Tüketiciye Verme Bildirim ID'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
    'VKN': {'required': 'conditional', 'type': 'int', 'label': 'Tüketiciye Veren Kurum No'},
    'UNO': {'required': 'conditional', 'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
}

TANIMSIZ_YERDEN_IADE = {
    'UTI': {'required': 'conditional', 'type': 'str', 'label': 'Tanımsız Yere Verme Bildirim ID'},
    'ADT': {'required': 'conditional', 'type': 'int', 'label': 'Adet'},
    'UNO': {'required': 'conditional', 'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': 'conditional', 'type': 'str', 'max': 20, 'label': 'Seri/Sıra Numarası'},
}

BILDIRIM_SORGULA = {
    'UNO': {'required': False, 'type': 'str', 'max': 23, 'label': 'Ürün Numarası'},
    'LNO': {'required': False, 'type': 'str', 'max': 36, 'label': 'Lot/Batch Numarası'},
    'SNO': {'required': False, 'type': 'str', 'max': 36, 'label': 'Seri/Sıra Numarası'},
    'ADT': {'required': False, 'type': 'int', 'label': 'Kayıt Sayısı (max 500)'},
    'OFF': {'required': False, 'type': 'str', 'label': 'Offset Adresi'},
}

# Bildirim tipi → alan spec eşlemesi
SPECS = {
    'uretim': URETIM,
    'verme': VERME,
    'tanimsiz_verme': TANIMSIZ_YERE_VERME,
    'tuketici_verme': TUKETICIYE_VERME,
    'alim': ALIM,
    'hek': HEK_ZAYIAT,
    'ihracat': IHRACAT,
    'kozmetik_verme': KOZMETIK_VERME,
    'tuketiciden_iade': TUKETICIDEN_IADE,
    'tanimsiz_yerden_iade': TANIMSIZ_YERDEN_IADE,
    'bildirim_sorgula': BILDIRIM_SORGULA,
}

