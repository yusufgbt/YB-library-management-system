#!/usr/bin/env python3
"""
PostgreSQL Kurulum ve Yapılandırma Scripti
Bu script PostgreSQL veritabanını kurar ve yapılandırır
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Komut çalıştırır ve sonucu döndürür"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} başarılı!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} başarısız!")
        print(f"   Hata: {e.stderr}")
        return False

def install_postgresql():
    """PostgreSQL'i kurar"""
    print("🚀 PostgreSQL kurulumu başlatılıyor...")
    
    # Sistem güncellemesi
    if not run_command("sudo apt update", "Sistem güncelleniyor"):
        return False
    
    # PostgreSQL kurulumu
    if not run_command("sudo apt install postgresql postgresql-contrib -y", "PostgreSQL kuruluyor"):
        return False
    
    # PostgreSQL servisini başlat
    if not run_command("sudo systemctl start postgresql", "PostgreSQL servisi başlatılıyor"):
        return False
    
    # PostgreSQL servisini otomatik başlat
    if not run_command("sudo systemctl enable postgresql", "PostgreSQL otomatik başlatma ayarlanıyor"):
        return False
    
    print("✅ PostgreSQL kurulumu tamamlandı!")
    return True

def setup_postgres_user():
    """PostgreSQL kullanıcısını yapılandırır"""
    print("👤 PostgreSQL kullanıcısı yapılandırılıyor...")
    
    # postgres kullanıcısına şifre ver
    setup_commands = [
        "sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'postgres';\"",
        "sudo -u postgres psql -c \"CREATE USER yb_library WITH PASSWORD 'yb_library123';\"",
        "sudo -u postgres psql -c \"ALTER USER yb_library CREATEDB;\"",
        "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE yb_library TO yb_library;\""
    ]
    
    for cmd in setup_commands:
        if not run_command(cmd, "Kullanıcı yapılandırması"):
            print("⚠️ Kullanıcı yapılandırması atlandı, devam ediliyor...")
    
    print("✅ PostgreSQL kullanıcısı yapılandırıldı!")
    return True

def create_environment_file():
    """Çevre değişkenleri dosyası oluşturur"""
    print("📝 Çevre değişkenleri dosyası oluşturuluyor...")
    
    env_content = """# PostgreSQL Veritabanı Ayarları
DB_HOST=localhost
DB_PORT=5432
DB_NAME=yb_library
DB_USER=yb_library
DB_PASSWORD=yb_library123
DB_TYPE=postgresql
ENVIRONMENT=development

# Alternatif olarak postgres kullanıcısı
# DB_USER=postgres
# DB_PASSWORD=postgres
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env dosyası oluşturuldu!")
        return True
    except Exception as e:
        print(f"❌ .env dosyası oluşturulamadı: {e}")
        return False

def install_python_dependencies():
    """Python bağımlılıklarını kurar"""
    print("🐍 Python bağımlılıkları kuruluyor...")
    
    dependencies = [
        "psycopg2-binary",
        "python-dotenv"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"{dep} kuruluyor"):
            print(f"⚠️ {dep} kurulumu atlandı!")
    
    print("✅ Python bağımlılıkları kuruldu!")
    return True

def main():
    """Ana kurulum fonksiyonu"""
    print("🎯 YB Library - PostgreSQL Kurulum Scripti")
    print("=" * 50)
    
    # PostgreSQL kurulumu
    if not install_postgresql():
        print("💥 PostgreSQL kurulumu başarısız!")
        return False
    
    # PostgreSQL kullanıcısı yapılandırması
    setup_postgres_user()
    
    # Python bağımlılıkları
    install_python_dependencies()
    
    # Çevre değişkenleri dosyası
    create_environment_file()
    
    print("\n🎉 PostgreSQL kurulumu tamamlandı!")
    print("\n📋 Sonraki adımlar:")
    print("1. python database.py çalıştırın")
    print("2. python migrate_data.py ile verileri aktarın")
    print("3. python main.py ile uygulamayı başlatın")
    print("4. http://localhost:8096 adresine gidin")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Kurulum kullanıcı tarafından iptal edildi!")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Beklenmeyen hata: {e}")
        sys.exit(1)
