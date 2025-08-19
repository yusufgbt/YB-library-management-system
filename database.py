# SQLite Veritabanı İşlemleri
import sqlite3
from contextlib import closing
from typing import List, Dict, Any, Optional
import os

def get_connection():
    """SQLite veritabanı bağlantısı oluşturur"""
    try:
        from config import get_db_path
        connection = sqlite3.connect(get_db_path())
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        raise

def init_database():
    """SQLite veritabanını başlatır ve tabloları oluşturur"""
    with closing(get_connection()) as connection:
        try:
            cursor = connection.cursor()
            
            # Books tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE,
                    year INTEGER
                );
            """)
            
            # Members tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    password_hash TEXT
                );
            """)
            
            # Loans tablosu
            cursor.execute("""
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
            """)
            
            # Users tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    is_admin BOOLEAN NOT NULL DEFAULT 0
                );
            """)
            
            connection.commit()
            print("✅ SQLite veritabanı başarıyla başlatıldı!")
            
        except sqlite3.Error as e:
            print(f"❌ Veritabanı başlatma hatası: {e}")
            raise

def create_database():
    """SQLite veritabanı dosyasını oluşturur (eğer yoksa)"""
    from config import get_db_path
    db_path = get_db_path()
    
    try:
        # Veritabanı dosyası yoksa oluştur
        if not os.path.exists(db_path):
            with closing(get_connection()) as connection:
                connection.close()
            print(f"✅ '{db_path}' veritabanı dosyası oluşturuldu!")
        else:
            print(f"ℹ️ '{db_path}' veritabanı dosyası zaten mevcut!")
            
    except sqlite3.Error as e:
        print(f"❌ Veritabanı oluşturma hatası: {e}")
        raise

def test_connection():
    """SQLite bağlantısını test eder"""
    try:
        with closing(get_connection()) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            print(f"✅ SQLite bağlantısı başarılı!")
            print(f"📊 Veritabanı versiyonu: {version[0]}")
            return True
    except Exception as e:
        print(f"❌ SQLite bağlantı hatası: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SQLite veritabanı kurulumu başlatılıyor...")
    try:
        create_database()
        init_database()
        test_connection()
        print("🎉 SQLite kurulumu tamamlandı!")
    except Exception as e:
        print(f"💥 Kurulum hatası: {e}")
