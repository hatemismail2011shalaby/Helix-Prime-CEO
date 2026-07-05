import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from memory_manager import get_memory_manager
from model_backend import get_model_backend
from tools import find_files_by_content, find_files_by_name, normalize_query_to_paths

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_MEMORY_PATH = PROJECT_ROOT / '06_memory' / 'sami_private_memory.json'


def _ensure_private_memory_dir() -> None:
    PRIVATE_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_private_memory() -> Dict[str, Any]:
    _ensure_private_memory_dir()
    try:
        return json.loads(PRIVATE_MEMORY_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {'search_history': [], 'notes': []}


def _save_private_memory(memory: Dict[str, Any]) -> None:
    try:
        PRIVATE_MEMORY_PATH.write_text(
            json.dumps(memory, indent=2, ensure_ascii=False), encoding='utf-8'
        )
    except Exception:
        pass


def _record_search(query: str, results: List[str]) -> None:
    memory = _load_private_memory()
    history = memory.setdefault('search_history', [])
    history.append({
        'timestamp': datetime.now().isoformat(),
        'query': query,
        'results': results[:20],
    })
    memory['search_history'] = history[-50:]
    _save_private_memory(memory)


def _resolve_search_roots(prompt: str) -> List[Path]:
    roots = normalize_query_to_paths(prompt)
    if not roots:
        roots = [PROJECT_ROOT]
    return roots


def _search_workspace(prompt: str) -> str:
    search_roots = _resolve_search_roots(prompt)
    query = prompt.strip()
    if 'resume' in query.lower():
        query = 'resume'

    if any(keyword in query.lower() for keyword in ['inside', 'content', 'contains', 'text', 'search content']):
        results = find_files_by_content(query, roots=search_roots)
    else:
        results = find_files_by_name(query, roots=search_roots)

    _record_search(prompt, results)

    if not results:
        root_list = ', '.join(str(root) for root in search_roots)
        return f"No files found for '{prompt}' in {root_list}."

    lines = [f"Found {len(results)} file(s):"]
    for path in results[:25]:
        lines.append(f"- {path}")
    return '\n'.join(lines)


def run() -> None:
    data = json.loads(sys.stdin.read())
    prompt = (data.get('prompt') or '').strip()
    backend = get_model_backend()

    if not prompt:
        print('Please provide a prompt.')
        return

    prompt_lower = prompt.lower()
    if any(keyword in prompt_lower for keyword in [
        'resume',
        'list files',
        'find file',
        'search file',
        'search workspace',
        'workspace search',
        'drive h',
        'h drive',
        'h:',
    ]):
        response = _search_workspace(prompt)
    else:
        response = backend.chat(prompt)

    try:
        memory_mgr = get_memory_manager()
        memory_mgr.add_accomplishment(
            'SAMI',
            f"Processed: {prompt[:50]}...",
            {'full_prompt': prompt, 'response_preview': response[:100]}
        )
    except Exception as e:
        print(f"⚠️  Could not log accomplishment: {e}", file=sys.stderr)

    print(response)


if __name__ == '__main__':
    run()
