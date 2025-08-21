# PostgreSQL Veritabanı Konfigürasyonu
import os

# Veritabanı ayarları
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'yb_library'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
}

# Geliştirme ortamı kontrolü
if os.getenv('ENVIRONMENT') == 'development':
    DB_CONFIG.update({
        'host': 'localhost',
        'port': '5432',
        'database': 'yb_library',
        'user': 'yb_library',
        'password': 'yb_library123',
    })

# Veritabanı URL'i
def get_database_url() -> str:
    """PostgreSQL veritabanı URL'ini döndürür"""
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Veritabanı bağlantı parametreleri
def get_connection_params() -> dict:
    """PostgreSQL bağlantı parametrelerini döndürür"""
    return DB_CONFIG.copy()
