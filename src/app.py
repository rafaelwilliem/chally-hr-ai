import sys
import os

# Memastikan terminal menggunakan encoding UTF-8 untuk karakter banner
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
from typing import NoReturn
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.align import Align
from rich import print as rprint

# Import logic modules
from interviewer import start_interview
from history import show_history
from analytics import run_analytics

console = Console()

def display_banner() -> None:
    """Menampilkan banner utama Challora AI."""
    banner = """
    [bold cyan]
    ██████╗██╗  ██╗ █████╗ ██╗     ██╗      ██████╗ ██████╗  █████╗ 
   ██╔════╝██║  ██║██╔══██╗██║     ██║     ██╔═══██╗██╔══██╗██╔══██╗
   ██║     ███████║███████║██║     ██║     ██║   ██║██████╔╝███████║
   ██║     ██╔══██║██╔══██║██║     ██║     ██║   ██║██╔══██╗██╔══██║
   ╚██████╗██║  ██║██║  ██║███████╗███████╗╚██████╔╝██║  ██║██║  ██║
    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
    [/bold cyan]
    [italic white]AI-Powered Screening Tool for Modern HR[/italic white]
    """
    console.print(Align.center(Panel(banner, border_style="bold blue")))

def clear_screen() -> None:
    """Membersihkan screen terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu() -> None:
    """Loop utama menu program."""
    while True:
        clear_screen()
        display_banner()
        
        table = Table(title="MAIN MENU", show_header=False, box=None)
        table.add_row("[1] Start New Interview", "[dim]|[/dim]", "Screening candidate with context")
        table.add_row("[2] View History", "[dim]|[/dim]", "Browse saved transcripts")
        table.add_row("[3] Run Analytics", "[dim]|[/dim]", "Analyze transcript with AI score")
        table.add_row("[0] Exit", "[dim]|[/dim]", "Close application")
        
        console.print(Align.center(Panel(table, border_style="cyan", title="Select an Option", expand=False)))
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "0"], default="1")
        
        if choice == "1":
            start_interview()
            Prompt.ask("\n[dim]Press Enter to return to menu[/dim]", show_choices=False, default="")
        elif choice == "2":
            show_history()
            Prompt.ask("\n[dim]Press Enter to return to menu[/dim]", show_choices=False, default="")
        elif choice == "3":
            run_analytics()
            Prompt.ask("\n[dim]Press Enter to return to menu[/dim]", show_choices=False, default="")
        elif choice == "0":
            console.print("[bold green]Goodbye![/bold green]")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program dihentikan paksa.[/bold red]")
        sys.exit(0)
