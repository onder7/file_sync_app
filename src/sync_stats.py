"""
Senkronizasyon istatistikleri sınıfı
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SyncStats:
    """Senkronizasyon istatistikleri sınıfı"""
    
    files_copied: int = 0
    bytes_copied: int = 0
    last_sync: Optional[datetime] = None
    current_file: str = ''
    start_time: Optional[datetime] = None
    
    def reset(self) -> None:
        """İstatistikleri sıfırla"""
        self.files_copied = 0
        self.bytes_copied = 0
        self.current_file = ''
        self.start_time = datetime.now()
        
    def update(self, bytes_copied: int = 0, files_copied: int = 0, current_file: str = '') -> None:
        """İstatistikleri güncelle"""
        self.bytes_copied += bytes_copied
        self.files_copied += files_copied
        self.current_file = current_file
        
    def complete(self) -> None:
        """Senkronizasyon tamamlandığında"""
        self.last_sync = datetime.now()
        
    def format_size(self, size: int) -> str:
        """Boyutu insan okunabilir formata çevir"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
        
    def format_speed(self, duration: float) -> str:
        """Transfer hızını formatla"""
        if duration <= 0:
            return "0 B/s"
        bytes_per_second = self.bytes_copied / duration
        return f"{self.format_size(bytes_per_second)}/s"
        
    def get_duration(self) -> float:
        """Geçen süreyi hesapla"""
        if not self.start_time:
            return 0.0
        end_time = self.last_sync or datetime.now()
        return (end_time - self.start_time).total_seconds()
        
    def get_summary(self) -> str:
        """Özet istatistik raporu oluştur"""
        duration = self.get_duration()
        return f"""Senkronizasyon İstatistikleri:
- Kopyalanan Dosya: {self.files_copied}
- Toplam Boyut: {self.format_size(self.bytes_copied)}
- Süre: {duration:.1f} saniye
- Ortalama Hız: {self.format_speed(duration)}"""