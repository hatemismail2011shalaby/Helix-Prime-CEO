# Stage 1: Build the Go binary
FROM golang:1.26-alpine AS builder

WORKDIR /build

# Copy Go module and source file directly into build root (flattened,
# so `go build` finds engine.go in its own working directory)
COPY 00_command_center/go.mod ./go.mod
COPY 00_command_center/engine.go ./engine.go

RUN go mod tidy
RUN CGO_ENABLED=0 go build -o engine engine.go

# Stage 2: Final runtime image
FROM python:3.11-slim-bookworm

# Update system packages to patch known vulnerabilities
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy ONLY the compiled binary from Stage 1 — no Go source, no go.mod
COPY --from=builder /build/engine /app/00_command_center/engine

# Copy Python application code explicitly (NOT the whole directory,
# to avoid pulling in go.mod/engine.go that live alongside it)
COPY 00_command_center/orchestrator.py /app/00_command_center/orchestrator.py
COPY 00_command_center/dispatcher.py /app/00_command_center/dispatcher.py
COPY 00_command_center/registry_validator.py /app/00_command_center/registry_validator.py
COPY 00_command_center/agents/ /app/00_command_center/agents/

# Copy remaining runtime directories
COPY config/ /app/config/
COPY 06_memory/ /app/06_memory/
COPY docs/ /app/docs/

# Install Python dependencies
RUN pip install --no-cache-dir ollama openai

# Ensure the engine binary has execute permissions
RUN chmod +x /app/00_command_center/engine

# Set the working directory for the final CMD — engine resolves
# orchestrator.py relative to its own executable location via
# os.Executable(), so it must run from this directory
WORKDIR /app/00_command_center

# Run the engine in daemon mode (no arguments = daemon mode,
# matching existing engine.go behavior)
CMD ["./engine"]