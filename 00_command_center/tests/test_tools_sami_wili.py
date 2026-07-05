from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "agents"))

from tools import find_files_by_content, find_files_by_name, normalize_query_to_paths
from agents import sami, wili


def test_find_files_by_name_matches_partial_filename(tmp_path: Path) -> None:
    folder = tmp_path / "docs"
    folder.mkdir()
    target = folder / "my_resume_document.txt"
    target.write_text("test content", encoding="utf-8")

    results = find_files_by_name("resume", roots=[folder])

    assert len(results) == 1
    assert str(target) in results


def test_find_files_by_content_matches_file_text(tmp_path: Path) -> None:
    folder = tmp_path / "notes"
    folder.mkdir()
    target = folder / "lesson_notes.md"
    target.write_text("This lesson contains the keyword Python and more.", encoding="utf-8")

    results = find_files_by_content("python", roots=[folder])

    assert len(results) == 1
    assert str(target) in results


def test_normalize_query_to_paths_returns_h_drive_and_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    paths = normalize_query_to_paths("Search the workspace and H: drive")

    assert Path("H:/") in paths
    assert Path.cwd() in paths


def test_sami_search_workspace_records_history_and_returns_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    temp_root = tmp_path / "workspace"
    temp_root.mkdir(parents=True)
    resume_file = temp_root / "resume_notes.txt"
    resume_file.write_text("A local resume example.", encoding="utf-8")

    monkeypatch.setattr(sami, "PRIVATE_MEMORY_PATH", tmp_path / "sami_private_memory.json")
    monkeypatch.setattr(sami, "normalize_query_to_paths", lambda query: [temp_root])

    output = sami._search_workspace("Find resume files")
    memory_content = json.loads((tmp_path / "sami_private_memory.json").read_text(encoding="utf-8"))

    assert "Found 1 file(s):" in output
    assert str(resume_file) in output
    assert memory_content["search_history"][-1]["query"] == "Find resume files"
    assert str(resume_file) in memory_content["search_history"][-1]["results"]


def test_sami_run_with_empty_prompt_prints_message(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"prompt": ""})))
    monkeypatch.setattr(sami, "get_model_backend", lambda: type("B", (), {"chat": lambda self, prompt: ""})())

    sami.run()

    captured = capsys.readouterr()
    assert "Please provide a prompt." in captured.out


def test_sami_run_search_prompt_uses_search_instead_of_backend(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    temp_root = tmp_path = Path(".").resolve()
    sample_file = temp_root / "resume_test.txt"
    sample_file.write_text("sample", encoding="utf-8")

    monkeypatch.setattr(sami, "PRIVATE_MEMORY_PATH", temp_root / "sami_private_memory.json")
    monkeypatch.setattr(sami, "normalize_query_to_paths", lambda query: [temp_root])

    class DummyBackend:
        def chat(self, prompt: str) -> str:
            raise AssertionError("Backend chat should not be called for search prompts")

    monkeypatch.setattr(sami, "get_model_backend", lambda: DummyBackend())
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"prompt": "search file resume"})))

    sami.run()
    captured = capsys.readouterr()

    assert "Found" in captured.out
    assert str(sample_file) in captured.out


def test_sami_resolves_workspace_to_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_root = tmp_path / "workspace-root"
    project_root.mkdir(parents=True)
    command_center_dir = project_root / "00_command_center"
    command_center_dir.mkdir(parents=True)

    monkeypatch.chdir(command_center_dir)
    monkeypatch.setattr(sami, "PROJECT_ROOT", project_root)

    roots = sami._resolve_search_roots("Search my workspace for resume")

    assert project_root in roots
    assert any(str(path).endswith("workspace-root") for path in roots)


