# P0 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the P0 trading loop for Quant Agent: unified data layer, nightly plan generation, approval-gated execution, reconciliation, and end-of-day review.

**Architecture:** P0 builds a deterministic core under `src/` and keeps the skill layer thin. External providers (`adata`, `xtdata`, `xtquant`) are hidden behind adapters so the planning, execution, and review modules can be tested with fake providers and a temporary SQLite database.

**Tech Stack:** Python 3.11+, pytest, SQLite, dataclasses, `adata`, `xtdata`, `xtquant`, PyYAML, loguru

---

## File Map

### New directories
- `docs/superpowers/plans/` — saved implementation plans
- `src/common/` — shared models, config loading, logging helpers
- `src/data/` — SQLite store, repositories, market data adapters
- `src/planning/` — signal scoring, candidate ranking, plan generation
- `src/execution/` — approval rules, order state machine, broker adapters, reconciliation
- `src/review/` — review summary and postmortem helpers
- `tests/common/`, `tests/data/`, `tests/planning/`, `tests/execution/`, `tests/review/`, `tests/agent/`

### Existing files to modify
- `README.md` — update setup and run flow after P0 lands
- `config/default.yaml` — keep source-of-truth defaults aligned with new config loader
- `skills/quant-agent/SKILL.md` — wire the new workflows after the core modules exist

### New files by responsibility
- `pyproject.toml` — dependency and pytest configuration
- `config/account.yaml.example` — broker/account sample config
- `config/strategy.yaml` — planning and risk defaults not suited for `default.yaml`
- `src/common/config.py` — load and validate YAML config into typed objects
- `src/common/models.py` — shared domain models (`Asset`, `Bar`, `CandidatePlan`, `OrderIntent`, `ReviewSummary`)
- `src/common/logger.py` — project logger factory
- `src/data/db.py` — SQLite connection management
- `src/data/schema.py` — schema creation helpers
- `src/data/repositories.py` — repositories for bars, plans, orders, fills, positions
- `src/data/provider_base.py` — provider protocols
- `src/data/adata_adapter.py` — research market-data adapter
- `src/data/xtdata_adapter.py` — real-trading market-data adapter
- `src/planning/signal_engine.py` — event/trend/fund flow scoring
- `src/planning/candidate_ranker.py` — ranking and filtering
- `src/planning/plan_generator.py` — produce next-day candidate plans
- `src/execution/approval.py` — approval and preflight checks
- `src/execution/order_state_machine.py` — deterministic order lifecycle
- `src/execution/broker_base.py` — broker protocol
- `src/execution/broker_xtquant.py` — xtquant broker adapter
- `src/execution/reconcile.py` — reconcile orders, fills, positions, account snapshots
- `src/review/trade_review.py` — structured day review
- `src/review/postmortem.py` — error pattern and missed-plan summaries
- `src/agent/orchestrator.py` — thin workflow entry for P0
- `tests/conftest.py` — shared fixtures

---

### Task 1: Tooling And Package Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/common/__init__.py`
- Create: `src/data/__init__.py`
- Create: `src/planning/__init__.py`
- Create: `src/execution/__init__.py`
- Create: `src/review/__init__.py`
- Create: `tests/conftest.py`
- Test: `tests/common/test_imports.py`

- [ ] **Step 1: Write the failing import smoke test**

```python
def test_package_imports():
    import src.common  # noqa: F401
    import src.data  # noqa: F401
    import src.planning  # noqa: F401
    import src.execution  # noqa: F401
    import src.review  # noqa: F401
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/common/test_imports.py -v`  
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create package skeleton and toolchain**

```toml
[project]
name = "quant-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "pandas",
  "numpy",
  "pyyaml",
  "loguru",
  "pytest",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 4: Run test to verify imports pass**

Run: `python3 -m pytest tests/common/test_imports.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/common src/data src/planning src/execution src/review tests/common/test_imports.py tests/conftest.py
git commit -m "chore: add package skeleton for p0 modules"
```

### Task 2: Typed Config And Domain Models

**Files:**
- Create: `config/account.yaml.example`
- Create: `config/strategy.yaml`
- Create: `src/common/config.py`
- Create: `src/common/models.py`
- Create: `src/common/logger.py`
- Test: `tests/common/test_config.py`
- Test: `tests/common/test_models.py`

- [ ] **Step 1: Write failing tests for config loading and domain models**

```python
from src.common.config import load_settings
from src.common.models import CandidatePlan

