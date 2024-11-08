from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Added

# Load environment variables
load_dotenv()

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
  fileConfig(config.config_file_name)  # Corrected line

# Add your model's MetaData object here for 'autogenerate' support
from app.models.base import Base
target_metadata = Base.metadata

# Override sqlalchemy.url with environment variable
def get_url():
  return os.getenv(
      "DATABASE_URL",
      "postgresql://user:password@db:5432/divergesapp"
  )

def run_migrations_offline() -> None:
  url = get_url()
  context.configure(
      url=url,
      target_metadata=target_metadata,
      literal_binds=True,
      dialect_opts={"paramstyle": "named"},
  )

  with context.begin_transaction():
      context.run_migrations()

def run_migrations_online() -> None:
  configuration = config.get_section(config.config_ini_section)
  configuration["sqlalchemy.url"] = get_url()
  connectable = engine_from_config(
      configuration,
      prefix="sqlalchemy.",
      poolclass=pool.NullPool,
  )

  with connectable.connect() as connection:
      context.configure(
          connection=connection, 
          target_metadata=target_metadata
      )

      with context.begin_transaction():
          context.run_migrations()

if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
