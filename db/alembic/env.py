import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None

# DATABASE_URL is the ONLY source of the connection URL (#312). alembic.ini used to
# carry a fallback with an inline password; in a public repo that is a committed
# credential, and nothing read it — every deployment path sets DATABASE_URL from a
# secret. Failing explicitly here beats connecting to a hardcoded default, and beats
# the opaque `None`-typed error alembic would otherwise raise several frames later.
database_url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not set and alembic.ini defines no sqlalchemy.url.\n"
        "Set it before running migrations, e.g.\n"
        "  export DATABASE_URL='postgresql://architect:<password>@localhost:5432/architect'\n"
        "In-cluster this is supplied by k8s/base/migration-job.yaml from the secret."
    )
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
