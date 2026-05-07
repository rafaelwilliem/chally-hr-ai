import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.align import Align
import sys

# Import logic modules
import config

console = Console()

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
    [bold cyan]Simplified HR AI Hub[/bold cyan]
    [italic white]Focusing on Candidate Scoring & Job Recommendation[/italic white]
    """
    console.print(Align.center(Panel(banner, border_style="bold blue")))

def clear_screen() -> None:
    """Membersihkan screen terminal."""
    console.clear()

def wait_for_enter() -> None:
    """Pause and wait for the user to return to menu."""
    Prompt.ask("\n[dim]Press Enter to return to menu[/dim]", show_choices=False, default="")

def run_api_server() -> None:
    """Menjalankan FastAPI server untuk integrasi."""
    console.print(Panel("[bold green]Starting AI API Server...[/bold green]"))
    console.print("[cyan]The AI is now serving requests for HR Scoring and Job Recommendations.[/cyan]")
    console.print("[yellow]Press Ctrl+C to stop the server.[/yellow]")
    
    import uvicorn
    # Import app from src.api
    try:
        from api import app
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        console.print(f"[bold red]Failed to start API server:[/bold red] {e}")

def main_menu() -> None:
    """Loop utama menu program."""
    while True:
        clear_screen()
        display_banner()
        
        table = Table(title="CHALLY AI HUB", show_header=False, box=None)
        table.add_row("[1] Start API Server", "[dim]|[/dim]", "Serve HR Scoring & Job Recommendation")
        table.add_row("[0] Exit", "[dim]|[/dim]", "Close application")
        
        console.print(Align.center(Panel(table, border_style="cyan", title="Select an Option", expand=False)))
        
        choice = Prompt.ask("Enter your choice", choices=["1", "0"], default="1")
        
        if choice == "1":
            run_api_server()
            wait_for_enter()
        elif choice == "0":
            console.print("[bold green]Goodbye![/bold green]")
            break

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program dihentikan paksa.[/bold red]")
        sys.exit(0)
