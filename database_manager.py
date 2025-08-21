# Veritabanı Yönetici Sınıfı
# PostgreSQL ve SQLite desteği
import os
import sqlite3
from contextlib import closing
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

class DatabaseManager(ABC):
    """Soyut veritabanı yönetici sınıfı"""
    
    @abstractmethod
    def get_connection(self):
        """Veritabanı bağlantısı döndürür"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """SQL sorgusu çalıştırır"""
        pass
    
    @abstractmethod
    def execute_update(self, query: str, params: tuple = None) -> int:
        """UPDATE/INSERT/DELETE sorgusu çalıştırır"""
        pass

class SQLiteManager(DatabaseManager):
    """SQLite veritabanı yöneticisi"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            from config import get_db_path
            self.db_path = get_db_path()
        else:
            self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """SQLite bağlantısı oluşturur"""
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """SQL sorgusu çalıştırır"""
        with closing(self.get_connection()) as connection, closing(connection.cursor()) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """UPDATE/INSERT/DELETE sorgusu çalıştırır"""
        with closing(self.get_connection()) as connection, closing(connection.cursor()) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            return cursor.rowcount
    
    def init_database(self):
        """Veritabanını başlatır"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Tabloları oluştur
        create_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                year INTEGER
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                password_hash TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                loan_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0
            );
            """
        ]
        
        for sql in create_tables_sql:
            self.execute_update(sql)
        
        # Varsayılan admin kullanıcısı
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Varsayılan admin kullanıcısını oluşturur"""
        try:
            # Admin kullanıcısı var mı kontrol et
            result = self.execute_query("SELECT COUNT(1) as count FROM users WHERE username = 'admin';")
            if result and result[0]['count'] == 0:
                # Salt ve hash oluştur
                import hashlib
                import secrets
                
                salt = secrets.token_hex(16)
                password = "Admin123!"
                password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
                
                # Admin kullanıcısını ekle
                self.execute_update(
                    "INSERT INTO users (username, password_hash, salt, is_admin) VALUES (?, ?, ?, 1);",
                    ("admin", password_hash, salt)
                )
                print("✅ Varsayılan admin kullanıcısı oluşturuldu!")
        except Exception as e:
            print(f"⚠️ Admin kullanıcısı oluşturulamadı: {e}")

class PostgreSQLManager(DatabaseManager):
    """PostgreSQL veritabanı yöneticisi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 paketi kurulu değil!")
    
    def get_connection(self):
        """PostgreSQL bağlantısı oluşturur"""
        connection = psycopg2.connect(**self.config)
        connection.autocommit = False
        return connection
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """SQL sorgusu çalıştırır"""
        with closing(self.get_connection()) as connection, closing(connection.cursor(cursor_factory=RealDictCursor)) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """UPDATE/INSERT/DELETE sorgusu çalıştırır"""
        with closing(self.get_connection()) as connection, closing(connection.cursor()) as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                connection.commit()
                return cursor.rowcount
            except Exception:
                connection.rollback()
                raise

class DatabaseFactory:
    """Veritabanı yönetici fabrikası"""
    
    @staticmethod
    def create_manager(db_type: str = "postgresql", **kwargs) -> DatabaseManager:
        """Veritabanı yöneticisi oluşturur"""
        if db_type.lower() == "postgresql":
            if not POSTGRES_AVAILABLE:
                print("⚠️ PostgreSQL paketi kurulu değil, SQLite kullanılıyor")
                return SQLiteManager(kwargs.get('db_path', 'database.db'))
            return PostgreSQLManager(kwargs)
        else:
            return SQLiteManager(kwargs.get('db_path', 'database.db'))

# Varsayılan veritabanı yöneticisi
def get_database_manager() -> DatabaseManager:
    """Varsayılan veritabanı yöneticisini döndürür"""
    # Çevre değişkenlerinden veritabanı tipini al
    db_type = os.getenv('DB_TYPE', 'postgresql')
    
    if db_type.lower() == 'postgresql':
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'yb_library'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres'),
        }
        return DatabaseFactory.create_manager('postgresql', **config)
    else:
        return SQLiteManager('./database.db')

# Test fonksiyonu
def test_database():
    """Veritabanı bağlantısını test eder"""
    try:
        db = get_database_manager()
        print(f"✅ Veritabanı bağlantısı başarılı: {type(db).__name__}")
        
        # Test sorgusu
        result = db.execute_query("SELECT 1 as test")
        print(f"✅ Test sorgusu başarılı: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Veritabanı test hatası: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Veritabanı test ediliyor...")
    test_database()
