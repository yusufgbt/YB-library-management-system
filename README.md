# 📚 Kütüphane Yönetim Sistemi

Modern ve kullanıcı dostu kütüphane yönetim platformu. NiceGUI ve SQLite kullanılarak geliştirilmiştir.

## ✨ Özellikler

- 🎨 **Modern UI**: Glassmorphism tasarım ve gradient arka planlar
- 📖 **Kitap Yönetimi**: Kitap ekleme, düzenleme, silme ve arama
- 👥 **Üye Yönetimi**: Üye kayıtları ve bilgi takibi
- 🔄 **Ödünç İşlemleri**: Kitap ödünç alma ve iade takibi
- 🔐 **Güvenli Giriş**: Şifreli kullanıcı yönetimi
- 📱 **Responsive**: Mobil ve masaüstü uyumlu tasarım
- 🌙 **Dark Mode**: Karanlık tema desteği

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- pip

### Adımlar
1. Repository'yi klonlayın:
```bash
git clone https://github.com/KULLANICI_ADIN/nicegui-library-system.git
cd nicegui-library-system
```

2. Virtual environment oluşturun:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate  # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Uygulamayı başlatın:
```bash
python main.py
```

5. Tarayıcıda açın: `http://localhost:8095`

## 🔑 Giriş Bilgileri

- **Kullanıcı adı:** `admin`
- **Şifre:** `admin123`

## 🛠️ Teknolojiler

- **Frontend**: NiceGUI (Python web framework)
- **Backend**: Python + SQLite
- **Database**: SQLite3
- **UI Components**: Quasar Design System
- **Authentication**: SHA256 + Salt

## 📁 Proje Yapısı

```
nicegui_sqlite/
├── main.py              # Ana uygulama dosyası
├── requirements.txt     # Python bağımlılıkları
├── README.md           # Bu dosya
├── GITHUB_SETUP.md     # GitHub entegrasyon rehberi
└── database.db         # SQLite veritabanı (otomatik oluşur)
```

## 🎯 Kullanım

### Ana Sayfa
- Sistem genel bakışı
- Hızlı erişim butonları
- İstatistik kartları

### Kitaplar
- Kitap ekleme/düzenleme/silme
- Başlık, yazar, ISBN arama
- Dünya klasiklerini toplu ekleme

### Üyeler
- Üye kayıt işlemleri
- İletişim bilgileri yönetimi
- Üye arama

### Ödünç İşlemleri
- Kitap ödünç alma
- İade takibi
- Aktif ödünç listesi

## 🔧 Geliştirme

### Yeni Özellik Ekleme
1. Feature branch oluşturun: `git checkout -b feature/yeni-ozellik`
2. Kodunuzu yazın ve test edin
3. Commit yapın: `git commit -m "✨ Yeni özellik eklendi"`
4. Push edin: `git push origin feature/yeni-ozellik`
5. Pull Request oluşturun

### Veritabanı Şeması
```sql
-- Kitaplar tablosu
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE,
    year INTEGER,
    status TEXT DEFAULT 'Müsait'
);

-- Üyeler tablosu
CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT
);

-- Ödünç tablosu
CREATE TABLE loans (
    id INTEGER PRIMARY KEY,
    book_id INTEGER,
    member_id INTEGER,
    loan_date TEXT,
    due_date TEXT,
    return_date TEXT,
    FOREIGN KEY (book_id) REFERENCES books (id),
    FOREIGN KEY (member_id) REFERENCES members (id)
);

-- Kullanıcılar tablosu
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL
);
```

## 📊 Ekran Görüntüleri

![Ana Sayfa](screenshots/main-page.png)
![Kitaplar](screenshots/books.png)
![Üyeler](screenshots/members.png)
![Ödünç](screenshots/loans.png)

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [NiceGUI](https://nicegui.io/) - Modern Python web framework
- [Quasar](https://quasar.dev/) - Vue.js UI framework
- [SQLite](https://www.sqlite.org/) - Hafif veritabanı

## 📞 İletişim

- **Proje Linki**: [https://github.com/KULLANICI_ADIN/nicegui-library-system](https://github.com/KULLANICI_ADIN/nicegui-library-system)
- **Issues**: [GitHub Issues](https://github.com/KULLANICI_ADIN/nicegui-library-system/issues)

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
