"""Alembic utils for tests."""

import os
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import URL
from starlette.concurrency import run_in_threadpool

PROJECT_PATH = Path(__file__).parent.parent.parent.resolve()


def make_alembic_config(
    cmd_opts: Namespace | SimpleNamespace, base_path: str = str(PROJECT_PATH)
) -> Config:
    """Make alembic config for stairway integration tests."""
    # Replace path to alembic.ini file to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(
        file_=cmd_opts.config,
        ini_section=cmd_opts.name,
        cmd_opts=cmd_opts,  # type: ignore[arg-type]
    )

    # Replace path to alembic folder to absolute
    alembic_location = config.get_main_option("script_location")
    assert alembic_location is not None
    if not os.path.isabs(alembic_location):
        config.set_main_option(
            "script_location", os.path.join(base_path, alembic_location)
        )
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url: URL | str | None = None) -> Config:
    """Provides Python object, representing alembic.ini file."""
    if isinstance(pg_url, URL):
        pg_url = pg_url.render_as_string(hide_password=False)
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_url=pg_url,
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options)


async def alembic_upgrade_head(config: Config) -> None:
    revisions_dir = ScriptDirectory.from_config(config)
    if revisions_dir.get_current_head():
        await run_in_threadpool(
            alembic_upgrade,
            config,
            revisions_dir.get_current_head(),  # type: ignore[arg-type]
        )  # noqa
