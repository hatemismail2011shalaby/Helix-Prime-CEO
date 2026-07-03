import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
from model_backend import get_model_backend

def run():
    data = json.loads(sys.stdin.read())
    prompt = data.get("prompt", "")
    backend = get_model_backend()
    response = backend.chat(prompt)
    print(response)

if __name__ == "__main__":
    run()