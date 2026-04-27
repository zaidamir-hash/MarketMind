from __future__ import annotations

import argparse
import sys

from app.db.session import SessionLocal
from app.services.prediction_actuals_service import reconcile_prediction_actuals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reconcile actual prices for matured AI predictions.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reconcile_parser = subparsers.add_parser("reconcile", help="Reconcile matured prediction actual prices.")
    reconcile_parser.add_argument("symbol", nargs="?", help="Optional symbol, for example AAPL.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = reconcile_prediction_actuals(db, symbol=getattr(args, "symbol", None))
        print(
            "SUCCESS: "
            f"scanned={result['scanned']} "
            f"updated={result['updated']} "
            f"remaining={result['remaining']}"
            + (f" symbol={result['symbol']}" if result["symbol"] else "")
        )
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
