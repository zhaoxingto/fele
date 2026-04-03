from collections.abc import Generator

from sqlalchemy import Connection, create_engine, inspect, text
from sqlalchemy.schema import CreateSchema
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import PlatformBase, TenantBase

is_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    pool_pre_ping=not is_sqlite,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def create_platform_tables() -> None:
    PlatformBase.metadata.create_all(bind=engine)


def ensure_columns(
    connection: Connection,
    table_name: str,
    columns: dict[str, str],
    *,
    schema: str | None = None,
) -> None:
    inspector = inspect(connection)
    existing_columns = {column["name"] for column in inspector.get_columns(table_name, schema=schema)}

    for column_name, definition in columns.items():
        if column_name in existing_columns:
            continue

        if schema and not is_sqlite:
            qualified_table = f'"{schema}"."{table_name}"'
        else:
            qualified_table = f'"{table_name}"'

        connection.execute(text(f"ALTER TABLE {qualified_table} ADD COLUMN {column_name} {definition}"))


def create_tenant_schema(schema_name: str) -> None:
    if is_sqlite:
        with engine.begin() as connection:
            tenant_connection = connection.execution_options(schema_translate_map={"tenant": None})
            TenantBase.metadata.create_all(bind=tenant_connection)
        return

    with engine.begin() as connection:
        connection.execute(CreateSchema(schema_name, if_not_exists=True))
        tenant_connection = connection.execution_options(schema_translate_map={"tenant": schema_name})
        TenantBase.metadata.create_all(bind=tenant_connection)


def set_search_path(connection: Connection, schema_name: str) -> None:
    if is_sqlite:
        return

    connection.execute(text(f'SET search_path TO "{schema_name}", public'))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
