#!/usr/bin/env python3
"""
Dosya Senkronizasyon Uygulaması
Çalıştırma Dosyası
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import traceback
from tkinter import messagebox

def setup_environment() -> None:
    """Çalışma ortamını hazırla"""
    # Uygulama dizinini sys.path'e ekle
    app_dir = Path(__file__).parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

def setup_logging() -> None:
    """Temel log ayarlarını yap"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

def show_error_message(title: str, message: str) -> None:
    """Hata mesajı göster"""
    try:
        messagebox.showerror(title, message)
    except:
        print(f"HATA: {title}\n{message}", file=sys.stderr)

def main() -> Optional[int]:
    """Ana fonksiyon"""
    try:
        # Ortamı hazırla
        setup_environment()
        setup_logging()

        # GUI'yi başlat
        from src.main_gui import SyncGUI
        app = SyncGUI()
        app.run()

        return 0

    except ModuleNotFoundError as e:
        error_msg = f"""Gerekli modül bulunamadı: {str(e)}

Lütfen gerekli modülleri yükleyin:
pip install -r requirements.txt"""
        show_error_message("Modül Hatası", error_msg)
        return 1

    except Exception as e:
        error_msg = f"""Beklenmeyen bir hata oluştu:
{str(e)}

Detaylı hata:
{''.join(traceback.format_exception(type(e), e, e.__traceback__))}"""
        
        show_error_message("Kritik Hata", error_msg)
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\nUygulama kullanıcı tarafından sonlandırıldı.", file=sys.stderr)
        sys.exit(130)  # 128 + SIGINT
    except Exception as e:
        print(f"Kritik hata: {str(e)}", file=sys.stderr)
        sys.exit(1)