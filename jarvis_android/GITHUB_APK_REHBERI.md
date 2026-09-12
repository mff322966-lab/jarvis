# GitHub üzerinden APK'yı otomatik derletme (Linux/WSL gerekmez!)

Bu yöntemde hiçbir şey kendi bilgisayarına kurman gerekmiyor. GitHub'ın ücretsiz
sunucuları senin için APK'yı derleyip hazır dosya olarak sunuyor.

## 1. GitHub'da yeni bir repo (depo) oluştur
1. https://github.com adresine gir, giriş yap.
2. Sağ üstteki **+** işaretine tıkla → **New repository**.
3. İsim ver, örneğin: `jarvis-android`
4. **Public** seç (Private de olur ama Actions dakika limiti Public'te daha rahat).
5. **Create repository** de.

## 2. jarvis_android klasörünü GitHub'a yükle
En kolay yol — tarayıcıdan sürükle-bırak:
1. Az önce oluşturduğun repo sayfasında **"uploading an existing file"** linkine tıkla.
2. `jarvis_android` klasörünün İÇİNDEKİ tüm dosya ve klasörleri (main.py, buildozer.spec,
   build_apk.md, .github klasörü dahil) oraya sürükle bırak.
   ⚠️ Önemli: `.github` klasörü gizli görünebilir, dosya gezgininde "gizli dosyaları göster"
   seçeneğini aç ki onu da sürükleyebilesin. Görünmüyorsa bana söyle, alternatif yöntem
   göstereyim (git komutlarıyla yükleme).
3. Altta **"Commit changes"** butonuna bas.

## 3. Derlemenin başlamasını bekle
1. Repo sayfasında üstteki **"Actions"** sekmesine tıkla.
2. **"Build Jarvis APK"** adında bir işlemin otomatik başladığını göreceksin
   (sarı nokta = çalışıyor, yeşil tik = bitti, kırmızı çarpı = hata var).
3. İlk derleme **15-30 dakika** sürebilir (Android SDK/NDK indirildiği için). Sabırlı ol.

## 4. APK'yı indir
1. İşlem yeşil tik olunca üstüne tıkla.
2. Sayfanın en altında **"Artifacts"** bölümünde **"jarvis-apk"** yazan bir dosya göreceksin.
3. Ona tıkla, bir .zip inecek. İçini açınca **.apk** dosyasını bulacaksın.

## 5. Telefona kurma
1. APK dosyasını telefonuna gönder (Google Drive, WhatsApp kendine mesaj, USB kablo — hangisi kolaysa).
2. Telefonda **Ayarlar > Güvenlik > Bilinmeyen kaynaklardan yükleme**yi aç.
3. APK'ya dokun, **Kur**'a bas.
4. Açılınca mikrofon izni isteyecek, **izin ver**.

## Hata alırsan
"Actions" sekmesinde kırmızı çarpı görürsen, üstüne tıkla, kırmızı yazan hata satırını
kopyalayıp bana gönder — birlikte düzeltiriz. Bu tür derleme hataları genelde
`buildozer.spec` içindeki bir ayarla ilgilidir, kolayca çözülür.
