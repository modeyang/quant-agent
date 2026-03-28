# Findings & Decisions

## Requirements
- 用户要求把 `SPEC.md` 衔接成实施计划
- 当前只拆解 `P0`
- 计划必须是可执行任务，而不是泛化路线图
- 需要明确文件路径、测试路径、验证命令和提交节奏
- 当前需要把独立仓库的进度文档与源目录真实历史同步

## Research Findings
- 当前独立仓库是从源目录 `/Users/yanggenxing/.openclaw/workspace-techAlpha/projects/quant-agent` 剥离出的代码快照，源码基本一致，主要缺少 git 历史上下文
- `SPEC.md` 已收敛为 `v2`，明确了 `P0 = 数据统一层 + 盘后计划 + 执行/对账 + 复盘 + 主 skill 编排壳`
- 现成 donor 中最重要的是：
  - `adata`：研究数据底座
  - `xtdata/xtquant`：实盘行情与执行
  - `a-share-short-decision`：盘后计划 donor
  - `trade-analysis`：复盘 donor
- `P0` 基础骨架已经落地，`README.md` 和源码都表明 `plan_only` 真实链路已完成
- `plan_only` slice 已通过源仓库分支 `feat/quant-agent-plan-only` 落地并合并，关键提交包括：
  - `ee1f02db`：research runtime wiring
  - `bf6cc981`：bulk candidate plan persistence
  - `15c6faed`：real `plan_only` orchestrator flow
  - `8d2734ba`：README / SKILL 文档同步
  - `168b0a2e`：`adata` 缺失时避免错误创建 DB
- 当前 `orchestrator` 已接入 runtime、provider、plan generator 和 SQLite 持久化，返回真实 planning 结果
- 当前 `candidate_plan` 已可落库，但 `run_log`、execution 主链接入、`monitoring`、`memory` 仍未完成
- 当前 `task_plan.md` / `progress.md` 落后于真实代码状态，需要按源目录历史回填

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| `P0` 计划采用新目录 `src/common`, `src/data`, `src/planning`, `src/execution`, `src/review` | 与 `SPEC v2` 一致，职责更清晰 |
| `src/agent/orchestrator.py` 作为最小编排入口 | 先保留 `src/agent/` 现有顶层语义，减少路径跳跃 |
| 所有外部依赖先通过 adapter/protocol 包装 | 避免把 `adata`、`xtquant` 直接耦合到核心逻辑 |
| 测试优先覆盖状态机、配置加载、SQLite 存储和计划生成 | 这是 `P0` 的高风险环节 |
| `plan_only` 本轮只打通 `adata -> generate_plan -> candidate_plan` | 这是最小真实价值闭环 |
| orchestrator / runtime 采用依赖注入 | 这样仍然能用 fake provider 做测试 |
| 本轮 SQLite 只持久化 `candidate_plan` | 把 `run_log` 延后到下一阶段，避免扩散范围 |
| 进度同步以源目录 git 历史为准 | 当前独立仓库缺少原始提交记录 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| 当前独立仓库缺少此前对话和提交历史 | 回查源目录、计划文档和 git log 进行恢复 |
| 当前本机环境没有 `pytest` / `PyYAML` | 只能先做文档与源码核对，测试需在装好依赖后重跑 |
| 上一轮 merge 收尾时并行 git 操作触发 `index.lock` | 后续所有主仓库 git 操作保持串行 |

## Resources
- `SPEC.md`
- `README.md`
- `config/default.yaml`
- `src/agent/orchestrator.py`
- `src/data/adata_adapter.py`
- `src/data/repositories.py`
- `src/planning/plan_generator.py`
- `/Users/yanggenxing/.openclaw/workspace-techAlpha/projects/quant-agent`
- `/Users/yanggenxing/.agents/skills/writing-plans/SKILL.md`
- `/Users/yanggenxing/opensrc/modeSkills/skills-unified/03-agent-framework/planning-with-files/SKILL.md`

## Visual/Browser Findings
- 无

## Status Update (2026-03-28)
- `P0` 主链（planning/execution/monitoring/review/memory）已可运行，且本地回归通过
- `shadow` 执行模式已支持可选 `auto_fill`，并可将模拟成交落库到 `fills`
- `run_log_stage_event` 已在 orchestrator 输出中透出：
  - `execution.stage_events`
  - `execution.stage_duration_seconds`
  - `execution.total_stage_duration_seconds`
  - `review.stage_timing_summary`
- 最小可上线硬化（Slice 1）已完成：
  - 执行门禁：`kill_switch` / `max_orders_per_run` / `max_order_notional`
  - 严格对账：`strict_reconcile` + mismatch 结构化告警
  - 上线缺口清单：`docs/go_live_todo.md`
- 当前唯一未闭环项：`xtquant` 实机初始化与连接验证（依赖外部环境）
- 下一阶段建议聚焦 `P1`：盘中轻监控增强与执行观测联动（保持人工审批边界不变）
