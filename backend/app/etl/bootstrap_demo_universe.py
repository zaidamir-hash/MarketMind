from __future__ import annotations

from app.db.session import SessionLocal
from app.services.ai_service import run_ai_pipeline_for_asset
from app.services.asset_catalog import list_demo_asset_categories
from app.services.risk_indicator_service import compute_risk_indicators_for_asset
from app.services.yfinance_etl_service import (
    fetch_prices_for_asset,
    onboard_asset_from_yfinance,
)


def bootstrap_demo_universe() -> int:
    summary: list[dict[str, object]] = []
    db = SessionLocal()

    try:
        for category in list_demo_asset_categories():
            for option in category.get("options", []):
                symbol = option["symbol"]
                result: dict[str, object] = {
                    "category": category["category_label"],
                    "symbol": symbol,
                    "status": "SUCCESS",
                    "message": "Curated demo asset prepared successfully.",
                    "daily_rows": 0,
                    "intraday_rows": 0,
                }

                try:
                    onboard_asset_from_yfinance(db, symbol)
                    result["onboard"] = "SUCCESS"
                except Exception as exc:
                    result["status"] = "FAIL"
                    result["message"] = f"Onboarding failed: {exc}"
                    result["onboard"] = "FAIL"
                    summary.append(result)
                    continue

                try:
                    daily_rows = fetch_prices_for_asset(db, symbol, period="1y", interval="1d")
                    result["daily_prices"] = "SUCCESS"
                    result["daily_rows"] = daily_rows
                except Exception as exc:
                    result["status"] = "FAIL"
                    result["message"] = f"Daily price fetch failed: {exc}"
                    result["daily_prices"] = "FAIL"
                    summary.append(result)
                    continue

                try:
                    intraday_rows = fetch_prices_for_asset(db, symbol, period="5d", interval="5m")
                    result["intraday_prices"] = "SUCCESS"
                    result["intraday_rows"] = intraday_rows
                except Exception as exc:
                    result["intraday_prices"] = "FAIL"
                    result["intraday_message"] = str(exc)

                try:
                    compute_risk_indicators_for_asset(db, symbol)
                    result["risk"] = "SUCCESS"
                except Exception as exc:
                    result["status"] = "FAIL"
                    result["message"] = f"Risk computation failed: {exc}"
                    result["risk"] = "FAIL"
                    summary.append(result)
                    continue

                try:
                    run_ai_pipeline_for_asset(db, symbol)
                    result["ai"] = "SUCCESS"
                except Exception as exc:
                    result["status"] = "FAIL"
                    result["message"] = f"AI pipeline failed: {exc}"
                    result["ai"] = "FAIL"

                summary.append(result)
    finally:
        db.close()

    success_count = sum(1 for row in summary if row["status"] == "SUCCESS")
    fail_count = len(summary) - success_count

    print("Bootstrapping MarketMind curated demo universe...")
    print(f"Categories: {len(list_demo_asset_categories())}")
    print(f"Assets processed: {len(summary)}")
    print(f"Successful assets: {success_count}")
    print(f"Failed assets: {fail_count}")

    for row in summary:
        status = row["status"]
        symbol = row["symbol"]
        message = row["message"]
        print(f"[{status}] {symbol}: {message}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(bootstrap_demo_universe())
