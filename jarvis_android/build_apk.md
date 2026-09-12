# Jarvis'i Android .apk dosyasına çevirme

Android APK'lar sadece **Linux (veya WSL)** üzerinde, Android SDK/NDK indirilerek derlenebilir.
Anthropic'in sunucusunda bu SDK'ları indirecek internet erişimi yok, bu yüzden APK'yı
**kendi bilgisayarında (Ubuntu/Linux önerilir, Windows'ta WSL2 ile de olur)** üreteceksin.
Talimatları harfiyen takip edersen 30-60 dakika içinde çalışan bir APK'n olur.

## 1. Linux ortamı hazırla
- Zaten Ubuntu/Linux kullanıyorsan direkt devam et.
- Windows kullanıyorsan: "WSL2 Ubuntu kurulumu" diye aratıp Microsoft Store'dan Ubuntu kur,
  sonra Ubuntu terminalini aç.

## 2. Gerekli sistem paketlerini kur
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv build-essential git \
    zip unzip openjdk-17-jdk autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

## 3. Sanal ortam oluştur ve buildozer kur
```bash
python3 -m venv jarvis-env
source jarvis-env/bin/activate
pip install --upgrade pip
pip install buildozer cython==0.29.36
```

## 4. Proje klasörüne gir
`main.py` ve `buildozer.spec` dosyalarının olduğu `jarvis_android` klasörüne gir:
```bash
cd jarvis_android
```

## 5. APK'yı derle (ilk seferde Android SDK/NDK otomatik indirilir, biraz sürer)
```bash
buildozer -v android debug
```

İşlem bitince APK dosyan şurada olacak:
```
bin/jarvis-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

## 6. Telefona yükleme
- APK dosyasını telefonuna aktar (USB kablo, Google Drive, Telegram "kendine gönder" vb.).
- Telefonunda **Ayarlar > Güvenlik > Bilinmeyen kaynaklardan yükleme**yi aç.
- APK dosyasına dokunup kur.
- İlk açılışta mikrofon iznini "izin ver" de.

### Sık karşılaşılan sorunlar
- **"buildozer command not found"** → `source jarvis-env/bin/activate` çalıştırmayı unutmuş olabilirsin.
- **İndirme çok uzun sürüyor** → İlk derlemede Android SDK/NDK (birkaç GB) indirilir, normaldir.
- **Derleme hata veriyor** → Hata mesajının tamamını kopyalayıp bana gönder, birlikte çözeriz.
- Ses tanıma sadece cihazda internet varken çalışır (Google servislerini kullanır).
