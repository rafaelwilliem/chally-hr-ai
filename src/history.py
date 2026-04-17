import os
import json
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel

import config

console = Console()

def list_transcripts():
    """Mengambil daftar file transkrip."""
    if not os.path.exists(config.TRANSCRIPT_DIR):
        return []
    return [f for f in os.listdir(config.TRANSCRIPT_DIR) if f.endswith(".json")]

def show_history():
    """Entry point untuk Menu 2: Menampilkan daftar transkrip."""
    files = list_transcripts()
    
    if not files:
        console.print("[yellow]Belum ada transkrip yang tersimpan.[/yellow]")
        input("\nTekan Enter untuk kembali...")
        return

    table = Table(title="Daftar Transkrip Interview")
    table.add_column("No", justify="center", style="cyan")
    table.add_column("Filename", style="white")
    
    for i, f in enumerate(files, 1):
        table.add_row(str(i), f)
        
    console.print(table)
    
    choice = Prompt.ask("Pilih nomor file untuk dibaca (atau '0' untuk kembali)", default="0")
    
    if choice == "0" or not choice.isdigit():
        return
    
    idx = int(choice) - 1
    if 0 <= idx < len(files):
        read_transcript(files[idx])
    else:
        console.print("[bold red]Pilihan tidak valid.[/bold red]")

def read_transcript(filename: str):
    """Membaca dan menampilkan isi transkrip."""
    path = os.path.join(config.TRANSCRIPT_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    console.print(Panel(f"[bold cyan]Transcript: {filename}[/bold cyan]", border_style="blue"))
    
    for msg in data.get("conversation", []):
        role = msg.get("role", "Unknown").capitalize()
        color = "cyan" if role in ["Chally", "Challora"] else "yellow"
        console.print(Panel(msg.get("content", ""), title=f"[{color}]{role}[/{color}]", border_style=color, padding=(0, 1)))
    
    input("\nTekan Enter untuk kembali ke menu...")
