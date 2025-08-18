# 🚀 GitHub Entegrasyonu Kurulum Rehberi

## 📋 Adım 1: GitHub'da Repository Oluştur
1. [GitHub.com](https://github.com) adresine git
2. Sağ üstteki **"+"** butonuna tıkla
3. **"New repository"** seç
4. Repository adı: `nicegui-library-system`
5. Açıklama: `Modern kütüphane yönetim sistemi - NiceGUI + SQLite`
6. **Public** seç
7. **"Create repository"** butonuna tıkla

## 🔗 Adım 2: Remote URL Ekle
Repository oluşturduktan sonra aşağıdaki komutu çalıştır:

```bash
git remote add origin https://github.com/KULLANICI_ADIN/nicegui-library-system.git
```

**Not:** `KULLANICI_ADIN` yerine kendi GitHub kullanıcı adını yaz!

## 📤 Adım 3: GitHub'a Push Et
```bash
git push -u origin main
```

## 🔐 Adım 4: GitHub Token Oluştur (İlk kez)
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **"Generate new token"** → **"Generate new token (classic)"**
3. Note: `nicegui-library-token`
4. Expiration: `90 days`
5. Scopes: `repo` (tüm repo izinleri)
6. **"Generate token"** butonuna tıkla
7. Token'ı kopyala ve güvenli bir yere kaydet

## 🔄 Adım 5: VS Code'da GitHub Entegrasyonu
1. VS Code'u aç
2. Sol tarafta **Source Control** (Git) ikonuna tıkla
3. **"Publish to GitHub"** butonuna tıkla
4. Repository adını gir: `nicegui-library-system`
5. Public/Private seç
6. **"OK"** butonuna tıkla

## ✨ Adım 6: Otomatik Sync
VS Code artık otomatik olarak:
- ✅ Commit'leri GitHub'a push edecek
- ✅ Pull/Push işlemlerini yapacak
- ✅ Branch'leri yönetecek
- ✅ Merge conflict'leri çözecek

## 🎯 Sonuç
Artık projeniz GitHub'da ve VS Code tam entegre! 🎉

---
**Not:** Bu dosyayı kurulum tamamlandıktan sonra silebilirsiniz.
