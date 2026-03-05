"""
ÜTS Hata Kodu → Türkçe Açıklama Eşlemesi

ÜTS API'den dönen hata kodlarını kullanıcı dostu Türkçe mesajlara çevirir.
Bilinmeyen kodlar için orijinal mesaj gösterilir.
"""

UTS_ERROR_MAP = {
    # Ürün hataları
    'UTS-H002': 'Tekil Ürün bulunamadı. Lütfen UNO (barkod) numarasını kontrol edin.',
    'UTS-H014': 'Ürün ÜTS sisteminde tanımlı değil. Ürün kaydını ÜTS portalından kontrol edin.',
    'UTS-H015': 'Ürün takip konfigürasyonu bulunamadı.',

    # Bildirim hataları
    'UTS-H052': 'Lot/Seri numarası eksik veya hatalı. Lütfen detaylı işlemlerden lot numarasını kontrol edin.',
    'UTS-H054': 'Adet (ADT) alanı hatalı. Lot takipli ürünlerde adet zorunludur.',
    'UTS-H055': 'Seri numaralı ürünlerde adet 1 olmalıdır veya verilmemelidir.',

    # Kurum hataları
    'UTS-H100': 'Alıcı kurum ÜTS\'de bulunamadı. KUN numarasını kontrol edin.',
    'UTS-H101': 'Gönderici kurum yetki hatası. Firma ÜTS\'de aktif olmalıdır.',
    'UTS-H105': 'Ürün stoğunuz ÜTS\'de yetersiz. Önce üretim veya alım bildirimi yapın.',

    # Tarih hataları
    'UTS-H130': 'Üretim tarihi (URT) formatı hatalı. YYYY-AA-GG formatında olmalıdır.',
    'UTS-H131': 'Son kullanma tarihi (SKT) üretim tarihinden önce olamaz.',

    # Tekrar hataları
    'UTS-H160': 'Bu bildirim daha önce yapılmış. Aynı ürün/lot/seri zaten kayıtlı.',
    'UTS-H170': 'Verilen bilgilere uyan bildirim bulunamadı.',

    # Genel
    'UTS-H001': 'Genel sistem hatası. Lütfen daha sonra tekrar deneyin.',
    'UTS-H003': 'Yetki hatası. API kullanıcı bilgilerinizi kontrol edin.',
    'UTS-H004': 'İstek formatı hatalı. Teknik destek ile iletişime geçin.',
}


def translate_uts_error(code, original_message=None):
    """
    ÜTS hata kodunu Türkçe mesaja çevirir.
    Bilinmeyen kodlar için: "[KOD] Orijinal mesaj" döndürür.
    """
    if code in UTS_ERROR_MAP:
        return f"[{code}] {UTS_ERROR_MAP[code]}"
    if original_message:
        return f"[{code}] {original_message}"
    return f"[{code}] Bilinmeyen ÜTS hatası."


def parse_uts_response(response_json):
    """
    ÜTS API yanıtını parse eder.
    Dönüş: {
        'success': bool,
        'snc': str or None (kayıt numarası),
        'bid': str or None (bildirim kodu),
        'errors': [{'code': str, 'message': str, 'translated': str}],
        'raw': dict
    }
    """
    result = {
        'success': False,
        'snc': None,
        'bid': None,
        'errors': [],
        'raw': response_json,
    }

    if not isinstance(response_json, dict):
        return result

    # SNC = başarılı kayıt numarası
    snc = response_json.get('SNC')
    if snc:
        result['success'] = True
        if isinstance(snc, dict):
            # SNC bazen dict olabilir: {"BID": "...", ...}
            result['snc'] = str(snc.get('BID', snc))
            result['bid'] = str(snc.get('BID', '')) if snc.get('BID') else None
        else:
            result['snc'] = str(snc)
            # BID ayrı alan olarak da gelebilir
            bid = response_json.get('BID')
            if bid:
                result['bid'] = str(bid)

    # MSJ = mesaj listesi
    messages = response_json.get('MSJ', [])
    if isinstance(messages, list):
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            tip = msg.get('TIP', '')
            code = msg.get('KOD', '')
            met = msg.get('MET', '')

            if tip == 'HATA':
                result['success'] = False
                result['errors'].append({
                    'code': code,
                    'message': met,
                    'translated': translate_uts_error(code, met),
                })

    return result

