# Quant Agent

A 股量化交易操作系统，按 Harness Engineering 方法构建。

> `Agent = LLM + Deterministic Modules + Data + Memory`

## 当前状态

🟡 `P0` 功能闭环已完成，当前处于“最小可上线硬化”阶段。当前已完成：
- 包骨架与 `pytest` 测试基线
- 类型化配置加载与共享领域模型
- SQLite 存储与 `candidate_plan` 仓储
- `adata / xtdata` provider 适配器契约
- 最小盘后计划引擎
- 审批规则、订单状态机、对账与复盘摘要
- `plan_only` 真实链路：`adata -> generate_plan -> SQLite -> orchestrator`
- `shadow_auto_fill` 模拟成交落库
- `run_log_stage_event` 阶段耗时透出
- 最小执行门禁：`kill_switch` / `max_orders_per_run` / `max_order_notional`
- 可选严格对账：`strict_reconcile`

上线关键 TODO 清单见：[docs/go_live_todo.md](docs/go_live_todo.md)。

## 快速开始

### 创建本地环境

```bash
python3 -m venv venv
./venv/bin/python -m pip install pytest pyyaml adata
```

### 运行当前测试

```bash
./venv/bin/python -m pytest tests/common tests/data tests/planning tests/execution tests/review tests/agent -v
```

### 当前 P0 入口

```bash
./venv/bin/python -c "from src.agent.orchestrator import run_p0_cycle; print(run_p0_cycle())"
```

如果本地没有 `adata`，可以继续使用测试里的 fake provider 验证 orchestrator 行为。

### CLI 入口（推荐用于定时调度）

先安装可执行脚本入口：

```bash
./venv/bin/python -m pip install -e .
```

运行计划模式（安全默认：`plan_only`、`kill_switch=true`）：

```bash
quant-agent run --mode plan_only --output json
```

运行手动执行模式（示例：显式审批、严格对账、关闭 kill switch）：

```bash
quant-agent run --mode manual_execute --broker-mode xtquant --approval-granted --strict-reconcile --no-kill-switch --output json
```

打印推荐 crontab 模板：

```bash
quant-agent cron-template --workspace "$(pwd)"
```

更多调度示例见：[docs/cron.example.md](docs/cron.example.md)。

### xtquant preflight（本地执行前检查）

```python
from src.execution.xtquant_preflight import run_xtquant_preflight

result = run_xtquant_preflight("config/account.yaml")
print(result["status"])
for check in result["checks"]:
    print(check["name"], check["status"], check["message"])
```

该检查不会触发真实下单或连接，仅用于验证配置文件与 `xtquant` 本地环境就绪性。

## 目录

```text
quant-agent/
├── SPEC.md
├── config/
├── src/
│   ├── agent/
│   ├── common/
│   ├── data/
│   ├── planning/
│   ├── execution/
│   └── review/
├── tests/
└── skills/
```

## 数据与执行分工

| 组件 | 角色 |
|------|------|
| `adata` | 开发/研究环境数据源 |
| `xtdata` | 实盘环境行情适配器 |
| `xtquant` | 实盘执行适配器 |

## License

MIT
