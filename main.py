import os
from contextlib import closing
import hashlib
import secrets
from datetime import date, datetime, timedelta
from typing import Optional, Any, List, Dict
from nicegui import ui, app
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import text

# PostgreSQL bağlantı bilgileri
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "library")
DB_USER = os.getenv("DB_USER", "library_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "library123")

# Admin bilgileri
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "yusufgbt")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "yusuf1234")

# Oturum yönetimi - Global değişken kullan
_LOGGED_IN_USERS = set()

# Database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Member(Base):
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    
    # Relationships
    loans = relationship("Loan", back_populates="member")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    
    # Relationships
    loans = relationship("Loan", back_populates="book")

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    loan_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    
    # Relationships
    book = relationship("Book", back_populates="loans")
    member = relationship("Member", back_populates="loans")

def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise

def init_db():
    # Database tablolarını oluştur
    Base.metadata.create_all(bind=engine)
    print("Database tabloları oluşturuldu!")

# Oturum yönetimi fonksiyonları
def is_logged_in() -> bool:
    """Kullanıcının oturum açıp açmadığını kontrol eder"""
    # Global değişkenden kontrol et
    return len(_LOGGED_IN_USERS) > 0

def login_user() -> None:
    """Kullanıcıyı oturum açmış olarak işaretler"""
    # Global değişkene ekle
    _LOGGED_IN_USERS.add("admin")
    print(f"Login successful. Logged in users: {_LOGGED_IN_USERS}")

def logout_user() -> None:
    """Kullanıcının oturumunu kapatır"""
    # Global değişkenden çıkar
    _LOGGED_IN_USERS.clear()
    print(f"Logout successful. Logged in users: {_LOGGED_IN_USERS}")

def require_login():
    """Oturum açma gereksinimi kontrolü"""
    # Basit login kontrolü
    if not is_logged_in():
        ui.navigate.to('/login')

# CSP Middleware: allow unsafe-eval for dev (fixes CSP eval error)
@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    csp = (
        "default-src 'self' data: blob: 'unsafe-inline' 'unsafe-eval'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' http: https:; "
        "style-src 'self' 'unsafe-inline' http: https:; "
        "img-src 'self' data: blob:; "
        "connect-src 'self' ws: wss: http: https:; "
        "font-src 'self' data:; "
        "frame-ancestors 'self';"
    )
    response.headers["Content-Security-Policy"] = csp
    return response

def create_member(name: str, email: str = None, phone: str = None) -> int:
    password = name + "123"  # Basit şifre
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    db = get_db()
    try:
        member = Member(
            name=name,
            email=email,
            phone=phone,
            password_hash=password_hash,
            salt=salt
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member.id
    finally:
        db.close()

def get_members() -> List[Dict[str, Any]]:
    db = get_db()
    try:
        members = db.query(Member).order_by(Member.name).all()
        return [
            {
                "id": member.id,
                "name": member.name,
                "email": member.email,
                "phone": member.phone,
                "password_hash": member.password_hash,
                "salt": member.salt
            }
            for member in members
        ]
    finally:
        db.close()

def get_member_password(member_id: int) -> str:
    db = get_db()
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if member:
            return member.name + "123"
        return "Bilinmiyor"
    finally:
        db.close()

def delete_member(member_id: int) -> None:
    db = get_db()
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if member:
            db.delete(member)
            db.commit()
    finally:
        db.close()

def create_book(title: str, author: str, isbn: str = None, year: int = None) -> int:
    db = get_db()
    try:
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            year=year
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return book.id
    finally:
        db.close()

def get_books() -> List[Dict[str, Any]]:
    db = get_db()
    try:
        books = db.query(Book).order_by(Book.title).all()
        return [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "year": book.year
            }
            for book in books
        ]
    finally:
        db.close()

def delete_book(book_id: int) -> None:
    db = get_db()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            db.delete(book)
            db.commit()
    finally:
        db.close()

def get_available_books() -> List[Dict[str, Any]]:
    db = get_db()
    try:
        # Ödünç verilmemiş kitapları bul
        subquery = db.query(Loan.book_id).filter(Loan.return_date.is_(None)).subquery()
        available_books = db.query(Book).filter(~Book.id.in_(subquery)).order_by(Book.title).all()
        
        return [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "year": book.year
            }
            for book in available_books
        ]
    finally:
        db.close()

