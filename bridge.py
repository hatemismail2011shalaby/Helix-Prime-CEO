import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Helix CEO AI Assistant", version="1.0.0")

PROJECT_ROOT = Path(__file__).resolve().parent
COMMAND_CENTER_DIR = PROJECT_ROOT / "00_command_center"
ORCHESTRATOR_PATH = COMMAND_CENTER_DIR / "orchestrator.py"


def _list_workspace_items(root: Path) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for path in sorted(root.iterdir()):
        if path.name.startswith("."):
            continue
        if path.is_dir():
            items.append({"name": path.name, "type": "folder", "path": str(path.relative_to(root))})
        elif path.is_file():
            items.append({"name": path.name, "type": "file", "path": str(path.relative_to(root))})
    return items


@app.get("/")
async def get_chat_ui() -> HTMLResponse:
    workspace_items = _list_workspace_items(PROJECT_ROOT)
    workspace_markup = "".join(
        f'<div class="tree-item {item["type"]}"><span>{"📁" if item["type"] == "folder" else "📄"}</span> {item["name"]}</div>'
        for item in workspace_items
    )

    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Helix CEO AI Assistant</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #07111f, #14253f); color: #f4f7fb; }}
    .layout {{ display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }}
    .sidebar {{ background: rgba(6, 13, 22, 0.95); border-right: 1px solid #2f4f74; padding: 16px; }}
    .workspace {{ padding: 16px; }}
    .card {{ background: rgba(13, 24, 40, 0.9); border: 1px solid #2f4f74; border-radius: 16px; padding: 16px; box-shadow: 0 16px 48px rgba(0,0,0,0.25); margin-bottom: 12px; }}
    h1, h2 {{ margin-top: 0; }}
    .agent-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }}
    .agent-chip {{ border-radius: 999px; padding: 8px 10px; font-size: 0.9rem; font-weight: 600; color: white; }}
    .sami {{ background: #2f80ed; }}
    .wili {{ background: #f2994a; }}
    .phili {{ background: #bb6bd9; }}
    .suby {{ background: #27ae60; }}
    .status {{ display: flex; align-items: center; gap: 6px; font-size: 0.95rem; color: #a9bcd9; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; background: #2ecc71; animation: pulse 1.2s infinite; }}
    .dot.idle {{ background: #f1c40f; animation: none; }}
    .messages {{ min-height: 320px; max-height: 56vh; overflow-y: auto; padding: 12px; border: 1px solid #2a3c57; border-radius: 12px; background: #060d16; margin-bottom: 12px; }}
    .msg {{ margin-bottom: 10px; padding: 10px 12px; border-radius: 10px; line-height: 1.45; }}
    .user {{ background: #1b4f72; margin-left: 40px; }}
    .agent-msg {{ background: #294b6f; margin-right: 40px; }}
    .thinking {{ background: #5c3c16; color: #ffe7b3; border-left: 4px solid #f2994a; }}
    .controls {{ display: flex; gap: 10px; }}
    input, select {{ padding: 10px 12px; border-radius: 10px; border: 1px solid #365a7f; background: #0d1728; color: white; }}
    input {{ flex: 1; }}
    button {{ padding: 10px 14px; border: none; border-radius: 10px; background: #2bb673; color: white; cursor: pointer; }}
    button:hover {{ background: #24a066; }}
    .tree-item {{ padding: 6px 0; color: #cfd8e3; font-size: 0.95rem; }}
    @keyframes pulse {{ 0% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(1.25); opacity: 0.7; }} 100% {{ transform: scale(1); opacity: 1; }} }}
  </style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <h2>Workspace</h2>
      <div class="status"><span class="dot"></span> Crew online</div>
      <div class="tree">{workspace_markup}</div>
    </aside>
    <main class="workspace">
      <div class="card">
        <h1>Helix CEO AI Assistant</h1>
        <p>ADHD-friendly command center with visible thinking, agent colors, and workspace context.</p>
        <div class="agent-row">
          <div class="agent-chip sami">SAMI</div>
          <div class="agent-chip wili">WILI</div>
          <div class="agent-chip phili">PHILI</div>
          <div class="agent-chip suby">SUBY</div>
        </div>
        <div id="messages" class="messages"></div>
        <div class="controls">
          <select id="agent">
            <option value="sami">SAMI</option>
            <option value="wili">WILI</option>
            <option value="phili">PHILI</option>
            <option value="suby">SUBY</option>
          </select>
          <input id="prompt" placeholder="Ask your crew something..." />
          <button onclick="sendMessage()">Send</button>
        </div>
      </div>
    </main>
  </div>
  <script>
    const messages = document.getElementById('messages');
    const prompt = document.getElementById('prompt');
    const agentSelect = document.getElementById('agent');

    function appendMessage(text, cls, label = '') {{
      const div = document.createElement('div');
      div.className = 'msg ' + cls;
      div.textContent = label ? `${{label}}: ${{text}}` : text;
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    }}

    function setThinking(active, agentName) {{
      const status = document.querySelector('.status');
      if (!status) return;
      status.innerHTML = active ? `<span class="dot"></span> ${{agentName}} is thinking…` : `<span class="dot idle"></span> Crew online`;
    }}

    async function sendMessage() {{
      const value = prompt.value.trim();
      if (!value) return;
      const selectedAgent = agentSelect.value;
      appendMessage(value, 'user', 'You');
      setThinking(true, selectedAgent.toUpperCase());
      prompt.value = '';
      try {{
        const response = await fetch('/api/chat', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ message: value, agent: selectedAgent }})
        }});
        const payload = await response.json();
        appendMessage(payload.reply, 'agent-msg', selectedAgent.toUpperCase());
      }} catch (error) {{
        appendMessage('Connection error: ' + error.message, 'agent-msg', 'SYSTEM');
      }} finally {{
        setThinking(false, '');
      }}
    }}

    prompt.addEventListener('keydown', (event) => {{
      if (event.key === 'Enter') {{
        event.preventDefault();
        sendMessage();
      }}
    }});
  </script>
</body>
</html>
    """)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(payload: Dict[str, str]) -> Dict[str, Any]:
    message = (payload.get("message") or "").strip()
    agent_name = (payload.get("agent") or "sami").strip()
    if not message:
        return {"reply": "Please enter a message.", "agent": agent_name}

    process = subprocess.run(
        [sys.executable, str(ORCHESTRATOR_PATH)],
        input=json.dumps({"agent_name": agent_name, "prompt": message}),
        text=True,
        capture_output=True,
        cwd=str(COMMAND_CENTER_DIR),
        timeout=90,
        check=False,
        encoding="utf-8",
        env={**os.environ, "PYTHONPATH": str(COMMAND_CENTER_DIR)},
    )

    if process.returncode != 0:
        reply = (process.stderr or process.stdout).strip() or "Agent execution failed."
    else:
        reply = process.stdout.strip() or "No response returned."

    return {"reply": reply, "agent": agent_name}
