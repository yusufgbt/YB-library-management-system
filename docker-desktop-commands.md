# 🐳 Docker Desktop Komutları

## 🚀 Hızlı Başlangıç (Kopyala-Yapıştır)

### 1. Uygulamayı Çek ve Çalıştır
```bash
# Uygulamayı Docker Hub'dan çek
docker pull yusufgbt/yb-library:latest

# PostgreSQL'i çek
docker pull postgres:15

# Uygulamayı çalıştır
docker run -d --name yb_library_app -p 8082:8082 yusufgbt/yb-library:latest

# PostgreSQL'i çalıştır
docker run -d --name yb_library_db -e POSTGRES_DB=library -e POSTGRES_USER=library_user -e POSTGRES_PASSWORD=library123 -p 5432:5432 postgres:15
```

### 2. Tek Komutla Her Şeyi Başlat
```bash
# docker-compose.yml dosyası varsa:
docker-compose up -d

# Yoksa manuel olarak:
docker run -d --name yb_library_db -e POSTGRES_DB=library -e POSTGRES_USER=library_user -e POSTGRES_PASSWORD=library123 -p 5432:5432 postgres:15 && docker run -d --name yb_library_app -e DB_HOST=host.docker.internal -e DB_PORT=5432 -e DB_NAME=library -e DB_USER=library_user -e DB_PASSWORD=library123 -e ADMIN_USERNAME=yusufgbt -e ADMIN_PASSWORD=yusuf1234 -p 8082:8082 yusufgbt/yb-library:latest
```

## 📱 Docker Desktop'ta Görüntüleme

1. **Docker Desktop'ı açın**
2. **Containers** sekmesine gidin
3. `yb_library_app` ve `yb_library_db` container'larını göreceksiniz
4. **Ports** sütununda 8082 ve 5432 portlarını göreceksiniz

## 🌐 Tarayıcıda Açma

- **Kütüphane Sistemi**: http://localhost:8082
- **Admin Giriş**: 
  - Kullanıcı: `yusufgbt`
  - Şifre: `yusuf1234`

## 🛑 Durdurma

```bash
# Container'ları durdur
docker stop yb_library_app yb_library_db

# Container'ları sil
docker rm yb_library_app yb_library_db

# Veya tek komutla
docker stop yb_library_app yb_library_db && docker rm yb_library_app yb_library_db
```

## 🔄 Yeniden Başlatma

```bash
# Container'ları yeniden başlat
docker restart yb_library_app yb_library_db
```

## 📊 Durum Kontrolü

```bash
# Çalışan container'ları listele
docker ps

# Tüm container'ları listele (durmuş olanlar dahil)
docker ps -a

# Container log'larını görüntüle
docker logs yb_library_app
docker logs yb_library_db
```

## 🎯 Önemli Notlar

- **Port 8082** kullanımdaysa, başka bir port kullanın
- **PostgreSQL** önce başlatılmalı
- **Veritabanı** otomatik oluşturulur
- **Admin girişi** otomatik aktif olur

## 🆘 Sorun Giderme

### Port Çakışması
```bash
# Port 8082'yi kullanan process'i bul
netstat -tlnp | grep 8082

# Eğer kullanımdaysa, farklı port kullan
docker run -d --name yb_library_app -p 8083:8082 yusufgbt/yb-library:latest
```

### Veritabanı Bağlantı Hatası
```bash
# PostgreSQL container'ının çalıştığını kontrol et
docker ps | grep postgres

# Log'ları kontrol et
docker logs yb_library_db
```


