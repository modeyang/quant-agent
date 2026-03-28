# Quant Agent

A 股量化交易操作系统，按 Harness Engineering 方法构建。

> `Agent = LLM + Deterministic Modules + Data + Memory`

## 当前状态

🟡 `P0` 开发中。当前已完成：
- 包骨架与 `pytest` 测试基线
- 类型化配置加载与共享领域模型
- SQLite 存储与 `candidate_plan` 仓储
- `adata / xtdata` provider 适配器契约
- 最小盘后计划引擎
- 审批规则、订单状态机、对账与复盘摘要
- `plan_only` 真实链路：`adata -> generate_plan -> SQLite -> orchestrator`

## 提交准则

为便于项目管理与回溯，采用以下规则：
- 每完成一个独立阶段，立即生成一个独立 commit。
- commit 需包含该阶段对应的代码、测试和文档同步。
- commit message 使用 `feat:` / `fix:` / `chore:` / `docs:` / `test:` 前缀。
- 提交后推送到远端，并在进度文档记录 commit id 与阶段说明。

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
