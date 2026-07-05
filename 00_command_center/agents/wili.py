"""
WILI - The Flying Executive
Orchestrates browser-based learning sessions and interactive teaching.
Handles lesson generation and launches the browser automatically.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import subprocess
import threading
import time
from pathlib import Path
from model_backend import get_model_backend

# Import memory manager for agent context
sys.path.insert(0, str(Path(__file__).parent.parent))
from memory_manager import get_memory_manager

class WILIAgent:
    """WILI: The Flying Executive - Orchestrates learning and browser interactions"""
    
    def __init__(self):
        self.backend = get_model_backend()
        self.project_root = Path(__file__).resolve().parents[2]
        self.browser_engine_dir = self.project_root.parent / "AI Automation Engineering" / "02_learning_system" / "browser_engine"
        self.lessons_dir = self.browser_engine_dir / "lessons"
        
    def execute_command(self, command: str, args: dict) -> str:
        """Main command dispatcher for WILI"""
        
        if command == "teach":
            topic = args.get("topic", "General Knowledge")
            return self.teach(topic)
        
        elif command == "query":
            question = args.get("question", "")
            return self.query(question)
        
        elif command == "list_lessons":
            return self.list_lessons()
        
        elif command == "context":
            agent = args.get("agent", "")
            return self.get_agent_context(agent)
        
        else:
            return f"â‌Œ Unknown WILI command: {command}. Try 'teach', 'query', 'list_lessons', or 'context'."
    
    def teach(self, topic: str) -> str:
        """
        Generate a lesson on the given topic and launch browser in interactive mode.
        Uses subprocess.Popen to run orchestrator.py non-blocking.
        Browser opens automatically.
        """
        print(f"\nًںڑپ WILI: Initiating teaching sequence for '{topic}'...")
        
        lesson_paths = self.generate_lesson(topic)
        
        if not lesson_paths:
            return f"â‌Œ Failed to generate lesson for '{topic}'."
        
        md_path, html_path = lesson_paths
        
        # Launch orchestrator.py in interactive mode (non-blocking) using Popen
        return self._launch_interactive_learning(topic, md_path, html_path)
    
    def generate_lesson(self, topic: str) -> tuple[Path, Path] | None:
        """
        Generate lesson markdown and HTML files.
        Returns (markdown_path, html_path) immediately.
        """
        try:
            # Ensure lessons directory exists
            self.lessons_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate lesson via model backend
            print(f"ًں“‌ Generating lesson content for '{topic}'...")
            prompt = f"""Create a detailed, structured Markdown lesson about "{topic}". Include:
1. Introduction
2. Key Concepts
3. Practical Examples
4. Quiz: 3 multiple-choice questions with clear answers indicated.

Format as valid Markdown without code fences."""
            
            lesson_content = self.backend.chat(prompt)
            
            # Save markdown
            topic_clean = topic.replace(' ', '_').lower()
            md_path = self.lessons_dir / f"{topic_clean}.md"
            md_path.write_text(lesson_content, encoding='utf-8')
            print(f"âœ“ Lesson saved: {md_path}")
            
            # Convert to HTML (simple version)
            html_path = md_path.with_suffix(".html")
            html_content = self._markdown_to_html(lesson_content, topic)
            html_path.write_text(html_content, encoding='utf-8')
            print(f"âœ“ HTML saved: {html_path}")
            
            return (md_path, html_path)
            
        except Exception as e:
            print(f"â‌Œ Lesson generation failed: {e}")
            return None
    
    def _launch_interactive_learning(self, topic: str, md_path: Path, html_path: Path) -> str:
        """
        Launch orchestrator.py in interactive mode (non-blocking).
        Browser will open automatically.
        """
        try:
            # Prepare command: orchestrator.py without --test flag (interactive mode)
            orchestrator_path = self.browser_engine_dir / "orchestrator.py"
            
            if not orchestrator_path.exists():
                return f"â‌Œ Orchestrator not found at {orchestrator_path}"
            
            print(f"ًںŒگ Launching interactive learning session...")
            print(f"   Orchestrator: {orchestrator_path}")
            print(f"   Topic: {topic}")
            
            # Use subprocess.Popen to launch without blocking
            # This starts the orchestrator in interactive mode (no --test flag)
            process = subprocess.Popen(
                [sys.executable, str(orchestrator_path), topic],
                cwd=str(self.browser_engine_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Return immediately with lesson info while process runs
            return f"""âœ“ Teaching session initiated for '{topic}'
   
ًں“‚ Lesson Files:
   â€¢ Markdown: {md_path}
   â€¢ HTML: {html_path}

ًںŒگ Browser Launch: Starting in background...
   
The orchestrator is running in interactive mode.
Your browser should open automatically with the lesson and quiz.
Press Ctrl+C in the orchestrator window to stop.

