import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()

@app.get("/")
async def get_terminal():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Helix Terminal</title>
    <style>
        body { background-color: #0c0c0c; color: #00ff00; font-family: 'Courier New', Courier, monospace; margin: 20px; }
        #output { height: 70vh; overflow-y: auto; border: 1px solid #333; padding: 10px; margin-bottom: 10px; white-space: pre-wrap; word-break: break-all; }
        #input-container { display: flex; gap: 10px; }
        input { flex-grow: 1; background: #1a1a1a; border: 1px solid #333; color: white; padding: 10px; outline: none; }
        button { background: #333; color: white; border: 1px solid #555; padding: 10px 20px; cursor: pointer; }
        button:hover { background: #444; }
    </style>
</head>
<body>
    <div id="output"></div>
    <div id="input-container">

        <input type, "text" id="input" placeholder="Type command and press Enter..." autofocus />
        <button id="sendBtn">Send</button>
    </div>
    <script>
        const output = document.getElementById('output');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('sendBtn');
        const ws = new WebSocket(`ws://${window.location.host}/ws`);

        ws.onmessage = (event) => {
            const msg = document.createElement('div');
            msg.textContent = event.data;
            output.appendChild(msg);
            output.scrollTop = output.scrollHeight;
        };

        function sendMessage() {
            if (input.value) {
                ws.send(input.value);
                input.value = '';
            }
        }

        sendBtn.onclick = sendMessage;
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        ws.onclose = () => {
            const msg = document.createElement('div');
            msg.style.color = 'red';
            msg.textContent = 'Connection closed.';
            output.appendChild(msg);
        };
    </script>
</body>
</html>
    """)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    process = None
    try:
        # Spawn the engine binary as a subprocess
        # cwd must be 00_command_center for correct path resolution in Go
        process = await asyncio.create_subprocess_exec(
            "./engine",
            cwd="00_command_center",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        async def read_from_process():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                await websocket.send_text(ed.decode('utf-8'))
            # If loop finishes because stdout closed, close the websocket
            await websocket.close()

        async def write_to_process():
            while True:
                data = await websocket.receive_text()
                process.stdin.write((data + "\n").encode('utf-8'))
                await process.stdin.drain()

        # Run both tasks concurrently

        # We use gather here; if either fails (e.g. WS closes, the other will be cleaned up
        # or we handle it in the exception block.
        try:
            await asyncio.gather(read_from_process(), write_to_process())
        except Exception:
            pass

    except WebSocketDisconnect:
        pass
    finally:
        if process and process.returncode is None:
            try:
                process.terminate()
                # Wait up to 5 seconds for graceful exit, then kill
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()
            except Exception:
                process.kill()