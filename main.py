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
      }
      
      /* Modern gradient arka plan */
      body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      }
      
      /* Card gölgeleri */
      .q-card {
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        border-radius: 16px;
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
      }
      
      .q-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
      }
      
      /* Button animasyonları */
      .q-btn {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: none;
        letter-spacing: 0.5px;
      }
      
      .q-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
      }
      
      /* Header güzelleştirme */
      .q-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
      }
      
      /* Table güzelleştirme */
      .q-table {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
      }
      
      .q-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
      }
      
      /* Input güzelleştirme */
      .q-input {
        border-radius: 12px;
        transition: all 0.3s ease;
      }
      
      .q-input:focus-within {
        transform: scale(1.02);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
      
      /* Chip güzelleştirme */
      .q-chip {
        border-radius: 20px;
        font-weight: 600;
        padding: 8px 16px;
      }
      
      /* Animasyonlar */
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
      
      .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
      }
      
      /* Responsive tasarım */
      @media (max-width: 768px) {
        .q-card {
          margin: 8px;
          border-radius: 12px;
        }
        
        .q-btn {
          padding: 8px 16px;
          font-size: 14px;
        }
      }
    </style>
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
            salt = secrets.token_hex(16)
            password = "admin123"
            password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt, is_admin) VALUES (?, ?, ?, 1);",
                ("admin", password_hash, salt),
            )
            connection.commit()


# ----------------------
# Veri erişim yardımcıları
# ----------------------


def list_books() -> List[sqlite3.Row]:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("SELECT * FROM books ORDER BY id DESC;")
        return cursor.fetchall()


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


def list_members() -> List[sqlite3.Row]:
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("SELECT * FROM members ORDER BY id DESC;")
        return cursor.fetchall()


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


def list_available_books() -> List[sqlite3.Row]:
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
        return cursor.fetchall()


