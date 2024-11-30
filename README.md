# Dosya Senkronizasyon Uygulaması

## Özellikler
- Klasör ve dosya bazlı senkronizasyon
- Otomatik senkronizasyon ve zamanlama
- Özelleştirilebilir dosya ve klasör desenleri
- Çoklu thread desteği ile hızlı kopyalama
- Yedekleme özelliği
- Detaylı loglama
- Kullanıcı dostu arayüz

## Kurulum
1. Uygulamayı indirin
2. Gerekli modülleri yükleyin:
   ```
   pip install -r requirements.txt
   ```
3. Uygulamayı başlatın:
   ```
   python run.py
   ```

## Kullanım
1. **Kaynak Klasör**: Senkronize edilecek dosyaların bulunduğu klasör
2. **Hedef Klasör**: Dosyaların kopyalanacağı klasör
3. **Klasör Desenleri**: Hangi klasörlerin senkronize edileceği (örn: "9H-C*")
4. **Dosya Desenleri**: Hangi dosyaların senkronize edileceği (örn: "*.wgl")
5. **Kontrol Aralığı**: Senkronizasyon kontrolü için bekleme süresi (saniye)

## Ayarlar
- **Klasör Desenleri**: Senkronize edilecek klasörleri belirler
  - Örnek: "9H-C*" (9H-C ile başlayan tüm klasörler)
  - Birden fazla desen için virgül kullanın: "9H-C*, TEST*"

- **Dosya Desenleri**: Senkronize edilecek dosyaları belirler
  - Örnek: "*.wgl" (wgl uzantılı tüm dosyalar)
  - Birden fazla desen için virgül kullanın: "*.wgl, *.txt"

- **Hariç Tutulan Desenler**: Senkronizasyona dahil edilmeyecek öğeler
  - Örnek: ".git/*, *.tmp"

- **Kontrol Aralığı**: Senkronizasyon kontrol sıklığı (saniye)
  - Önerilen: 10-60 saniye arası

- **Thread Sayısı**: Paralel kopyalama işlemi sayısı
  - Önerilen: 2-8 arası

## Loglar
- Loglar `logs` klasöründe tutulur
- Her gün için ayrı log dosyası oluşturulur
- Format: `file_sync_YYYYMMDD.log`

## Yedekleme
- "Değiştirilen Dosyaları Yedekle" seçeneği aktif edildiğinde:
  - Değiştirilen dosyaların yedeği alınır
  - Yedek format: `dosyaadi.uzanti.bak.timestamp`

## E-posta Bildirimleri
- Hata durumlarında e-posta bildirimi
- Senkronizasyon özeti gönderimi
- Gmail veya özel SMTP sunucu desteği

## Lisanslama

- Tam sürüm özellikleri:
  - Sınırsız klasör senkronizasyonu
  - E-posta bildirimleri
  - Yedekleme özellikleri
  - Öncelikli destek

## Sistem Gereksinimleri
- Windows 7 veya üzeri
- Minimum 2GB RAM
- Python 3.8 veya üzeri

## Güvenlik
- Uygulama sadece belirlenen klasörler üzerinde çalışır
- Sistem dosyalarına müdahale etmez
- Tüm işlemler loglanır

## Destek ve İletişim
- E-posta: onder7@gmail.com
- GitHub: https://github.com/onder7
- Web: https://ondernet.net

## Lisans
Bu yazılım MIT lisansı altında dağıtılmaktadır.

## Versiyon Geçmişi
### v2.1.0 (2024-02-29)

- E-posta bildirimleri eklendi
- Performans iyileştirmeleri yapıldı
- Hata düzeltmeleri

### v2.0.0 (2024-02-16)
- İlk sürüm
- Temel senkronizasyon özellikleri
- GUI arayüz
- Loglama sistemi