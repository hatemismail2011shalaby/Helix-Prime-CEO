import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Helix CEO AI Assistant", version="1.0.0")

PROJECT_ROOT = Path(__file__).resolve().parent
COMMAND_CENTER_DIR = PROJECT_ROOT / "00_command_center"
ORCHESTRATOR_PATH = COMMAND_CENTER_DIR / "orchestrator.py"


@app.get("/")
async def get_chat_ui() -> HTMLResponse:
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Helix CEO AI Assistant</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #07111f, #14253f); color: #f4f7fb; }
    .shell { max-width: 920px; margin: 0 auto; padding: 24px; }
    .card { background: rgba(13, 24, 40, 0.9); border: 1px solid #2f4f74; border-radius: 16px; padding: 20px; box-shadow: 0 16px 48px rgba(0,0,0,0.25); }
    h1 { margin-top: 0; }
    .messages { min-height: 400px; max-height: 60vh; overflow-y: auto; padding: 12px; border: 1px solid #2a3c57; border-radius: 12px; background: #060d16; margin-bottom: 12px; }
    .msg { margin-bottom: 10px; padding: 10px 12px; border-radius: 10px; }
    .user { background: #1b4f72; margin-left: 40px; }
    .agent { background: #294b6f; margin-right: 40px; }
    .controls { display: flex; gap: 10px; }
    input, select { padding: 10px 12px; border-radius: 10px; border: 1px solid #365a7f; background: #0d1728; color: white; }
    input { flex: 1; }
    button { padding: 10px 14px; border: none; border-radius: 10px; background: #2bb673; color: white; cursor: pointer; }
    button:hover { background: #24a066; }
  </style>
</head>
<body>
  <div class="shell">
    <div class="card">
      <h1>Helix CEO AI Assistant</h1>
      <p>Chat with your local crew without opening the terminal.</p>
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
  </div>
  <script>
    const messages = document.getElementById('messages');
    const prompt = document.getElementById('prompt');
    const agent = document.getElementById('agent');

    function appendMessage(text, cls) {
      const div = document.createElement('div');
      div.className = 'msg ' + cls;
      div.textContent = text;
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    }

    async function sendMessage() {
      const value = prompt.value.trim();
      if (!value) return;
      appendMessage(value, 'user');
      prompt.value = '';
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: value, agent: agent.value })
        });
        const payload = await response.json();
        appendMessage(payload.reply, 'agent');
      } catch (error) {
        appendMessage('Connection error: ' + error.message, 'agent');
      }
    }

    prompt.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
      }
    });
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