def test_wili_teach_creates_html_and_launches_orchestrator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    agent = wili.WILIAgent()
    lessons_dir = tmp_path / "lessons"
    lessons_dir.mkdir(parents=True)
    orchestrator_dir = tmp_path / "browser_engine"
    orchestrator_dir.mkdir(parents=True)
    orchestrator_script = orchestrator_dir / "orchestrator.py"
    orchestrator_script.write_text("print('orchestrator started')", encoding="utf-8")

    monkeypatch.setattr(agent, "browser_engine_dir", orchestrator_dir)
    monkeypatch.setattr(agent, "lessons_dir", lessons_dir)
    monkeypatch.setattr(agent, "backend", type("B", (), {"chat": lambda self, prompt: "# Topic\n## Details\nLearning content."})())

    started = []

    def fake_popen(args: list[str], cwd: str, stdout: Any, stderr: Any, text: bool) -> Any:
        started.append((args, cwd))
        return type("P", (), {"pid": 12345})()

    monkeypatch.setattr(wili.subprocess, "Popen", fake_popen)

    result = agent.teach("Test Topic")
    lesson_md = lessons_dir / "test_topic.md"
    lesson_html = lessons_dir / "test_topic.html"

    assert lesson_md.exists()
    assert lesson_html.exists()
    assert "Lesson Files" in result
    assert "Process ID: 12345" in result
    assert started[0][0][1] == str(orchestrator_script)
    assert started[0][1] == str(orchestrator_dir)


def test_wili_start_lesson_host_command_starts_http_server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    agent = wili.WILIAgent()
    lessons_dir = tmp_path / "lessons"
    lessons_dir.mkdir(parents=True)
    monkeypatch.setattr(agent, "lessons_dir", lessons_dir)

    started = []
    def fake_popen(args: list[str], cwd: str, stdout: Any, stderr: Any, text: bool) -> Any:
        started.append((args, cwd))
        return type("P", (), {"pid": 54321})()

    monkeypatch.setattr(wili.subprocess, "Popen", fake_popen)

    result = agent.start_lesson_host(8000)

    assert "Local lesson host started on port 8000." in result
    assert "Serving:" in result
    assert "terminate process PID 54321" in result
    assert started[0][0] == [sys.executable, "-m", "http.server", "8000"]
    assert started[0][1] == str(lessons_dir)


def test_wili_teach_warns_when_local_host_unavailable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    agent = wili.WILIAgent()
    lessons_dir = tmp_path / "lessons"
    lessons_dir.mkdir(parents=True)
    orchestrator_dir = tmp_path / "browser_engine"
    orchestrator_dir.mkdir(parents=True)
    orchestrator_script = orchestrator_dir / "orchestrator.py"
    orchestrator_script.write_text("print('orchestrator started')", encoding="utf-8")

    monkeypatch.setattr(agent, "browser_engine_dir", orchestrator_dir)
    monkeypatch.setattr(agent, "lessons_dir", lessons_dir)
    monkeypatch.setattr(agent, "backend", type("B", (), {"chat": lambda self, prompt: "# Topic\n## Details\nLearning content."})())
    monkeypatch.setattr(agent, "_is_local_host_reachable", lambda host, port, timeout=0.4: False)

    def fake_popen(args: list[str], cwd: str, stdout: Any, stderr: Any, text: bool) -> Any:
        return type("P", (), {"pid": 12345})()

    monkeypatch.setattr(wili.subprocess, "Popen", fake_popen)

    result = agent.teach("Test Topic")

    assert "WARNING: A local lesson host is not currently running on localhost:8000." in result
    assert "http://localhost:8000/test_topic.html" in result


def test_wili_generate_lesson_adds_fallback_quiz_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    agent = wili.WILIAgent()
    lessons_dir = tmp_path / "lessons"
    lessons_dir.mkdir(parents=True)
    monkeypatch.setattr(agent, "lessons_dir", lessons_dir)
    monkeypatch.setattr(agent, "backend", type("B", (), {"chat": lambda self, prompt: "# Test Topic\n## Details\nThis is content without a quiz."})())

    lesson_paths = agent.generate_lesson("Test Topic")
    assert lesson_paths is not None

    md_path, html_path = lesson_paths
    saved_markdown = md_path.read_text(encoding="utf-8")
    saved_html = html_path.read_text(encoding="utf-8")

    assert "## Quiz" in saved_markdown
    assert "Interactive Quiz" in saved_html
