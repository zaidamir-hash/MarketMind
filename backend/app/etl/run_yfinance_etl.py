from __future__ import annotations

import argparse

from app.db.session import SessionLocal
from app.services.yfinance_etl_service import (
    fetch_prices_for_all_active_assets,
    fetch_prices_for_asset,
    onboard_asset_from_yfinance,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run MarketMind yfinance ETL tasks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    onboard_parser = subparsers.add_parser("onboard", help="Onboard one asset from yfinance.")
    onboard_parser.add_argument("symbol")

    prices_parser = subparsers.add_parser("prices", help="Fetch prices for one asset.")
    prices_parser.add_argument("symbol")
    prices_parser.add_argument("--period", default="5d")
    prices_parser.add_argument("--interval", default="5m")

    prices_all_parser = subparsers.add_parser(
        "prices-all",
        help="Fetch prices for all active assets.",
    )
    prices_all_parser.add_argument("--period", default="5d")
    prices_all_parser.add_argument("--interval", default="5m")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.command == "onboard":
            asset = onboard_asset_from_yfinance(db, args.symbol)
            print(f"SUCCESS: onboarded {asset.symbol} ({asset.asset_id})")
            return 0

        if args.command == "prices":
            rows_inserted = fetch_prices_for_asset(
                db,
                args.symbol,
                period=args.period,
                interval=args.interval,
            )
            print(f"SUCCESS: inserted {rows_inserted} price rows for {args.symbol.upper()}")
            return 0

        if args.command == "prices-all":
            summary = fetch_prices_for_all_active_assets(
                db,
                period=args.period,
                interval=args.interval,
            )
            for item in summary:
                print(f"{item['symbol']}: {item['status']} (rows_inserted={item['rows_inserted']})")
                if item.get("message"):
                    print(f"  message: {item['message']}")
            return 0 if all(item["status"] == "SUCCESS" for item in summary) else 1

        parser.print_help()
        return 1
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
