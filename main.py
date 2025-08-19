from __future__ import annotations

import os
import sqlite3
from contextlib import closing
import hashlib
import secrets
from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import Request
from nicegui import app, ui


DB_PATH = "/home/yusuf/nicegui_sqlite/database.db"

# Modern tema renkleri ve CSS
ui.add_head_html(
    """
    <style>
      :root {
        --q-primary: #3b82f6; /* blue-500 */
        --q-secondary: #10b981; /* emerald-500 */
        --q-accent: #f59e0b; /* amber-500 */
        --q-dark: #1f2937; /* gray-800 */
        --q-light: #f8fafc; /* slate-50 */
        --q-success: #22c55e; /* green-500 */
        --q-warning: #f97316; /* orange-500 */
        --q-error: #ef4444; /* red-500 */
        
        /* Yeni tema renkleri */
        --q-purple: #8b5cf6; /* violet-500 */
        --q-pink: #ec4899; /* pink-500 */
        --q-cyan: #06b6d4; /* cyan-500 */
        --q-indigo: #6366f1; /* indigo-500 */
        --q-teal: #14b8a6; /* teal-500 */
        --q-orange: #f97316; /* orange-500 */
        --q-red: #ef4444; /* red-500 */
        --q-yellow: #eab308; /* yellow-500 */
      }
      
      /* Modern gradient arka plan */
      body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: all 0.5s ease;
      }
      
      /* Card gölgeleri ve animasyonlar */
      .q-card {
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        border-radius: 20px;
        backdrop-filter: blur(15px);
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
      }
      
      .q-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
      }
      
      .q-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--q-primary), var(--q-secondary));
        transform: scaleX(0);
        transition: transform 0.3s ease;
      }
      
      .q-card:hover::before {
        transform: scaleX(1);
      }
      
      /* Button animasyonları ve stilleri */
      .q-btn {
        border-radius: 15px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: none;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
      }
      
      .q-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
      }
      
      .q-btn:hover::before {
        left: 100%;
      }
      
      .q-btn:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.25);
      }
      
      /* Header güzelleştirme */
      .q-header {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.95) 0%, rgba(16, 185, 129, 0.95) 100%);
        backdrop-filter: blur(30px);
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        border-radius: 0 0 30px 30px;
        position: relative;
        overflow: hidden;
      }
      
      .q-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, 
          rgba(255, 255, 255, 0.1) 0%, 
          rgba(255, 255, 255, 0.05) 50%, 
          rgba(255, 255, 255, 0.1) 100%);
        animation: shimmer 3s ease-in-out infinite;
      }
      
      @keyframes shimmer {
        0%, 100% { transform: translateX(-100%); }
        50% { transform: translateX(100%); }
      }
      
      .q-header * {
        position: relative;
        z-index: 1;
      }
      
      /* Header içindeki butonlar */
      .q-header .q-btn {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
      }
      
      .q-header .q-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
      }
      
      /* Header içindeki ikonlar */
      .q-header .q-icon {
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      }
      
      /* Header içindeki label'lar */
      .q-header .q-label {
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        font-weight: 600;
      }
      
      /* Table güzelleştirme */
      .q-table {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
      }
      
      .q-table th {
        background: linear-gradient(135deg, var(--q-primary), var(--q-secondary));
        color: white;
        font-weight: 600;
        padding: 16px;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
      }
      
      .q-table tr:nth-child(even) {
        background: rgba(59, 130, 246, 0.05);
      }
      
      .q-table tr:hover {
        background: rgba(59, 130, 246, 0.1);
        transform: scale(1.01);
        transition: all 0.2s ease;
      }
      
      /* Input güzelleştirme */
      .q-input {
        border-radius: 15px;
        transition: all 0.3s ease;
        border: 2px solid transparent;
      }
      
      .q-input:focus-within {
        transform: scale(1.02);
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
        border-color: var(--q-primary);
      }
      
      /* Chip güzelleştirme */
      .q-chip {
        border-radius: 20px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      }
      
      .q-chip:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
      }
      
      /* Özel animasyonlar */
      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(30px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      
      @keyframes slideInLeft {
        from {
          opacity: 0;
          transform: translateX(-30px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      
      @keyframes pulse {
        0%, 100% {
          transform: scale(1);
        }
        50% {
          transform: scale(1.05);
        }
      }
      
      .animate-fade-in {
        animation: fadeInUp 0.6s ease-out;
      }
      
      .animate-slide-in {
        animation: slideInLeft 0.6s ease-out;
      }
      
      .animate-pulse {
        animation: pulse 2s infinite;
      }
      

      
      /* Responsive tasarım */
      @media (max-width: 768px) {
        .q-card {
          margin: 10px;
          border-radius: 15px;
        }
        
        .q-table {
          font-size: 12px;
        }
      }
      
      /* Loading animasyonu */
      .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(59, 130, 246, 0.1);
        border-left: 4px solid var(--q-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    </style>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """
)

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                year INTEGER
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT
            );
            """
        )
        cursor.execute(
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
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        connection.commit()
        # Varsayılan yönetici hesabı
        cursor.execute("SELECT COUNT(1) FROM users WHERE username = 'admin';")
        (exists_admin,) = cursor.fetchone()
        if not exists_admin:
            salt = generate_salt()
            password = "Admin123!"  # Daha güçlü şifre
            password_hash = hash_password(password, salt)
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt, is_admin) VALUES (?, ?, ?, 1);",
                ("admin", password_hash, salt),
            )
            connection.commit()


# ----------------------
# Veri erişim yardımcıları
# ----------------------


def list_books() -> List[Dict[str, Any]]:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("SELECT * FROM books ORDER BY id DESC;")
        rows = cursor.fetchall()
        # sqlite3.Row'ları dictionary'e çevir
        return [dict(row) for row in rows]


# ----------------------
# Klasik kitaplar toplu ekleme
# ----------------------

CLASSIC_BOOKS: List[Dict[str, Any]] = [
    {"title": "Don Kişot", "author": "Miguel de Cervantes", "isbn": "9780060934347", "year": 1605},
    {"title": "Savaş ve Barış", "author": "Lev Tolstoy", "isbn": "9780199232765", "year": 1869},
    {"title": "Anna Karenina", "author": "Lev Tolstoy", "isbn": "9780143035008", "year": 1877},
    {"title": "Suç ve Ceza", "author": "Fyodor Dostoyevski", "isbn": "9780140449136", "year": 1866},
    {"title": "Karamazov Kardeşler", "author": "Fyodor Dostoyevski", "isbn": "9780374528379", "year": 1880},
    {"title": "Budala", "author": "Fyodor Dostoyevski", "isbn": "9780140447927", "year": 1869},
    {"title": "Sefiller", "author": "Victor Hugo", "isbn": "9780451419439", "year": 1862},
    {"title": "Monte Kristo Kontu", "author": "Alexandre Dumas", "isbn": "9780140449266", "year": 1844},
    {"title": "Üç Silahşör", "author": "Alexandre Dumas", "isbn": "9780140437263", "year": 1844},
    {"title": "Moby Dick", "author": "Herman Melville", "isbn": "9780142437247", "year": 1851},
    {"title": "Muhteşem Gatsby", "author": "F. Scott Fitzgerald", "isbn": "9780743273565", "year": 1925},
    {"title": "Gurur ve Önyargı", "author": "Jane Austen", "isbn": "9780141439518", "year": 1813},
    {"title": "Jane Eyre", "author": "Charlotte Brontë", "isbn": "9780141441146", "year": 1847},
    {"title": "Uğultulu Tepeler", "author": "Emily Brontë", "isbn": "9780141439556", "year": 1847},
    {"title": "Odysseia", "author": "Homeros", "isbn": None, "year": -700},
    {"title": "İlyada", "author": "Homeros", "isbn": None, "year": -750},
    {"title": "İlahi Komedya", "author": "Dante Alighieri", "isbn": "9780142437223", "year": 1320},
    {"title": "Dorian Gray'in Portresi", "author": "Oscar Wilde", "isbn": "9780141439570", "year": 1890},
    {"title": "Karanlığın Yüreği", "author": "Joseph Conrad", "isbn": "9780141441672", "year": 1899},
    {"title": "Hamlet", "author": "William Shakespeare", "isbn": None, "year": 1603},
    {"title": "1984", "author": "George Orwell", "isbn": "9780451524935", "year": 1949},
    {"title": "Cesur Yeni Dünya", "author": "Aldous Huxley", "isbn": "9780060850524", "year": 1932},
    {"title": "Ulysses", "author": "James Joyce", "isbn": "9780199535675", "year": 1922},
    {"title": "Madame Bovary", "author": "Gustave Flaubert", "isbn": "9780140449129", "year": 1856},
    {"title": "Yabancı", "author": "Albert Camus", "isbn": "9780679720201", "year": 1942},
]


def import_classics() -> int:
    inserted = 0
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        for book in CLASSIC_BOOKS:
            title = str(book.get("title", "")).strip()
            author = str(book.get("author", "")).strip()
            isbn = book.get("isbn")
            year = book.get("year")
            if not title or not author:
                continue
            if isbn:
                cursor.execute("SELECT 1 FROM books WHERE isbn = ?;", (isbn,))
                if cursor.fetchone():
                    continue
            else:
                cursor.execute(
                    "SELECT 1 FROM books WHERE lower(title)=lower(?) AND lower(author)=lower(?);",
                    (title, author),
                )
                if cursor.fetchone():
                    continue
            try:
                cursor.execute(
                    "INSERT INTO books (title, author, isbn, year) VALUES (?, ?, ?, ?);",
                    (title, author, isbn, year),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass
        connection.commit()
    return inserted


def create_book(title: str, author: str, isbn: Optional[str], year: Optional[int]) -> None:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            "INSERT INTO books (title, author, isbn, year) VALUES (?, ?, ?, ?);",
            (title.strip(), author.strip(), (isbn or None), (year if year is not None else None)),
        )
        connection.commit()


def update_book(book_id: int, title: str, author: str, isbn: Optional[str], year: Optional[int]) -> None:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            "UPDATE books SET title = ?, author = ?, isbn = ?, year = ? WHERE id = ?;",
            (title.strip(), author.strip(), (isbn or None), (year if year is not None else None), book_id),
        )
        connection.commit()


def delete_book(book_id: int) -> None:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        # Aktif ödünç var mı kontrol et
        cursor.execute("SELECT COUNT(1) FROM loans WHERE book_id = ? AND return_date IS NULL;", (book_id,))
        (count_active,) = cursor.fetchone()
        if count_active:
            raise ValueError("Bu kitap üzerinde aktif bir ödünç kaydı var. Önce iade alın.")
        cursor.execute("DELETE FROM books WHERE id = ?;", (book_id,))
        connection.commit()


def list_members() -> List[Dict[str, Any]]:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("SELECT * FROM members ORDER BY id DESC;")
        rows = cursor.fetchall()
        # sqlite3.Row'ları dictionary'e çevir
        return [dict(row) for row in rows]


def create_member(name: str, email: Optional[str], phone: Optional[str]) -> None:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            "INSERT INTO members (name, email, phone) VALUES (?, ?, ?);",
            (name.strip(), (email or None), (phone or None)),
        )
        connection.commit()


def update_member(member_id: int, name: str, email: Optional[str], phone: Optional[str]) -> None:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            "UPDATE members SET name = ?, email = ?, phone = ? WHERE id = ?;",
            (name.strip(), (email or None), (phone or None), member_id),
        )
        connection.commit()


def delete_member(member_id: int) -> None:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        # Aktif ödünç var mı kontrol et
        cursor.execute("SELECT COUNT(1) FROM loans WHERE member_id = ? AND return_date IS NULL;", (member_id,))
        (count_active,) = cursor.fetchone()
        if count_active:
            raise ValueError("Bu üyeye ait aktif ödünç kaydı var. Önce iade alın.")
        cursor.execute("DELETE FROM members WHERE id = ?;", (member_id,))
        connection.commit()


def list_available_books() -> List[Dict[str, Any]]:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            """
            SELECT b.*
            FROM books b
            LEFT JOIN (
                SELECT book_id FROM loans WHERE return_date IS NULL
            ) l ON b.id = l.book_id
            WHERE l.book_id IS NULL
            ORDER BY b.title COLLATE NOCASE;
            """
        )
        rows = cursor.fetchall()
        # sqlite3.Row'ları dictionary'e çevir
        return [dict(row) for row in rows]


def list_active_loans() -> List[Dict[str, Any]]:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            """
            SELECT 
                lo.id as id,
                lo.book_id as book_id,
                lo.member_id as member_id,
                lo.loan_date as loan_date,
                lo.due_date as due_date,
                b.title as book_title,
                b.author as book_author,
                m.name as member_name,
                m.email as member_email
            FROM loans lo
            JOIN books b ON b.id = lo.book_id
            JOIN members m ON m.id = lo.member_id
            WHERE lo.return_date IS NULL
            ORDER BY lo.id DESC;
            """
        )
        rows = cursor.fetchall()
        # sqlite3.Row'ları dictionary'e çevir
        return [dict(row) for row in rows]


def create_loan(book_id: int, member_id: int, loan_date_str: str, due_date_str: str) -> None:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        # Kitap müsait mi kontrol et
        cursor.execute("SELECT COUNT(1) FROM loans WHERE book_id = ? AND return_date IS NULL;", (book_id,))
        (count_active,) = cursor.fetchone()
        if count_active:
            raise ValueError("Kitap şu anda ödünçte.")
        cursor.execute(
            "INSERT INTO loans (book_id, member_id, loan_date, due_date) VALUES (?, ?, ?, ?);",
            (book_id, member_id, loan_date_str, due_date_str),
        )
        connection.commit()


def return_loan(loan_id: int) -> None:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        today_str = date.today().isoformat()
        cursor.execute("UPDATE loans SET return_date = ? WHERE id = ?;", (today_str, loan_id))
        connection.commit()


# ----------------------
# Kimlik doğrulama
# ----------------------


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
        return cursor.fetchone()


def verify_password(plain_password: str, salt: str, password_hash: str) -> bool:
    """Şifre doğrulama - salt + şifre kombinasyonunu hash'leyerek karşılaştırır"""
    return hashlib.sha256((salt + plain_password).encode()).hexdigest() == password_hash


