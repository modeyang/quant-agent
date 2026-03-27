---
name: quant-agent
description: A股量化交易操作系统主 skill。负责串联盘后计划、审批执行、对账和收盘复盘的 P0 工作流。
---

# Quant Agent Skill

A 股量化交易操作系统的编排入口。当前阶段暴露 `P0` 工作流，其中 `plan_only` 已接入真实 `adata` 研究链路；复杂策略和实盘执行仍保持解耦。

## 当前能力

- **盘后计划**：通过 `adata` 生成结构化候选计划并落库
- **审批执行**：人工确认门控、订单状态机
- **对账复盘**：成交对账、计划差异摘要
- **工作流编排**：统一从 `src.agent.orchestrator` 进入

## P0 入口

```python
from src.agent.orchestrator import run_p0_cycle

result = run_p0_cycle(mode="plan_only")
```

## 使用方式

```
用户: "先跑盘后计划"
Agent: 调用 P0 orchestration → 使用 `adata` 拉取研究数据 → 生成计划并返回 planning / execution / review 三段状态

用户: "今天只看计划，不执行"
Agent: 以 `plan_only` 模式运行，跳过执行链
```

## 配置文件

- `config/default.yaml`
- `config/account.yaml.example`
- `config/strategy.yaml`

## 后续扩展

后续 `P1/P2` 将把：
- `xtdata / xtquant` 真正接入 orchestrator
- 候选池筛选扩展到 `MX_StockPick / pywencai`
- 盘中轻监控与收盘复盘接入完整工作流
