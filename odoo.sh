#!/bin/bash
# Odoo Yönetim Scripti
# Kullanım: ./odoo.sh [start|restart|update|update-custom|kill]

PYTHON="/home/arch/odoo/venv/bin/python"
ODOO_BIN="/home/arch/odoo/odoo-bin"
CONF="/home/arch/odoo/odoo.conf"
DB="rd-odoo-uts"
MODULE="uts_integration"
CUSTOM_ADDONS_DIR="/home/arch/odoo/custom_addons"

do_kill() {
    echo ">>> Odoo durduruluyor..."
    pkill -f "odoo-bin" 2>/dev/null || true
    sleep 1
    echo ">>> Odoo durduruldu."
}

do_start() {
    echo ">>> Odoo başlatılıyor (DB: $DB)..."
    $PYTHON $ODOO_BIN -c $CONF -d $DB --dev=reload,xml
}

do_update_module() {
    echo ">>> Modül güncelleniyor: $MODULE ..."
    $PYTHON $ODOO_BIN -c $CONF -d $DB -u $MODULE --stop-after-init
    echo ">>> Güncelleme tamamlandı. Odoo başlatılıyor..."
    do_start
}

do_update_custom() {
    # custom_addons klasöründeki tüm modülleri otomatik tespit et
    echo ">>> Custom Addons modülleri tespit ediliyor..."
    MODULES=$(ls -d $CUSTOM_ADDONS_DIR/*/ 2>/dev/null | xargs -I{} basename {} | tr '\n' ',' | sed 's/,$//')
    
    if [ -z "$MODULES" ]; then
        echo ">>> HATA: Hiç custom modül bulunamadı!"
        exit 1
    fi
    
    echo ">>> Güncellenecek modüller: $MODULES"
    $PYTHON $ODOO_BIN -c $CONF -d $DB -u $MODULES --stop-after-init
    echo ">>> Güncelleme tamamlandı. Odoo başlatılıyor..."
    do_start
}

case "$1" in
    start)
        do_start
        ;;
    restart)
        do_kill
        do_start
        ;;
    update)
        do_kill
        do_update_module
        ;;
    update-custom)
        do_kill
        do_update_custom
        ;;
    kill)
        do_kill
        ;;
    *)
        echo "Kullanım: $0 {start|restart|update|update-custom|kill}"
        echo ""
        echo "  start          - Odoo'yu başlat"
        echo "  restart        - Odoo'yu yeniden başlat (kill + start)"
        echo "  update         - uts_integration modülünü güncelle ve başlat"
        echo "  update-custom  - custom_addons klasöründeki TÜM modülleri güncelle ve başlat"
        echo "  kill           - Odoo'yu durdur"
        exit 1
        ;;
esac
