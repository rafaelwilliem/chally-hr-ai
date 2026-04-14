import sys
import os

# Memastikan terminal menggunakan encoding UTF-8 untuk karakter banner
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Menambahkan folder src ke path agar module di dalamnya bisa di-import langsung
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import logika utama dari src/app.py
from app import main_menu

if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program dihentikan paksa.[/bold red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Terjadi kesalahan fatal:[/bold red] {e}")
        sys.exit(1)
