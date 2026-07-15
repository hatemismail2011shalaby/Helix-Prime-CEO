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

            topic_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", topic.strip().lower())
            html_path = self.browser_engine_dir.parent / "lessons" / f"{topic_clean}.html"
            if html_path.exists():
                file_url = html_path.absolute().as_uri()
                return (
                    f"âœ“ Teaching session initiated for '{topic}' (Orchestrator PID: {process.pid}).\n"
                    f"Lesson HTML is available at: {file_url}\n"
                    f"Open the URL above in your browser to continue learning."
                )

            return (
                f"âœ“ Teaching session initiated for '{topic}' (Orchestrator PID: {process.pid}).\n"
                "Learning Orchestrator is starting. The lesson HTML file has not yet appeared, "
                "but should be available shortly under the learning system lessons directory."
            )
        except Exception as e:
            return f"â‌Œ Failed to delegate to learning orchestrator: {e}"

    def _build_local_lesson_url(self, topic: str) -> str:
        topic_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", topic.strip().lower())
        return f"{LOCAL_LESSON_HOST}/{topic_clean}.html"

    def _is_local_host_reachable(self, host: str, port: int, timeout: float = 0.4) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False
    
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

            lesson_url = self._build_local_lesson_url(topic)
            host_ready = self._is_local_host_reachable("127.0.0.1", 8000)
            if host_ready:
                host_message = f"Open the lesson in your browser at: {lesson_url}"
            else:
                host_message = (
                    f"Lesson HTML is generated at: {html_path}\n"
                    f"WARNING: A local lesson host is not currently running on localhost:8000.\n"
                    f"Start a static host for the lessons directory, then open: {lesson_url}"
                )

            return f"""âœ“ Teaching session initiated for '{topic}'
   
ًں“‚ Lesson Files:
   â€¢ Markdown: {md_path}
   â€¢ HTML: {html_path}

ًںŒگ Browser Launch: Starting in background...
{host_message}

The orchestrator is running in interactive mode.
Your browser should open automatically with the lesson and quiz.
Press Ctrl+C in the orchestrator window to stop.

Process ID: {process.pid}"""
            
        except Exception as e:
            return f"â‌Œ Failed to launch interactive session: {e}"

    def start_lesson_host(self, port: int = 8000) -> str:
        """Start a local static lesson host serving the lessons directory."""
        try:
            if not self.lessons_dir.exists():
                return f"â‌Œ Lessons directory not found: {self.lessons_dir}"

            command = [sys.executable, "-m", "http.server", str(port)]
            process = subprocess.Popen(
                command,
                cwd=str(self.lessons_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            lesson_url = f"http://localhost:{port}/"
            self.lesson_host_process = process
            return (
                f"âœ“ Local lesson host started on port {port}.\n"
                f"Serving: {self.lessons_dir}\n"
                f"Open the lesson index at: {lesson_url}\n"
                f"To stop it, terminate process PID {process.pid}."
            )
        except Exception as e:
            return f"â‌Œ Failed to start lesson host: {e}"

    def stop_lesson_host(self) -> str:
        """Stop the previously started local lesson host process cleanly."""
        if self.lesson_host_process is None:
            return "â‌Œ No local lesson host process is currently running."

        if self.lesson_host_process.poll() is not None:
            self.lesson_host_process = None
            return "âœ“ The local lesson host process has already exited."

        try:
            self.lesson_host_process.terminate()
            self.lesson_host_process.wait(timeout=5)
            pid = self.lesson_host_process.pid
            self.lesson_host_process = None
            return f"âœ“ Local lesson host stopped cleanly (PID {pid})."
        except Exception:
            try:
                self.lesson_host_process.kill()
                self.lesson_host_process.wait(timeout=2)
                pid = self.lesson_host_process.pid
                self.lesson_host_process = None
                return f"âœ“ Local lesson host force-stopped (PID {pid})."
            except Exception as e:
                return f"â‌Œ Failed to stop the local lesson host cleanly: {e}"
    
    def query(self, question: str) -> str:
        """Ask WILI a question about the learning content"""
        if not question:
            return "â‌Œ Please provide a question to query."
        
        print(f"ًں§  WILI processing query: {question}")

        try:
            context = self.retriever.retrieve(question, top_k=3)
        except Exception:
            context = []

        if context:
            context_block = "Relevant past lessons/queries:\n" + "\n".join(context) + "\n\n"
            augmented_question = f"{context_block}Question: {question}"
        else:
            augmented_question = question

        response = self.backend.chat(augmented_question)

        try:
            self.retriever.index_text(
                source_id=f"wili_query_{datetime.now().isoformat()}",
                text=f"Q: {question}\nA: {response}",
            )
        except Exception:
            pass

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
        """Convert markdown lesson to styled, ADHD-friendly interactive HTML"""
        import markdown
        rendered_body = markdown.markdown(
            markdown_content, extensions=['fenced_code', 'tables']
        )

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
            line-height: 1.7;
            padding: 20px;
        }}
        .container {{
            max-width: 720px;
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
            background-color: #16232b;
            border-left: 4px solid #00b0ff;
            padding: 10px 16px;
            margin-top: 32px;
            margin-bottom: 16px;
            border-radius: 4px;
        }}
        h3 {{
            color: #b3e5fc;
            margin-top: 24px;
            margin-bottom: 10px;
        }}
        strong {{
            color: #00e676;
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
            border: 2px solid #00e676;
            border-left: 5px solid #00e676;
            padding: 20px;
            margin-top: 32px;
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
        <h1>{topic}</h1>
        <div class="lesson-content">
            {rendered_body}
        </div>
        <div class="quiz-section">
            <h2>Interactive Quiz</h2>
            <textarea id="ans" placeholder="Enter your detailed response here..."></textarea>
            <button onclick="submitAnswer()">Submit Answer</button>
            <p id="msg" style="display: none; color: #00e676; margin-top: 10px;">Answer submitted successfully.</p>
            <div id="feedback-area" style="display: none; background: #16232b; border-left: 4px solid #00b0ff; padding: 15px; margin-top: 15px; border-radius: 4px;">
                <strong style="color: #00b0ff;">Tutor Evaluation:</strong>
                <p id="evaluation-text" style="margin-top: 8px;"></p>
            </div>
        </div>
    </div>

    <script>
        function submitAnswer() {{
            const answer = document.getElementById('ans').value;
            if (!answer.trim()) {{
                alert('Please enter an answer.');
                return;
            }}

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
                const feedbackArea = document.getElementById('feedback-area');
                const evalText = document.getElementById('evaluation-text');
                if (data.evaluation) {{
                    evalText.textContent = data.evaluation;
                    feedbackArea.style.display = 'block';
                }}
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

