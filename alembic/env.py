"""Alembic environment config"""

import os
from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context

from dotenv import load_dotenv

from agritechtz.models import Base

# pylint:disable=no-member

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment
DATABASE_URL = os.getenv("DATABASE_SYNC_URL")

# Interpret the config file for Python logging.
config = context.config

# Set the SQLAlchemy URL from the DATABASE_URL environment variable
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configure logging
fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
