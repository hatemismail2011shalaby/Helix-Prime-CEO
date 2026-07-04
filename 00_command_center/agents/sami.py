import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
from pathlib import Path
from model_backend import get_model_backend
from memory_manager import get_memory_manager

def run():
    data = json.loads(sys.stdin.read())
    prompt = data.get("prompt", "")
    backend = get_model_backend()
    response = backend.chat(prompt)
    
    # Log accomplishment to memory
    try:
        memory_mgr = get_memory_manager()
        memory_mgr.add_accomplishment(
            "SAMI",
            f"Processed: {prompt[:50]}...",
            {"full_prompt": prompt, "response_preview": response[:100]}
        )
    except Exception as e:
        print(f"⚠️  Could not log accomplishment: {e}", file=sys.stderr)
    
    print(response)

if __name__ == "__main__":
    run()