Process ID: {process.pid}"""
            
        except Exception as e:
            return f"â‌Œ Failed to launch interactive session: {e}"
    
    def query(self, question: str) -> str:
        """Ask WILI a question about the learning content"""
        if not question:
            return "â‌Œ Please provide a question to query."
        
        print(f"ًں§  WILI processing query: {question}")
        response = self.backend.chat(question)
        return f"WILI's Response:\n{response}"
    
    def get_agent_context(self, agent_name: str) -> str:
        """Get context about what another agent has accomplished"""
        if not agent_name:
            agent_name = "SAMI"
        
        try:
            memory_mgr = get_memory_manager()
            
            if agent_name.upper() == "SAMI":
                accomplishments = memory_mgr.get_accomplishments_summary("SAMI")
                return f"""ًں“ٹ Context About SAMI:
â”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پ
{accomplishments}

SAMI is the CEO Orchestrator coordinating all agents."""
            
            elif agent_name.upper() == "PHILI":
                accomplishments = memory_mgr.get_accomplishments_summary("PHILI")
                return f"""ًں“ٹ Context About PHILI:
â”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پ
{accomplishments}

PHILI is your personal philosopher focusing on self-development."""
            
            elif agent_name.upper() == "SUBY":
                accomplishments = memory_mgr.get_accomplishments_summary("SUBY")
                return f"""ًں“ٹ Context About SUBY:
â”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پ
{accomplishments}

SUBY is the creator generating web apps and platforms."""
            
            else:
                all_summaries = memory_mgr.get_all_agent_summaries()
                return all_summaries
        
        except Exception as e:
            return f"âڑ ï¸ڈ  Could not retrieve context: {e}"
    
    def list_lessons(self) -> str:
        """List all available lessons"""
        if not self.lessons_dir.exists():
            return "ًں“‚ No lessons directory found."
        
        lessons = list(self.lessons_dir.glob("*.md"))
        
        if not lessons:
            return "ًں“‚ No lessons available. Use 'teach' command to create one."
        
        output = "ًں“ڑ Available Lessons:\n"
        for i, lesson in enumerate(lessons, 1):
            size = lesson.stat().st_size / 1024  # KB
            output += f"   {i}. {lesson.stem} ({size:.1f} KB)\n"
        
        return output
    
    def _markdown_to_html(self, markdown_content: str, topic: str) -> str:
        """Convert markdown lesson to basic interactive HTML"""
        
        # Simple markdown to HTML conversion
        html_content = markdown_content.replace('\n# ', '\n<h1>')
        html_content = html_content.replace('\n## ', '\n<h2>')
        html_content = html_content.replace('\n### ', '\n<h3>')
        
        # Wrap in HTML structure
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Session: {topic}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background-color: #0c0c0c;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 40px;
        }}
        h1 {{
            color: #00e676;
            margin-bottom: 20px;
            border-bottom: 2px solid #00e676;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #00b0ff;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        h3 {{
            color: #b3e5fc;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        p {{
            margin-bottom: 15px;
            opacity: 0.9;
        }}
        code {{
            background: #000;
            color: #ffeb3b;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #000;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
        }}
        pre code {{
            display: block;
            padding: 0;
            background: none;
            color: #00ff00;
        }}
        textarea {{
            width: 100%;
            height: 120px;
            background: #2c2c2c;
            color: white;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            margin: 20px 0;
            resize: vertical;
        }}
        button {{
            background: #00e676;
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }}
        button:hover {{
            background: #00c853;
        }}
        .quiz-section {{
            background: #263238;
            border-left: 5px solid #00e676;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .lesson-loading {{
            text-align: center;
            color: #00b0ff;
            padding: 40px;
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ًںژ“ {topic}</h1>
        <div class="lesson-content">
            {markdown_content}
        </div>
        <div class="quiz-section">
            <h2>ًں“‌ Interactive Quiz</h2>
            <textarea id="ans" placeholder="Enter your detailed response here..."></textarea>
            <button onclick="submitAnswer()">Submit Answer</button>
            <p id="msg" style="display: none; color: #00e676; margin-top: 10px;">âœ“ Answer submitted successfully.</p>
        </div>
    </div>
    
    <script>
        function submitAnswer() {{
            const answer = document.getElementById('ans').value;
            if (!answer.trim()) {{
                alert('Please enter an answer.');
                return;
            }}
            
            // Send to backend (if available)
            fetch('http://localhost:5000/submit', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    topic: '{topic}',
                    content: answer,
                    question_index: 1,
                    total_questions: 3
                }})
            }})
            .then(r => r.json())
            .then(data => {{
                document.getElementById('msg').style.display = 'block';
                console.log('Answer response:', data);
            }})
            .catch(e => console.error('Submission error:', e));
        }}
    </script>
</body>
</html>"""


def run():
    """Main entry point for WILI agent"""
    try:
        data = json.loads(sys.stdin.read())
        command = data.get("command", "teach")
        args = data.get("args", {})
        
        wili = WILIAgent()
        response = wili.execute_command(command, args)
        print(response)
        
    except json.JSONDecodeError as e:
        print(f"â‌Œ Invalid JSON input: {e}")
    except Exception as e:
        print(f"â‌Œ WILI Error: {e}")


if __name__ == "__main__":
    run()