def test_load_settings_reads_default_yaml(tmp_path):
    settings = load_settings("config/default.yaml")
    assert settings.agent.mode == "manual"

def test_candidate_plan_defaults_to_pending():
    plan = CandidatePlan(symbol="600000.SH", asset_type="stock", score=80.0)
    assert plan.status == "planned"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/common/test_config.py tests/common/test_models.py -v`  
Expected: FAIL with missing modules/classes

- [ ] **Step 3: Implement minimal config and model layer**

```python
@dataclass
class CandidatePlan:
    symbol: str
    asset_type: str
    score: float
    status: str = "planned"

def load_settings(path: str) -> Settings:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Settings.from_dict(raw)
```

- [ ] **Step 4: Run tests and inspect loaded values**

Run: `python3 -m pytest tests/common/test_config.py tests/common/test_models.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add config/account.yaml.example config/strategy.yaml src/common/config.py src/common/models.py src/common/logger.py tests/common/test_config.py tests/common/test_models.py
git commit -m "feat: add typed config and shared domain models"
```

### Task 3: SQLite Store And Repositories

**Files:**
- Create: `src/data/db.py`
- Create: `src/data/schema.py`
- Create: `src/data/repositories.py`
- Test: `tests/data/test_schema.py`
- Test: `tests/data/test_repositories.py`

- [ ] **Step 1: Write failing tests for schema creation and repository writes**

```python
from src.data.db import connect_db
from src.data.schema import init_schema
from src.data.repositories import PlanRepository

