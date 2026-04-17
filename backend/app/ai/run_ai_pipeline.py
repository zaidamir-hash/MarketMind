from __future__ import annotations

import argparse
import sys

from app.db.session import SessionLocal
from app.services.ai_service import run_ai_pipeline_for_all_active_assets, run_ai_pipeline_for_asset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the MarketMind AI pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run AI pipeline for one asset.")
    run_parser.add_argument("symbol", help="Ticker symbol, for example AAPL or BTC-USD.")

    subparsers.add_parser("run-all", help="Run AI pipeline for all active assets.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.command == "run":
            result = run_ai_pipeline_for_asset(db, args.symbol)
            print(f"SUCCESS: {result['symbol']} AI pipeline completed.")
            return 0

        summary = run_ai_pipeline_for_all_active_assets(db)
        success_count = sum(1 for item in summary if item["status"] == "SUCCESS")
        print(f"Completed AI pipeline for {len(summary)} assets. Successful: {success_count}.")
        for item in summary:
            print(f"- {item['symbol']}: {item['status']} {item.get('message', '')}".rstrip())
        return 0 if all(item["status"] == "SUCCESS" for item in summary) else 1
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
