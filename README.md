# 🏛️ YB Kütüphane Sistemi

Modern web tabanlı kütüphane yönetim sistemi. PostgreSQL veritabanı, NiceGUI ve pgAdmin ile geliştirilmiştir.

## 🚀 Docker ile Hızlı Başlangıç

### Docker Desktop'ta Çalıştırma

#### Yöntem 1: Docker Hub'dan Çekme (Önerilen)
```bash
# 1. Docker Desktop'ı açın
# 2. Terminal'de şu komutları çalıştırın:

# Uygulamayı çek
docker pull yusufgbt/yb-library:latest

# PostgreSQL'i çek
docker pull postgres:15

# pgAdmin'i çek
docker pull dpage/pgadmin4:latest

# 3. docker-compose.yml dosyasını kullanarak çalıştır
docker-compose up -d
```

#### Yöntem 2: Manuel Container Oluşturma
```bash
# 1. PostgreSQL container'ı oluştur
docker run -d \
  --name yb_library_db \
  -e POSTGRES_DB=library \
  -e POSTGRES_USER=library_user \
  -e POSTGRES_PASSWORD=library123 \
  -p 5432:5432 \
  postgres:15

# 2. pgAdmin container'ı oluştur
docker run -d \
  --name yb_library_pgadmin \
  -e PGADMIN_DEFAULT_EMAIL=admin@yblibrary.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin123 \
  -p 5050:80 \
  dpage/pgadmin4:latest

# 3. Uygulama container'ı oluştur
docker run -d \
  --name yb_library_app \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=library \
  -e DB_USER=library_user \
  -e DB_PASSWORD=library123 \
  -e ADMIN_USERNAME=yusufgbt \
  -e ADMIN_PASSWORD=yusuf1234 \
  -p 8082:8082 \
  yusufgbt/yb-library:latest
```

## 🌐 Erişim Bilgileri

- **Kütüphane Uygulaması**: http://localhost:8082
- **pgAdmin (Veritabanı Yönetimi)**: http://localhost:5050
- **PostgreSQL**: localhost:5432
- **Admin Giriş (Kütüphane)**: 
  - Kullanıcı: `yusufgbt`
  - Şifre: `yusuf1234`
- **pgAdmin Giriş**: 
  - Email: `admin@yblibrary.com`
  - Şifre: `admin123`

## 📋 Özellikler

- 📚 **Kitap Yönetimi**: Ekleme, silme, listeleme
- 👥 **Üye Yönetimi**: Üye ekleme, silme, listeleme
- 📖 **Ödünç Verme**: Kitap ödünç verme ve iade işlemleri
- 🔐 **Güvenli Giriş**: Admin paneli
- 🎨 **Modern UI**: NiceGUI ile responsive tasarım
- 🗄️ **Veritabanı Yönetimi**: pgAdmin ile PostgreSQL yönetimi

## 🗄️ pgAdmin Kullanımı

### pgAdmin'e Giriş
1. Tarayıcıda http://localhost:5050 adresini açın
2. Giriş bilgileri:
   - **Email**: `admin@yblibrary.com`
   - **Şifre**: `admin123`

### Veritabanı Bağlantısı
1. **Add New Server** butonuna tıklayın
2. **General** sekmesinde:
   - **Name**: `YB Library DB` (istediğiniz isim)
3. **Connection** sekmesinde:
   - **Host**: `yb_library_db` (Docker Compose ile) veya `host.docker.internal` (manuel)
   - **Port**: `5432`
   - **Database**: `library`
   - **Username**: `library_user`
   - **Password**: `library123`
4. **Save** butonuna tıklayın

### Veritabanı İşlemleri
- **Tabloları görüntüleme**: Schemas → public → Tables
- **Veri ekleme/düzenleme**: Tabloya sağ tık → View/Edit Data
- **SQL sorguları**: Tools → Query Tool

## 🗄️ Migration Sistemi

### 📋 Migration Nedir?

Migration sistemi, veritabanı şemasını güvenli ve kontrollü bir şekilde değiştirmek için kullanılır. Alembic kütüphanesi ile geliştirilmiştir.

### 🚀 Hızlı Migration Komutları

