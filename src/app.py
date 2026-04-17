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
from assistant_v2 import ChallyAssistantV2
import config

console = Console()
assistant = ChallyAssistantV2()

def display_banner() -> None:
    """Menampilkan banner utama Chally AI."""
    banner = """
    [bold yellow]
     ██████╗ ██╗  ██╗  █████╗  ██╗      ██╗     ██╗   ██╗     █████╗  ██╗
    ██╔════╝ ██║  ██║ ██╔══██╗ ██║      ██║     ╚██╗ ██╔╝    ██╔══██╗ ██║
    ██║      ███████║ ███████║ ██║      ██║      ╚████╔╝     ███████║ ██║
    ██║      ██╔══██║ ██╔══██║ ██║      ██║       ╚██╔╝      ██╔══██║ ██║
    ╚██████╗ ██║  ██║ ██║  ██║ ███████╗ ███████╗   ██║       ██║  ██║ ██║
     ╚═════╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚══════╝ ╚══════╝   ╚═╝       ╚═╝  ╚═╝ ╚═╝
    [/bold yellow]
    [bold cyan]V2: HR Intelligence Assistant[/bold cyan]
    [italic white]Leveling up your HR game with Batch Analysis & AI Insights[/italic white]
    """
    console.print(Align.center(Panel(banner, border_style="bold blue")))

def clear_screen() -> None:
    """Membersihkan screen terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def run_intelligence_hub() -> None:
    """Entry point for Batch CV Analysis."""
    console.print(Panel("[bold green]Intelligence Hub: Batch CV Analysis[/bold green]"))
    
    jd_file = os.path.join(config.CONTEXT_DIR, "jd_sample.txt")
    cv_folder = os.path.join(config.CONTEXT_DIR, "cv_batch")
    
    if not os.path.exists(jd_file):
        console.print(f"[bold red]JD file not found at {jd_file}[/bold red]")
        return
        
    try:
        with console.status("[bold cyan]Loading documents...[/bold cyan]"):
            data = assistant.load_documents(cv_folder, jd_file)
            
        if not data["cvs"]:
            console.print(f"[yellow]No CVs found in {cv_folder}. Please add .txt files.[/yellow]")
            return
            
        console.print(f"[cyan]Found {len(data['cvs'])} CVs. Starting analysis...[/cyan]")
        
        with console.status("[bold purple]AI is analyzing candidates...[/bold purple]"):
            assistant.analyze_fit(data["jd"], data["cvs"])
            
        assistant.display_leaderboard()
        
    except Exception as e:
        console.print(f"[bold red]Error in Intelligence Hub:[/bold red] {e}")

def run_branding_coach() -> None:
    """Entry point for Personal Branding Coach."""
    console.print(Panel("[bold magenta]Personal Branding Coach[/bold magenta]"))
    console.print("Paste your dry work experience description below (press Ctrl+Z or Ctrl+D to submit):")
    
    # Simple multi-line input
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
            
    text = "\n".join(lines).strip()
    if not text:
        console.print("[yellow]Empty input.[/yellow]")
        return
        
    try:
        with console.status("[bold magenta]Polishing your profile...[/bold magenta]"):
            refined = assistant.personal_branding_coach(text)
            
        console.print("\n[bold green]REFINED VERSION:[/bold green]")
        console.print(Panel(refined, border_style="magenta"))
    except Exception as e:
        console.print(f"[bold red]Error in Branding Coach:[/bold red] {e}")

def main_menu() -> None:
    """Loop utama menu program."""
    while True:
        clear_screen()
        display_banner()
        
        table = Table(title="MAIN MENU", show_header=False, box=None)
        table.add_row("[1] Intelligence Hub", "[dim]|[/dim]", "Batch CV Screening & Leaderboard")
        table.add_row("[2] Branding Coach", "[dim]|[/dim]", "Polish work descriptions for impact")
        table.add_row("[3] View History", "[dim]|[/dim]", "Browse past analysis (v1 chats)")
        table.add_row("[0] Exit", "[dim]|[/dim]", "Close application")
        
        console.print(Align.center(Panel(table, border_style="cyan", title="Select an Option", expand=False)))
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "0"], default="1")
        
        if choice == "1":
            run_intelligence_hub()
            Prompt.ask("\n[dim]Press Enter to return to menu[/dim]", show_choices=False, default="")
        elif choice == "2":
            run_branding_coach()
            Prompt.ask("\n[dim]Press Enter to return to menu[/dim]", show_choices=False, default="")
        elif choice == "3":
            show_history()
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
