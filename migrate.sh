#!/bin/bash

# YB Library Migration Script
# Bu script Alembic migration'larını yönetir

echo "🏛️ YB Library Migration Sistemi"
echo "================================"

# Migrations klasörüne git
cd migrations

case "$1" in
    "upgrade")
        echo "📈 Migration'ları yükseltiliyor..."
        alembic upgrade head
        ;;
    "downgrade")
        if [ -z "$2" ]; then
            echo "❌ Downgrade için revision ID gerekli!"
            echo "Kullanım: ./migrate.sh downgrade <revision_id>"
            exit 1
        fi
        echo "📉 Migration'ı düşürülüyor: $2"
        alembic downgrade $2
        ;;
    "current")
        echo "📍 Mevcut migration durumu:"
        alembic current
        ;;
    "history")
        echo "📚 Migration geçmişi:"
        alembic history
        ;;
    "heads")
        echo "🎯 Head revision'lar:"
        alembic heads
        ;;
    "create")
        if [ -z "$2" ]; then
            echo "❌ Yeni migration için mesaj gerekli!"
            echo "Kullanım: ./migrate.sh create <mesaj>"
            exit 1
        fi
        echo "🆕 Yeni migration oluşturuluyor: $2"
        alembic revision --autogenerate -m "$2"
        ;;
    "stamp")
        if [ -z "$2" ]; then
            echo "❌ Stamp için revision ID gerekli!"
            echo "Kullanım: ./migrate.sh stamp <revision_id>"
            exit 1
        fi
        echo "🏷️ Migration stamp ediliyor: $2"
        alembic stamp $2
        ;;
    *)
        echo "📖 Kullanım:"
        echo "  ./migrate.sh upgrade          - Migration'ları yükselt"
        echo "  ./migrate.sh downgrade <id>   - Migration'ı düşür"
        echo "  ./migrate.sh current          - Mevcut durumu göster"
        echo "  ./migrate.sh history          - Geçmişi göster"
        echo "  ./migrate.sh heads            - Head revision'ları göster"
        echo "  ./migrate.sh create <mesaj>   - Yeni migration oluştur"
        echo "  ./migrate.sh stamp <id>       - Migration stamp et"
        echo ""
        echo "📝 Örnekler:"
        echo "  ./migrate.sh upgrade"
        echo "  ./migrate.sh create 'Add new table'"
        echo "  ./migrate.sh downgrade 355423c466cd"
        ;;
esac

echo ""
echo "✅ Migration işlemi tamamlandı!"


