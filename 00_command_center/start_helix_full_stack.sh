#!/bin/bash
# Starts the full Helix Prime CEO local stack: lesson host + feedback grader.
# Orchestrator itself is called on-demand (not a long-running server).

LESSONS_DIR="/mnt/h/AI Automation Engineering/02_learning_system/browser_engine/lessons"
BROWSER_ENGINE_DIR="/mnt/h/AI Automation Engineering/02_learning_system/browser_engine"

echo "--- Starting lesson file host on :8000 ---"
cd "$LESSONS_DIR"
nohup python3 -m http.server 8000 > /tmp/helix_lesson_host.log 2>&1 &
echo "Lesson host PID: $!"

echo "--- Starting feedback/grading server on :5000 ---"
cd "$BROWSER_ENGINE_DIR"
nohup python3 feedback_handler.py > /tmp/helix_feedback.log 2>&1 &
echo "Feedback server PID: $!"

echo "--- All background services started. Logs: /tmp/helix_lesson_host.log , /tmp/helix_feedback.log ---"
echo "--- Use 'bash run_helix.sh <agent> \"<prompt>\"' from anywhere for agent calls. ---"
