"""
Ana GUI Uygulaması
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional
from pathlib import Path
import threading
from datetime import datetime
import os
import json

from .file_sync import FileSync
from .sync_config import SyncConfig
from .exceptions import SyncError, ValidationError
from .notification_service import EmailConfig, EmailNotificationService
from .gui_components import (
    PathSelector, ConfigEntry, DateFilterFrame,
    StatusBar, AboutDialog, ControlButtons,
    EmailSettingsDialog
)



class SyncGUI:
    """Ana GUI sınıfı"""
    def __init__(self):
        self.file_sync = FileSync()
        self.load_email_config()
        self.setup_main_window()
        self.create_widgets()
        self.load_config()
        self.setup_bindings()
    
    def load_email_config(self):
        """E-posta ayarlarını yükle"""
        self.email_config = EmailConfig()
        config_path = Path('email_config.json')
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.email_config = EmailConfig(
                        smtp_server=config_data.get('smtp_server', 'smtp.gmail.com'),
                        smtp_port=int(config_data.get('smtp_port', 587)),
                        username=config_data.get('username', ''),
                        password=config_data.get('password', ''),
                        from_email=config_data.get('from_email', ''),
                        to_emails=config_data.get('to_emails', []),
                        use_ssl=config_data.get('use_ssl', True)
                    )
            except Exception as e:
                logging.error(f"E-posta ayarları yüklenirken hata: {str(e)}")

    def save_email_config(self):
        """E-posta ayarlarını kaydet"""
        try:
            config_data = {
                'smtp_server': self.email_config.smtp_server,
                'smtp_port': self.email_config.smtp_port,
                'username': self.email_config.username,
                'password': self.email_config.password,
                'from_email': self.email_config.from_email,
                'to_emails': self.email_config.to_emails,
                'use_ssl': self.email_config.use_ssl
            }
            
            with open('email_config.json', 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
                
        except Exception as e:
            logging.error(f"E-posta ayarları kaydedilirken hata: {str(e)}")
            messagebox.showerror("Hata", f"E-posta ayarları kaydedilemedi: {str(e)}")

    def setup_main_window(self):
        """Ana pencere ayarları"""
        self.root = tk.Tk()
        self.root.title("Dosya Senkronizasyon Uygulaması v2.1")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # İkon ayarla (varsa)
        icon_path = Path(__file__).parent.parent / 'assets' / 'icon.ico'
        if icon_path.exists():
            self.root.iconbitmap(icon_path)
        
        # Stil ayarları
        style = ttk.Style()
        style.configure('TLabel', padding=(5, 5))
        style.configure('TButton', padding=(5, 5))
        style.configure('TEntry', padding=(2, 2))
        self.create_menu()
        # Ana frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    def create_menu(self):
        """Menü çubuğunu oluştur"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Ayarları Kaydet", command=self.save_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.on_closing)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        tools_menu.add_command(label="E-posta Ayarları", command=self.show_email_settings)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Hakkında", command=self.show_about)    
    def show_email_settings(self):
        """E-posta ayarları penceresini göster"""
        def on_save(new_config):
            self.email_config = new_config
            self.save_email_config()
            
        EmailSettingsDialog(self.root, self.email_config, callback=on_save)

    def send_error_notification(self, error_message: str, details: Optional[dict] = None):
        """Hata bildirimini e-posta ile gönder"""
        try:
            # E-posta servisi yapılandırılmış mı kontrol et
            if not self.email_config.username or not self.email_config.to_emails:
                logging.warning("E-posta bildirimi yapılandırılmamış")
                return
                
            # Detayları hazırla
            error_details = {
                'Kaynak Klasör': self.source_selector.path,
                'Hedef Klasör': self.target_selector.path,
                'Zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Hata Mesajı': error_message
            }
            
            if details:
                error_details.update(details)
            
            # E-posta servisini oluştur ve gönder
            notification_service = EmailNotificationService(self.email_config)
            notification_service.send_error_notification(
                error_message=error_message,
                details=error_details
            )
            
        except Exception as e:
            logging.error(f"E-posta bildirimi gönderilirken hata: {str(e)}")

    def handle_sync_error(self, error):
        """Senkronizasyon hatalarını işle ve bildir"""
        error_msg = str(error)
        logging.error(f"Senkronizasyon hatası: {error_msg}")
        
        # GUI'yi güncelle
        self.control_buttons.set_running_state(False)
        self.status_bar.update_status(f"Hata: {error_msg}")
        
        # Hata detaylarını hazırla
        error_details = {
            'Dosya Sayısı': self.file_sync.stats.files_copied,
            'Toplam Boyut': self.file_sync.stats.format_size(self.file_sync.stats.bytes_copied),
            'Son İşlem': self.file_sync.stats.current_file
        }
        
        # E-posta bildirimi gönder
        self.send_error_notification(error_msg, error_details)
        
        # Kullanıcıya göster
        messagebox.showerror("Hata", error_msg)

    def start_sync(self):
        """Senkronizasyonu başlat"""
        try:
            # Yolları doğrula
            source = self.source_selector.path
            target = self.target_selector.path
            
            if not source or not target:
                raise ValidationError("Kaynak ve hedef klasörler seçilmelidir!")

            if not Path(source).exists():
                raise ValidationError(f"Kaynak klasör bulunamadı: {source}")

            # Ayarları kaydet ve senkronizasyonu başlat
            self.save_settings()
            self.file_sync.status_callback = self.update_status
            self.file_sync.start(source, target)
            
            # GUI durumunu güncelle
            self.control_buttons.set_running_state(True)
            self.status_bar.update_status("Senkronizasyon başlatıldı...")
            
            # İstatistik güncelleme thread'i
            self.stats_thread = threading.Thread(target=self.stats_updater, daemon=True)
            self.stats_thread.start()

        except Exception as e:
            self.handle_sync_error(e)
            
    def create_widgets(self):
        """GUI bileşenlerini oluştur"""
        # Kaynak ve hedef klasör seçicileri
        self.source_selector = PathSelector(
            self.main_frame,
            "Kaynak Klasör:",
            self.on_source_changed
        )
        self.source_selector.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.target_selector = PathSelector(
            self.main_frame,
            "Hedef Klasör:",
            self.on_target_changed
        )
        self.target_selector.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Yapılandırma girişleri
        self.config_frame = ttk.LabelFrame(self.main_frame, text="Senkronizasyon Ayarları", padding=10)
        self.config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Klasör desenleri
        self.folder_patterns = ConfigEntry(
            self.config_frame,
            "Klasör Desenleri:",
            self.file_sync.config.folder_patterns,
            "Hangi klasörlerin senkronize edileceğini belirler.\nÖrnek: *.git, temp*"
        )
        self.folder_patterns.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)

        # Dosya desenleri
        self.file_patterns = ConfigEntry(
            self.config_frame,
            "Dosya Desenleri:",
            self.file_sync.config.file_patterns,
            "Hangi dosyaların senkronize edileceğini belirler.\nÖrnek: *.txt, *.doc"
        )
        self.file_patterns.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)

        # Hariç tutulanlar
        self.exclude_patterns = ConfigEntry(
            self.config_frame,
            "Hariç Tutulan:",
            self.file_sync.config.exclude_patterns,
            "Senkronizasyona dahil edilmeyecek öğeler.\nÖrnek: *.tmp, .git/*"
        )
        self.exclude_patterns.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)

        # Kontrol aralığı
        self.check_interval = ConfigEntry(
            self.config_frame,
            "Kontrol Aralığı (sn):",
            str(self.file_sync.config.check_interval),
            "Senkronizasyon kontrol sıklığı (saniye)"
        )
        self.check_interval.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)

        # Thread sayısı
        self.max_threads = ConfigEntry(
            self.config_frame,
            "Maximum Thread:",
            str(self.file_sync.config.max_threads),
            "Eşzamanlı kopyalama işlemi sayısı"
        )
        self.max_threads.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=2)
        # Yedekleme seçeneği
        self.backup_var = tk.BooleanVar(value=self.file_sync.config.backup_enabled)
        self.backup_check = ttk.Checkbutton(
            self.config_frame,
            text="Değiştirilen Dosyaları Yedekle",
            variable=self.backup_var
        )
        self.backup_check.grid(row=5, column=0, sticky=tk.W, pady=2)

        # Tarih filtreleme
        self.date_filter = DateFilterFrame(self.main_frame)
        self.date_filter.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.date_filter.enabled_var.set(self.file_sync.config.date_filter_enabled)

        # Kontrol butonları
        self.control_buttons = ControlButtons(self.main_frame)
        self.control_buttons.grid(row=4, column=0, columnspan=3, pady=10)

        # Buton komutlarını ayarla
        self.control_buttons.start_button.config(command=self.start_sync)
        self.control_buttons.stop_button.config(command=self.stop_sync)
        self.control_buttons.save_button.config(command=self.save_settings)
        self.control_buttons.about_button.config(command=self.show_about)

        # Durum çubuğu
        self.status_bar = StatusBar(self.main_frame)
        self.status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Grid yapılandırması
        self.config_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

    def load_config(self):
        """Yapılandırmayı yükle"""
        try:
            config = self.file_sync.config
            
            # Tarih filtresi ayarları
            self.date_filter.enabled_var.set(config.date_filter_enabled)
            
            if config.start_date:
                start_date = datetime.strptime(config.start_date, '%Y-%m-%d')
                self.date_filter.start_date.set_date(start_date)
                
            if config.end_date:
                end_date = datetime.strptime(config.end_date, '%Y-%m-%d')
                self.date_filter.end_date.set_date(end_date)
                
        except Exception as e:
            logging.error(f"Yapılandırma yükleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Yapılandırma yüklenirken hata oluştu: {str(e)}")

    def save_settings(self):
        """Ayarları kaydet"""
        try:
            # Temel ayarları güncelle
            self.file_sync.config.file_patterns = self.file_patterns.value
            self.file_sync.config.folder_patterns = self.folder_patterns.value
            self.file_sync.config.exclude_patterns = self.exclude_patterns.value
            self.file_sync.config.check_interval = int(self.check_interval.value)
            self.file_sync.config.backup_enabled = self.backup_var.get()
            self.file_sync.config.max_threads = int(self.max_threads.value)
            
            # Tarih filtresi ayarları
            self.file_sync.config.date_filter_enabled = self.date_filter.enabled_var.get()
            self.file_sync.config.start_date = self.date_filter.start_date.get_date().strftime('%Y-%m-%d')
            self.file_sync.config.end_date = self.date_filter.end_date.get_date().strftime('%Y-%m-%d')
            
            # Yapılandırmayı kaydet
            self.file_sync.config.save()
            
            messagebox.showinfo("Bilgi", "Ayarlar başarıyla kaydedildi!")
            
        except Exception as e:
            logging.error(f"Ayarları kaydetme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken hata oluştu: {str(e)}")

    def update_status(self, message: str, progress: Optional[float] = None):
        """Durum çubuğunu güncelle"""
        self.status_bar.update_status(message, progress)

    def update_stats(self):
        """İstatistik çubuğunu güncelle"""
        stats = self.file_sync.stats
        if stats.last_sync:
            stats_text = (
                f"Son Senkronizasyon: {stats.last_sync.strftime('%H:%M:%S')} | "
                f"Kopyalanan: {stats.files_copied} dosya | "
                f"Toplam: {stats.format_size(stats.bytes_copied)}"
            )
            self.status_bar.update_stats(stats_text)

    def show_about(self):
        """Hakkında penceresini göster"""
        AboutDialog(self.root)
    def start_sync(self):
        """Senkronizasyonu başlat"""
        try:
            # Yolları doğrula
            source = self.source_selector.path
            target = self.target_selector.path
            
            if not source or not target:
                raise ValidationError("Kaynak ve hedef klasörler seçilmelidir!")

            if not Path(source).exists():
                raise ValidationError(f"Kaynak klasör bulunamadı: {source}")

            # Ayarları kaydet
            self.save_settings()
            
            # GUI durumunu güncelle
            self.control_buttons.set_running_state(True)
            self.status_bar.update_status("Senkronizasyon başlatıldı...", 0)

            # Callback'i ayarla
            def status_callback(message, progress=None):
                self.root.after(0, lambda: self.update_status(message, progress))

            self.file_sync.status_callback = status_callback
            
            # Senkronizasyon thread'ini başlat
            def sync_thread_func():
                try:
                    self.file_sync.start(source, target)
                except Exception as e:
                    self.root.after(0, lambda: self.handle_sync_error(e))

            self.sync_thread = threading.Thread(target=sync_thread_func)
            self.sync_thread.daemon = True
            self.sync_thread.start()
            
            # İstatistik güncelleyiciyi başlat
            self.start_stats_updater()

        except Exception as e:
            self.handle_sync_error(e)

    def handle_sync_error(self, error):
        """Senkronizasyon hatalarını işle"""
        logging.error(f"Senkronizasyon hatası: {str(error)}")
        self.control_buttons.set_running_state(False)
        self.status_bar.update_status(f"Hata: {str(error)}")
        messagebox.showerror("Hata", str(error))

    def start_stats_updater(self):
        """İstatistik güncelleyiciyi başlat"""
        def update():
            if self.file_sync.is_running:
                self.update_stats()
                self.root.after(1000, update)  # Her 1 saniyede bir güncelle
        
        self.root.after(0, update)

    def update_status(self, message: str, progress: Optional[float] = None):
        """Durum çubuğunu güncelle"""
        try:
            self.status_bar.update_status(message, progress)
            self.root.update_idletasks()
        except Exception as e:
            logging.error(f"Durum güncelleme hatası: {str(e)}")

    def update_stats(self):
        """İstatistik çubuğunu güncelle"""
        try:
            stats = self.file_sync.stats
            if stats.last_sync:
                duration = stats.get_duration()
                if duration > 0:
                    speed = stats.format_speed(duration)
                    stats_text = (
                        f"Kopyalanan: {stats.files_copied} dosya | "
                        f"Toplam: {stats.format_size(stats.bytes_copied)} | "
                        f"Hız: {speed}"
                    )
                    self.status_bar.update_stats(stats_text)
        except Exception as e:
            logging.error(f"İstatistik güncelleme hatası: {str(e)}")

    def stop_sync(self):
        """Senkronizasyonu durdur"""
        try:
            self.file_sync.stop()
            self.control_buttons.set_running_state(False)
            self.status_bar.update_status("Senkronizasyon durduruldu")
        except Exception as e:
            logging.error(f"Senkronizasyon durdurma hatası: {str(e)}")
            messagebox.showerror("Hata", str(e))
    def stop_sync(self):
        """Senkronizasyonu durdur"""
        try:
            self.file_sync.stop()
            self.control_buttons.set_running_state(False)
            self.status_bar.update_status("Senkronizasyon durduruldu")
        except Exception as e:
            logging.error(f"Senkronizasyon durdurma hatası: {str(e)}")
            messagebox.showerror("Hata", str(e))

    def stats_updater(self):
        """İstatistik güncelleme döngüsü"""
        while self.file_sync.is_running:
            try:
                self.update_stats()
                self.root.after(1000)  # 1 saniye bekle
            except Exception as e:
                logging.error(f"İstatistik güncelleme hatası: {str(e)}")

    def on_source_changed(self, path: str):
        """Kaynak klasör değiştiğinde"""
        logging.info(f"Kaynak klasör seçildi: {path}")
        self._check_path_permissions(path, "kaynak")

    def on_target_changed(self, path: str):
        """Hedef klasör değiştiğinde"""
        logging.info(f"Hedef klasör seçildi: {path}")
        self._check_path_permissions(path, "hedef")

    def _check_path_permissions(self, path: str, path_type: str):
        """Klasör izinlerini kontrol et"""
        if not path:
            return
            
        try:
            test_file = os.path.join(path, '.test_write_permission')
            Path(test_file).touch()
            os.remove(test_file)
        except Exception as e:
            messagebox.showwarning(
                "İzin Uyarısı",
                f"Seçilen {path_type} klasörde yazma izni yok!\nHata: {str(e)}"
            )

    def setup_bindings(self):
        """Olay bağlayıcıları"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Ctrl+S ile kaydetme
        self.root.bind('<Control-s>', lambda e: self.save_settings())
        
        # ESC ile durdurma
        self.root.bind('<Escape>', lambda e: self.stop_sync() if self.file_sync.is_running else None)
        
        # F1 ile Hakkında
        self.root.bind('<F1>', lambda e: self.show_about())
        
        # F5 ile başlatma/durdurma
        self.root.bind('<F5>', self._toggle_sync)

    def _toggle_sync(self, event=None):
        """Senkronizasyonu başlat/durdur"""
        if self.file_sync.is_running:
            self.stop_sync()
        else:
            self.start_sync()

    def on_closing(self):
        """Uygulama kapatılırken"""
        if self.file_sync.is_running:
            if messagebox.askokcancel("Uyarı", 
                "Senkronizasyon devam ediyor. Çıkmak istediğinize emin misiniz?"):
                self.stop_sync()
            else:
                return
        self.root.destroy()

    def run(self):
        """Uygulamayı başlat"""
        try:
            # Merkeze konumlandır
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
            
            # Ana döngüyü başlat
            self.root.mainloop()
            
        except Exception as e:
            logging.critical(f"Uygulama hatası: {str(e)}")
            messagebox.showerror("Kritik Hata", f"Uygulama hatası:\n{str(e)}")
            raise

if __name__ == "__main__":
    try:
        app = SyncGUI()
        app.run()
    except Exception as e:
        logging.critical(f"Başlatma hatası: {str(e)}")
        messagebox.showerror("Kritik Hata", f"Uygulama başlatılamadı:\n{str(e)}")