"""
GUI Bileşenleri
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from tkcalendar import DateEntry
from typing import Callable, Optional
import webbrowser
from pathlib import Path
from datetime import datetime
import logging

# E-posta servisi importları
from .notification_service import EmailConfig, EmailNotificationService
class PathSelector(ttk.Frame):
    """Klasör seçim bileşeni"""
    def __init__(self, parent, label: str, callback: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.callback = callback
        
        self.path_var = tk.StringVar()
        
        ttk.Label(self, text=label).grid(row=0, column=0, sticky=tk.W)
        self.entry = ttk.Entry(self, textvariable=self.path_var)
        self.entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(self, text="Gözat", command=self._browse).grid(row=0, column=2)
        
        self.columnconfigure(1, weight=1)
        
    def _browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            if self.callback:
                self.callback(folder)
                
    @property
    def path(self) -> str:
        return self.path_var.get()
    
    @path.setter
    def path(self, value: str):
        self.path_var.set(value)

class ConfigEntry(ttk.Frame):
    """Yapılandırma giriş bileşeni"""
    def __init__(self, parent, label: str, default: str = "", tooltip: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.value_var = tk.StringVar(value=default)
        
        ttk.Label(self, text=label).grid(row=0, column=0, sticky=tk.W)
        self.entry = ttk.Entry(self, textvariable=self.value_var)
        self.entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        if tooltip:
            ToolTip(self.entry, tooltip)
        
        self.columnconfigure(1, weight=1)
        
    @property
    def value(self) -> str:
        return self.value_var.get()
    
    @value.setter
    def value(self, val: str):
        self.value_var.set(val)

class DateFilterFrame(ttk.LabelFrame):
    """Tarih filtreleme bileşeni"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Tarih Filtreleme", padding="5", **kwargs)
        
        self.enabled_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(self, text="Tarih Filtresini Etkinleştir",
                       variable=self.enabled_var).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(self, text="Başlangıç:").grid(row=1, column=0, sticky=tk.W)
        self.start_date = DateEntry(self, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.start_date.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(self, text="Bitiş:").grid(row=2, column=0, sticky=tk.W)
        self.end_date = DateEntry(self, width=12, background='darkblue',
                                foreground='white', borderwidth=2)
        self.end_date.grid(row=2, column=1, padx=5, pady=2)
        
        # Tarihleri bugüne ayarla
        today = datetime.now()
        self.start_date.set_date(today)
        self.end_date.set_date(today)

class StatusBar(ttk.Frame):
    """Durum çubuğu bileşeni"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status_var = tk.StringVar(value="Hazır")
        self.stats_var = tk.StringVar(value="")
        
        # Durum etiketi
        self.status_label = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, pady=(0, 2))
        
        # İstatistik etiketi
        self.stats_label = ttk.Label(self, textvariable=self.stats_var)
        self.stats_label.pack(fill=tk.X)
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(self, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(2, 0))
        
    def update_status(self, message: str, progress: Optional[float] = None):
        """Durum bilgisini güncelle"""
        self.status_var.set(message)
        if progress is not None:
            self.progress['value'] = progress
        self.update_idletasks()
        
    def update_stats(self, stats_message: str):
        """İstatistikleri güncelle"""
        self.stats_var.set(stats_message)
        self.update_idletasks()

class AboutDialog(tk.Toplevel):
    """Hakkında dialog penceresi"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.title("Hakkında")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Modal pencere yap
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._center_window()
        
    def _create_widgets(self):
        content_frame = ttk.Frame(self, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        ttk.Label(content_frame, text="Dosya Senkronizasyon Uygulaması",
                 font=('Helvetica', 14, 'bold')).pack(pady=(0, 10))
        
        # Versiyon
        ttk.Label(content_frame, text="Versiyon 2.1",
                 font=('Helvetica', 10)).pack()
        
        # Geliştirici
        ttk.Label(content_frame, text="Geliştirici: Önder AKÖZ",
                 font=('Helvetica', 10)).pack(pady=(10, 0))
        
        # Detaylı bilgi
        info_text = scrolledtext.ScrolledText(
            content_frame, width=50, height=20,
            wrap=tk.WORD, font=('Helvetica', 9)
        )
        info_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # README dosyasından içeriği yükle
        readme_path = Path(__file__).parent.parent / 'README.md'
        if readme_path.exists():
            info_text.insert(tk.INSERT, readme_path.read_text(encoding='utf-8'))
        else:
            info_text.insert(tk.INSERT, "Detaylı bilgi dosyası bulunamadı.")
        
        info_text.config(state=tk.DISABLED)
        
        # İletişim butonları
        contact_frame = ttk.Frame(content_frame)
        contact_frame.pack(pady=10)
        
        self._create_contact_button(contact_frame, "Email",
                                  lambda: webbrowser.open('mailto:onder7@gmail.com'))
        self._create_contact_button(contact_frame, "LinkedIn",
                                  lambda: webbrowser.open('https://www.linkedin.com/in/mustafa-%C3%B6nder-ak%C3%B6z-23174592/'))
        self._create_contact_button(contact_frame, "GitHub",
                                  lambda: webbrowser.open('https://github.com/onder7'))
        self._create_contact_button(contact_frame, "WWW",
                                  lambda: webbrowser.open('https://ondernet.net'))
        
        # Kapat butonu
        ttk.Button(content_frame, text="Kapat",
                  command=self.destroy).pack(pady=(10, 0))
        
    def _create_contact_button(self, parent, text: str, command: Callable):
        """İletişim butonu oluştur"""
        ttk.Button(parent, text=text, command=command).pack(side=tk.LEFT, padx=5)
        
    def _center_window(self):
        """Pencereyi ekranın ortasına konumlandır"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class ControlButtons(ttk.Frame):
    """Kontrol butonları bileşeni"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.start_button = ttk.Button(self, text="Başlat")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(self, text="Durdur", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(self, text="Ayarları Kaydet")
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.about_button = ttk.Button(self, text="Hakkında")
        self.about_button.pack(side=tk.LEFT, padx=5)
        
    def set_running_state(self, is_running: bool):
        """Butonların durumunu güncelle"""
        self.start_button.config(state=tk.DISABLED if is_running else tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL if is_running else tk.DISABLED)

class ToolTip:
    """Tooltip (ipucu) bileşeni"""
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind('<Enter>', self.schedule)
        self.widget.bind('<Leave>', self.hide)
        self.widget.bind('<Button>', self.hide)

    def schedule(self, event=None):
        """Tooltip gösterme zamanlaması"""
        self.unschedule()
        self.id = self.widget.after(500, self.show)

    def unschedule(self):
        """Tooltip gösterme iptal"""
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self, event=None):
        """Tooltip'i göster"""
        x = y = 0
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # Tooltip penceresi oluştur
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("TkDefaultFont", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self, event=None):
        """Tooltip'i gizle"""
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
        self.unschedule()
"""
GUI Bileşenleri
"""



class EmailSettingsDialog(tk.Toplevel):
    """E-posta ayarları dialog penceresi"""
    def __init__(self, parent, email_config, callback=None):
        super().__init__(parent)
        self.title("E-posta Ayarları")
        self.email_config = email_config
        self.callback = callback
        
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Modal pencere yap
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._load_config()
        self._center_window()
        
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # SMTP Ayarları
        smtp_frame = ttk.LabelFrame(main_frame, text="SMTP Ayarları", padding="5")
        smtp_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(smtp_frame, text="SMTP Sunucu:").grid(row=0, column=0, sticky=tk.W)
        self.smtp_server = ttk.Entry(smtp_frame)
        self.smtp_server.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(smtp_frame, text="Port:").grid(row=1, column=0, sticky=tk.W)
        self.smtp_port = ttk.Entry(smtp_frame)
        self.smtp_port.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        self.use_ssl = tk.BooleanVar()
        ttk.Checkbutton(smtp_frame, text="SSL/TLS Kullan", 
                       variable=self.use_ssl).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # Kullanıcı Bilgileri
        auth_frame = ttk.LabelFrame(main_frame, text="Kimlik Bilgileri", padding="5")
        auth_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(auth_frame, text="E-posta:").grid(row=0, column=0, sticky=tk.W)
        self.username = ttk.Entry(auth_frame)
        self.username.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(auth_frame, text="Şifre:").grid(row=1, column=0, sticky=tk.W)
        self.password = ttk.Entry(auth_frame, show="*")
        self.password.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        # Bildirim Ayarları
        notify_frame = ttk.LabelFrame(main_frame, text="Bildirim Ayarları", padding="5")
        notify_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(notify_frame, text="Bildirim Alıcıları:").grid(row=0, column=0, sticky=tk.W)
        self.recipients = scrolledtext.ScrolledText(notify_frame, height=4)
        self.recipients.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Label(notify_frame, 
                 text="Her satıra bir e-posta adresi yazın").grid(row=2, column=0, sticky=tk.W)
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Test Et", 
                  command=self._test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Kaydet", 
                  command=self._save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="İptal", 
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
    def _load_config(self):
        """Mevcut ayarları yükle"""
        try:
            self.smtp_server.insert(0, self.email_config.smtp_server)
            self.smtp_port.insert(0, str(self.email_config.smtp_port))
            self.use_ssl.set(self.email_config.use_ssl)
            self.username.insert(0, self.email_config.username)
            self.password.insert(0, self.email_config.password)
            
            if self.email_config.to_emails:
                self.recipients.insert('1.0', '\n'.join(self.email_config.to_emails))
        except Exception as e:
            logging.error(f"Ayarlar yüklenirken hata: {str(e)}")
            messagebox.showerror("Hata", f"Ayarlar yüklenirken hata oluştu: {str(e)}")
            
    def _save_settings(self):
        """Ayarları kaydet"""
        try:
            # Değerleri güncelle
            self.email_config.smtp_server = self.smtp_server.get()
            self.email_config.smtp_port = int(self.smtp_port.get())
            self.email_config.use_ssl = self.use_ssl.get()
            self.email_config.username = self.username.get()
            self.email_config.from_email = self.username.get()
            self.email_config.password = self.password.get()
            
            # Alıcıları ayarla
            recipients = self.recipients.get('1.0', tk.END).strip()
            self.email_config.to_emails = [
                email.strip() 
                for email in recipients.split('\n') 
                if email.strip()
            ]
            
            if self.callback:
                self.callback(self.email_config)
                
            messagebox.showinfo("Bilgi", "E-posta ayarları kaydedildi!")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken hata oluştu: {str(e)}")
            
    def _test_connection(self):
        """E-posta bağlantısını test et"""
        try:
            # Geçici config oluştur
            test_config = EmailConfig(
                smtp_server=self.smtp_server.get(),
                smtp_port=int(self.smtp_port.get()),
                username=self.username.get(),
                password=self.password.get(),
                from_email=self.username.get(),
                use_ssl=self.use_ssl.get()
            )
            
            # Test servisi oluştur
            service = EmailNotificationService(test_config)
            
            if service.test_connection():
                messagebox.showinfo("Başarılı", "E-posta bağlantısı başarılı!")
            else:
                messagebox.showerror("Hata", "Bağlantı başarısız!")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Bağlantı testi sırasında hata: {str(e)}")
            
    def _center_window(self):
        """Pencereyi merkeze konumlandır"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
def _test_connection(self):
        """E-posta bağlantısını test et"""
        try:
            # Test config oluştur
            test_config = EmailConfig(
                smtp_server=self.smtp_server.get(),
                smtp_port=int(self.smtp_port.get()),
                username=self.username.get(),
                password=self.password.get(),
                from_email=self.username.get(),
                to_emails=[self.username.get()],  # Test için sadece gönderen adrese gönder
                use_ssl=self.use_ssl.get()
            )
            
            # Test servisi oluştur
            service = EmailNotificationService(test_config)
            
            # Önce bağlantıyı test et
            if service.test_connection():
                msg = "SMTP bağlantısı başarılı! Test e-postası gönderiliyor..."
                messagebox.showinfo("Bilgi", msg)
                
                # Test e-postası gönder
                if service.send_test_email():
                    msg = "Test e-postası başarıyla gönderildi!\nLütfen gelen kutunuzu kontrol edin."
                    messagebox.showinfo("Başarılı", msg)
                else:
                    messagebox.showerror("Hata", "Test e-postası gönderilemedi!")
            else:
                messagebox.showerror("Hata", "SMTP bağlantı testi başarısız!")
                
        except Exception as e:
            error_msg = f"Test sırasında hata oluştu:\n{str(e)}"
            messagebox.showerror("Hata", error_msg)
            logging.error(error_msg)