#!/bin/bash
# Helix Prime CEO — single entrypoint. Always run this from anywhere via:
#   bash "/mnt/h/Helix CEO AI Assistant/00_command_center/run_helix.sh" <agent_name> <prompt>
cd "/mnt/h/Helix CEO AI Assistant/00_command_center"
export HELIX_MODEL_BACKEND=ollama
export OLLAMA_MODEL=helix-coder:latest
echo "{\"agent_name\":\"$1\",\"prompt\":\"$2\"}" | python3 orchestrator.py
