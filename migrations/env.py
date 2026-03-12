# Alembic configuration
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.models.base import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata
