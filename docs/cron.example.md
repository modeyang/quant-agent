# Quant Agent Cron Examples

本文档给出 `quant-agent` CLI 的最小可上线 crontab 模板，分为：

- `plan_only`：盘后生成候选计划，不触发下单
- `manual_execute`：盘中执行（需显式审批参数）

## 1) 生成模板

在仓库根目录执行：

```bash
quant-agent cron-template --workspace "$(pwd)"
```

## 2) 推荐 crontab（Asia/Shanghai）

示例假设仓库路径为 `/opt/quant-agent`：

```cron
# 1) 15:05 工作日盘后，生成 next-day 计划
5 15 * * 1-5 cd /opt/quant-agent && quant-agent run --mode plan_only --output json >> /opt/quant-agent/data/logs/cron-plan-only.log 2>&1

# 2) 09:31 工作日盘中，手动执行模式（显式审批 + 严格对账 + 关闭 kill switch）
31 9 * * 1-5 cd /opt/quant-agent && quant-agent run --mode manual_execute --broker-mode xtquant --approval-granted --strict-reconcile --no-kill-switch --output json >> /opt/quant-agent/data/logs/cron-manual-execute.log 2>&1
```

## 3) 运行前检查

- 确保 `quant-agent` 已通过 `pip install -e .` 安装到目标 Python 环境
- 确保 `config/account.yaml` 与执行端依赖（如 `xtquant`）在运行环境可用
- 首次上线建议先只启用 `plan_only` cron，确认日志与数据落库后再启用执行 cron
