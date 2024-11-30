"""
E-posta Bildirim Servisi
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
import logging
from typing import List, Optional
from datetime import datetime
import ssl

@dataclass
class EmailConfig:
    """E-posta yapılandırma sınıfı"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    from_email: str = ""
    to_emails: List[str] = None
    use_ssl: bool = True

    def __post_init__(self):
        if self.to_emails is None:
            self.to_emails = []

class EmailNotificationService:
    """E-posta bildirim servisi"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self._setup_logging()

    def _setup_logging(self):
        """Loglama ayarlarını yapılandır"""
        self.logger = logging.getLogger(__name__)
        
        # Dosyaya loglama
        try:
            fh = logging.FileHandler('logs/email_service.log', encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            
            # Konsola loglama
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        except Exception as e:
            print(f"Loglama yapılandırma hatası: {e}")

    def send_notification(self, subject: str, message: str, details: Optional[dict] = None) -> bool:
        """Genel bildirim gönderme metodu"""
        try:
            if not self.config.username or not self.config.to_emails:
                self.logger.warning("E-posta ayarları eksik")
                return False

            # HTML içeriği oluştur
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; }}
                        .message {{ 
                            padding: 15px;
                            border-radius: 4px;
                            margin: 10px 0;
                        }}
                        .error {{ 
                            color: #721c24;
                            background-color: #f8d7da;
                            border: 1px solid #f5c6cb;
                        }}
                        .info {{
                            color: #0c5460;
                            background-color: #d1ecf1;
                            border: 1px solid #bee5eb;
                        }}
                        .details {{ 
                            background-color: #f8f9fa;
                            border: 1px solid #dee2e6;
                            padding: 15px;
                            border-radius: 4px;
                            margin: 10px 0;
                        }}
                        .footer {{ 
                            margin-top: 30px;
                            color: #6c757d;
                            font-size: 0.9em;
                            border-top: 1px solid #dee2e6;
                            padding-top: 10px;
                        }}
                        table {{ width: 100%; border-collapse: collapse; }}
                        th, td {{ 
                            text-align: left;
                            padding: 8px;
                            border: 1px solid #dee2e6;
                        }}
                        th {{ background-color: #f8f9fa; }}
                    </style>
                </head>
                <body>
                    <h2>{subject}</h2>
                    <div class="message {'error' if 'hata' in subject.lower() else 'info'}">
                        {message}
                    </div>
            """

            if details:
                html_content += '<div class="details"><h3>Detaylar:</h3><table>'
                for key, value in details.items():
                    if isinstance(value, dict):
                        # Alt detaylar için nested tablo
                        html_content += f'<tr><th colspan="2">{key}</th></tr>'
                        for k, v in value.items():
                            html_content += f'<tr><td>{k}</td><td>{v}</td></tr>'
                    else:
                        html_content += f'<tr><td>{key}</td><td>{value}</td></tr>'
                html_content += '</table></div>'

            html_content += f"""
                    <div class="footer">
                        <p>Bu e-posta otomatik olarak gönderilmiştir.</p>
                        <p>Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </body>
            </html>
            """

            # E-posta oluştur
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.from_email
            msg['To'] = ', '.join(self.config.to_emails)
            msg.attach(MIMEText(html_content, 'html'))

            # SMTP bağlantısı ve gönderim
            context = ssl.create_default_context() if self.config.use_ssl else None
            
            self.logger.debug(f"SMTP bağlantısı kuruluyor: {self.config.smtp_server}:{self.config.smtp_port}")
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_ssl:
                    self.logger.debug("STARTTLS başlatılıyor")
                    server.starttls(context=context)
                
                self.logger.debug(f"Oturum açılıyor: {self.config.username}")
                server.login(self.config.username, self.config.password)
                
                self.logger.debug(f"E-posta gönderiliyor: {msg['To']}")
                server.send_message(msg)
                
            self.logger.info(f"E-posta başarıyla gönderildi: {subject}")
            return True

        except Exception as e:
            self.logger.error(f"E-posta gönderimi sırasında hata: {str(e)}", exc_info=True)
            return False

    def send_error_notification(self, error_message: str, details: Optional[dict] = None) -> bool:
        """Hata bildirimi gönder"""
        subject = f"Dosya Senkronizasyon Hatası - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self.send_notification(subject, error_message, details)

    def send_test_email(self) -> bool:
        """Test e-postası gönder"""
        subject = f"Dosya Senkronizasyon Test E-postası - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        message = "Bu bir test e-postasıdır. E-posta bildirimleri düzgün çalışıyor."
        details = {
            'SMTP Ayarları': {
                'Sunucu': self.config.smtp_server,
                'Port': self.config.smtp_port,
                'SSL/TLS': 'Aktif' if self.config.use_ssl else 'Pasif'
            },
            'Gönderen': self.config.from_email,
            'Alıcılar': ', '.join(self.config.to_emails)
        }
        return self.send_notification(subject, message, details)

    def test_connection(self) -> bool:
        """SMTP bağlantısını test et"""
        try:
            self.logger.debug(f"SMTP bağlantı testi başlıyor: {self.config.smtp_server}:{self.config.smtp_port}")
            
            context = ssl.create_default_context() if self.config.use_ssl else None
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port, timeout=10) as server:
                server.set_debuglevel(1)
                
                if self.config.use_ssl:
                    server.starttls(context=context)
                
                if self.config.username and self.config.password:
                    server.login(self.config.username, self.config.password)
                
                self.logger.info("SMTP bağlantı testi başarılı!")
                return True

        except Exception as e:
            self.logger.error(f"SMTP bağlantı testi başarısız: {str(e)}", exc_info=True)
            return False