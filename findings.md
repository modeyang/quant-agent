# Findings & Decisions

## Requirements
- 用户要求把 `SPEC.md` 衔接成实施计划
- 当前只拆解 `P0`
- 计划必须是可执行任务，而不是泛化路线图
- 需要明确文件路径、测试路径、验证命令和提交节奏

## Research Findings
- 当前仓库仍是脚手架状态，`src/` 和 `tests/` 只有 `.gitkeep`
- `SPEC.md` 已收敛为 `v2`，明确了 `P0 = 数据统一层 + 盘后计划 + 执行/对账 + 复盘 + 主 skill 编排壳`
- 现成 donor 中最重要的是：
  - `adata`：研究数据底座
  - `xtdata/xtquant`：实盘行情与执行
  - `a-share-short-decision`：盘后计划 donor
  - `trade-analysis`：复盘 donor
- 当前 `orchestrator` 仍是薄壳，只返回静态状态
- 当前 `adata_adapter`、`PlanRepository`、`generate_plan` 已存在，最短真实链路是把它们串起来
- 当前 `candidate_plan` 已可落库，但还没有 `run_log` 和 `orchestrator` 级别的数据库写入

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| `P0` 计划采用新目录 `src/common`, `src/data`, `src/planning`, `src/execution`, `src/review` | 与 `SPEC v2` 一致，职责更清晰 |
| `src/agent/orchestrator.py` 作为最小编排入口 | 先保留 `src/agent/` 现有顶层语义，减少路径跳跃 |
| 所有外部依赖先通过 adapter/protocol 包装 | 避免把 `adata`、`xtquant` 直接耦合到核心逻辑 |
| 测试优先覆盖状态机、配置加载、SQLite 存储和计划生成 | 这是 `P0` 的高风险环节 |
| 下一步只打通 `adata -> generate_plan -> candidate_plan` | 这是最小真实价值闭环 |
| orchestrator 本轮采用依赖注入 | 这样仍然能用 fake provider 做测试 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| 当前没有 `pyproject.toml`、测试基建和包结构 | 把它们纳入 `P0` 的第一任务 |
| 上一轮 merge 收尾时并行 git 操作触发 `index.lock` | 后续所有主仓库 git 操作保持串行 |

## Resources
- `SPEC.md`
- `README.md`
- `config/default.yaml`
- `src/agent/orchestrator.py`
- `src/data/adata_adapter.py`
- `src/data/repositories.py`
- `src/planning/plan_generator.py`
- `/Users/yanggenxing/.agents/skills/writing-plans/SKILL.md`
- `/Users/yanggenxing/opensrc/modeSkills/skills-unified/03-agent-framework/planning-with-files/SKILL.md`

## Visual/Browser Findings
- 无