```bash
# Migration durumunu kontrol et
./migrate.sh current

# Migration geçmişini gör
./migrate.sh history

# Yeni migration oluştur
./migrate.sh create "Migration açıklaması"

# Migration'ları uygula
./migrate.sh upgrade

# Migration'ı geri al
./migrate.sh downgrade <revision_id>
```

### 📊 Mevcut Migration'lar

1. **İlk Şema (355423c466cd)**
   - `books` tablosu (kitaplar)
   - `members` tablosu (üyeler)
   - `users` tablosu (kullanıcılar)
   - `loans` tablosu (ödünç verme)

2. **Yaş Kolonu Ekleme (9c90999e7bf3)**
   - `members` tablosuna `age` kolonu eklendi

### 🔧 Migration Yönetimi

#### Yeni Özellik Ekleme
```bash
# 1. Model'i güncelle (main.py)
# 2. Migration oluştur
./migrate.sh create "Add new feature"

# 3. Migration'ı uygula
./migrate.sh upgrade
```

#### Hata Durumunda Geri Alma
```bash
# Son migration'ı geri al
./migrate.sh downgrade -1

# Belirli bir versiyona geri dön
./migrate.sh downgrade 355423c466cd
```

### 📚 Detaylı Dokümantasyon

Migration sistemi hakkında detaylı bilgi için [MIGRATION_README.md](MIGRATION_README.md) dosyasını inceleyin.

---

## 🛠️ Geliştirme

### Yerel Geliştirme
```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# PostgreSQL'i başlat
docker run -d --name postgres_dev -e POSTGRES_DB=library -e POSTGRES_USER=library_user -e POSTGRES_PASSWORD=library123 -p 5432:5432 postgres:15

# Uygulamayı çalıştır
python main.py
```

### Docker Build
```bash
# İmaj oluştur
docker build -t yb-library .

# Çalıştır
docker run -p 8082:8082 yb-library
```

## 📁 Proje Yapısı

```
yb-library-postgresql/
├── main.py                    # Ana uygulama
├── Dockerfile                 # Docker imaj tanımı
├── docker-compose.yml         # Container orchestration (PostgreSQL + pgAdmin + App)
├── requirements.txt           # Python bağımlılıkları
├── .dockerignore              # Docker build optimizasyonu
├── migrate.sh                 # Migration yönetim script'i
├── MIGRATION_README.md        # Detaylı migration dokümantasyonu
├── migrations/                # Alembic migration dosyaları
│   ├── alembic.ini           # Alembic konfigürasyonu
│   ├── env.py                # Migration ortam ayarları
│   ├── script.py.mako        # Migration template'i
│   └── versions/             # Migration versiyonları
│       ├── 355423c466cd_initial_database_schema.py
│       └── 9c90999e7bf3_add_age_column_to_members_table.py
└── README.md                 # Bu dosya
```

## 🔧 Docker Compose Komutları

```bash
# Tüm servisleri başlat (PostgreSQL + pgAdmin + App)
docker-compose up -d

# Servisleri durdur
docker-compose down

# Log'ları görüntüle
docker-compose logs app
docker-compose logs postgres
docker-compose logs pgadmin

# Servisleri yeniden başlat
docker-compose restart

# Tüm verileri sil (dikkatli kullanın!)
docker-compose down -v
```

## 🐛 Sorun Giderme

### Port Çakışması
```bash
# Port 8082 kullanımda mı kontrol et
netstat -tlnp | grep 8082
# veya
ss -tlnp | grep 8082

# Eğer kullanımdaysa, docker-compose.yml'da port değiştir
```

### Veritabanı Bağlantı Hatası
```bash
# PostgreSQL container'ının çalıştığını kontrol et
docker ps | grep postgres

# Log'ları kontrol et
docker-compose logs postgres
```

### pgAdmin Bağlantı Hatası
```bash
# pgAdmin container'ının çalıştığını kontrol et
docker ps | grep pgadmin

# Log'ları kontrol et
docker-compose logs pgadmin
```

## 📊 Sistem Gereksinimleri

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **RAM**: Minimum 2GB
- **Disk**: Minimum 1GB boş alan

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

- **Geliştirici**: Yusuf Bakar
- **Email**: yusufgs2727@gmail.com
- **GitHub**: [@yusufgbt](https://github.com/yusufgbt)
- **Docker Hub**: [yusufgbt/yb-library](https://hub.docker.com/r/yusufgbt/yb-library)

---

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**
