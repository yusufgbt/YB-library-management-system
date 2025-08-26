# 🏛️ YB Library Migration Sistemi

Bu dokümantasyon, YB Library projesinde Alembic kullanarak veritabanı migration'larını nasıl yöneteceğinizi açıklar.

## 📋 İçindekiler

- [Kurulum](#kurulum)
- [Temel Kullanım](#temel-kullanım)
- [Migration Komutları](#migration-komutları)
- [Örnekler](#örnekler)
- [Sorun Giderme](#sorun-giderme)

## 🚀 Kurulum

### Gereksinimler

```bash
pip install alembic psycopg2-binary
```

### İlk Kurulum

```bash
# Alembic'i başlat
alembic init migrations

# alembic.ini dosyasını düzenle
# sqlalchemy.url = postgresql://user:pass@localhost/dbname

# env.py dosyasını düzenle
# target_metadata = Base.metadata
```

## 🔧 Temel Kullanım

### Migration Script'i

Proje kök dizininde `migrate.sh` script'i bulunur:

```bash
# Script'i çalıştırılabilir yap
chmod +x migrate.sh

# Yardım
./migrate.sh
```

### Manuel Alembic Komutları

```bash
# Migrations klasörüne git
cd migrations

# Mevcut durumu kontrol et
alembic current

# Migration geçmişini gör
alembic history

# Head revision'ları gör
alembic heads
```

## 📚 Migration Komutları

### 1. Migration Oluşturma

```bash
# Otomatik migration (önerilen)
alembic revision --autogenerate -m "Migration açıklaması"

# Manuel migration
alembic revision -m "Migration açıklaması"
```

### 2. Migration Çalıştırma

```bash
# En son migration'a kadar yükselt
alembic upgrade head

# Belirli bir revision'a yükselt
alembic upgrade <revision_id>

# Bir adım yükselt
alembic upgrade +1
```

### 3. Migration Geri Alma

```bash
# Bir adım geri al
alembic downgrade -1

# Belirli bir revision'a geri al
alembic downgrade <revision_id>

# En başa geri al
alembic downgrade base
```

### 4. Migration Durumu

```bash
# Mevcut revision
alembic current

# Migration geçmişi
alembic history

# Head revision'lar
alembic heads
```

## 📝 Örnekler

### Yeni Tablo Ekleme

```bash
# 1. Model'i güncelle (main.py)
class NewTable(Base):
    __tablename__ = "new_table"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# 2. Migration oluştur
./migrate.sh create "Add new table"

# 3. Migration'ı çalıştır
./migrate.sh upgrade
```

### Tablo Değiştirme

```bash
# 1. Model'i güncelle
class Book(Base):
    __tablename__ = "books"
    # Yeni kolon ekle
    new_column = Column(String)

# 2. Migration oluştur
./migrate.sh create "Add new column to books"

# 3. Migration'ı çalıştır
./migrate.sh upgrade
```

### Migration Geri Alma

```bash
# Son migration'ı geri al
./migrate.sh downgrade -1

# Belirli bir revision'a geri al
./migrate.sh downgrade 355423c466cd
```

## 🗄️ Veritabanı Yapısı

### Mevcut Tablolar

- **books**: Kitap bilgileri
- **members**: Üye bilgileri  
- **users**: Kullanıcı hesapları
- **loans**: Ödünç verme kayıtları

### Alembic Tabloları

- **alembic_version**: Migration versiyonları

## ⚠️ Önemli Notlar

### 1. Migration Öncesi

- Veritabanı yedeği alın
- Test ortamında deneyin
- Production'da dikkatli olun

### 2. Migration Sırasında

- Migration'ları sırayla çalıştırın
- Hata durumunda rollback yapın
- Log'ları kontrol edin

### 3. Migration Sonrası

- Veritabanı şemasını doğrulayın
- Uygulamayı test edin
- Performansı kontrol edin

## 🔍 Sorun Giderme

### Yaygın Hatalar

#### 1. "Can't locate revision" Hatası

```bash
# Migration geçmişini kontrol et
alembic history

# Eksik migration'ları bul
alembic heads

# Migration'ı stamp et
alembic stamp <revision_id>
```

#### 2. "Multiple head revisions" Hatası

```bash
# Head revision'ları gör
alembic heads

# Eski revision'ları sil
rm migrations/versions/old_revision.py

# Migration'ı tekrar çalıştır
alembic upgrade head
```

#### 3. Veritabanı Bağlantı Hatası

```bash
# Bağlantıyı test et
docker exec -it yb_library_db psql -U library_user -d library

# alembic.ini'deki URL'i kontrol et
sqlalchemy.url = postgresql://library_user:library123@localhost:5432/library
```

### Debug Komutları

```bash
# Detaylı log
alembic upgrade head --verbose

# SQL'i göster
alembic upgrade head --sql

# Migration durumu
alembic show <revision_id>
```

## 📚 Faydalı Linkler

- [Alembic Dokümantasyonu](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Migration](https://docs.sqlalchemy.org/en/14/core/engines.html)
- [PostgreSQL Alembic](https://alembic.sqlalchemy.org/en/latest/dialects/postgresql.html)

## 🤝 Katkıda Bulunma

1. Migration oluştururken açıklayıcı mesajlar yazın
2. Test migration'ları ekleyin
3. Dokümantasyonu güncel tutun
4. Hata durumlarını rapor edin

---

**💡 İpucu**: Her zaman migration'ları test ortamında deneyin ve production'a geçmeden önce yedek alın!


