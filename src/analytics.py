import os
import json
import google.generativeai as genai
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel

import config

console = Console()

def run_analytics():
    """Entry point untuk Menu 3: Menganalisis transkrip dengan AI."""
    files = [f for f in os.listdir(config.TRANSCRIPT_DIR) if f.endswith(".json")]
    
    if not files:
        console.print("[yellow]Tidak ada transkrip untuk dianalisis.[/yellow]")
        input("\nTekan Enter untuk kembali...")
        return

    # Tampilkan daftar file (sama seperti history)
    table = Table(title="Pilih Transkrip untuk Dianalisis")
    for i, f in enumerate(files, 1):
        table.add_row(str(i), f)
    console.print(table)
    
    choice = Prompt.ask("Pilih nomor file", default="0")
    if choice == "0" or not choice.isdigit(): return
    
    idx = int(choice) - 1
    if 0 <= idx < len(files):
        analyze_file(files[idx])

def analyze_file(filename: str):
    """Mengirim transkrip ke LLM untuk evaluasi."""
    path = os.path.join(config.TRANSCRIPT_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # (LOGIKA AI): Kita mempassing seluruh transkrip ke model 
    # untuk mendapatkan ringkasan evaluasi objektif.
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.MODEL_NAME)
    
    prompt = f"""
    Tugasmu adalah menganalisis transkrip interview di bawah ini.
    Berikan penilaian objektif dalam format tabel yang mencakup:
    1. Overall Score (1-10)
    2. Technical Skill Fit (Kecocokan dengan JD)
    3. Soft Skills
    4. Red Flags (jika ada)
    5. Recommendation (Hire/No Hire/Next Stage)

    [TRANSCRIPT DATA]
    {json.dumps(data, indent=2)}
    
    Berikan output dalam format Markdown yang rapi agar bisa dirender dengan baik.
    """
    
    try:
        with console.status("[bold purple]Menganalisis hasil interview...[/bold purple]"):
            response = model.generate_content(prompt)
        
        console.print(Panel(response.text, title="Evaluation Result", border_style="purple"))
        
    except Exception as e:
        console.print(f"[bold red]Gagal melakukan analisis:[/bold red] {str(e)}")
    
    input("\nTekan Enter untuk kembali...")
