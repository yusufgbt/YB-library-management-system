# Kütüphane Uygulaması (NiceGUI + SQLite)

Basit bir kütüphane yönetim sistemi. NiceGUI arayüzü ile kitap/üye yönetimi ve ödünç-iade takibi sağlar. Veriler `SQLite` üzerinde tutulur.

## Özellikler
- Kitap ekleme, düzenleme, silme
- Üye ekleme, düzenleme, silme
- Kitabı uygun/ödünçte durum takibi
- Ödünç verme ve iade alma

## Gerekli Yazılımlar
- Python 3.9+

## Kurulum
```bash
cd /home/yusuf/nicegui_sqlite
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma
```bash
python main.py
```
Ardından tarayıcıdan `http://localhost:8080` adresine gidin.

## Dosya Yapısı
- `main.py`: Uygulamanın giriş noktası ve tüm arayüz/iş mantığı
- `database.db`: SQLite veritabanı dosyası (otomatik oluşturulur)
- `requirements.txt`: Python bağımlılıkları

## Notlar
- Veritabanı yolu: `/home/yusuf/nicegui_sqlite/database.db`
- Port meşgulse `main.py` içinde `ui.run(port=XXXX)` ile farklı bir port seçebilirsiniz.
- Canlı yenileme gerekmez; `ui.run(reload=False)` ile başlar.
