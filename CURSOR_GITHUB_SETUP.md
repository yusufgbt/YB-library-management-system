# 🚀 Cursor + GitHub Entegrasyonu Kurulum Rehberi

## 🎯 Tamamlanan Adımlar

✅ **Git Repository başlatıldı**
✅ **Cursor GitHub extension'ları kuruldu**
✅ **Profesyonel README oluşturuldu**
✅ **Commit'ler yapıldı**

## 🔧 Kurulan Extension'lar

- **GitHub Pull Requests**: `github.vscode-pull-request-github`
- **GitLens**: `eamodio.gitlens` (Git geçmişi ve blame)
- **Git Graph**: `mhutchie.git-graph` (Git branch görselleştirme)

## 🚀 Cursor'da GitHub Entegrasyonu

### 1. Cursor'u Aç
```bash
cursor .
```

### 2. GitHub Hesabını Bağla
1. **Command Palette** aç: `Ctrl+Shift+P` (Windows/Linux) veya `Cmd+Shift+P` (Mac)
2. **"GitHub: Sign in"** yaz ve seç
3. GitHub hesabınızla giriş yapın
4. Gerekli izinleri verin

### 3. Source Control Panel
1. Sol tarafta **Source Control** (Git) ikonuna tıkla
2. **"Publish to GitHub"** butonuna tıkla (eğer görünüyorsa)
3. Repository adını gir: `nicegui-library-system`
4. Public/Private seç
5. **"OK"** butonuna tıkla

## 🎨 Cursor GitHub Özellikleri

### Source Control Panel
- ✅ **Commit yapma** - Değişiklikleri commit et
- ✅ **Branch değiştirme** - Farklı branch'lere geç
- ✅ **Merge conflict çözme** - Çakışmaları çöz
- ✅ **Git log görüntüleme** - Commit geçmişini gör

### GitHub Integration
- ✅ **Pull Request oluşturma** - GitHub'da PR aç
- ✅ **Issue yönetimi** - Issue'ları takip et
- ✅ **Code review** - Kod incelemesi yap
- ✅ **Branch protection** - Branch koruma kuralları

### GitLens Features
- ✅ **Line-by-line blame** - Satır satır kim yazdı
- ✅ **Git history** - Dosya geçmişi
- ✅ **Branch comparison** - Branch karşılaştırma
- ✅ **File history** - Dosya değişim geçmişi

### Git Graph Features
- ✅ **Görsel branch yönetimi** - Branch'leri görsel olarak gör
- ✅ **Commit grafikleri** - Git geçmişini grafik olarak gör
- ✅ **Branch merging** - Branch birleştirme işlemleri

## 🔄 Günlük Kullanım

### Yeni Özellik Ekleme
```bash
# Yeni branch oluştur
git checkout -b feature/yeni-ozellik

# Kod yaz ve test et
# ...

# Commit yap
git add .
git commit -m "✨ Yeni özellik eklendi"

# Push et
git push origin feature/yeni-ozellik

# GitHub'da Pull Request oluştur
```

### Güncellemeleri Alma
```bash
# Ana branch'e geç
git checkout main

# Güncellemeleri al
git pull origin main

# Feature branch'i güncelle
git checkout feature/yeni-ozellik
git rebase main
```

## 🎯 Cursor'da Git Kullanımı

### 1. Source Control Panel
- Sol tarafta Git ikonuna tıkla
- Değişiklikleri gör ve stage et
- Commit mesajı yaz ve commit yap

### 2. GitLens Panel
- Sol tarafta GitLens ikonuna tıkla
- Git geçmişini görüntüle
- Branch'leri yönet

### 3. Git Graph
- Command Palette'de **"Git Graph: View Git Graph"** yaz
- Görsel Git geçmişini görüntüle

### 4. GitHub Pull Requests
- Sol tarafta GitHub ikonuna tıkla
- Pull Request'leri görüntüle
- Yeni PR oluştur

## 🔐 GitHub Token Kurulumu

### 1. GitHub Token Oluştur
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **"Generate new token"** → **"Generate new token (classic)"**
3. Note: `cursor-library-token`
4. Expiration: `90 days`
5. Scopes: `repo` (tüm repo izinleri)
6. **"Generate token"** butonuna tıkla
7. Token'ı kopyala ve güvenli bir yere kaydet

### 2. Cursor'da Token Kullan
- Cursor otomatik olarak GitHub token'ını kullanacak
- Gerekirse Command Palette'den **"GitHub: Sign in"** yap

## 🎯 Sonuç

Artık Cursor'unuz GitHub ile tam entegre! 🎉

### Kullanabileceğiniz Özellikler:
- 📝 **Otomatik commit** ve push
- 🔄 **Pull/Push** işlemleri
- 🌿 **Branch yönetimi**
- 🔍 **Git geçmişi** görüntüleme
- 📊 **Görsel Git grafikleri**
- 🔗 **GitHub Issues** ve **Pull Requests**

### Sonraki Adımlar:
1. GitHub'da repository oluştur
2. Remote URL ekle
3. İlk push yap
4. Cursor'da GitHub hesabını bağla

## 🆚 Cursor vs VS Code

### Cursor Avantajları:
- 🚀 **Daha hızlı** performans
- 🤖 **AI destekli** kod yazımı
- 🎨 **Modern arayüz**
- 🔍 **Gelişmiş arama** özellikleri

### GitHub Entegrasyonu:
- ✅ **Aynı extension'lar** çalışır
- ✅ **Aynı Git komutları** kullanılır
- ✅ **Aynı GitHub özellikleri** mevcut

---

**Not:** Bu dosyayı kurulum tamamlandıktan sonra silebilirsiniz.
