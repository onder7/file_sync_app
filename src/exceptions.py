"""
Özel exception sınıfları
"""

class SyncError(Exception):
    """Temel senkronizasyon hatası"""
    pass

class ConfigError(SyncError):
    """Yapılandırma hatası"""
    pass

class ValidationError(SyncError):
    """Doğrulama hatası"""
    pass

class FileOperationError(SyncError):
    """Dosya işlem hatası"""
    pass

class ThreadError(SyncError):
    """Thread yönetim hatası"""
    pass

class NetworkError(SyncError):
    """Ağ bağlantısı hatası"""
    pass

class PermissionError(SyncError):
    """İzin hatası"""
    pass

class InterruptError(SyncError):
    """Kesinti hatası"""
    pass