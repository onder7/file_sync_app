# File Synchronization Application
# Dosya Senkronizasyon Uygulaması
[Türkçe Version](TR-README.md)
![image](https://github.com/user-attachments/assets/e885c99d-098e-457d-89c3-bd5b0fbc413e)
## Features
- Folder and file-based synchronization
- Automatic synchronization and scheduling
- Customizable file and folder patterns
- Fast copying with multi-thread support
- Backup functionality
- Detailed logging
- User-friendly interface

## Installation
1. Download the application
2. Install required modules:
   ```
   pip install -r requirements.txt
   ```
3. Start the application:
>>>>>>> d6cd7d558d01d37034368c48461595fb192eb78c
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
=======
## Usage
1. **Source Folder**: Folder containing files to be synchronized
2. **Target Folder**: Folder where files will be copied
3. **Folder Patterns**: Which folders to synchronize (e.g., "9H-C*")
4. **File Patterns**: Which files to synchronize (e.g., "*.wgl")
5. **Check Interval**: Waiting period for synchronization check (seconds)

## Settings
- **Folder Patterns**: Determines folders to be synchronized
  - Example: "9H-C*" (all folders starting with 9H-C)
  - Use commas for multiple patterns: "9H-C*, TEST*"

- **File Patterns**: Determines files to be synchronized
  - Example: "*.wgl" (all files with wgl extension)
  - Use commas for multiple patterns: "*.wgl, *.txt"

- **Excluded Patterns**: Items to be excluded from synchronization
  - Example: ".git/*, *.tmp"

- **Check Interval**: Synchronization check frequency (seconds)
  - Recommended: 10-60 seconds

- **Thread Count**: Number of parallel copy operations
  - Recommended: 2-8

## Logs
- Logs are kept in the `logs` folder
- Separate log file for each day
- Format: `file_sync_YYYYMMDD.log`

## Backup
- When "Backup Modified Files" option is enabled:
  - Modified files are backed up
  - Backup format: `filename.extension.bak.timestamp`

## Email Notifications
- Email notification for error conditions
- Synchronization summary delivery
- Gmail or custom SMTP server support

## Licensing

- Full version features:
  - Unlimited folder synchronization
  - Email notifications
  - Backup features
  - Priority support

## System Requirements
- Windows 7 or higher
- Minimum 2GB RAM
- Python 3.8 or higher

## Security
- Application works only on specified folders
- Does not interfere with system files
- All operations are logged

## Support and Contact
- Email: onder7@gmail.com
- GitHub: https://github.com/onder7
- Web: https://ondernet.net

## License
This software is distributed under the MIT license.

## Version History
### v2.1.0 (2024-02-29)
- Added email notifications
- Performance improvements
- Bug fixes

### v2.0.0 (2024-02-16)
- Initial release
- Basic synchronization features
- GUI interface
- Logging system
>>>>>>> d6cd7d558d01d37034368c48461595fb192eb78c
