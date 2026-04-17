from __future__ import annotations

import argparse
import sys

from app.db.session import SessionLocal
from app.services.risk_indicator_service import (
    compute_risk_indicators_for_all_active_assets,
    compute_risk_indicators_for_asset,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run MarketMind risk indicator ETL jobs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compute_parser = subparsers.add_parser("compute", help="Compute risk indicators for one asset.")
    compute_parser.add_argument("symbol", help="Ticker symbol, for example AAPL or BTC-USD.")

    subparsers.add_parser("compute-all", help="Compute risk indicators for all active assets.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.command == "compute":
            indicator = compute_risk_indicators_for_asset(db, args.symbol)
            print(
                f"SUCCESS: computed risk indicators for {args.symbol.strip().upper()} "
                f"at {indicator.computed_at.isoformat()}."
            )
            return 0

        summary = compute_risk_indicators_for_all_active_assets(db)
        success_count = sum(1 for item in summary if item["status"] == "SUCCESS")
        print(f"Completed risk indicator batch for {len(summary)} assets. Successful: {success_count}.")
        for item in summary:
            symbol = item["symbol"]
            status_text = item["status"]
            message = item.get("message") or ""
            print(f"- {symbol}: {status_text} {message}".rstrip())
        return 0 if all(item["status"] == "SUCCESS" for item in summary) else 1
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
