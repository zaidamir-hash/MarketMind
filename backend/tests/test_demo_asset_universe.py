from app.services.asset_catalog import load_demo_asset_universe


def test_demo_asset_universe_has_expected_shape() -> None:
    catalog = load_demo_asset_universe()
    categories = catalog["categories"]

    assert len(categories) == 5
    assert sum(1 for category in categories if category["is_crypto"]) == 1
    assert sum(1 for category in categories if category["country"] == "Pakistan") == 4

    symbols = [
        option["symbol"]
        for category in categories
        for option in category["options"]
    ]

    assert all(len(category["options"]) == 10 for category in categories)
    assert len(symbols) == 50
    assert len(set(symbols)) == 50
