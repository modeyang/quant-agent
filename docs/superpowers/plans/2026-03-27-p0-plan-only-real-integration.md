# P0 Plan-Only Real Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current placeholder P0 orchestrator into a real `plan_only` workflow backed by `adata`, `generate_plan`, and SQLite persistence.

**Architecture:** Keep this slice narrow. The orchestrator should accept injected dependencies, fetch market data from an `AdataAdapter`, transform raw provider output into ranked candidate plans, persist plans into SQLite, and return both structured results and a minimal summary. Real `xtquant` execution remains out of scope for this slice.

**Tech Stack:** Python 3.11+, pytest, SQLite, dataclasses, `adata`, PyYAML

---

## File Map

### Modify
- `src/agent/orchestrator.py`
- `src/data/repositories.py`
- `src/common/models.py`
- `README.md`
- `skills/quant-agent/SKILL.md`

### Create
- `src/data/runtime.py`
- `tests/agent/test_plan_only_orchestrator.py`
- `tests/data/test_runtime.py`

---

### Task 1: Runtime Wiring For Research Mode

**Files:**
- Create: `src/data/runtime.py`
- Test: `tests/data/test_runtime.py`

- [ ] **Step 1: Write failing runtime tests**

```python
def test_build_research_runtime_returns_db_and_provider(tmp_path):
    runtime = build_research_runtime(db_path=tmp_path / "quant.db", provider=fake_provider)
    assert runtime.provider is fake_provider
    assert runtime.plan_repo is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./venv/bin/python -m pytest tests/data/test_runtime.py -v`  
Expected: FAIL with missing runtime module

- [ ] **Step 3: Implement a tiny runtime container**

```python
@dataclass
class ResearchRuntime:
    provider: MarketDataProvider
    conn: sqlite3.Connection
    plan_repo: PlanRepository
```

- [ ] **Step 4: Re-run tests**

Run: `./venv/bin/python -m pytest tests/data/test_runtime.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/runtime.py tests/data/test_runtime.py
git commit -m "feat: add research runtime wiring"
```

### Task 2: Persistable Plan Records

**Files:**
- Modify: `src/data/repositories.py`
- Modify: `src/common/models.py`
- Test: `tests/data/test_repositories.py`

- [ ] **Step 1: Add failing test for bulk plan persistence**

```python
def test_plan_repository_saves_bulk_plans(tmp_path):
    repo = PlanRepository(connect_db(tmp_path / "quant.db"))
    init_schema(repo.conn)
    repo.save_candidate_plans("run-1", [CandidatePlan(symbol="600000.SH", asset_type="stock", score=80.0)])
    assert len(repo.list_by_run("run-1")) == 1
```

- [ ] **Step 2: Run targeted test**

Run: `./venv/bin/python -m pytest tests/data/test_repositories.py -v`  
Expected: FAIL because bulk save is missing

- [ ] **Step 3: Implement bulk persistence helper**

```python
def save_candidate_plans(self, run_id: str, plans: list[CandidatePlan]) -> None:
    for plan in plans:
        self.save_plan(run_id, plan.symbol, plan.asset_type, plan.score, plan.status)
```

- [ ] **Step 4: Re-run repository tests**

Run: `./venv/bin/python -m pytest tests/data/test_repositories.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/repositories.py src/common/models.py tests/data/test_repositories.py
git commit -m "feat: add bulk candidate plan persistence"
```

### Task 3: Real Plan-Only Orchestrator

**Files:**
- Modify: `src/agent/orchestrator.py`
- Test: `tests/agent/test_plan_only_orchestrator.py`

- [ ] **Step 1: Write failing orchestrator integration tests**

```python
def test_run_p0_cycle_plan_only_persists_ranked_plans(tmp_path, fake_provider):
    result = run_p0_cycle(
        mode="plan_only",
        runtime=build_research_runtime(tmp_path / "quant.db", fake_provider),
        symbols=["600000.SH"],
    )
    assert result["planning"]["status"] == "ready"
    assert result["planning"]["plan_count"] == 1
```

- [ ] **Step 2: Run tests to verify failure**

Run: `./venv/bin/python -m pytest tests/agent/test_plan_only_orchestrator.py -v`  
Expected: FAIL because the orchestrator is still static

- [ ] **Step 3: Implement `plan_only` flow**

```python
bars = runtime.provider.get_daily_bars(symbols, start, end)
candidates = derive_candidates_from_bars(bars)
plans = generate_plan(run_id, candidates, min_score)
runtime.plan_repo.save_candidate_plans(run_id, plans)
```

- [ ] **Step 4: Re-run orchestrator and dependent tests**

Run: `./venv/bin/python -m pytest tests/agent/test_plan_only_orchestrator.py tests/common tests/data tests/planning -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/agent/orchestrator.py tests/agent/test_plan_only_orchestrator.py
git commit -m "feat: wire plan-only orchestrator to real planning flow"
```

### Task 4: Documentation Sync

**Files:**
- Modify: `README.md`
- Modify: `skills/quant-agent/SKILL.md`

- [ ] **Step 1: Update README with real `plan_only` usage**
- [ ] **Step 2: Update SKILL.md to describe the runtime-backed plan flow**
- [ ] **Step 3: Run full suite**

Run: `./venv/bin/python -m pytest tests/agent tests/common tests/data tests/planning tests/execution tests/review -v`  
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add README.md skills/quant-agent/SKILL.md
git commit -m "docs: document runtime-backed plan-only workflow"
```

---

## Definition Of Done

This slice is complete when:
- `run_p0_cycle(mode="plan_only")` returns real plan output
- candidate plans are persisted into SQLite
- the runtime can be created with injected provider and DB path
- tests cover orchestrator, runtime, and persistence behavior
- docs match the new behavior
