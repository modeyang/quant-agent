# Repository Guidelines

## Project Structure & Module Organization
This repository is still in a scaffold stage. Treat `SPEC.md` as the architecture source of truth and update it when interfaces or responsibilities change.

- `src/agent/`: orchestration, decision flow, and memory-facing logic
- `src/tools/`: market-data and broker adapters
- `src/strategies/`: signal and strategy implementations
- `src/utils/`: shared helpers such as logging and validation
- `config/default.yaml`: checked-in defaults only
- `skills/quant-agent/SKILL.md`: OpenClaw skill contract
- `tests/`: mirror the `src/` layout as code is added
- `data/cache/` and `data/logs/`: generated artifacts, never hand-maintained

Most directories currently contain `.gitkeep`; add new modules inside the existing package layout instead of creating new top-level folders.

## Build, Test, and Development Commands
Use `uv` as the default tool for Python dependency management and execution:

- `uv sync --group dev --group research`: create/update the local environment with test and research dependencies
- `uv run python -m compileall src`: quick syntax check before commit
- `uv run pytest tests -q`: run the test suite
- `uv run quant-agent run --mode plan_only --output json`: run the safe default entrypoint

If a reusable workflow changes, document it here and in the PR description.

Avoid mixing `pip`/`venv` commands into the primary workflow unless there is a concrete compatibility reason.

## Coding Style & Naming Conventions
Use Python with 4-space indentation and PEP 8 naming:

- `snake_case` for modules, functions, and variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants

Keep broker/data wrappers thin; put decision logic in `src/agent/` or `src/strategies/`. Match new YAML keys to the lowercase, grouped style already used in `config/default.yaml`.

## Testing Guidelines
Create tests as `tests/test_<module>.py`. Prefer deterministic unit tests with mocked market data and broker responses; do not depend on live MiniQMT sessions or network calls. For each new module, add at least one happy-path test and one failure-path test.

## Commit & Pull Request Guidelines
Recent history uses short prefixed subjects such as `feat:` and `docs:`. Follow that pattern and keep messages imperative, for example `feat: add akshare data adapter`.

Phase-based commit rule:
- Every completed independent phase must produce one dedicated commit.
- Each phase commit should include code, tests, and doc updates for that phase.
- Record the commit ID in project progress artifacts (for example `task_plan.md` / `progress.md`) to keep milestones traceable.

PRs should include:

- a short summary of behavior changes
- affected paths and config updates
- test evidence (`pytest`, manual checks, or both)
- sample output when analysis or trading flows change

## Security & Configuration Tips
Never commit `config/account.yaml`, `config/secrets.yaml`, cached market data, or logs. Keep new execution paths safe by default and preserve manual confirmation for any order-placement flow until risk controls are fully tested.