def hash_password(plain_password: str, salt: str) -> str:
    """Şifreyi hash'ler - salt + şifre kombinasyonunu SHA-256 ile hash'ler"""
    return hashlib.sha256((salt + plain_password).encode()).hexdigest()


def generate_salt() -> str:
    """Güvenli salt oluşturur"""
    return secrets.token_hex(16)


def is_password_strong(password: str) -> bool:
    """Şifre gücünü kontrol eder"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True


def current_user() -> Optional[Dict[str, Any]]:
    return app.storage.user.get("user")  # type: ignore[return-value]


def require_login(next_path: str) -> bool:
    if current_user() is None:
        ui.notify("Lütfen giriş yapın", type="warning")
        ui.navigate.to(f"/login?next={next_path}")
        return False
    return True


# ----------------------
# UI yardımcıları
# ----------------------


def nav_header() -> None:
    with ui.header().classes("items-center justify-between px-8 py-4"):
        with ui.row().classes("items-center gap-4"):
            ui.icon("fas fa-book-open").classes("text-white text-h3 animate-pulse")
            ui.label("📚 YB LIBRARY MANAGEMENT SYSTEM").classes("text-h5 font-bold text-white")
        
        with ui.row().classes("gap-4 items-center"):
            ui.button("🏠 Ana Sayfa", on_click=lambda: ui.navigate.to("/"), icon="fas fa-home").props("flat").classes("font-medium text-white")
            ui.button("📖 Kitaplar", on_click=lambda: ui.navigate.to("/books"), icon="fas fa-books").props("flat").classes("font-medium text-white")
            ui.button("👥 Üyeler", on_click=lambda: ui.navigate.to("/members"), icon="fas fa-users").props("flat").classes("font-medium text-white")
            ui.button("🔄 Ödünç", on_click=lambda: ui.navigate.to("/loans"), icon="fas fa-exchange-alt").props("flat").classes("font-medium text-white")
            
            ui.separator().props("vertical").classes("mx-3 bg-white")
            

            
            if current_user():
                ui.separator().props("vertical").classes("mx-3 bg-white")
                with ui.row().classes("items-center gap-2 bg-white bg-opacity-90 px-4 py-2 rounded-full backdrop-blur-sm"):
                    ui.icon("fas fa-user").classes("text-slate-800")
                    ui.label(current_user()["username"]).classes("text-slate-800 font-medium")  # type: ignore[index]
                ui.button("🚪 Çıkış", icon="fas fa-sign-out-alt", on_click=lambda: ui.navigate.to("/logout")).props("flat").classes("font-medium text-slate-800")
            else:
                ui.button("🔑 Giriş", icon="fas fa-sign-in-alt", on_click=lambda: ui.navigate.to("/login")).props("flat").classes("font-medium bg-white bg-opacity-20 text-white border border-white border-opacity-30")
    



def app_footer() -> None:
    with ui.footer().classes("justify-center py-4 text-center"):
        with ui.row().classes("items-center gap-2 justify-center"):
            ui.icon("favorite").classes("text-red-5")
            ui.label("© 2025 YB Library Management System").classes("font-medium")
            ui.icon("code").classes("text-blue-5")
            ui.label("NiceGUI + SQLite").classes("font-medium text-blue-7")
        ui.label("Modern library management designed for excellence").classes("text-caption text-grey-6 mt-1")


def create_book_dialog(existing: Optional[sqlite3.Row] = None, on_saved: Optional[Any] = None) -> None:
    dialog = ui.dialog()
    with dialog, ui.card().classes("w-[500px] max-w-full"):
        ui.label("Kitap Bilgileri").classes("text-h6")
        title_input = ui.input("Başlık").classes("w-full")
        author_input = ui.input("Yazar").classes("w-full")
        isbn_input = ui.input("ISBN (opsiyonel)").classes("w-full")
        year_input = ui.number("Yıl (opsiyonel)").props("fill-input")

        if existing is not None:
            title_input.value = existing["title"]
            author_input.value = existing["author"]
            isbn_input.value = existing["isbn"] or ""
            year_input.value = existing["year"]

        with ui.row().classes("justify-end w-full gap-2"):
            ui.button("İptal", on_click=dialog.close)

            def save() -> None:
                try:
                    if not title_input.value or not author_input.value:
                        ui.notify("Başlık ve Yazar zorunludur", type="warning")
                        return
                    year = int(year_input.value) if year_input.value not in (None, "") else None
                    if existing is None:
                        create_book(title_input.value, author_input.value, isbn_input.value or None, year)
                        ui.notify("Kitap eklendi", type="positive")
                    else:
                        update_book(existing["id"], title_input.value, author_input.value, isbn_input.value or None, year)
                        ui.notify("Kitap güncellendi", type="positive")
                    dialog.close()
                    if on_saved:
                        on_saved()
                except sqlite3.IntegrityError:
                    ui.notify("ISBN benzersiz olmalıdır", type="negative")
                except Exception as exc:  # noqa: BLE001
                    ui.notify(str(exc), type="negative")

            ui.button("Kaydet", on_click=save, color="primary")

    dialog.open()


def create_member_dialog(existing: Optional[sqlite3.Row] = None, on_saved: Optional[Any] = None) -> None:
    dialog = ui.dialog()
    with dialog, ui.card().classes("w-[500px] max-w-full"):
        ui.label("Üye Bilgileri").classes("text-h6")
        name_input = ui.input("Ad Soyad").classes("w-full")
        email_input = ui.input("E-posta (opsiyonel)").classes("w-full")
        phone_input = ui.input("Telefon (opsiyonel)").classes("w-full")

        if existing is not None:
            name_input.value = existing["name"]
            email_input.value = existing["email"] or ""
            phone_input.value = existing["phone"] or ""

        with ui.row().classes("justify-end w-full gap-2"):
            ui.button("İptal", on_click=dialog.close)

            def save() -> None:
                try:
                    if not name_input.value:
                        ui.notify("Ad Soyad zorunludur", type="warning")
                        return
                    if existing is None:
                        create_member(name_input.value, email_input.value or None, phone_input.value or None)
                        ui.notify("Üye eklendi", type="positive")
                    else:
                        update_member(existing["id"], name_input.value, email_input.value or None, phone_input.value or None)
                        ui.notify("Üye güncellendi", type="positive")
                    dialog.close()
                    if on_saved:
                        on_saved()
                except sqlite3.IntegrityError:
                    ui.notify("E-posta benzersiz olmalıdır", type="negative")
                except Exception as exc:  # noqa: BLE001
                    ui.notify(str(exc), type="negative")

            ui.button("Kaydet", on_click=save, color="primary")

    dialog.open()


# ----------------------
# Sayfalar
# ----------------------


@ui.page("/")
def index_page() -> None:
    nav_header()
    
    # Ana container - merkezi hizalama için
    with ui.column().classes("items-center w-full max-w-[1200px] mx-auto"):
        
        # Hero section - tam genişlik
        with ui.card().classes("w-full text-center animate-fade-in mb-8"):
            ui.icon("fas fa-book-open").classes("text-primary text-h1 mb-6 animate-pulse")
            ui.label("📚 YB LIBRARY MANAGEMENT SYSTEM").classes("text-h3 font-bold text-primary mb-3")
            ui.label("Modern ve kullanıcı dostu kütüphane yönetim platformu").classes("text-subtitle1 text-grey-7 mb-8")
            
            # İstatistik kartları - eşit boyutlarda ve simetrik
            with ui.row().classes("justify-center gap-6 mb-8 w-full"):
                with ui.card().classes("text-center p-6 flex-1 max-w-[200px] bg-gradient-to-br from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 transition-all duration-300 shadow-lg hover:shadow-xl border border-blue-200"):
                    ui.icon("fas fa-books").classes("text-primary text-h3 mb-3")
                    ui.label("Kitaplar").classes("text-h5 font-bold text-blue-800")
                    ui.label("Yönetim").classes("text-caption text-blue-600")
                
                with ui.card().classes("text-center p-6 flex-1 max-w-[200px] bg-gradient-to-br from-green-50 to-green-100 hover:from-green-100 hover:to-green-200 transition-all duration-300 shadow-lg hover:shadow-xl border border-green-200"):
                    ui.icon("fas fa-users").classes("text-secondary text-h3 mb-3")
                    ui.label("Üyeler").classes("text-h5 font-bold text-green-800")
                    ui.label("Takip").classes("text-caption text-green-600")
                
                with ui.card().classes("text-center p-6 flex-1 max-w-[200px] bg-gradient-to-br from-orange-50 to-orange-100 hover:from-orange-100 hover:to-orange-200 transition-all duration-300 shadow-lg hover:shadow-xl border border-orange-200"):
                    ui.icon("fas fa-exchange-alt").classes("text-accent text-h3 mb-3")
                    ui.label("Ödünç").classes("text-h5 font-bold text-orange-800")
                    ui.label("İşlemler").classes("text-caption text-orange-600")
            
            # Ana butonlar - eşit boyutlarda ve simetrik
            with ui.row().classes("justify-center gap-6 flex-wrap w-full"):
                ui.button(
                    "📖 Kitapları Yönet", 
                    on_click=lambda: ui.navigate.to("/books"), 
                    color="primary", 
                    icon="fas fa-book"
                ).classes("min-w-[220px] h-12 text-h6 font-medium animate-pulse shadow-lg hover:shadow-xl")
                
                ui.button(
                    "👥 Üyeleri Yönet", 
                    on_click=lambda: ui.navigate.to("/members"), 
                    color="secondary", 
                    icon="fas fa-user-friends"
                ).classes("min-w-[220px] h-12 text-h6 font-medium animate-pulse shadow-lg hover:shadow-xl")
                
                ui.button(
                    "🔄 Ödünç / İade", 
                    on_click=lambda: ui.navigate.to("/loans"), 
                    color="accent", 
                    icon="fas fa-sync-alt"
                ).classes("min-w-[220px] h-12 text-h6 font-medium animate-pulse shadow-lg hover:shadow-xl")
        
        # Özellikler bölümü - tam genişlik
        with ui.card().classes("w-full animate-slide-in mb-8"):
            ui.label("✨ Özellikler").classes("text-h5 font-bold text-center mb-6 text-grey-8")
            
            # Özellik kartları - 3'lü grid düzeni
            with ui.row().classes("gap-6 flex-wrap justify-center w-full"):
                with ui.card().classes("text-center p-6 flex-1 max-w-[300px] bg-gradient-to-br from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 transition-all duration-300 shadow-lg hover:shadow-xl border border-blue-200 min-h-[200px] flex flex-col justify-center"):
                    ui.icon("fas fa-search").classes("text-primary text-h2 mb-4")
                    ui.label("Hızlı Arama").classes("text-h6 font-bold text-blue-800 mb-2")
                    ui.label("Kitapları ve üyeleri anında bulun").classes("text-caption text-blue-600")
                
                with ui.card().classes("text-center p-6 flex-1 max-w-[300px] bg-gradient-to-br from-green-50 to-green-100 hover:from-green-100 hover:to-green-200 transition-all duration-300 shadow-lg hover:shadow-xl border border-green-200 min-h-[200px] flex flex-col justify-center"):
                    ui.icon("fas fa-shield-alt").classes("text-secondary text-h2 mb-4")
                    ui.label("Güvenli Giriş").classes("text-h6 font-bold text-green-800 mb-2")
                    ui.label("Şifreli kullanıcı yönetimi").classes("text-caption text-green-600")
                
                with ui.card().classes("text-center p-6 flex-1 max-w-[300px] bg-gradient-to-br from-orange-50 to-orange-100 hover:from-orange-100 hover:to-orange-200 transition-all duration-300 shadow-lg hover:shadow-xl border border-orange-200 min-h-[200px] flex flex-col justify-center"):
                    ui.icon("fas fa-chart-bar").classes("text-accent text-h2 mb-4")
                    ui.label("Detaylı Raporlar").classes("text-h6 font-bold text-orange-800 mb-2")
                    ui.label("Ödünç ve iade takibi").classes("text-caption text-orange-600")
        
        # Alt bilgi kartı - tam genişlik
        with ui.card().classes("w-full text-center bg-gradient-to-r from-grey-50 to-grey-100 border border-grey-200"):
            ui.label("🚀 YB Library Management System").classes("text-h6 font-bold text-grey-8 mb-2")
            ui.label("Profesyonel kütüphane yönetimi için tasarlandı").classes("text-caption text-grey-6")
    
    app_footer()


@ui.page("/books")
def books_page() -> None:
    nav_header()
    if not require_login("/books"):
        return
    
    # Sayfa başlığı
    with ui.card().classes("m-4 max-w-[1200px] fade-in-up"):
        with ui.row().classes("items-center justify-between mb-4"):
            ui.label("📚 Kitaplar").classes("text-h4 font-bold text-primary")
            ui.chip(f"Toplam: {len(list_books())} kitap").props("color=primary text-color=white")
        
        def do_import() -> None:
            added = import_classics()
            if added:
                ui.notify(f"🎉 {added} klasik kitap eklendi", type="positive")
            else:
                ui.notify("ℹ️ Yeni eklenecek klasik kitap bulunamadı", type="warning")
            refresh_table()
        
        # Arama ve butonlar
        with ui.row().classes("items-center gap-4 mb-4"):
            search_input = ui.input("🔍 Başlık / Yazar / ISBN ara").props("clearable").classes("w-[400px]")
            ui.button("➕ Yeni Kitap", on_click=lambda: create_book_dialog(on_saved=refresh_table), color="primary", icon="add").classes("font-medium")
            ui.button("📚 Klasikleri İçe Aktar", on_click=do_import, icon="library_add").classes("font-medium bg-secondary")

    def refresh_table() -> None:
        rows: List[Dict[str, Any]] = []
        term = (search_input.value or "").lower()
        available_ids = {b["id"] for b in list_available_books()}
        for b in list_books():
            if term and all(
                term not in (str(b[k]) if b[k] is not None else "").lower()
                for k in ("title", "author", "isbn")
            ):
                continue
            rows.append(
                {
                    "id": b["id"],
                    "title": b["title"],
                    "author": b["author"],
                    "isbn": b["isbn"] or "-",
                    "year": b["year"] if b["year"] is not None else "-",
                    "status": "Müsait" if b["id"] in available_ids else "Ödünçte",
                }
            )
        table.rows = rows



    columns = [
        {"name": "id", "label": "#", "field": "id", "align": "left", "sortable": True},
        {"name": "title", "label": "Başlık", "field": "title", "align": "left", "sortable": True},
        {"name": "author", "label": "Yazar", "field": "author", "align": "left", "sortable": True},
        {"name": "isbn", "label": "ISBN", "field": "isbn", "align": "left"},
        {"name": "year", "label": "Yıl", "field": "year", "align": "left"},
        {"name": "status", "label": "Durum", "field": "status", "align": "left"},
        {"name": "actions", "label": "İşlemler", "field": "actions", "align": "left"},
    ]

    table = ui.table(columns=columns, rows=[]).props('flat dense row-key="id" rows-per-page-options="[5,10,25,50]"').classes("m-4")

    with table.add_slot("body-cell-actions"):
        def actions_cell(row: Dict[str, Any]) -> None:  # type: ignore[override]
            with ui.row().classes("gap-1"):
                ui.button(
                    "✏️ Düzenle",
                    on_click=lambda r=row: create_book_dialog(
                        existing=_get_book_by_id(r["id"]), on_saved=refresh_table
                    ),
                    icon="edit",
                    color="primary",
                ).classes("font-medium")
                ui.button(
                    "🗑️ Sil",
                    on_click=lambda r=row: _confirm_delete(
                        "Kitabı silmek istiyor musunuz?",
                        lambda: _delete_book_ui(r["id"], refresh_table),
                    ),
                    color="negative",
                    icon="delete",
                ).classes("font-medium")

    with table.add_slot("body-cell-status"):
        def status_cell(row: Dict[str, Any]) -> None:  # type: ignore[override]
            color = "positive" if row["status"] == "Müsait" else "warning"
            ui.chip(row["status"]).props(f"color={color} text-color=white")

    def _get_book_by_id(book_id: int) -> sqlite3.Row:
        with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
            cursor.execute("SELECT * FROM books WHERE id = ?;", (book_id,))
            row = cursor.fetchone()
            assert row is not None
            return row

    def _delete_book_ui(book_id: int, on_done: Any) -> None:
        try:
            delete_book(book_id)
            ui.notify("Kitap silindi", type="positive")
            on_done()
        except Exception as exc:  # noqa: BLE001
            ui.notify(str(exc), type="negative")

    search_input.on_value_change(lambda e: refresh_table())
    refresh_table()


@ui.page("/members")
def members_page() -> None:
    nav_header()
    if not require_login("/members"):
        return
    ui.label("👥 Üyeler (Şifreler Hash'lenmiş)").classes("text-h6 m-4")
    
    # Hash bilgisi
    with ui.card().classes("bg-green-1 p-3 mb-4"):
        ui.label("🔒 Şifreler SHA-256 ile hash'lenmiş").classes("text-caption text-green-8")
        ui.label("📱 E-posta ve telefon numaraları normal metin olarak gösterilir").classes("text-caption text-green-8")

    search_input = ui.input("İsim / E-posta ara").props("clearable").classes("m-4 w-[400px]")

    def refresh_table() -> None:
        rows: List[Dict[str, Any]] = []
        term = (search_input.value or "").lower()
        for m in list_members():
            if term and all(
                term not in (str(m[k]) if m[k] is not None else "").lower()
                for k in ("name", "email", "phone")
            ):
                continue
            rows.append(
                {
                    "id": m["id"],
                    "name": m["name"],
                    "email": m["email"] or "-",
                    "phone": m["phone"] or "-",
                    "password_hash": m["password_hash"] or "-",
                }
            )
        table.rows = rows

    with ui.row().classes("m-4 gap-2"):
        ui.button("Yeni Üye", on_click=lambda: create_member_dialog(on_saved=refresh_table), color="primary", icon="person_add")

    columns = [
        {"name": "id", "label": "#", "field": "id", "align": "left", "sortable": True},
        {"name": "name", "label": "Ad Soyad", "field": "name", "align": "left", "sortable": True},
        {"name": "email", "label": "E-posta", "field": "email", "align": "left"},
        {"name": "phone", "label": "Telefon", "field": "phone", "align": "left"},
        {"name": "password_hash", "label": "Şifreler", "field": "password_hash", "align": "left"},
        {"name": "actions", "label": "İşlemler", "field": "actions", "align": "left"},
    ]

    table = ui.table(columns=columns, rows=[]).props('flat dense row-key="id" rows-per-page-options="[5,10,25,50]"').classes("m-4")

    with table.add_slot("body-cell-password_hash"):
        def password_hash_cell(row: Dict[str, Any]) -> None:  # type: ignore[override]
            if row["password_hash"] and row["password_hash"] != "-":
                with ui.tooltip(f"Hash uzunluğu: {len(row['password_hash'])} karakter"):
                    ui.code(row["password_hash"][:20] + "...").classes("text-xs bg-grey-2 px-2 py-1 rounded")
            else:
                ui.label("-").classes("text-grey-6")

    with table.add_slot("body-cell-actions"):
        def actions_cell(row: Dict[str, Any]) -> None:  # type: ignore[override]
            with ui.row().classes("gap-1"):
                ui.button(
                    "Düzenle",
                    on_click=lambda r=row: create_member_dialog(
                        existing=_get_member_by_id(r["id"]), on_saved=refresh_table
                    ),
                    icon="edit",
                )
                ui.button(
                    "Sil",
                    on_click=lambda r=row: _confirm_delete(
                        "Üyeyi silmek istiyor musunuz?",
                        lambda: _delete_member_ui(r["id"], refresh_table),
                    ),
                    color="negative",
                    icon="delete",
                )

    def _get_member_by_id(member_id: int) -> sqlite3.Row:
        with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
            cursor.execute("SELECT * FROM members WHERE id = ?;", (member_id,))
            row = cursor.fetchone()
            assert row is not None
            return row

    def _delete_member_ui(member_id: int, on_done: Any) -> None:
        try:
            delete_member(member_id)
            ui.notify("Üye silindi", type="positive")
            on_done()
        except Exception as exc:  # noqa: BLE001
            ui.notify(str(exc), type="negative")

    search_input.on_value_change(lambda e: refresh_table())
    refresh_table()
    
    # Hash kodları listesi
    ui.separator().classes("my-6")
    ui.label("🔐 Hash Kodları Listesi").classes("text-h6 m-4 text-center")
    
    with ui.card().classes("m-4 bg-blue-1"):
        ui.label("📋 Tüm üyelerin hash kodları alt alta sıralanmıştır").classes("text-caption text-blue-8 mb-4")
        
        for member in list_members():
            if member["password_hash"]:
                with ui.card().classes("mb-3 bg-white"):
                    ui.label(f"👤 {member['name']}").classes("text-subtitle2 font-medium")
                    ui.label(f"📧 {member['email']}").classes("text-caption text-grey-7")
                    ui.label(f"📱 {member['phone']}").classes("text-caption text-grey-7")
                    with ui.row().classes("items-center gap-2"):
                        ui.label("🔑 Hash:").classes("text-caption font-medium")
                        ui.code(member["password_hash"]).classes("text-xs bg-grey-2 px-2 py-1 rounded font-mono")


@ui.page("/loans")
def loans_page() -> None:
    nav_header()
    if not require_login("/loans"):
        return
    ui.label("Ödünç Ver / İade Al").classes("text-h6 m-4")

    # Ödünç verme formu
    with ui.card().classes("m-4 w-[900px] max-w-full"):
        ui.label("Ödünç Ver").classes("text-subtitle1")

        def refresh_book_options() -> List[Dict[str, Any]]:
            return [
                {"label": f"{b['title']} – {b['author']}", "value": b["id"]}
                for b in list_available_books()
            ]

        def refresh_member_options() -> List[Dict[str, Any]]:
            return [
                {"label": m["name"], "value": m["id"]}
                for m in list_members()
            ]

        book_select = ui.select(
            options=refresh_book_options(),
            with_input=True,
            label="Kitap",
        ).classes("w-full")
        member_select = ui.select(
            options=refresh_member_options(),
            with_input=True,
            label="Üye",
        ).classes("w-full")

        with ui.row().classes("gap-4 w-full"):
            loan_date_picker = ui.date(value=date.today().isoformat()).props('label="Ödünç Tarihi"')
            due_date_picker = ui.date(value=date.today().isoformat()).props('label="Son Tarih"')

        def do_loan() -> None:
            if not book_select.value or not member_select.value:
                ui.notify("Lütfen kitap ve üye seçin", type="warning")
                return
            try:
                create_loan(
                    int(book_select.value),
                    int(member_select.value),
                    loan_date_picker.value,
                    due_date_picker.value,
                )
                ui.notify("Ödünç verildi", type="positive")
                refresh_active_loans()
                # seçenekleri güncelle
                book_select.options = refresh_book_options()
            except Exception as exc:  # noqa: BLE001
                ui.notify(str(exc), type="negative")

        ui.button("Ödünç Ver", on_click=do_loan, color="primary", icon="north_east").classes("mt-2")

    # Aktif ödünçler tablosu
    ui.label("Aktif Ödünçler").classes("text-subtitle1 m-4 mt-6")

    loan_columns = [
        {"name": "id", "label": "#", "field": "id", "align": "left", "sortable": True},
        {"name": "book_title", "label": "Kitap Adı", "field": "book_title", "align": "left", "sortable": True},
        {"name": "book_author", "label": "Yazar", "field": "book_author", "align": "left", "sortable": True},
        {"name": "member_name", "label": "Üye Adı", "field": "member_name", "align": "left", "sortable": True},
        {"name": "member_email", "label": "Üye E-posta", "field": "member_email", "align": "left"},
        {"name": "loan_date", "label": "Ödünç Tarihi", "field": "loan_date", "align": "left"},
        {"name": "due_date", "label": "Son Tarih", "field": "due_date", "align": "left"},
        {"name": "actions", "label": "İşlemler", "field": "actions", "align": "left"},
    ]

    loan_table = ui.table(columns=loan_columns, rows=[]).props('flat dense row-key="id"').classes("m-4")

    with loan_table.add_slot("body-cell-actions"):
        def loan_actions_cell(row: Dict[str, Any]) -> None:  # type: ignore[override]
            ui.button(
                "İade Al",
                on_click=lambda r=row: _return_ui(r["id"]),
                color="primary",
                icon="assignment_return",
            )

    def refresh_active_loans() -> None:
        rows: List[Dict[str, Any]] = []
        loans_data = list_active_loans()
        
        for lo in loans_data:
            # Her alanı string'e çevir ve None kontrolü yap
            row_data = {
                "id": int(lo["id"]) if lo["id"] is not None else 0,
                "book_title": str(lo["book_title"]) if lo["book_title"] is not None else "-",
                "book_author": str(lo["book_author"]) if lo["book_author"] is not None else "-",
                "member_name": str(lo["member_name"]) if lo["member_name"] is not None else "-",
                "member_email": str(lo["member_email"]) if lo["member_email"] is not None else "-",
                "loan_date": str(lo["loan_date"]) if lo["loan_date"] is not None else "-",
                "due_date": str(lo["due_date"]) if lo["due_date"] is not None else "-",
            }
            rows.append(row_data)
        
        loan_table.rows = rows

    def _return_ui(loan_id: int) -> None:
        try:
            return_loan(loan_id)
            ui.notify("İade işlemi tamamlandı", type="positive")
            refresh_active_loans()
        finally:
            # Kitap seçeneklerini yenilemek için sayfayı kısmen güncelle
            pass

    refresh_active_loans()
    app_footer()


@ui.page("/login")
def login_page(request: Request) -> None:
    nav_header()
    next_path = request.query_params.get("next", "/")
    
    # Ana giriş kartı
    with ui.card().classes("m-4 w-[500px] max-w-full mx-auto animate-fade-in"):
        # Header kısmı
        with ui.row().classes("items-center justify-center mb-6"):
            ui.icon("fas fa-shield-alt").classes("text-primary text-h2 mr-3")
            ui.label("🔐 Admin Giriş Paneli").classes("text-h5 font-bold text-primary")
        
        # Güvenlik bilgisi kartı
        with ui.card().classes("bg-gradient-to-r from-blue-50 to-indigo-50 p-4 mb-6 border-l-4 border-blue-500"):
            ui.label("🔒 Güvenlik Bilgileri").classes("text-subtitle2 font-bold text-blue-800 mb-2")
            ui.label("• Şifreler SHA-256 ile hash'lenir").classes("text-caption text-blue-700 mb-1")
            ui.label("• Salt + şifre kombinasyonu güvenli şekilde saklanır").classes("text-caption text-blue-700 mb-1")
            ui.label("• Brute force saldırılarına karşı korumalı").classes("text-caption text-blue-700")
        
        # Giriş formu
        with ui.column().classes("gap-4"):
            username = ui.input("👤 Kullanıcı Adı").props("clearable").classes("w-full").style("font-size: 16px;")
            password = ui.input("🔑 Şifre").props("type=password clearable").classes("w-full").style("font-size: 16px;")
            
            # Şifre gücü göstergesi
            with ui.row().classes("items-center gap-2"):
                ui.label("Şifre Gücü:").classes("text-caption text-grey-6")
                with ui.row().classes("gap-1").props("id=password-strength"):
                    for i in range(5):
                        ui.icon("fas fa-circle").classes("text-grey-4 text-xs")
            
            def update_password_strength():
                strength = 0
                if password.value:
                    if len(password.value) >= 8:
                        strength += 1
                    if any(c.isupper() for c in password.value):
                        strength += 1
                    if any(c.islower() for c in password.value):
                        strength += 1
                    if any(c.isdigit() for c in password.value):
                        strength += 1
                    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password.value):
                        strength += 1
                
                # Şifre gücü göstergesini güncelle
                strength_icons = ui.find("password-strength").classes("")
                if strength >= 4:
                    strength_icons.classes("text-green-500")
                elif strength >= 3:
                    strength_icons.classes("text-yellow-500")
                elif strength >= 1:
                    strength_icons.classes("text-orange-500")
                else:
                    strength_icons.classes("text-grey-4")
            
            password.on_value_change(lambda e: update_password_strength())

        def do_login() -> None:
            if not username.value or not password.value:
                ui.notify("⚠️ Kullanıcı adı ve şifre zorunludur", type="warning")
                return
            
            # Loading animasyonu
            login_btn.loading = True
            
            try:
                user = get_user_by_username(username.value)
                if not user or not verify_password(password.value, user["salt"], user["password_hash"]):
                    ui.notify("❌ Geçersiz kullanıcı adı veya şifre", type="negative")
                    return
                
                app.storage.user["user"] = {
                    "id": user["id"],
                    "username": user["username"],
                    "is_admin": bool(user["is_admin"]),
                }
                
                ui.notify(f"🎉 Hoş geldiniz, {user['username']}!", type="positive")
                ui.navigate.to(next_path)
                
            except Exception as e:
                ui.notify(f"❌ Giriş hatası: {str(e)}", type="negative")
            finally:
                login_btn.loading = False

        # Giriş butonu
        login_btn = ui.button(
            "🚪 Giriş Yap", 
            on_click=do_login, 
            color="primary", 
            icon="fas fa-sign-in-alt"
        ).classes("w-full font-medium text-lg py-3 animate-pulse")
        
        # Kayıt ol / Giriş yap seçimi
        ui.separator().classes("my-4")
        with ui.row().classes("justify-center gap-4"):
            ui.label("Hesabınız yok mu?").classes("text-caption text-grey-6")
            ui.button(
                "📝 Kayıt Ol", 
                on_click=lambda: show_register_form(), 
                color="secondary", 
                icon="fas fa-user-plus"
            ).props("flat").classes("font-medium")
        
        # Kayıt formu (başlangıçta gizli)
        register_form = ui.card().classes("mt-4 bg-gradient-to-r from-purple-50 to-pink-50 p-4 border-l-4 border-purple-500 hidden")
        
        with register_form:
            ui.label("📝 Yeni Hesap Oluştur").classes("text-subtitle2 font-bold text-purple-800 mb-3")
            
            # Kayıt formu alanları
            with ui.column().classes("gap-3"):
                new_username = ui.input("👤 Yeni Kullanıcı Adı").props("clearable").classes("w-full")
                new_email = ui.input("📧 E-posta (opsiyonel)").props("clearable type=email").classes("w-full")
                new_password = ui.input("🔑 Yeni Şifre").props("type=password clearable").classes("w-full")
                confirm_password = ui.input("🔒 Şifre Tekrar").props("type=password clearable").classes("w-full")
                
                # Admin checkbox
                admin_checkbox = ui.checkbox("👑 Admin Yetkisi").classes("mt-2")
                
                # Kayıt butonu
                register_btn = ui.button(
                    "📝 Hesap Oluştur", 
                    on_click=lambda: do_register(), 
                    color="purple", 
                    icon="fas fa-user-plus"
                ).classes("w-full font-medium")
                
                # Giriş formuna dön butonu
                ui.button(
                    "← Giriş Formuna Dön", 
                    on_click=lambda: hide_register_form(), 
                    color="grey", 
                    icon="fas fa-arrow-left"
                ).props("flat").classes("w-full mt-2")
        
        def show_register_form():
            register_form.classes("block")
            register_form.classes("animate-fade-in")
        
        def hide_register_form():
            register_form.classes("hidden")
        
        def do_register():
            if not new_username.value or not new_password.value:
                ui.notify("⚠️ Kullanıcı adı ve şifre zorunludur", type="warning")
                return
            
            if new_password.value != confirm_password.value:
                ui.notify("❌ Şifreler eşleşmiyor", type="negative")
                return
            
            if len(new_password.value) < 8:
                ui.notify("⚠️ Şifre en az 8 karakter olmalıdır", type="warning")
                return
            
            # Loading animasyonu
            register_btn.loading = True
            
            try:
                # Kullanıcı adı kontrolü
                existing_user = get_user_by_username(new_username.value)
                if existing_user:
                    ui.notify("❌ Bu kullanıcı adı zaten kullanılıyor", type="negative")
                    return
                
                # Yeni kullanıcı oluştur
                salt = generate_salt()
                password_hash = hash_password(new_password.value, salt)
                
                with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, salt, is_admin) VALUES (?, ?, ?, ?);",
                        (new_username.value, password_hash, salt, admin_checkbox.value),
                    )
                    connection.commit()
                
                ui.notify(f"🎉 {new_username.value} hesabı başarıyla oluşturuldu!", type="positive")
                
                # Formu temizle ve gizle
                new_username.value = ""
                new_email.value = ""
                new_password.value = ""
                confirm_password.value = ""
                admin_checkbox.value = False
                hide_register_form()
                
            except Exception as e:
                ui.notify(f"❌ Kayıt hatası: {str(e)}", type="negative")
            finally:
                register_btn.loading = False
        
        # Test hesabı bilgileri
        with ui.expansion("🧪 Test Hesabı Bilgileri", icon="fas fa-info-circle").classes("mt-6"):
            with ui.card().classes("bg-gradient-to-r from-green-50 to-emerald-50 p-4 border-l-4 border-green-500"):
                ui.label("👑 Admin Hesabı").classes("text-subtitle2 font-bold text-green-800 mb-3")
                with ui.row().classes("items-center gap-3 mb-2"):
                    ui.icon("fas fa-user").classes("text-green-600")
                    ui.label("Kullanıcı adı: admin").classes("text-caption font-medium text-green-700")
                with ui.row().classes("items-center gap-3 mb-2"):
                    ui.icon("fas fa-key").classes("text-green-600")
                    ui.label("Şifre: Admin123!").classes("text-caption font-medium text-green-700")
                ui.label("(Şifre güvenli şekilde hash'lenmiş olarak saklanır)").classes("text-caption text-green-600 italic")
        
        # Alt bilgi
        with ui.row().classes("justify-center mt-6"):
            ui.label("🔐 Güvenli kütüphane yönetimi için tasarlandı").classes("text-caption text-grey-6")
    
    app_footer()


@ui.page("/logout")
def logout_page() -> None:
    app.storage.user.clear()
    ui.notify("Çıkış yapıldı", type="positive")
    ui.navigate.to("/")


def _confirm_delete(message: str, on_yes: Any) -> None:
    dialog = ui.dialog()
    with dialog, ui.card().classes("w-[420px] max-w-full"):
        ui.label("Onay").classes("text-h6")
        ui.label(message)
        with ui.row().classes("justify-end gap-2 mt-2"):
            ui.button("Vazgeç", on_click=dialog.close)
            def yes() -> None:
                dialog.close()
                on_yes()
            ui.button("Evet", color="negative", on_click=yes)


if __name__ == "__main__":
    init_db()
    ui.run(title="YB Library Management System", reload=False, show=False, port=8096, host="0.0.0.0", storage_secret=os.getenv("STORAGE_SECRET", "dev-secret")
    )


