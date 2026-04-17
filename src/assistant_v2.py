import os
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

import config

console = Console()

class ChallyAssistantV2:
    """HR Intelligence Assistant (v2) for batch CV processing and analysis.
    
    This class handles document processing, scoring logic, and personal branding
    using the Gemini 1.5 Flash model.
    """

    def __init__(self) -> None:
        """Initializes the Gemini API and generative model."""
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
            
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.MODEL_NAME)
        self.results: List[Dict[str, Any]] = []

    def load_documents(self, cv_folder: str, jd_path: str) -> Dict[str, Any]:
        """Loads CVs from a folder and Job Description from a file.
        
        Args:
            cv_folder: Path to the directory containing CV files (.txt).
            jd_path: Path to the Job Description text file.
            
        Returns:
            A dictionary containing JD text and a list of CV data.
        """
        if not os.path.exists(jd_path):
            raise FileNotFoundError(f"Job Description file not found at {jd_path}")
            
        with open(jd_path, 'r', encoding='utf-8') as f:
            jd_text = f.read()

        cvs = []
        if not os.path.exists(cv_folder):
            os.makedirs(cv_folder)
            
        for filename in os.listdir(cv_folder):
            if filename.endswith(".txt"):
                path = os.path.join(cv_folder, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    cvs.append({
                        "filename": filename,
                        "content": f.read()
                    })
        
        return {"jd": jd_text, "cvs": cvs}

    def analyze_fit(self, jd_text: str, cvs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Performs batch analysis of CVs against a Job Description.
        
        Utilizes Gemini 1.5 Flash's large context window to process multiple CVs.
        
        Args:
            jd_text: The job description to match against.
            cvs: A list of dictionaries containing CV content.
            
        Returns:
            A list of analysis results for each candidate.
        """
        if not cvs:
            return []

        # Construct a single batch prompt
        cvs_formatted = "\n---\n".join([f"CANDIDATE: {c['filename']}\n{c['content']}" for c in cvs])
        
        prompt = f"""
        You are Chally AI, an HR Intelligence Specialist. 
        Analyze the following candidates against the provided Job Description.
        
        [JOB DESCRIPTION]
        {jd_text}
        
        [CANDIDATE LIST]
        {cvs_formatted}
        
        TASK:
        1. Rate each candidate from 0-100 based on fit.
        2. Provide 'Technical Reasoning' (max 3 points) focused on specific tool/skill matches.
        3. Identify 'Core Strength'.
        
        OUTPUT FORMAT (JSON STRICT):
        Return ONLY a JSON array of objects with these keys:
        [
          {{
            "filename": "candidate_file.txt",
            "score": 85,
            "technical_reasoning": ["point 1", "point 2"],
            "core_strength": "string"
          }}
        ]
        """

        try:
            response = self.model.generate_content(prompt)
            # Handle potential markdown formatting in response
            text = response.text.strip()
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()
            
            self.results = json.loads(text)
            return self.results
        except Exception as e:
            console.print(f"[bold red]AI Processing Error:[/bold red] {e}")
            return []

    def personal_branding_coach(self, work_desc: str) -> str:
        """Transforms dry work descriptions into high-impact language.
        
        Args:
            work_desc: The original, dry work experience description.
            
        Returns:
            A polished version with metrics and action verbs.
        """
        prompt = f"""
        You are a Personal Branding Coach. Rewrite the following dry job description 
        to be high-impact, professional, and focus on achievements/metrics.
        
        [ORIGINAL DESCRIPTION]
        {work_desc}
        
        RULES:
        1. Use strong Action Verbs (Implemented, Scaled, Orchestrated).
        2. Quantify achievements where possible (e.g., 'Increased efficiency by 20%').
        3. Keep it punchy and professional.
        4. Use Bahasa Indonesia yang profesional.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error: {e}"

    def display_leaderboard(self) -> None:
        """Displays the analysis results in a beautiful Rich Table."""
        if not self.results:
            console.print("[yellow]No analysis results found.[/yellow]")
            return

        table = Table(title="🏆 Candidate Leaderboard (Top Tier)", header_style="bold magenta")
        table.add_column("Rank", justify="center", style="cyan")
        table.add_column("Candidate", style="bold white")
        table.add_column("Score", justify="right", style="green")
        table.add_column("Technical Reasoning", style="dim")
        table.add_column("Core Strength", style="italic")

        # Sort results by score descending
        sorted_results = sorted(self.results, key=lambda x: x['score'], reverse=True)

        for i, res in enumerate(sorted_results, 1):
            reasoning = "\n".join([f"• {p}" for p in res.get('technical_reasoning', [])])
            table.add_row(
                str(i),
                res.get('filename', 'Unknown'),
                f"{res.get('score', 0)}/100",
                reasoning,
                res.get('core_strength', 'N/A')
            )

        console.print(Panel(table, border_style="blue", padding=(1, 1)))