def test_init_schema_creates_candidate_plan_table(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    rows = conn.execute("select name from sqlite_master where type='table' and name='candidate_plan'").fetchall()
    assert rows

def test_plan_repository_round_trip(tmp_path):
    conn = connect_db(tmp_path / "quant.db")
    init_schema(conn)
    repo = PlanRepository(conn)
    repo.save_plan("run-1", "600000.SH", "stock", 85.0)
    saved = repo.list_by_run("run-1")
    assert saved[0]["symbol"] == "600000.SH"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/data/test_schema.py tests/data/test_repositories.py -v`  
Expected: FAIL with missing database helpers

- [ ] **Step 3: Implement DB helpers and minimal repositories**

```python
def connect_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()
```

- [ ] **Step 4: Run tests and add one duplicate-key guard test**

Run: `python3 -m pytest tests/data/test_schema.py tests/data/test_repositories.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/db.py src/data/schema.py src/data/repositories.py tests/data/test_schema.py tests/data/test_repositories.py
git commit -m "feat: add sqlite store and repositories"
```

### Task 4: Market Data Provider Interfaces And Adapters

**Files:**
- Create: `src/data/provider_base.py`
- Create: `src/data/adata_adapter.py`
- Create: `src/data/xtdata_adapter.py`
- Test: `tests/data/test_adata_adapter.py`
- Test: `tests/data/test_provider_contracts.py`

- [ ] **Step 1: Write failing tests for provider contracts**

```python
from src.data.provider_base import MarketDataProvider

def test_market_data_provider_exposes_required_methods():
    required = {"get_daily_bars", "get_intraday_bars", "get_asset_master"}
    assert required.issubset(set(dir(MarketDataProvider)))
```

- [ ] **Step 2: Write failing adapter test with fake adata module**

```python
def test_adata_adapter_maps_daily_bars(fake_adata_module):
    adapter = AdataAdapter(fake_adata_module)
    rows = adapter.get_daily_bars(["600000.SH"], "2026-03-01", "2026-03-10")
    assert rows[0].symbol == "600000.SH"
```

- [ ] **Step 3: Implement provider protocol and adapter mapping**

```python
class MarketDataProvider(Protocol):
    def get_daily_bars(self, symbols: list[str], start: str, end: str) -> list[Bar]: ...
    def get_intraday_bars(self, symbols: list[str], trade_date: str) -> list[Bar]: ...
    def get_asset_master(self) -> list[Asset]: ...
```

- [ ] **Step 4: Run tests to verify adapter shape, not live API behavior**

Run: `python3 -m pytest tests/data/test_provider_contracts.py tests/data/test_adata_adapter.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/provider_base.py src/data/adata_adapter.py src/data/xtdata_adapter.py tests/data/test_provider_contracts.py tests/data/test_adata_adapter.py
git commit -m "feat: add market data provider adapters"
```

### Task 5: Nightly Planning Pipeline

**Files:**
- Create: `src/planning/signal_engine.py`
- Create: `src/planning/candidate_ranker.py`
- Create: `src/planning/plan_generator.py`
- Test: `tests/planning/test_signal_engine.py`
- Test: `tests/planning/test_plan_generator.py`

- [ ] **Step 1: Write failing tests for score generation and plan ordering**

```python
from src.planning.signal_engine import score_candidate
from src.planning.plan_generator import generate_plan

def test_score_candidate_combines_event_trend_and_fund_flow():
    score = score_candidate(event_score=80, trend_score=70, flow_score=90, weights={"event": 0.4, "trend": 0.3, "flow": 0.3})
    assert score == 80.0

def test_generate_plan_returns_ranked_candidates():
    plans = generate_plan(run_id="run-1", candidates=[{"symbol": "600000.SH", "score": 82.0}, {"symbol": "510300.SH", "score": 75.0}])
    assert plans[0].symbol == "600000.SH"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/planning/test_signal_engine.py tests/planning/test_plan_generator.py -v`  
Expected: FAIL with missing planning modules

- [ ] **Step 3: Implement minimal planning engine**

```python
def score_candidate(event_score: float, trend_score: float, flow_score: float, weights: dict[str, float]) -> float:
    return round(
        event_score * weights["event"] +
        trend_score * weights["trend"] +
        flow_score * weights["flow"],
        2,
    )
```

- [ ] **Step 4: Run tests and add one watch-threshold case**

Run: `python3 -m pytest tests/planning/test_signal_engine.py tests/planning/test_plan_generator.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/planning/signal_engine.py src/planning/candidate_ranker.py src/planning/plan_generator.py tests/planning/test_signal_engine.py tests/planning/test_plan_generator.py
git commit -m "feat: add nightly planning pipeline"
```

### Task 6: Approval Rules And Order State Machine

**Files:**
- Create: `src/execution/approval.py`
- Create: `src/execution/order_state_machine.py`
- Create: `src/execution/broker_base.py`
- Create: `src/execution/broker_xtquant.py`
- Test: `tests/execution/test_approval.py`
- Test: `tests/execution/test_order_state_machine.py`

- [ ] **Step 1: Write failing tests for approval and state transitions**

```python
from src.execution.approval import require_manual_approval
from src.execution.order_state_machine import OrderStateMachine

def test_new_position_requires_manual_approval():
    assert require_manual_approval(action="open", approved=False) is True

def test_order_state_machine_blocks_duplicate_submission():
    sm = OrderStateMachine(plan_id="plan-1")
    sm.approve()
    sm.submit()
    assert sm.can_submit() is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/execution/test_approval.py tests/execution/test_order_state_machine.py -v`  
Expected: FAIL with missing execution modules

- [ ] **Step 3: Implement minimal approval logic and state machine**

```python
ALLOWED_TRANSITIONS = {
    "planned": {"approved"},
    "approved": {"submitted"},
    "submitted": {"partial_fill", "filled", "canceled", "rejected"},
}
```

- [ ] **Step 4: Run tests and add one reconcile-ready transition case**

Run: `python3 -m pytest tests/execution/test_approval.py tests/execution/test_order_state_machine.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/execution/approval.py src/execution/order_state_machine.py src/execution/broker_base.py src/execution/broker_xtquant.py tests/execution/test_approval.py tests/execution/test_order_state_machine.py
git commit -m "feat: add approval rules and order state machine"
```

### Task 7: Reconciliation And End-Of-Day Review

**Files:**
- Create: `src/execution/reconcile.py`
- Create: `src/review/trade_review.py`
- Create: `src/review/postmortem.py`
- Test: `tests/execution/test_reconcile.py`
- Test: `tests/review/test_trade_review.py`

- [ ] **Step 1: Write failing tests for reconciliation output and review summary**

```python
from src.execution.reconcile import reconcile_run
from src.review.trade_review import build_trade_review

def test_reconcile_run_marks_filled_order_as_reconciled():
    result = reconcile_run(
        orders=[{"order_id": "o1", "status": "filled"}],
        fills=[{"order_id": "o1", "qty": 100}],
    )
    assert result["reconciled"] == 1

def test_build_trade_review_summarizes_plan_vs_actual():
    review = build_trade_review(planned=2, executed=1, rejected=1)
    assert review.executed_count == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/execution/test_reconcile.py tests/review/test_trade_review.py -v`  
Expected: FAIL with missing modules

- [ ] **Step 3: Implement reconciliation and review layer**

```python
def reconcile_run(orders: list[dict], fills: list[dict]) -> dict:
    filled_ids = {fill["order_id"] for fill in fills}
    reconciled = sum(1 for order in orders if order["order_id"] in filled_ids)
    return {"reconciled": reconciled}
```

- [ ] **Step 4: Run tests and add one mismatch warning case**

Run: `python3 -m pytest tests/execution/test_reconcile.py tests/review/test_trade_review.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/execution/reconcile.py src/review/trade_review.py src/review/postmortem.py tests/execution/test_reconcile.py tests/review/test_trade_review.py
git commit -m "feat: add reconciliation and end-of-day review"
```

### Task 8: P0 Orchestration And Docs

**Files:**
- Create: `src/agent/orchestrator.py`
- Modify: `skills/quant-agent/SKILL.md`
- Modify: `README.md`
- Test: `tests/agent/test_orchestrator.py`

- [ ] **Step 1: Write failing orchestration test**

```python
from src.agent.orchestrator import run_p0_cycle

def test_run_p0_cycle_returns_plan_execute_review_sections():
    result = run_p0_cycle(mode="plan_only")
    assert {"planning", "execution", "review"}.issubset(result.keys())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/agent/test_orchestrator.py -v`  
Expected: FAIL with missing orchestrator

- [ ] **Step 3: Implement thin orchestrator and document workflow**

```python
def run_p0_cycle(mode: str = "plan_only") -> dict:
    return {
        "planning": {"status": "ready"},
        "execution": {"status": "skipped" if mode == "plan_only" else "pending"},
        "review": {"status": "pending"},
    }
```

- [ ] **Step 4: Run targeted tests and a full smoke suite**

Run: `python3 -m pytest tests/agent/test_orchestrator.py tests/common tests/data tests/planning tests/execution tests/review -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/agent/orchestrator.py skills/quant-agent/SKILL.md README.md tests/agent/test_orchestrator.py
git commit -m "feat: wire p0 orchestration workflow"
```

---

## Manual Review Checklist

- `P0` 是否只覆盖 `src/data`, `src/planning`, `src/execution`, `src/review`, `src/agent` 五条主线
- 是否所有外部依赖都藏在 adapter 后面
- 是否每个任务都先写测试，再写最小实现
- 是否 `xtquant` 相关代码只通过协议和 fake broker 测试
- 是否 `README.md` 和 `skills/quant-agent/SKILL.md` 在最后同步

## Definition Of Done

P0 完成时，仓库应满足：
- 可加载配置并初始化 SQLite
- 可从 fake/real provider 读取统一形状的数据
- 可生成结构化次日交易计划
- 可对计划执行审批和状态流转
- 可完成订单/成交/持仓基础对账
- 可生成结构化收盘复盘结果
- 可通过一个薄编排入口串起上述流程
