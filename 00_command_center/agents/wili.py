"""
WILI - The Flying Executive
Orchestrates browser-based learning sessions and interactive teaching.
Handles lesson generation and launches the browser automatically.

Fully self-contained — no dependency on AI Automation Engineering.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import re
import socket
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from model_backend import get_model_backend
from rag.retriever import get_retriever

LOCAL_LESSON_HOST = "http://localhost:8000"

# Import memory manager for agent context
sys.path.insert(0, str(Path(__file__).parent.parent))
from memory_manager import get_memory_manager


class WILIAgent:
    """WILI: The Flying Executive - Orchestrates learning and browser interactions.
    
    This agent is fully self-contained within Helix Prime CEO. It generates lessons,
    serves them via a local HTTP server, and launches an interactive browser session
    — all without any dependency on the AI Automation Engineering repository.
    """
    
    def __init__(self):
        self.backend = get_model_backend()
        self.retriever = get_retriever()
        self.project_root = Path(__file__).resolve().parents[2]
        # Self-contained lesson directory inside Helix Prime CEO
        self.lessons_dir = self.project_root / "generated_lessons"
        self.lesson_host_process: subprocess.Popen | None = None
        
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
        
        elif command == "start_lesson_host":
            port = int(args.get("port", 8000))
            return self.start_lesson_host(port)

        elif command == "stop_lesson_host":
            return self.stop_lesson_host()
        
        elif command == "context":
            agent = args.get("agent", "")
            return self.get_agent_context(agent)
        
        else:
            return f"❌ Unknown WILI command: {command}. Try 'teach', 'query', 'list_lessons', 'start_lesson_host', 'stop_lesson_host', or 'context'."
    
    def teach(self, topic: str) -> str:
        """
        Generate a lesson on the given topic and launch browser in interactive mode.
        """
        print(f"\n🚁 WILI: Generating lesson for '{topic}' and launching interactive session...")
        lesson_paths = self.generate_lesson(topic)
        if lesson_paths is None:
            return f"❌ Failed to generate lesson for '{topic}'."

        md_path, html_path = lesson_paths
        if not html_path.exists():
            return f"❌ Lesson HTML file was not created for '{topic}'."

        return self._launch_interactive_learning(topic, md_path, html_path)

    def _launch_interactive_learning(self, topic: str, md_path: Path, html_path: Path) -> str:
        """
        Launch a local HTTP server for the lesson and open it in the browser.
        """
        try:
            # Ensure lesson host is running
            host_result = self.start_lesson_host(8000)
            if "❌" in host_result:
                return host_result
            
            # Give the server a moment to start
            time.sleep(1)
            
            topic_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", topic.strip().lower())
            lesson_url = f"{LOCAL_LESSON_HOST}/{topic_clean}.html"
            
            # Try to open in browser
            import webbrowser
            webbrowser.open(lesson_url)
            
            return f"""✅ Teaching session initiated for '{topic}'
   
📚 Lesson Files:
   • Markdown: {md_path}
   • HTML: {html_path}

🌐 Browser Launch: Opening {lesson_url}

The lesson server is running in the background.
Open the URL above in your browser to continue learning.
Press Ctrl+C in the terminal to stop the server when done.

Process ID: {self.lesson_host_process.pid if self.lesson_host_process else 'N/A'}"""
            
        except Exception as e:
            return f"❌ Failed to launch interactive session: {e}"

    def start_lesson_host(self, port: int = 8000) -> str:
        """Start a local static lesson host serving the lessons directory."""
        try:
            if not self.lessons_dir.exists():
                self.lessons_dir.mkdir(parents=True, exist_ok=True)

            if self.lesson_host_process and self.lesson_host_process.poll() is None:
                return f"✅ Local lesson host already running on port {port}.\nServing: {self.lessons_dir}\nOpen the lesson index at: http://localhost:{port}/"

            command = [sys.executable, "-m", "http.server", str(port)]
            process = subprocess.Popen(
                command,
                cwd=str(self.lessons_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.lesson_host_process = process
            lesson_url = f"http://localhost:{port}/"
            return (
                f"✅ Local lesson host started on port {port}.\n"
                f"Serving: {self.lessons_dir}\n"
                f"Open the lesson index at: {lesson_url}\n"
                f"To stop it, use 'stop_lesson_host' command (PID {process.pid})."
            )
        except Exception as e:
            return f"❌ Failed to start lesson host: {e}"

    def stop_lesson_host(self) -> str:
        """Stop the local lesson host."""
        if self.lesson_host_process and self.lesson_host_process.poll() is None:
            pid = self.lesson_host_process.pid
            self.lesson_host_process.terminate()
            self.lesson_host_process.wait(timeout=5)
            self.lesson_host_process = None
            return f"✅ Lesson host stopped (PID {pid})."
        return "ℹ️ No lesson host running."
    
    def generate_lesson(self, topic: str) -> tuple[Path, Path] | None:
        """
        Generate lesson markdown and HTML files.
        Returns (markdown_path, html_path) immediately.
        """
        try:
            # Ensure lessons directory exists
            self.lessons_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate lesson via model backend
            print(f"📝 Generating lesson content for '{topic}'...")
            prompt = f"""Create a detailed, structured Markdown lesson about "{topic}". Include:
1. Introduction
2. Key Concepts
3. Practical Examples
4. Quiz: 3 multiple-choice questions with clear answers indicated.

