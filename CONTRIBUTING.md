# Contributing to Helix CEO AI Assistant

## Getting Oriented

Before contributing, please read these documents in order:

1. **CONSTITUTION_000_DAY_ZERO.md** (read this first — it explains why this project exists, not just how it works)
2. [README.md](./README.md)
3. [docs/00_CONSTITUTION.md](./docs/00_CONSTITUTION.md)
4. [docs/LOCAL_RUNBOOK.md](./docs/LOCAL_RUNBOOK.md)

## Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Code Standards

- Follow the Helix Clean Code Constitution (docs/00_CONSTITUTION.md)
- All agents must pass constitution check before execution
- Memory logging is mandatory for all agent interactions
- Crash isolation must be preserved

## Testing

- Test agent changes with `python agents/<agent>.py` via stdin JSON
- Verify engine builds with `go build -o engine.exe engine.go`
- Run crash isolation tests before submitting

## Commit Messages

Use conventional commits:
- `feat:` new capability
- `fix:` bug fix
- `refactor:` code restructuring
- `docs:` documentation updates
- `test:` test additions