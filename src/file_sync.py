"""
Ana dosya senkronizasyon sınıfı
"""

import os
import shutil
import time
import logging
import fnmatch
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import queue
from typing import Callable, Optional, List, Dict
import json
import traceback

from .sync_config import SyncConfig
from .sync_stats import SyncStats
from .notification_service import EmailConfig, EmailNotificationService
from .exceptions import (
    SyncError, FileOperationError, ValidationError,
    ThreadError, PermissionError, InterruptError
)

class FileSync:
    """Dosya senkronizasyon sınıfı"""
    
    def __init__(self):
        """Başlatıcı"""
        self.config = SyncConfig.from_file()
        self.setup_logging()
        self.sync_queue: queue.Queue = queue.Queue()
        self.is_running: bool = False
        self.sync_thread: Optional[threading.Thread] = None
        self.stats = SyncStats()
        self.status_callback: Optional[Callable[[str], None]] = None
        self._stop_event = threading.Event()
        self.load_email_config()

    def setup_logging(self) -> None:
        """Loglama ayarlarını yapılandır"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'file_sync_{datetime.now().strftime("%Y%m%d")}.log'
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
        )
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        # Önceki handlers'ları temizle
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    def load_email_config(self):
        """E-posta ayarlarını yükle"""
        try:
            config_path = Path('email_config.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.email_config = EmailConfig(
                        smtp_server=config_data.get('smtp_server', ''),
                        smtp_port=int(config_data.get('smtp_port', 587)),
                        username=config_data.get('username', ''),
                        password=config_data.get('password', ''),
                        from_email=config_data.get('from_email', ''),
                        to_emails=config_data.get('to_emails', []),
                        use_ssl=config_data.get('use_ssl', True)
                    )
                    logging.info("E-posta ayarları yüklendi")
            else:
                self.email_config = None
                logging.warning("E-posta yapılandırma dosyası bulunamadı")
        except Exception as e:
            logging.error(f"E-posta ayarları yüklenemedi: {str(e)}")
            self.email_config = None
    def send_error_notification(self, error_message: str, file_info: dict = None):
        """Hata bildirimini e-posta ile gönder"""
        if not self.email_config or not self.email_config.username:
            logging.warning("E-posta bildirimi yapılandırılmamış")
            return False

        try:
            # Hata detaylarını hazırla
            error_details = {
                'Zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Hata': error_message,
                'İstatistikler': {
                    'Kopyalanan Dosya Sayısı': self.stats.files_copied,
                    'Toplam Boyut': self.stats.format_size(self.stats.bytes_copied),
                    'Son İşlem': self.stats.current_file
                }
            }

            if file_info:
                error_details.update(file_info)

            # Hata stack trace'i ekle
            stack_trace = traceback.format_exc()
            if stack_trace != "NoneType: None\n":
                error_details['Stack Trace'] = stack_trace

            # E-posta gönder
            notification_service = EmailNotificationService(self.email_config)
            notification_service.send_error_notification(
                error_message=f"Dosya Senkronizasyon Hatası: {error_message}",
                details=error_details
            )
            logging.info("Hata bildirimi e-posta ile gönderildi")
            return True

        except Exception as e:
            logging.error(f"Hata bildirimi gönderilemedi: {str(e)}")
            return False

    def validate_paths(self, source: str, target: str) -> None:
        """Yolları doğrula"""
        try:
            if not source or not target:
                raise ValidationError("Kaynak ve hedef yollar boş olamaz")
                
            source_path = Path(source)
            target_path = Path(target)
                
            if not source_path.exists():
                raise ValidationError(f"Kaynak klasör bulunamadı: {source}")
                
            if not source_path.is_dir():
                raise ValidationError(f"Kaynak bir klasör değil: {source}")
                
            # Hedef klasörün alt klasör kontrolü
            if target_path.exists() and source_path in target_path.parents:
                raise ValidationError("Hedef klasör, kaynak klasörün alt klasörü olamaz")
                
            # Yazma izinleri kontrolü
            try:
                os.makedirs(target, exist_ok=True)
                test_file = Path(target) / '.write_test'
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                raise PermissionError(f"Hedef klasöre yazma izni yok: {str(e)}")
                
            logging.debug(f"Yol doğrulaması başarılı: {source} -> {target}")
            
        except Exception as e:
            logging.error(f"Yol doğrulama hatası: {str(e)}")
            raise

    def should_copy_file(self, source_path: str) -> bool:
        """Dosyanın kopyalanıp kopyalanmayacağını kontrol et"""
        try:
            if not self.config.date_filter_enabled:
                return True

            file_time = datetime.fromtimestamp(os.path.getmtime(source_path))
            
            if self.config.start_date:
                try:
                    start_date = datetime.strptime(self.config.start_date, '%Y-%m-%d')
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    if file_time < start_date:
                        logging.debug(f"Dosya tarihi başlangıç tarihinden önce: {source_path}")
                        return False
                except ValueError as e:
                    logging.error(f"Başlangıç tarihi format hatası: {e}")
                    
            if self.config.end_date:
                try:
                    end_date = datetime.strptime(self.config.end_date, '%Y-%m-%d')
                    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    if file_time > end_date:
                        logging.debug(f"Dosya tarihi bitiş tarihinden sonra: {source_path}")
                        return False
                except ValueError as e:
                    logging.error(f"Bitiş tarihi format hatası: {e}")
                    
            return True
            
        except Exception as e:
            logging.error(f"Tarih kontrolü hatası ({source_path}): {str(e)}")
            return True
    def copy_file(self, src: str, dst: str) -> None:
        """Dosyayı ilerleme bilgisi ile kopyala"""
        try:
            # Hedef dizini kontrol et ve oluştur
            dst_dir = os.path.dirname(dst)
            os.makedirs(dst_dir, exist_ok=True)

            file_size = os.path.getsize(src)
            chunk_size = 1024 * 1024  # 1MB chunks

            # Büyük dosyaları chunk'lar halinde kopyala
            if file_size > chunk_size:
                with open(src, 'rb') as fsrc:
                    with open(dst, 'wb') as fdst:
                        copied = 0
                        while True:
                            if self._stop_event.is_set():
                                raise InterruptError("Kopyalama işlemi kullanıcı tarafından durduruldu")
                                
                            chunk = fsrc.read(chunk_size)
                            if not chunk:
                                break
                            fdst.write(chunk)
                            copied += len(chunk)
                            
                            if self.status_callback:
                                progress = (copied / file_size) * 100
                                self.status_callback(
                                    f"Kopyalanıyor: {os.path.basename(src)} - %{progress:.1f}",
                                    progress
                                )
            else:
                # Küçük dosyaları direkt kopyala
                shutil.copy2(src, dst)
                if self.status_callback:
                    self.status_callback(f"Kopyalandı: {os.path.basename(src)}", 100)

            # Tarih ve izinleri kopyala
            shutil.copystat(src, dst)

            # İstatistikleri güncelle
            self.stats.update(
                bytes_copied=file_size,
                files_copied=1,
                current_file=os.path.basename(src)
            )

            logging.debug(f"Dosya başarıyla kopyalandı: {src} -> {dst}")

        except PermissionError as e:
            error_msg = f"Dosya erişim izni hatası ({src}): {str(e)}"
            self.send_error_notification(error_msg, {
                'Kaynak Dosya': src,
                'Hedef Dosya': dst,
                'Hata Türü': 'İzin Hatası',
                'Dosya Boyutu': self.stats.format_size(file_size)
            })
            raise PermissionError(error_msg)

        except InterruptError:
            raise

        except Exception as e:
            error_msg = f"Dosya kopyalama hatası ({src}): {str(e)}"
            self.send_error_notification(error_msg, {
                'Kaynak Dosya': src,
                'Hedef Dosya': dst,
                'Hata Türü': 'Kopyalama Hatası'
            })
            raise FileOperationError(error_msg)

    def create_backup(self, file_path: str) -> Optional[str]:
        """Dosyanın yedeğini oluştur"""
        if not self.config.backup_enabled:
            return None
            
        try:
            timestamp = int(time.time())
            backup_dir = Path(file_path).parent / 'backups'
            backup_dir.mkdir(exist_ok=True)
            
            # Yedek dosya adını oluştur
            file_name = Path(file_path).name
            backup_name = f"{file_name}.bak.{timestamp}"
            backup_path = backup_dir / backup_name
            
            # Dosyayı yedekle
            shutil.copy2(file_path, backup_path)
            logging.info(f'Yedek oluşturuldu: {backup_path}')
            
            # Eski yedekleri temizle (opsiyonel)
            self._cleanup_old_backups(backup_dir, file_name)
            
            return str(backup_path)
            
        except Exception as e:
            error_msg = f"Yedek oluşturma hatası ({file_path}): {str(e)}"
            logging.error(error_msg)
            self.send_error_notification(error_msg, {
                'Dosya': file_path,
                'Hata Türü': 'Yedekleme Hatası'
            })
            return None

    def _cleanup_old_backups(self, backup_dir: Path, file_name: str, max_backups: int = 5):
        """Eski yedekleri temizle"""
        try:
            # Dosyaya ait tüm yedekleri bul
            backups = list(backup_dir.glob(f"{file_name}.bak.*"))
            backups.sort(key=lambda x: os.path.getctime(x))
            
            # Maksimum yedek sayısını aş if len(backups) > max_backups:
            if len(backups) > max_backups:
                # En eski yedekleri sil
                for old_backup in backups[:-max_backups]:
                    try:
                        old_backup.unlink()
                        logging.debug(f"Eski yedek silindi: {old_backup}")
                    except Exception as e:
                        logging.warning(f"Eski yedek silinirken hata: {e}")
                        
        except Exception as e:
            logging.error(f"Yedek temizleme hatası: {str(e)}")
    def sync_files(self, source: str, target: str) -> None:
        """Dosyaları senkronize et"""
        try:
            self.validate_paths(source, target)
            self.stats.reset()

            # Thread havuzunu oluştur
            with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
                futures = []
                
                # Tüm dosyaları tara
                for root, dirs, files in os.walk(source):
                    if self._stop_event.is_set():
                        break

                    # Klasör filtreleme
                    dirs[:] = [
                        d for d in dirs
                        if any(fnmatch.fnmatch(d, pat.strip())
                            for pat in self.config.folder_patterns.split(','))
                    ]

                    for file in files:
                        if self._stop_event.is_set():
                            break

                        # Dosya filtreleme
                        if not any(fnmatch.fnmatch(file, pat.strip())
                                 for pat in self.config.file_patterns.split(',')):
                            continue

                        # Hariç tutma kontrolü
                        if any(fnmatch.fnmatch(file, pat.strip())
                             for pat in self.config.exclude_patterns.split(',')):
                            logging.debug(f"Dosya hariç tutuldu: {file}")
                            continue

                        source_path = os.path.join(root, file)
                        rel_path = os.path.relpath(source_path, source)
                        target_path = os.path.join(target, rel_path)

                        if self.should_copy_file(source_path):
                            if (not os.path.exists(target_path) or
                                os.path.getmtime(source_path) > os.path.getmtime(target_path)):
                                
                                if os.path.exists(target_path):
                                    self.create_backup(target_path)
                                    
                                futures.append(
                                    executor.submit(self.copy_file, source_path, target_path)
                                )

                # İşlemleri takip et ve hataları yakala
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"Dosya kopyalama hatası: {str(e)}")
                        if not isinstance(e, InterruptError):
                            self.send_error_notification(str(e))
                            if self.status_callback:
                                self.status_callback(f"Hata: {str(e)}")

            # İstatistikleri güncelle
            self.stats.complete()
            
            # Özet log
            summary = self.stats.get_summary()
            logging.info(summary)
            if self.status_callback:
                self.status_callback(f"Senkronizasyon tamamlandı: {summary}")

        except InterruptError:
            logging.info("Senkronizasyon kullanıcı tarafından durduruldu")
            if self.status_callback:
                self.status_callback("Senkronizasyon durduruldu")
            raise

        except Exception as e:
            error_msg = f'Senkronizasyon hatası: {str(e)}'
            logging.error(error_msg)
            self.send_error_notification(error_msg, {
                'Kaynak Klasör': source,
                'Hedef Klasör': target,
                'Hata Türü': 'Senkronizasyon Hatası'
            })
            raise SyncError(error_msg)

    def start(self, source: str, target: str) -> None:
        """Senkronizasyonu başlat"""
        if self.is_running:
            logging.warning("Senkronizasyon zaten çalışıyor")
            return

        self.is_running = True
        self._stop_event.clear()
        
        try:
            self.sync_thread = threading.Thread(
                target=self._sync_worker,
                args=(source, target),
                name="SyncThread"
            )
            self.sync_thread.daemon = True
            self.sync_thread.start()
            
        except Exception as e:
            self.is_running = False
            error_msg = f"Thread başlatma hatası: {str(e)}"
            self.send_error_notification(error_msg)
            raise ThreadError(error_msg)

    def stop(self) -> None:
        """Senkronizasyonu durdur"""
        if not self.is_running:
            return
            
        self._stop_event.set()
        self.is_running = False
        
        if self.sync_thread and self.sync_thread.is_alive():
            try:
                self.sync_thread.join(timeout=5.0)
                if self.sync_thread.is_alive():
                    raise ThreadError("Thread durdurulamadı")
            except Exception as e:
                error_msg = f"Thread durdurma hatası: {str(e)}"
                logging.error(error_msg)
                self.send_error_notification(error_msg)
                
        self._stop_event.clear()

    def _sync_worker(self, source: str, target: str) -> None:
        """Senkronizasyon worker thread'i"""
        try:
            while self.is_running and not self._stop_event.is_set():
                try:
                    self.sync_files(source, target)
                    
                    # Kontrol aralığı kadar bekle
                    wait_start = time.time()
                    while (time.time() - wait_start < self.config.check_interval and 
                           not self._stop_event.is_set()):
                        time.sleep(0.1)  # Küçük aralıklarla kontrol et
                        
                except InterruptError:
                    logging.info("Senkronizasyon durduruldu")
                    break
                except Exception as e:
                    error_msg = f"Senkronizasyon hatası: {str(e)}"
                    logging.error(error_msg)
                    self.send_error_notification(error_msg)
                    if self.status_callback:
                        self.status_callback(f"Hata: {str(e)}")
                    break
                    
        finally:
            self.is_running = False
            if self.status_callback:
                self.status_callback("Senkronizasyon tamamlandı")