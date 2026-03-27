# Task Plan: Quant Agent Plan-Only Real Integration

## Goal
把已落地的 `P0` 骨架推进成可运行的 `plan_only` 真实链路：使用 `adata` 拉取数据，生成结构化计划，写入 SQLite，并由 orchestrator 返回真实结果。

## Current Phase
Phase 7

## Phases

### Phase 1: Requirements & Discovery
- [x] 读取 `SPEC.md` 并确认下一步只做 `plan_only` 真实集成
- [x] 检查当前 orchestrator、adapter、repository 的真实缺口
- [x] 收敛实现范围，不把 `xtquant` 实盘执行混入本轮
- **Status:** complete

### Phase 2: Planning & Structure
- [x] 定义 `plan_only` 真实链路的模块边界
- [x] 写出 focused implementation plan
- [x] 更新 findings 和 progress
- **Status:** complete

### Phase 3: Implementation
- [x] 通过 `feat/quant-agent-plan-only` 分支完成实现并合并回源仓库 `main`
- [x] 实现 `adata -> generate_plan -> SQLite -> orchestrator` 真实链路
- [x] 同步 README / SKILL 文档，并补上 `adata` 缺失时的保护
- **Status:** complete

### Phase 4: Progress Sync & Next Handoff
- [x] 从源目录 `/Users/yanggenxing/.openclaw/workspace-techAlpha/projects/quant-agent` 回收历史进度
- [x] 核对当前仓库与源目录源码状态基本一致
- [x] 基于真实历史规划下一阶段（`run_log` / execution / monitoring / memory）
- **Status:** complete

### Phase 5: Data Layer Extension (Run Logs & Execution Persistence)
- [x] 扩展 SQLite schema：`run_log`、`orders`、`fills`、`account_snapshot`
- [x] 新增 repository 并注入 runtime（为 execution 主链打基础）
- [x] 补齐数据层测试并通过全量回归
- **Status:** complete

### Phase 6: Execution Wiring Next
- [x] 在 orchestrator 中接入审批 -> 下单 -> 对账的最小 execution 主链
- [x] 将 `run_log` 状态流转接入 orchestrator 生命周期
- [x] 先使用 fake broker 跑通端到端测试，再决定 `xtquant` 接入时机
- **Status:** complete

### Phase 7: Monitoring & Memory Minimal Slice
- [ ] 增加 `monitoring` 最小可运行模块（计划失效/强化检查占位）
- [ ] 增加 `memory` 最小可运行模块（结构化写入占位）
- [ ] 在 orchestrator 中打通 review -> memory 的最小落库链路
- **Status:** in_progress

## Key Questions
1. `xtquant` 真实接入是放在 P0 收尾还是 P1 起步更稳妥？
2. monitoring 最小 slice 是否只做“计划失效检查”，还是同时加“强化信号提示”？
3. memory 首版是否先写 SQLite 表，再补摘要策略？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 本轮只做 `plan_only` 真实集成 | 降低范围，优先把研究模式跑通 |
| 研究模式使用 `adata` 作为唯一真实数据源 | 当前最容易本地验证，且不需要 Windows / MiniQMT |
| orchestrator / runtime 采用 provider injection | 便于 fake provider 测试和后续切换 `xtdata` |
| 本轮 SQLite 只持久化 `candidate_plan` | 先打通最短真实价值闭环，`run_log` 延后到下一阶段 |
| orchestrator 返回结构化 planning / execution / review 三段结果 | 便于 skill 编排和测试断言 |
| `xtquant` 保持 mockable，不进入本轮 orchestrator | 避免把研究链路和实盘执行耦合在一起 |
| 当前独立仓库视为源目录项目的剥离快照 | 源目录 git 历史可作为真实进度依据 |
| 下一阶段优先补数据层持久化基础（`run_log` + execution 相关表） | 能先把执行链数据闭环打底，再接 orchestration |
| execution 主链先以 fake broker 跑通并固化测试 | 在不依赖 `xtquant` 的前提下先验证编排正确性 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `python` 命令不存在 | 1 | 改用 `python3` |
| 主仓库并行 git 命令导致 `index.lock` | 1 | 后续 git 操作改为串行 |
| 当前独立仓库缺少历史上下文 | 1 | 回查源目录与提交历史恢复进度 |

## Notes
- `plan_only` focused plan 位于 `docs/superpowers/plans/2026-03-27-p0-plan-only-real-integration.md`
- 源目录中的关键提交：`ee1f02db`、`bf6cc981`、`15c6faed`、`8d2734ba`、`168b0a2e`
- 源目录中的 `feat/quant-agent-plan-only` 已合并到 `main`
- 本轮新增持久化表和 repository 后，下一步进入 execution wiring
- execution wiring 已完成，下一步进入 monitoring/memory 最小切片