def list_active_loans() -> List[sqlite3.Row]:
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
        return cursor.fetchall()


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
    return hashlib.sha256((salt + plain_password).encode()).hexdigest() == password_hash


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
    with ui.header().classes("items-center justify-between px-6 py-3"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("menu_book").classes("text-primary text-h4")
            ui.label("📚 Kütüphane").classes("text-h5 font-bold text-primary")
        
        with ui.row().classes("gap-3 items-center"):
            ui.button("🏠 Ana Sayfa", on_click=lambda: ui.navigate.to("/"), icon="home").props("flat").classes("font-medium")
            ui.button("📖 Kitaplar", on_click=lambda: ui.navigate.to("/books"), icon="library_books").props("flat").classes("font-medium")
            ui.button("👥 Üyeler", on_click=lambda: ui.navigate.to("/members"), icon="group").props("flat").classes("font-medium")
            ui.button("🔄 Ödünç", on_click=lambda: ui.navigate.to("/loans"), icon="sync_alt").props("flat").classes("font-medium")
            
            ui.separator().props("vertical").classes("mx-2")
            
            dark = ui.dark_mode()
            ui.button(icon="dark_mode", on_click=dark.toggle).props("round flat").classes("ml-2")
            
            if current_user():
                ui.separator().props("vertical").classes("mx-2")
                with ui.row().classes("items-center gap-2 bg-blue-1 px-3 py-1 rounded-full"):
                    ui.icon("person").classes("text-primary")
                    ui.label(current_user()["username"]).classes("font-medium text-primary")  # type: ignore[index]
                ui.button("🚪 Çıkış", icon="logout", on_click=lambda: ui.navigate.to("/logout")).props("flat").classes("font-medium")
            else:
                ui.button("🔑 Giriş", icon="login", on_click=lambda: ui.navigate.to("/login")).props("flat").classes("font-medium bg-primary text-white")


def app_footer() -> None:
    with ui.footer().classes("justify-center py-4 text-center"):
        with ui.row().classes("items-center gap-2 justify-center"):
            ui.icon("favorite").classes("text-red-5")
            ui.label("© 2025 Kütüphane Uygulaması").classes("font-medium")
            ui.icon("code").classes("text-blue-5")
            ui.label("NiceGUI + SQLite").classes("font-medium text-blue-7")
        ui.label("Modern kütüphane yönetimi için tasarlandı").classes("text-caption text-grey-6 mt-1")


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
    
    # Hero section
    with ui.card().classes("m-4 max-w-[1000px] text-center fade-in-up"):
        ui.icon("menu_book").classes("text-primary text-h1 mb-4")
        ui.label("📚 Kütüphane Yönetim Sistemi").classes("text-h3 font-bold text-primary mb-2")
        ui.label("Modern ve kullanıcı dostu kütüphane yönetim platformu").classes("text-subtitle1 text-grey-7 mb-6")
        
        # İstatistik kartları
        with ui.row().classes("justify-center gap-4 mb-6"):
            with ui.card().classes("text-center p-4 min-w-[120px] bg-blue-1"):
                ui.icon("library_books").classes("text-primary text-h4 mb-2")
                ui.label("Kitaplar").classes("text-h6 font-bold")
                ui.label("Yönetim").classes("text-caption")
            
            with ui.card().classes("text-center p-4 min-w-[120px] bg-green-1"):
                ui.icon("group").classes("text-secondary text-h4 mb-2")
                ui.label("Üyeler").classes("text-h6 font-bold")
                ui.label("Takip").classes("text-caption")
            
            with ui.card().classes("text-center p-4 min-w-[120px] bg-orange-1"):
                ui.icon("sync_alt").classes("text-accent text-h4 mb-2")
                ui.label("Ödünç").classes("text-h6 font-bold")
                ui.label("İşlemler").classes("text-caption")
        
        # Ana butonlar
        with ui.row().classes("justify-center gap-4 flex-wrap"):
            ui.button(
                "📖 Kitapları Yönet", 
                on_click=lambda: ui.navigate.to("/books"), 
                color="primary", 
                icon="library_books",
                size="lg"
            ).classes("min-w-[200px]")
            
            ui.button(
                "👥 Üyeleri Yönet", 
                on_click=lambda: ui.navigate.to("/members"), 
                color="secondary", 
                icon="group",
                size="lg"
            ).classes("min-w-[200px]")
            
            ui.button(
                "🔄 Ödünç / İade", 
                on_click=lambda: ui.navigate.to("/loans"), 
                color="accent", 
                icon="sync_alt",
                size="lg"
            ).classes("min-w-[200px]")
    
    # Özellikler bölümü
    with ui.card().classes("m-4 max-w-[1000px] fade-in-up"):
        ui.label("✨ Özellikler").classes("text-h5 font-bold text-center mb-4")
        with ui.row().classes("gap-4 flex-wrap justify-center"):
            with ui.card().classes("text-center p-4 min-w-[200px] bg-blue-1"):
                ui.icon("search").classes("text-primary text-h3 mb-2")
                ui.label("Hızlı Arama").classes("text-subtitle1 font-bold")
                ui.label("Kitapları ve üyeleri anında bulun").classes("text-caption")
            
            with ui.card().classes("text-center p-4 min-w-[200px] bg-green-1"):
                ui.icon("security").classes("text-secondary text-h3 mb-2")
                ui.label("Güvenli Giriş").classes("text-subtitle1 font-bold")
                ui.label("Şifreli kullanıcı yönetimi").classes("text-caption")
            
            with ui.card().classes("text-center p-4 min-w-[200px] bg-orange-1"):
                ui.icon("analytics").classes("text-accent text-h3 mb-2")
                ui.label("Detaylı Raporlar").classes("text-subtitle1 font-bold")
                ui.label("Ödünç ve iade takibi").classes("text-caption")
    
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
        
        # Arama ve butonlar
        with ui.row().classes("items-center gap-4 mb-4"):
            search_input = ui.input("🔍 Başlık / Yazar / ISBN ara").props("clearable").classes("w-[400px]")
            ui.button("➕ Yeni Kitap", on_click=lambda: create_book_dialog(on_saved=refresh_table), color="primary", icon="add").classes("font-medium")
            ui.button("📚 Klasikleri İçe Aktar", on_click=do_import, icon="library_add").classes("font-medium bg-secondary")
        
        def do_import() -> None:
            added = import_classics()
            if added:
                ui.notify(f"🎉 {added} klasik kitap eklendi", type="positive")
            else:
                ui.notify("ℹ️ Yeni eklenecek klasik kitap bulunamadı", type="warning")
            refresh_table()

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
                    size="sm",
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
                    size="sm",
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
    ui.label("Üyeler").classes("text-h6 m-4")

    search_input = ui.input("İsim / E-posta ara").props("clearable").classes("m-4 w-[400px]")

    def refresh_table() -> None:
        rows: List[Dict[str, Any]] = []
        term = (search_input.value or "").lower()
        for m in list_members():
            if term and all(
                term not in (str(m[k]) if m[k] is not None else "").lower()
                for k in ("name", "email")
            ):
                continue
            rows.append(
                {
                    "id": m["id"],
                    "name": m["name"],
                    "email": m["email"] or "-",
                    "phone": m["phone"] or "-",
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
        {"name": "actions", "label": "İşlemler", "field": "actions", "align": "left"},
    ]

    table = ui.table(columns=columns, rows=[]).props('flat dense row-key="id" rows-per-page-options="[5,10,25,50]"').classes("m-4")

    with table.add_slot("body-cell-actions"):
        def actions_cell(row: Dict[str, Any]) -> None:  # type: ignore[override]
            with ui.row().classes("gap-1"):
                ui.button(
                    "Düzenle",
                    on_click=lambda r=row: create_member_dialog(
                        existing=_get_member_by_id(r["id"]), on_saved=refresh_table
                    ),
                    size="sm",
                    icon="edit",
                )
                ui.button(
                    "Sil",
                    on_click=lambda r=row: _confirm_delete(
                        "Üyeyi silmek istiyor musunuz?",
                        lambda: _delete_member_ui(r["id"], refresh_table),
                    ),
                    color="negative",
                    size="sm",
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
                size="sm",
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
    with ui.card().classes("m-4 w-[420px] max-w-full"):
        ui.label("Giriş Yap").classes("text-h6")
        username = ui.input("Kullanıcı adı").classes("w-full")
        password = ui.input("Şifre").props("type=password").classes("w-full")

        def do_login() -> None:
            if not username.value or not password.value:
                ui.notify("Kullanıcı adı ve şifre zorunludur", type="warning")
                return
            user = get_user_by_username(username.value)
            if not user or not verify_password(password.value, user["salt"], user["password_hash"]):
                ui.notify("Geçersiz bilgiler", type="negative")
                return
            app.storage.user["user"] = {
                "id": user["id"],
                "username": user["username"],
                "is_admin": bool(user["is_admin"]),
            }
            ui.notify("Hoş geldiniz", type="positive")
            ui.navigate.to(next_path)

        ui.button("Giriş", on_click=do_login, color="primary", icon="login").classes("mt-2")
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
    ui.run(title="Kütüphane", reload=False, show=False, port=8095, host="0.0.0.0", storage_secret=os.getenv("STORAGE_SECRET", "dev-secret")
    )


