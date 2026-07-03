# Stage 1: Build the Go binary
FROM golang:1.26-alpine AS builder

WORKDIR /build

COPY 00_command_center/go.mod ./go.mod
COPY 00_command_center/engine.go ./engine.go

RUN go mod tidy
RUN CGO_ENABLED=0 go build -o engine engine.go

# Stage 2: Final runtime image
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /build/engine /app/00_command_center/engine

COPY 00_command_center/orchestrator.py /app/00_command_center/orchestrator.py
COPY 00_command_center/dispatcher.py /app/00_command_center/dispatcher.py
COPY 00_command_center/registry_validator.py /app/00_command_center/registry_validator.py
COPY 00_command_center/agents/ /app/00_command_center/agents/

COPY config/ /app/config/
COPY 06_memory/ /app/06_memory/
COPY docs/ /app/docs/

# NEW: copy the WebSocket bridge into the image root
COPY bridge.py /app/bridge.py

# NEW: fastapi + uvicorn added alongside existing dependencies
RUN pip install --no-cache-dir ollama openai fastapi "uvicorn[standard]"

RUN chmod +x /app/00_command_center/engine

# NOTE: working directory stays at /app (NOT 00_command_center) now,
# because bridge.py itself sets cwd="00_command_center" internally 
# when it spawns the engine subprocess — uvicorn must run from /app 
# where bridge.py actually lives
WORKDIR /app

# Render (and most platforms) inject a PORT env var — bind to it
EXPOSE 8000
CMD ["sh", "-c", "uvicorn bridge:app --host 0.0.0.0 --port ${PORT:-8000}"]