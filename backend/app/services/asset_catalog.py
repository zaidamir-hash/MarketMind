from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "demo_asset_universe.json"


@lru_cache
def load_demo_asset_universe() -> dict[str, Any]:
    with CATALOG_PATH.open("r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def list_demo_asset_categories() -> list[dict[str, Any]]:
    return list(load_demo_asset_universe().get("categories", []))


def list_demo_asset_options() -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for category in list_demo_asset_categories():
        options.extend(category.get("options", []))
    return options


def get_demo_universe_symbols() -> list[str]:
    return [option["symbol"] for option in list_demo_asset_options()]
