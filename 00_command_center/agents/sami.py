import sys
sys.stdout.reconfigure(encoding='utf-8')

import json, ollama

def run():
    data = json.loads(sys.stdin.read())
    prompt = data.get("prompt", "")
    response = ollama.chat(
        model="qwen3:8b",
        messages=[{"role": "user", "content": prompt}]
    )
    print(response['message']['content'])

if __name__ == "__main__":
    run()
