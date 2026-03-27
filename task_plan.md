# Task Plan: Quant Agent Plan-Only Real Integration

## Goal
把已落地的 `P0` 骨架推进成可运行的 `plan_only` 真实链路：使用 `adata` 拉取数据，生成结构化计划，写入 SQLite，并由 orchestrator 返回真实结果。

## Current Phase
Phase 2

## Phases

### Phase 1: Requirements & Discovery
- [x] 读取 `SPEC.md` 并确认下一步只做 `plan_only` 真实集成
- [x] 检查当前 orchestrator、adapter、repository 的真实缺口
- [x] 收敛实现范围，不把 `xtquant` 实盘执行混入本轮
- **Status:** complete

### Phase 2: Planning & Structure
- [x] 定义 `plan_only` 真实链路的模块边界
- [ ] 写出 focused implementation plan
- [ ] 更新 findings 和 progress
- **Status:** in_progress

### Phase 3: Implementation
- [ ] 创建 worktree
- [ ] 实现 adata-backed planning flow
- [ ] 验证、分步提交并同步 GitHub
- **Status:** pending

## Key Questions
1. `plan_only` 应该直接接真实 `adata`，还是先做 provider injection？
2. SQLite 落库应该只持久化 `candidate_plan`，还是顺便加 `run_log`？
3. orchestrator 返回值是否需要兼顾人读摘要和结构化字段？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 本轮只做 `plan_only` 真实集成 | 降低范围，优先把研究模式跑通 |
| 研究模式使用 `adata` 作为唯一真实数据源 | 当前最容易本地验证，且不需要 Windows / MiniQMT |
| `xtquant` 保持 mockable，不进入本轮 orchestrator | 避免把研究链路和实盘执行耦合在一起 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `python` 命令不存在 | 1 | 改用 `python3` |
| 主仓库并行 git 命令导致 `index.lock` | 1 | 后续 git 操作改为串行 |

## Notes
- 本轮计划文档保存到 `docs/superpowers/plans/`
- 计划写完后进入新 worktree 实现
