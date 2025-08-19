# SQLite Veritabanı Konfigürasyonu
import os

# Veritabanı ayarları
DB_PATH = os.getenv('DB_PATH', './database.db')

# Geliştirme ortamı kontrolü
if os.getenv('ENVIRONMENT') == 'development':
    DB_PATH = './database_dev.db'

# Veritabanı URL'i
def get_database_url() -> str:
    """SQLite veritabanı URL'ini döndürür"""
    return f"sqlite:///{DB_PATH}"

# Veritabanı yolu
def get_db_path() -> str:
    """Veritabanı dosya yolunu döndürür"""
    return DB_PATH
