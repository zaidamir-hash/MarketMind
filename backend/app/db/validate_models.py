"""Validate ORM table names against the existing MarketMind schema."""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db import Base
from app.db import models as _models  # noqa: F401
from app.db.session import engine


EXPECTED_TABLE_COUNT = 14
SCHEMA_NAME = "marketmind"


def main() -> int:
    expected_tables = sorted(
        table.name for table in Base.metadata.sorted_tables if table.schema == SCHEMA_NAME
    )

    try:
        with engine.connect() as connection:
            actual_tables = sorted(
                connection.execute(
                    text(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = :schema_name
                          AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                        """
                    ),
                    {"schema_name": SCHEMA_NAME},
                ).scalars()
            )
    except SQLAlchemyError as exc:
        print("FAIL: could not validate models against the database.")
        print(f"Error: {exc.__class__.__name__}: {exc}")
        return 1

    expected_set = set(expected_tables)
    actual_set = set(actual_tables)
    missing_tables = sorted(expected_set - actual_set)
    extra_tables = sorted(actual_set - expected_set)

    print("Expected ORM tables:")
    for table_name in expected_tables:
        print(f"- {table_name}")

    print("")
    print("Actual database tables:")
    for table_name in actual_tables:
        print(f"- {table_name}")

    print("")
    print(f"Expected ORM table count: {len(expected_tables)}")
    print(f"Actual database table count: {len(actual_tables)}")

    if missing_tables:
        print("")
        print("Missing tables in database:")
        for table_name in missing_tables:
            print(f"- {table_name}")

    if extra_tables:
        print("")
        print("Extra known schema tables in database:")
        for table_name in extra_tables:
            print(f"- {table_name}")

    table_count_matches = len(expected_tables) == EXPECTED_TABLE_COUNT == len(actual_tables)
    if missing_tables or extra_tables or not table_count_matches:
        print("")
        print("FAIL: ORM models do not match the database table set exactly.")
        return 1

    print("")
    print("PASS: ORM models match the 14 base tables in schema 'marketmind'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
