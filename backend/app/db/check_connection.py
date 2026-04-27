from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlsplit, urlunsplit

from app.core.config import get_settings
from app.db.session import engine


def redact_database_url(database_url: str) -> str:
    parsed = urlsplit(database_url)
    if parsed.password is None:
        return database_url

    username = parsed.username or ""
    host = parsed.hostname or ""
    netloc = f"{username}:***@{host}"
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"

    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def main() -> int:
    settings = get_settings()

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).scalar_one()
            schema_exists = connection.execute(
                text(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.schemata
                        WHERE schema_name = 'marketmind'
                    )
                    """
                )
            ).scalar_one()
    except SQLAlchemyError as exc:
        print("Database connection check failed.")
        print(f"Database URL: {redact_database_url(settings.DATABASE_URL)}")
        print(f"Error: {exc.__class__.__name__}: {exc}")
        return 1

    if not schema_exists:
        print("Database connected, but schema 'marketmind' was not found.")
        return 1

    print("Database connection check passed.")
    print("SELECT 1 succeeded.")
    print("Schema 'marketmind' exists.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
