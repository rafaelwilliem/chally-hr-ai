import os
import json
import google.generativeai as genai
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from typing import List, Dict, Any

import config

console = Console()

class AIInterviewer:
    def __init__(self):
        # Inisialisasi API Gemini
        if not config.GEMINI_API_KEY:
            raise ValueError("API Key tidak ditemukan. Pastikan sudah diatur di file .env")
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.MODEL_NAME)
        self.chat_history: List[Dict[str, str]] = []
        self.session_data: Dict[str, Any] = {}

    def load_context(self, jd_path: str, cv_path: str) -> None:
        """Loading context Job Description (JD) dan Curriculum Vitae (CV)."""
        # (LOGIKA AI): Mengambil data teks dari file eksternal agar LLM tahu role apa yang dicari 
        # dan siapa kandidat yang sedang dihadapi.
        with open(jd_path, 'r', encoding='utf-8') as f:
            jd_text = f.read()
        with open(cv_path, 'r', encoding='utf-8') as f:
            cv_text = f.read()
            
        self.session_data = {
            "jd": jd_text,
            "cv": cv_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # (LOGIKA AI): System Instruction sebagai 'personality' interviewer.
        # Kita masukkan JD dan CV ke dalam prompt awal untuk memberikan context penuh (RAG sederhana).
        self.system_prompt = f"""
        Kamu adalah 'Challora', seorang Senior HR Interviewer yang profesional namun komunikatif.
        Tugasmu adalah melakukan screening awal terhadap kandidat berdasarkan Job Description (JD) dan CV di bawah ini.
        
        [JOB DESCRIPTION]
        {jd_text}
        
        [CANDIDATE CV]
        {cv_text}
        
        ATURAN INTERVIEW:
        1. Mulailah dengan sapaan ramah dan perkenalan singkat.
        2. Tanyakan maksimal 1 pertanyaan setiap sesi agar tidak membebani kandidat.
        3. Fokus pada kecocokan skill teknis dan budaya kerja (culture fit).
        4. Jika durasi sudah cukup (sekitar 5-7 pertanyaan), akhiri interview dengan sopan.
        5. Gunakan Bahasa Indonesia yang formal namun tetap relaks.
        """
        
        # Inisialisasi chat dengan system prompt
        self.chat = self.model.start_chat(history=[])
        # (LOGIKA AI): Mengirim instruksi sistem diawal agar chat state memahami perannya.
        self.chat.send_message(self.system_prompt)

    def start_chat_loop(self) -> None:
        """Looping percakapan interview."""
        console.print(Panel("[bold green]Interview Dimulai. Ketik 'exit' atau 'selesai' untuk berhenti.[/bold green]"))
        
        # (LOGIKA AI): Mengambil pesan sapaan awal dari AI setelah diberikan instruksi sistem.
        # Kita panggil sekali tanpa input untuk memicu AI menyapa lebih dulu.
        ai_response = self.chat.send_message("Silakan sapa kandidat dan mulai interview.")
        console.print(f"\n[bold cyan]Challora:[/bold cyan] {ai_response.text}")
        self.chat_history.append({"role": "challora", "content": ai_response.text})

        while True:
            user_input = console.input("\n[bold yellow]Anda:[/bold yellow] ").strip()
            
            if user_input.lower() in ["exit", "selesai", "quit"]:
                break
            
            self.chat_history.append({"role": "candidate", "content": user_input})
            
            # (LOGIKA AI): Mengirim input kandidat ke model. 
            # Objek 'self.chat' menyimpan state percakapan sehingga kita tidak perlu 
            # mengirim semua history secara manual setiap kali (menghemat token dan kode).
            try:
                with console.status("[italic]Challora sedang berpikir...[/italic]"):
                    response = self.chat.send_message(user_input)
                
                console.print(f"\n[bold cyan]Challora:[/bold cyan] {response.text}")
                self.chat_history.append({"role": "challora", "content": response.text})
                
            except Exception as e:
                console.print(f"[bold red]Error dari API:[/bold red] {str(e)}")
                break

        # Selesai loop, simpan file
        if self.chat_history:
            filename = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_path = self.save_transcript(filename)
            console.print(f"\n[bold green]Interview selesai! Transkrip disimpan di:[/bold green] {save_path}")

    def save_transcript(self, filename: str) -> str:
        """Menyimpan seluruh percakapan ke file JSON."""
        # Gabungkan data session (JD/CV) dan history chat
        final_data = {
            "metadata": self.session_data,
            "conversation": self.chat_history
        }
        
        path = os.path.join(config.TRANSCRIPT_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        
        return path

def start_interview():
    """Entry point untuk Menu 1."""
    try:
        interviewer = AIInterviewer()
        
        # Contoh hardcoded sementara, nanti bisa dibuat Input Prompt menggunakan Rich.
        jd_file = os.path.join(config.CONTEXT_DIR, "jd_sample.txt")
        cv_file = os.path.join(config.CONTEXT_DIR, "cv_sample.txt")
        
        if not os.path.exists(jd_file) or not os.path.exists(cv_file):
            console.print("[bold red]File JD atau CV contoh tidak ditemukan di folder data/context/.[/bold red]")
            return

        interviewer.load_context(jd_file, cv_file)
        interviewer.start_chat_loop()
        
    except Exception as e:
        console.print(f"[bold red]Gagal memulai interview:[/bold red] {str(e)}")
