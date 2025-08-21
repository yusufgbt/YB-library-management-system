# PostgreSQL Veritabanı İşlemleri
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import closing
from typing import List, Dict, Any, Optional
from config import get_connection_params

def get_connection():
    """PostgreSQL veritabanı bağlantısı oluşturur"""
    try:
        connection = psycopg2.connect(**get_connection_params())
        connection.autocommit = False
        return connection
    except psycopg2.Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        raise

def init_database():
    """PostgreSQL veritabanını başlatır ve tabloları oluşturur"""
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        try:
            # Books tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    isbn VARCHAR(20) UNIQUE,
                    year INTEGER
                );
            """)
            
            # Members tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    phone VARCHAR(20),
                    password_hash VARCHAR(255)
                );
            """)
            
            # Loans tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans (
                    id SERIAL PRIMARY KEY,
                    book_id INTEGER NOT NULL,
                    member_id INTEGER NOT NULL,
                    loan_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    return_date DATE,
                    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE,
                    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
                );
            """)
            
            # Users tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    salt VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)
            
            connection.commit()
            print("✅ PostgreSQL veritabanı başarıyla başlatıldı!")
            
        except psycopg2.Error as e:
            connection.rollback()
            print(f"❌ Veritabanı başlatma hatası: {e}")
            raise

def create_database():
    """PostgreSQL veritabanını oluşturur (eğer yoksa)"""
    # Önce postgres veritabanına bağlan
    params = get_connection_params()
    db_name = params.pop('database')
    
    try:
        connection = psycopg2.connect(**params)
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Veritabanı var mı kontrol et
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_name};")
            print(f"✅ '{db_name}' veritabanı oluşturuldu!")
        else:
            print(f"ℹ️ '{db_name}' veritabanı zaten mevcut!")
            
        cursor.close()
        connection.close()
        
    except psycopg2.Error as e:
        print(f"❌ Veritabanı oluşturma hatası: {e}")
        raise

def test_connection():
    """PostgreSQL bağlantısını test eder"""
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✅ PostgreSQL bağlantısı başarılı!")
                print(f"📊 Veritabanı versiyonu: {version[0]}")
                return True
    except Exception as e:
        print(f"❌ PostgreSQL bağlantı hatası: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PostgreSQL veritabanı kurulumu başlatılıyor...")
    try:
        create_database()
        init_database()
        test_connection()
        print("🎉 PostgreSQL kurulumu tamamlandı!")
    except Exception as e:
        print(f"💥 Kurulum hatası: {e}")
