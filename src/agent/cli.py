"""Command line entrypoint for Quant Agent scheduling."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from src.agent.orchestrator import run_p0_cycle


SUPPORTED_MODES = ("plan_only", "manual_execute")
SUPPORTED_BROKER_MODES = ("shadow", "xtquant", "injected")


def _parse_symbols(raw_symbols: str | None) -> list[str] | None:
    if raw_symbols is None:
        return None
    symbols = [item.strip() for item in raw_symbols.split(",") if item.strip()]
    return symbols or None


def _result_exit_code(result: dict[str, object], mode: str) -> int:
    if mode == "plan_only":
        planning = result.get("planning", {})
        if isinstance(planning, dict) and planning.get("status") == "unavailable":
            return 1
        return 0

    execution = result.get("execution", {})
    if isinstance(execution, dict) and execution.get("status") in {"failed", "unavailable"}:
        return 1
    return 0


def _cron_templates(workspace: Path) -> str:
    log_dir = workspace / "data" / "logs"
    plan_log = log_dir / "cron-plan-only.log"
    execute_log = log_dir / "cron-manual-execute.log"

    lines = [
        "# Quant Agent cron template (Asia/Shanghai, Mon-Fri)",
        "# 1) 15:05 plan_only: generate next-day plans and review signals",
        f"5 15 * * 1-5 cd {workspace} && quant-agent run --mode plan_only --output json >> {plan_log} 2>&1",
        "# 2) 09:31 manual_execute: requires explicit approval and disabling kill switch",
        (
            f"31 9 * * 1-5 cd {workspace} && "
            "quant-agent run --mode manual_execute --broker-mode xtquant "
            "--approval-granted --strict-reconcile --no-kill-switch --output json "
            f">> {execute_log} 2>&1"
        ),
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quant-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a single P0 orchestrator cycle.")
    run_parser.add_argument("--mode", choices=SUPPORTED_MODES, default="plan_only")
    run_parser.add_argument("--symbols", help="Comma-separated symbols, e.g. 600000.SH,000001.SZ")
    run_parser.add_argument(
        "--broker-mode",
        choices=SUPPORTED_BROKER_MODES,
        default="shadow",
        help="Broker mode for execution stage.",
    )
    run_parser.add_argument(
        "--approval-granted",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether manual execution approval is granted.",
    )
    run_parser.add_argument(
        "--strict-reconcile",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable strict reconcile checks.",
    )
    run_parser.add_argument(
        "--kill-switch",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable kill switch for execution safety.",
    )
    run_parser.add_argument("--output", choices=("json",), default="json")

    cron_parser = subparsers.add_parser("cron-template", help="Print recommended crontab templates.")
    cron_parser.add_argument(
        "--workspace",
        default=str(Path.cwd()),
        help="Workspace path used in rendered crontab lines.",
    )

    return parser


def _run_command(args: argparse.Namespace) -> int:
    symbols = _parse_symbols(args.symbols)
    result = run_p0_cycle(
        mode=args.mode,
        symbols=symbols,
        broker_mode=args.broker_mode,
        approval_granted=bool(args.approval_granted),
        strict_reconcile=bool(args.strict_reconcile),
        kill_switch=bool(args.kill_switch),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return _result_exit_code(result, mode=args.mode)


def _cron_template_command(args: argparse.Namespace) -> int:
    print(_cron_templates(Path(args.workspace).resolve()))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_command(args)
    if args.command == "cron-template":
        return _cron_template_command(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