Format as valid Markdown without code fences."""
            
            lesson_content = self.backend.chat(prompt)
            
            # Ensure quiz content is present for interactive learning
            lower_content = lesson_content.lower()
            if "## quiz" not in lower_content and "quiz:" not in lower_content:
                lesson_content += (
                    "\n\n## Quiz\n"
                    "1. What is the main idea of this lesson?\n"
                    "- Answer: The main idea is to understand the core concepts of the topic.\n\n"
                    "2. Name one key concept covered.\n"
                    "- Answer: One key concept is described in the lesson.\n\n"
                    "3. How can you apply this topic in a real project?\n"
                    "- Answer: Apply the knowledge through practical examples and exercises.\n"
                )

            # Save markdown
            topic_clean = "".join(c if c.isalnum() or c in "_-" else "_" for c in topic.lower())
            md_path = self.lessons_dir / f"{topic_clean}.md"
            md_path.write_text(lesson_content, encoding='utf-8')
            print(f"✅ Lesson saved: {md_path}")
            
            # Convert to HTML (simple version)
            html_path = md_path.with_suffix(".html")
            html_content = self._markdown_to_html(lesson_content, topic)
            html_path.write_text(html_content, encoding='utf-8')
            print(f"✅ HTML saved: {html_path}")
            
            return (md_path, html_path)
            
        except Exception as e:
            print(f"❌ Lesson generation failed: {e}")
            return None
    
    def _markdown_to_html(self, markdown_text: str, title: str) -> str:
        """Simple Markdown to HTML conversion for lesson display."""
        import html
        
        # Basic markdown conversion
        html_lines = []
        lines = markdown_text.split('\n')
        in_code = False
        code_buffer = []
        
        for line in lines:
            if line.startswith('```'):
                if not in_code:
                    html_lines.append('<pre><code>')
                    in_code = True
                else:
                    html_lines.append('</code></pre>')
                    in_code = False
                continue
            
            if in_code:
                html_lines.append(html.escape(line))
                continue
            
            # Headers
            if line.startswith('# '):
                html_lines.append(f'<h1>{html.escape(line[2:])}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{html.escape(line[3:])}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3>{html.escape(line[4:])}</h3>')
            # Bold
            elif '**' in line:
                line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                html_lines.append(f'<p>{line}</p>')
            # List items
            elif line.strip().startswith('- '):
                html_lines.append(f'<li>{html.escape(line.strip()[2:])}</li>')
            # Empty line
            elif not line.strip():
                html_lines.append('<br>')
            else:
                html_lines.append(f'<p>{html.escape(line)}</p>')
        
        body = '\n'.join(html_lines)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - Helix Prime CEO Lesson</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; color: #1a1a2e; }}
        h1 {{ color: #0b1f3a; border-bottom: 2px solid #143a6b; padding-bottom: 0.5rem; }}
        h2 {{ color: #143a6b; margin-top: 2rem; }}
        h3 {{ color: #1e5a8a; }}
        pre {{ background: #f5f5f5; padding: 1rem; border-radius: 8px; overflow-x: auto; }}
        code {{ background: #f0f0f0; padding: 0.2rem 0.4rem; border-radius: 4px; }}
        li {{ margin: 0.5rem 0; }}
        .quiz {{ background: #e8f0fe; border-left: 4px solid #143a6b; padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0; }}
        .quiz h3 {{ margin-top: 0; color: #0b1f3a; }}
    </style>
</head>
<body>
    <h1>{html.escape(title)}</h1>
    <p><em>Generated by WILI — Helix Prime CEO Learning & Development Director</em></p>
    <hr>
    {body}
    <hr>
    <p><small>Helix Prime CEO — Fully Automated Agentic Organization</small></p>
</body>
</html>"""

    def list_lessons(self) -> str:
        """List all generated lessons."""
        if not self.lessons_dir.exists():
            return "📚 No lessons generated yet. Use 'teach <topic>' to create one."
        
        lessons = list(self.lessons_dir.glob("*.md"))
        if not lessons:
            return "📚 No lessons generated yet. Use 'teach <topic>' to create one."
        
        lines = ["📚 Generated Lessons:"]
        for lesson in sorted(lessons):
            topic = lesson.stem.replace('_', ' ').title()
            html_exists = lesson.with_suffix('.html').exists()
            status = "✅ HTML ready" if html_exists else "⚠️ Markdown only"
            lines.append(f"  • {topic} — {status}")
        return "\n".join(lines)

    def query(self, question: str) -> str:
        """Answer a question using the RAG retriever and model backend."""
        if not question.strip():
            return "❌ Please provide a question."
        
        try:
            # Retrieve relevant context
            context_docs = self.retriever.retrieve(question, top_k=5)
            context = "\n\n".join([doc.get('content', '') for doc in context_docs])
            
            prompt = f"""Answer the question based on the provided context. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question}

Answer:"""
            
            answer = self.backend.chat(prompt)
            return f"🤔 **Question:** {question}\n\n💡 **Answer:** {answer}"
        except Exception as e:
            return f"❌ Query failed: {e}"

    def get_agent_context(self, agent: str) -> str:
        """Get context/memory for a specific agent."""
        try:
            memory = get_memory_manager()
            ctx = memory.get_agent_context(agent)
            if ctx:
                return f"🧠 Context for {agent}:\n{ctx}"
            return f"ℹ️ No context found for agent: {agent}"
        except Exception as e:
            return f"❌ Failed to get context: {e}"


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
        print(f"❌ Invalid JSON input: {e}")
    except Exception as e:
        print(f"❌ WILI Error: {e}")


if __name__ == "__main__":
    run()

