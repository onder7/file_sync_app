"""
Senkronizasyon yapılandırma sınıfı
"""

from dataclasses import dataclass
import configparser
import os
from typing import Optional
from .exceptions import ConfigError

@dataclass
class SyncConfig:
    """Senkronizasyon yapılandırma sınıfı"""
    
    # Varsayılan değerler
    check_interval: int = 10
    file_patterns: str = '*.*'
    folder_patterns: str = '.*'
    exclude_patterns: str = '.git/*,*.tmp'
    backup_enabled: bool = False
    max_threads: int = 4
    date_filter_enabled: bool = False
    start_date: str = ''
    end_date: str = ''

    @classmethod
    def from_file(cls, config_path: str = 'config.ini') -> 'SyncConfig':
        """Yapılandırmayı dosyadan yükle"""
        try:
            config = configparser.ConfigParser()
            
            if os.path.exists(config_path):
                config.read(config_path, encoding='utf-8')
                return cls(
                    check_interval=config.getint('DEFAULT', 'check_interval', fallback=10),
                    file_patterns=config.get('DEFAULT', 'file_patterns', fallback='*.*'),
                    folder_patterns=config.get('DEFAULT', 'folder_patterns', fallback='.*'),
                    exclude_patterns=config.get('DEFAULT', 'exclude_patterns', fallback='.git/*,*.tmp'),
                    backup_enabled=config.getboolean('DEFAULT', 'backup_enabled', fallback=False),
                    max_threads=config.getint('DEFAULT', 'max_threads', fallback=4),
                    date_filter_enabled=config.getboolean('DEFAULT', 'date_filter_enabled', fallback=False),
                    start_date=config.get('DEFAULT', 'start_date', fallback=''),
                    end_date=config.get('DEFAULT', 'end_date', fallback='')
                )
            return cls()
            
        except Exception as e:
            raise ConfigError(f"Yapılandırma yükleme hatası: {str(e)}")

    def save(self, config_path: str = 'config.ini') -> None:
        """Yapılandırmayı dosyaya kaydet"""
        try:
            config = configparser.ConfigParser()
            config['DEFAULT'] = {
                'check_interval': str(self.check_interval),
                'file_patterns': self.file_patterns,
                'folder_patterns': self.folder_patterns,
                'exclude_patterns': self.exclude_patterns,
                'backup_enabled': str(self.backup_enabled).lower(),
                'max_threads': str(self.max_threads),
                'date_filter_enabled': str(self.date_filter_enabled).lower(),
                'start_date': self.start_date,
                'end_date': self.end_date
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
        except Exception as e:
            raise ConfigError(f"Yapılandırma kaydetme hatası: {str(e)}")

    def validate(self) -> None:
        """Yapılandırma değerlerini doğrula"""
        if self.check_interval < 1:
            raise ConfigError("Kontrol aralığı 1'den küçük olamaz")
            
        if self.max_threads < 1:
            raise ConfigError("Thread sayısı 1'den küçük olamaz")
            
        if not self.file_patterns:
            raise ConfigError("Dosya desenleri boş olamaz")
            
        if not self.folder_patterns:
            raise ConfigError("Klasör desenleri boş olamaz")

    def __post_init__(self):
        """Dataclass sonrası başlatıcı"""
        self.validate()