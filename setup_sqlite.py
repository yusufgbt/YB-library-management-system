#!/usr/bin/env python3
"""
SQLite Veritabanı Kurulum Scripti
Bu script SQLite veritabanını kurar ve yapılandırır
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

def check_sqlite():
    """SQLite'ın kurulu olup olmadığını kontrol eder"""
    print("🔍 SQLite kontrol ediliyor...")
    
    # Python'da sqlite3 modülü varsayılan olarak gelir
    try:
        import sqlite3
        print("✅ SQLite3 Python modülü mevcut!")
        return True
    except ImportError:
        print("❌ SQLite3 Python modülü bulunamadı!")
        return False

def create_environment_file():
    """Çevre değişkenleri dosyası oluşturur"""
    print("📝 Çevre değişkenleri dosyası oluşturuluyor...")
    
    env_content = """# SQLite Veritabanı Ayarları
DB_PATH=./database.db
DB_TYPE=sqlite
ENVIRONMENT=development
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
        "nicegui"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"{dep} kuruluyor"):
            print(f"⚠️ {dep} kurulumu atlandı!")
    
    print("✅ Python bağımlılıkları kuruldu!")
    return True

def main():
    """Ana kurulum fonksiyonu"""
    print("🎯 YB Library - SQLite Kurulum Scripti")
    print("=" * 50)
    
    # SQLite kontrolü
    if not check_sqlite():
        print("💥 SQLite kurulumu başarısız!")
        return False
    
    # Python bağımlılıkları
    install_python_dependencies()
    
    # Çevre değişkenleri dosyası
    create_environment_file()
    
    print("\n🎉 SQLite kurulumu tamamlandı!")
    print("\n📋 Sonraki adımlar:")
    print("1. python database.py çalıştırın")
    print("2. python main.py ile uygulamayı başlatın")
    print("3. http://localhost:8096 adresine gidin")
    
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