def get_active_loans() -> List[Dict[str, Any]]:
    db = get_db()
    try:
        active_loans = db.query(Loan, Book.title.label('book_title'), Member.name.label('member_name'))\
            .join(Book, Loan.book_id == Book.id)\
            .join(Member, Loan.member_id == Member.id)\
            .filter(Loan.return_date.is_(None))\
            .order_by(Loan.loan_date.desc())\
            .all()
        
        return [
            {
                "id": loan.Loan.id,
                "book_id": loan.Loan.book_id,
                "member_id": loan.Loan.member_id,
                "loan_date": loan.Loan.loan_date.isoformat() if loan.Loan.loan_date else None,
                "due_date": loan.Loan.due_date.isoformat() if loan.Loan.due_date else None,
                "return_date": loan.Loan.return_date.isoformat() if loan.Loan.return_date else None,
                "book_title": loan.book_title,
                "member_name": loan.member_name
            }
            for loan in active_loans
        ]
    finally:
        db.close()

def create_loan(book_id: int, member_id: int, loan_date: str, due_date: str) -> int:
    db = get_db()
    try:
        # Tarih değerlerini güvenli şekilde parse et
        if not loan_date or not due_date:
            raise ValueError("Tarih değerleri boş olamaz")
        
        # ui.date() bileşeni ISO format döndürür (YYYY-MM-DD)
        loan_date_obj = datetime.strptime(loan_date, "%Y-%m-%d").date()
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
        
        # Tarih kontrolü
        if loan_date_obj > due_date_obj:
            raise ValueError("Ödünç tarihi, son tarihten sonra olamaz")
        
        loan = Loan(
            book_id=book_id,
            member_id=member_id,
            loan_date=loan_date_obj,
            due_date=due_date_obj
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan.id
    except ValueError as e:
        raise e
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def return_book(loan_id: int) -> None:
    db = get_db()
    try:
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if loan:
            loan.return_date = date.today()
            db.commit()
    finally:
        db.close()

def delete_duplicate_members() -> int:
    """Aynı isimde birden fazla üye varsa, en düşük id'li kaydı tutar, diğerlerini siler.
    Silmeden önce bu üyelerin ödünç kayıtlarını tutulan üyeye devreder.
    Dönüş değeri: silinen üye sayısı
    """
    db = get_db()
    deleted_count = 0
    try:
        duplicates = db.query(Member.name).group_by(Member.name).having(func.count(Member.id) > 1).all()
        for (name,) in duplicates:
            same_members = db.query(Member).filter(Member.name == name).order_by(Member.id.asc()).all()
            if not same_members:
                continue
            keep = same_members[0]
            for redundant in same_members[1:]:
                # Ödünç kayıtlarını devret
                db.query(Loan).filter(Loan.member_id == redundant.id).update({Loan.member_id: keep.id}, synchronize_session=False)
                db.delete(redundant)
                deleted_count += 1
            db.commit()
        return deleted_count
    finally:
        db.close()

def delete_duplicate_books() -> int:
    """Aynı başlığa sahip birden fazla kitap varsa, en düşük id'li kaydı tutar, diğerlerini siler.
    Silmeden önce bu kitapların ödünç kayıtlarını tutulan kitaba devreder.
    Dönüş değeri: silinen kitap sayısı
    """
    db = get_db()
    deleted_count = 0
    try:
        duplicates = db.query(Book.title).group_by(Book.title).having(func.count(Book.id) > 1).all()
        for (title,) in duplicates:
            same_books = db.query(Book).filter(Book.title == title).order_by(Book.id.asc()).all()
            if not same_books:
                continue
            keep = same_books[0]
            for redundant in same_books[1:]:
                # Ödünç kayıtlarını devret
                db.query(Loan).filter(Loan.book_id == redundant.id).update({Loan.book_id: keep.id}, synchronize_session=False)
                db.delete(redundant)
                deleted_count += 1
            db.commit()
        return deleted_count
    finally:
        db.close()

def add_sample_data():
    # 15 üye ekle
    member_names = [
        "Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Özkan", "Ali Çelik",
        "Zeynep Arslan", "Mustafa Şahin", "Elif Yıldız", "Hasan Öztürk", "Selin Korkmaz",
        "Emre Aydın", "Deniz Yalçın", "Büşra Koç", "Can Özkan", "Merve Taş"
    ]
    
    for name in member_names:
        email = f"{name.lower().replace(' ', '.')}@email.com"
        phone = f"05{secrets.token_hex(3)}"
        create_member(name, email, phone)
    
    # 100 kitap ekle
    book_data = [
        ("Suç ve Ceza", "Dostoyevski"), ("1984", "George Orwell"), ("Dönüşüm", "Kafka"),
        ("Yabancı", "Camus"), ("Küçük Prens", "Saint-Exupéry"), ("Şeker Portakalı", "Vasconcelos"),
        ("Fareler ve İnsanlar", "Steinbeck"), ("Hayvan Çiftliği", "Orwell"), ("Bülbülü Öldürmek", "Lee"),
        ("Çavdar Tarlasında Çocuklar", "Salinger"), ("Gurur ve Önyargı", "Austen"), ("Jane Eyre", "Brontë"),
        ("Uğultulu Tepeler", "Brontë"), ("Madame Bovary", "Flaubert"), ("Sefiller", "Hugo"),
        ("Notre Dame'ın Kamburu", "Hugo"), ("Üç Silahşörler", "Dumas"), ("Kont Monte Cristo", "Dumas"),
        ("Kırmızı ve Siyah", "Stendhal"), ("Parma Manastırı", "Stendhal"), ("Karamazov Kardeşler", "Dostoyevski"),
        ("Budala", "Dostoyevski"), ("Ecinniler", "Dostoyevski"), ("Anna Karenina", "Tolstoy"),
        ("Savaş ve Barış", "Tolstoy"), ("Diriliş", "Tolstoy"), ("Çehov Hikayeleri", "Çehov"),
        ("Vanya Dayı", "Çehov"), ("Üç Kız Kardeş", "Çehov"), ("Vişne Bahçesi", "Çehov"),
        ("Gogol Hikayeleri", "Gogol"), ("Ölü Canlar", "Gogol"), ("Müfettiş", "Gogol"),
        ("Taras Bulba", "Gogol"), ("Puşkin Şiirleri", "Puşkin"), ("Yevgeni Onegin", "Puşkin"),
        ("Kaptanın Kızı", "Puşkin"), ("Boris Godunov", "Puşkin"), ("Lermontov Şiirleri", "Lermontov"),
        ("Zamanımızın Kahramanı", "Lermontov"), ("Nekrasov Şiirleri", "Nekrasov"),
        ("Turgenev Hikayeleri", "Turgenev"), ("Babalar ve Oğullar", "Turgenev"), ("İlk Aşk", "Turgenev"),
        ("Günlerden Bir Gün", "Turgenev"), ("Rudin", "Turgenev"), ("Noble Nest", "Turgenev"),
        ("Smoke", "Turgenev"), ("Spring Torrents", "Turgenev"), ("King Lear", "Shakespeare"),
        ("Hamlet", "Shakespeare"), ("Macbeth", "Shakespeare"), ("Romeo ve Juliet", "Shakespeare"),
        ("Othello", "Shakespeare"), ("Fırtına", "Shakespeare"), ("Kış Masalı", "Shakespeare"),
        ("Hırçın Kız", "Shakespeare"), ("Venedik Taciri", "Shakespeare"), ("Julius Caesar", "Shakespeare"),
        ("Antony ve Cleopatra", "Shakespeare"), ("Coriolanus", "Shakespeare"), ("Timon of Athens", "Shakespeare"),
        ("Troilus ve Cressida", "Shakespeare"), ("Pericles", "Shakespeare"), ("Cymbeline", "Shakespeare"),
        ("İki Soylu Akraba", "Shakespeare"), ("Edward III", "Shakespeare"), ("Sir Thomas More", "Shakespeare"),
        ("Cardenio", "Shakespeare"), ("Love's Labour's Won", "Shakespeare"), ("The Tempest", "Shakespeare"),
        ("The Winter's Tale", "Shakespeare"), ("Cymbeline", "Shakespeare"), ("Pericles", "Shakespeare"),
        ("The Two Noble Kinsmen", "Shakespeare"), ("Henry VIII", "Shakespeare"), ("Richard III", "Shakespeare"),
        ("Richard II", "Shakespeare"), ("Henry IV Part 1", "Shakespeare"), ("Henry IV Part 2", "Shakespeare"),
        ("Henry V", "Shakespeare"), ("Henry VI Part 1", "Shakespeare"), ("Henry VI Part 2", "Shakespeare"),
        ("Henry VI Part 3", "Shakespeare"), ("Richard III", "Shakespeare"), ("King John", "Shakespeare"),
        ("The Merchant of Venice", "Shakespeare"), ("The Taming of the Shrew", "Shakespeare"),
        ("Much Ado About Nothing", "Shakespeare"), ("Love's Labour's Lost", "Shakespeare"),
        ("A Midsummer Night's Dream", "Shakespeare"), ("The Comedy of Errors", "Shakespeare"),
        ("The Two Gentlemen of Verona", "Shakespeare"), ("The Merry Wives of Windsor", "Shakespeare"),
        ("As You Like It", "Shakespeare"), ("Twelfth Night", "Shakespeare"), ("Measure for Measure", "Shakespeare"),
        ("All's Well That Ends Well", "Shakespeare"), ("Troilus and Cressida", "Shakespeare"),
        ("Coriolanus", "Shakespeare"), ("Titus Andronicus", "Shakespeare"), ("Timon of Athens", "Shakespeare"),
        ("Pericles", "Shakespeare"), ("Cymbeline", "Shakespeare"), ("The Winter's Tale", "Shakespeare"),
        ("The Tempest", "Shakespeare"), ("The Two Noble Kinsmen", "Shakespeare"), ("Henry VIII", "Shakespeare"),
        ("Sir Thomas More", "Shakespeare"), ("Cardenio", "Shakespeare"), ("Love's Labour's Won", "Shakespeare")
    ]
    
    for title, author in book_data:
        isbn = f"978{secrets.token_hex(8)}"
        year = 1800 + (hash(title + author) % 200)
        create_book(title, author, isbn, year)

# UI fonksiyonları
def nav_header():
    with ui.header().classes("bg-blue-600 text-white"):
        with ui.row().classes("w-full max-w-[1200px] mx-auto items-center justify-between"):
            ui.label("📚 YB Kütüphane").classes("text-h5 font-bold")
            with ui.row().classes("gap-4"):
                ui.button("🏠 Ana Sayfa", on_click=lambda: ui.navigate.to("/")).classes("text-white")
                ui.button("📖 Kitaplar", on_click=lambda: ui.navigate.to("/books")).classes("text-white")
                ui.button("👥 Üyeler", on_click=lambda: ui.navigate.to("/members")).classes("text-white")
                ui.button("📚 Ödünç", on_click=lambda: ui.navigate.to("/loans")).classes("text-white")
                ui.button("➕ Örnek Veri", on_click=add_sample_data).classes("text-white")
                
                def do_logout():
                    logout_user()
                    ui.notify("Çıkış yapıldı!", type="positive")
                    ui.navigate.to("/login")
                
                ui.button("🚪 Çıkış", on_click=do_logout).classes("text-white bg-red-600 hover:bg-red-700")

def app_footer():
    with ui.footer().classes("bg-gray-100 text-center py-4"):
        ui.label("© 2024 YB Kütüphane Sistemi").classes("text-gray-600")

# Login sayfası
@ui.page("/login")
def login_page() -> None:
    with ui.column().classes("w-full h-screen flex justify-center items-center bg-gradient-to-br from-blue-50 to-indigo-100"):
        with ui.card().classes("w-[400px] p-8 shadow-lg"):
            with ui.column().classes("w-full gap-6"):
                # Logo ve başlık
                with ui.row().classes("w-full justify-center"):
                    ui.label("🏛️").classes("text-6xl")
                ui.label("YB Kütüphane Sistemi").classes("text-h5 font-bold text-center text-gray-700")
                ui.label("Admin Giriş").classes("text-h6 text-center text-gray-500 mb-4")
                
                # Giriş formu
                username_input = ui.input("Kullanıcı Adı", placeholder="Admin kullanıcı adı").classes("w-full")
                password_input = ui.input("Şifre", placeholder="Admin şifresi", password=True).classes("w-full")
                
                def do_login():
                    if username_input.value == ADMIN_USERNAME and password_input.value == ADMIN_PASSWORD:
                        login_user()
                        ui.notify("Başarıyla giriş yapıldı!", type="positive")
                        
                        # Hemen ana sayfaya yönlendir
                        ui.navigate.to("/")
                    else:
                        ui.notify("Kullanıcı adı veya şifre hatalı!", type="negative")
                        password_input.value = ""
                
                # Enter tuşu ile giriş
                password_input.on('keydown.enter', do_login)
                
                ui.button("Giriş Yap", on_click=do_login, color="primary").classes("w-full mt-4")
                
                # Bilgi notu
                with ui.card().classes("w-full p-4 bg-blue-50 border-l-4 border-blue-400 mt-4"):
                    ui.label("ℹ️ Varsayılan Giriş Bilgileri").classes("text-sm font-bold text-blue-700")
                    ui.label("Kullanıcı: yusufgbt").classes("text-sm text-blue-600")
                    ui.label("Şifre: yusuf1234").classes("text-sm text-blue-600")

# Ana sayfa
@ui.page("/")
def home_page() -> None:
    require_login()  # Oturum kontrolü
    nav_header()
    
    with ui.column().classes("w-full max-w-[1200px] mx-auto p-6"):
        ui.label("🏠 Hoş Geldiniz!").classes("text-h3 font-bold mb-6")
        
        with ui.row().classes("gap-6"):
            with ui.card().classes("flex-1 p-6"):
                ui.label("📖 Kitaplar").classes("text-h5 font-bold mb-2")
                ui.label("Kütüphanedeki tüm kitapları görüntüleyin ve yönetin.")
                ui.button("Kitaplara Git", on_click=lambda: ui.navigate.to("/books"), color="primary").classes("mt-4")
            
            with ui.card().classes("flex-1 p-6"):
                ui.label("👥 Üyeler").classes("text-h5 font-bold mb-2")
                ui.label("Sistem üyelerini yönetin ve bilgilerini görüntüleyin.")
                ui.button("Üyelere Git", on_click=lambda: ui.navigate.to("/members"), color="primary").classes("mt-4")
            
            with ui.card().classes("flex-1 p-6"):
                ui.label("📚 Ödünç").classes("text-h5 font-bold mb-2")
                ui.label("Kitap ödünç verme ve iade işlemlerini yönetin.")
                ui.button("Ödünç Sayfasına Git", on_click=lambda: ui.navigate.to("/loans"), color="primary").classes("mt-4")
    
    app_footer()

# Kitaplar sayfası
@ui.page("/books")
def books_page() -> None:
    require_login()  # Oturum kontrolü
    nav_header()
    
    with ui.column().classes("w-full max-w-[1200px] mx-auto p-6"):
        with ui.row().classes("justify-between items-center mb-6"):
            ui.label("📖 Kitap Yönetimi").classes("text-h4 font-bold")
            ui.button("➕ Yeni Kitap", on_click=lambda: create_book_dialog(on_saved=refresh_books), color="primary")
        
        books_grid = ui.grid(columns=1, rows=0).classes("w-full")
        
        def refresh_books():
            books_grid.clear()
            books = get_books()
            for book in books:
                with books_grid:
                    with ui.card().classes("w-full p-4"):
                        with ui.row().classes("justify-between items-start"):
                            with ui.column().classes("flex-1"):
                                ui.label(book["title"]).classes("text-h6 font-bold")
                                ui.label(f"Yazar: {book['author']}").classes("text-caption")
                                if book["isbn"]:
                                    ui.label(f"ISBN: {book['isbn']}").classes("text-caption")
                                if book["year"]:
                                    ui.label(f"Yıl: {book['year']}").classes("text-caption")
                            
                            with ui.row().classes("gap-2"):
                                ui.button("🗑️", on_click=lambda b=book: delete_book_and_refresh(b["id"]), color="negative")
        
        def delete_book_and_refresh(book_id: int):
            delete_book(book_id)
            refresh_books()
            ui.notify("Kitap silindi", type="positive")
        
        refresh_books()
    
    app_footer()

# Üyeler sayfası
@ui.page("/members")
def members_page() -> None:
    require_login()  # Oturum kontrolü
    nav_header()
    
    with ui.column().classes("w-full max-w-[1200px] mx-auto p-6"):
        with ui.row().classes("justify-between items-center mb-6"):
            ui.label("👥 Üye Yönetimi").classes("text-h4 font-bold")
            ui.button("➕ Yeni Üye", on_click=lambda: create_member_dialog(on_saved=refresh_members), color="primary")
        
        members_grid = ui.grid(columns=1, rows=0).classes("w-full")
        
        def refresh_members():
            members_grid.clear()
            members = get_members()
            for member in members:
                with members_grid:
                    with ui.card().classes("w-full p-4"):
                        with ui.row().classes("justify-between items-start"):
                            with ui.column().classes("flex-1"):
                                ui.label(member["name"]).classes("text-h6 font-bold")
                                if member["email"]:
                                    ui.label(f"E-posta: {member['email']}").classes("text-caption")
                                if member["phone"]:
                                    ui.label(f"Telefon: {member['phone']}").classes("text-caption")
                                ui.label(f"🔑 Şifre: {get_member_password(member['id'])}").classes("text-caption text-green-600")
                                ui.label(f"🔐 Hash: {member['password_hash'][:20]}...").classes("text-caption text-gray-500")
                            
                            with ui.row().classes("gap-2"):
                                ui.button("🗑️", on_click=lambda m=member: delete_member_and_refresh(m["id"]), color="negative")
        
        def delete_member_and_refresh(member_id: int):
            delete_member(member_id)
            refresh_members()
            ui.notify("Üye silindi", type="positive")
        
        refresh_members()
    
    app_footer()

# Ödünç sayfası
@ui.page("/loans")
def loans_page() -> None:
    require_login()  # Oturum kontrolü
    nav_header()
    
    with ui.column().classes("w-full max-w-[1200px] mx-auto p-6"):
        ui.label("📚 Ödünç Verme Sistemi").classes("text-h4 font-bold mb-6")
        
        # Yeni ödünç verme
        with ui.card().classes("w-full p-6 mb-6"):
            ui.label("🆕 Yeni Ödünç").classes("text-h6 font-bold mb-4")
            
            with ui.row().classes("gap-4 w-full"):
                # Kitap seçimi
                with ui.column().classes("flex-1"):
                    ui.label("📖 Kitap").classes("text-caption mb-1")
                    book_select = ui.select(
                        options=[(book["id"], f"{book['title']} - {book['author']}") for book in get_available_books()],
                        label="Kitap Seçin"
                    ).classes("w-full")
                
                # Üye seçimi
                with ui.column().classes("flex-1"):
                    ui.label("👤 Üye").classes("text-caption mb-1")
                    member_select = ui.select(
                        options=[(member["id"], member["name"]) for member in get_members()],
                        label="Üye Seçin"
                    ).classes("w-full")
            
            with ui.row().classes("gap-4 w-full"):
                # Ödünç tarihi
                with ui.column().classes("flex-1"):
                    ui.label("📅 Ödünç Tarihi").classes("text-caption mb-1")
                    loan_date = ui.date().classes("w-full")
                    loan_date.value = date.today().isoformat()
                
                # Son tarih (varsayılan 30 gün)
                with ui.column().classes("flex-1"):
                    ui.label("⏰ Son Tarih").classes("text-caption mb-1")
                    due_date = ui.date().classes("w-full")
                    due_date.value = (date.today() + timedelta(days=30)).isoformat()
            
            def borrow_book():
                if not book_select.value or not member_select.value:
                    ui.notify("Lütfen kitap ve üye seçin", type="warning")
                    return
                
                if not loan_date.value or not due_date.value:
                    ui.notify("Lütfen tarihleri seçin", type="warning")
                    return
                
                try:
                    # Select değerlerinden sadece ID'leri al
                    book_id = book_select.value[0] if isinstance(book_select.value, tuple) else book_select.value
                    member_id = member_select.value[0] if isinstance(member_select.value, tuple) else member_select.value
                    
                    create_loan(book_id, member_id, loan_date.value, due_date.value)
                    ui.notify("Kitap ödünç verildi!", type="positive")
                    book_select.value = None
                    member_select.value = None
                    refresh_loans()
                except ValueError as e:
                    ui.notify(f"Tarih Hatası: {str(e)}", type="negative")
                except Exception as e:
                    ui.notify(f"Genel Hata: {str(e)}", type="negative")
            
            ui.button("📚 Ödünç Ver", on_click=borrow_book, color="primary").classes("mt-4")
        
        # Aktif ödünçler
        with ui.card().classes("w-full p-6"):
            ui.label("📋 Aktif Ödünçler").classes("text-h6 font-bold mb-4")
            
            loans_grid = ui.grid(columns=1, rows=0).classes("w-full")
            
            def refresh_loans():
                loans_grid.clear()
                active_loans = get_active_loans()
                for loan in active_loans:
                    with loans_grid:
                        with ui.card().classes("w-full p-4"):
                            with ui.row().classes("justify-between items-start"):
                                with ui.column().classes("flex-1"):
                                    ui.label(f"📖 {loan['book_title']}").classes("text-h6 font-bold")
                                    ui.label(f"👤 {loan['member_name']}").classes("text-caption")
                                    ui.label(f"📅 Ödünç: {loan['loan_date']}").classes("text-caption")
                                    ui.label(f"⏰ Son: {loan['due_date']}").classes("text-caption")
                                
                                with ui.row().classes("gap-2"):
                                    ui.button("📦 İade Et", on_click=lambda l=loan: return_book_and_refresh(l["id"]), color="positive")
            
            def return_book_and_refresh(loan_id: int):
                return_book(loan_id)
                refresh_loans()
                ui.notify("Kitap iade edildi!", type="positive")
            
            refresh_loans()
    
    app_footer()

# Dialog fonksiyonları
def create_book_dialog(on_saved: Optional[Any] = None) -> None:
    dialog = ui.dialog()
    with dialog, ui.card().classes("w-[500px] max-w-full"):
        ui.label("Kitap Bilgileri").classes("text-h6")
        title_input = ui.input("Başlık").classes("w-full")
        author_input = ui.input("Yazar").classes("w-full")
        isbn_input = ui.input("ISBN (opsiyonel)").classes("w-full")
        year_input = ui.input("Yıl (opsiyonel)").classes("w-full")

        with ui.row().classes("justify-end w-full gap-2"):
            ui.button("İptal", on_click=dialog.close)

            def save() -> None:
                try:
                    if not title_input.value or not author_input.value:
                        ui.notify("Başlık ve Yazar zorunludur", type="warning")
                        return
                    year = int(year_input.value) if year_input.value not in (None, "") else None
                    create_book(title_input.value, author_input.value, isbn_input.value or None, year)
                    ui.notify("Kitap eklendi", type="positive")
                    dialog.close()
                    if on_saved:
                        on_saved()
                except Exception as exc:
                    ui.notify(str(exc), type="negative")

            ui.button("Kaydet", on_click=save, color="primary")

    dialog.open()

def create_member_dialog(on_saved: Optional[Any] = None) -> None:
    dialog = ui.dialog()
    with dialog, ui.card().classes("w-[500px] max-w-full"):
        ui.label("Üye Bilgileri").classes("text-h6")
        name_input = ui.input("Ad Soyad").classes("w-full")
        email_input = ui.input("E-posta (opsiyonel)").classes("w-full")
        phone_input = ui.input("Telefon (opsiyonel)").classes("w-full")

        with ui.row().classes("justify-end w-full gap-2"):
            ui.button("İptal", on_click=dialog.close)

            def save() -> None:
                try:
                    if not name_input.value:
                        ui.notify("Ad Soyad zorunludur", type="warning")
                        return
                    create_member(name_input.value, email_input.value or None, phone_input.value or None)
                    ui.notify("Üye eklendi", type="positive")
                    dialog.close()
                    if on_saved:
                        on_saved()
                except Exception as exc:
                    ui.notify(str(exc), type="negative")

            ui.button("Kaydet", on_click=save, color="primary")

    dialog.open()

# Uygulama başlatma
if __name__ in {"__main__", "__mp_main__"}:
    init_db()
    print(f"🚀 Uygulama başlatılıyor... Port: 8082")
    ui.run(
        host="0.0.0.0",  # Docker için gerekli
        port=8082, 
        title="YB Kütüphane Sistemi", 
        show=False, 
        storage_secret='dev-secret'
    )
