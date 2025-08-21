#!/usr/bin/env python3
"""
SQLite'dan PostgreSQL'e Veri Migrasyon Scripti
Bu script SQLite verilerini PostgreSQL'e aktarır
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import closing
import os
from dotenv import load_dotenv
import sys

# .env dosyasını yükle
load_dotenv()

def get_postgres_connection():
    """PostgreSQL bağlantısı oluşturur"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'yb_library'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        return connection
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL bağlantı hatası: {e}")
        raise

def create_postgres_tables():
    """PostgreSQL tablolarını oluşturur"""
    print("🏗️ PostgreSQL tabloları oluşturuluyor...")
    
    with closing(get_postgres_connection()) as connection:
        with closing(connection.cursor()) as cursor:
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
                print("✅ PostgreSQL tabloları oluşturuldu!")
                
            except psycopg2.Error as e:
                connection.rollback()
                print(f"❌ Tablo oluşturma hatası: {e}")
                raise

def migrate_data():
    """Verileri SQLite'dan PostgreSQL'e aktarır"""
    print("🔄 Veri migrasyonu başlatılıyor...")
    
    # SQLite yedek dosyasını oku
    try:
        with open('sqlite_backup.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✅ SQLite yedek dosyası okundu")
    except FileNotFoundError:
        print("❌ sqlite_backup.json dosyası bulunamadı!")
        return False
    
    with closing(get_postgres_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            try:
                # Members verilerini aktar
                if data.get('members'):
                    print(f"👥 {len(data['members'])} üye aktarılıyor...")
                    for member in data['members']:
                        cursor.execute("""
                            INSERT INTO members (name, email, phone, password_hash) 
                            VALUES (%s, %s, %s, %s)
                        """, (member['name'], member['email'], member['phone'], member['password_hash']))
                
                # Books verilerini aktar
                if data.get('books'):
                    print(f"📚 {len(data['books'])} kitap aktarılıyor...")
                    for book in data['books']:
                        cursor.execute("""
                            INSERT INTO books (title, author, isbn, year) 
                            VALUES (%s, %s, %s, %s)
                        """, (book['title'], book['author'], book['isbn'], book['year']))
                
                # Loans verilerini aktar
                if data.get('loans'):
                    print(f"📖 {len(data['loans'])} ödünç kaydı aktarılıyor...")
                    for loan in data['loans']:
                        cursor.execute("""
                            INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date) 
                            VALUES (%s, %s, %s, %s, %s)
                        """, (loan['book_id'], loan['member_id'], loan['loan_date'], loan['due_date'], loan['return_date']))
                
                # Users verilerini aktar
                if data.get('users'):
                    print(f"👤 {len(data['users'])} kullanıcı aktarılıyor...")
                    for user in data['users']:
                        # SQLite'tan gelen integer'ı boolean'a çevir
                        is_admin = bool(user['is_admin'])
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, salt, is_admin) 
                            VALUES (%s, %s, %s, %s)
                        """, (user['username'], user['password_hash'], user['salt'], is_admin))
                
                connection.commit()
                print("✅ Veri migrasyonu tamamlandı!")
                return True
                
            except psycopg2.Error as e:
                connection.rollback()
                print(f"❌ Veri aktarma hatası: {e}")
                raise

def verify_migration():
    """Migrasyon sonrası veri kontrolü"""
    print("🔍 Migrasyon sonrası veri kontrolü...")
    
    with closing(get_postgres_connection()) as connection:
        with closing(connection.cursor(cursor_factory=RealDictCursor)) as cursor:
            try:
                # Tablo sayılarını kontrol et
                tables = ['members', 'books', 'loans', 'users']
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cursor.fetchone()
                    print(f"📊 {table}: {result['count']} kayıt")
                
                return True
                
            except psycopg2.Error as e:
                print(f"❌ Veri kontrol hatası: {e}")
                return False

def main():
    """Ana migrasyon fonksiyonu"""
    print("🎯 SQLite → PostgreSQL Veri Migrasyonu")
    print("=" * 50)
    
    try:
        # Tabloları oluştur
        create_postgres_tables()
        
        # Verileri aktar
        if migrate_data():
            # Kontrol et
            verify_migration()
            print("\n🎉 Migrasyon başarıyla tamamlandı!")
        else:
            print("\n💥 Migrasyon başarısız!")
            return False
            
    except Exception as e:
        print(f"\n💥 Migrasyon hatası: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Migrasyon kullanıcı tarafından iptal edildi!")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Beklenmeyen hata: {e}")
        sys.exit(1)
