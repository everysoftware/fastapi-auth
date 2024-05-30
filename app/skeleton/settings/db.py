from abc import ABC

from sqlalchemy import URL

from .url import ConnectionUrl


class DatabaseServer(ConnectionUrl, ABC):
    dialect: str
    sync_driver: str
    async_driver: str

    def get_dsn(self, db: str, sync: bool = True) -> str:
        driver = self.sync_driver if sync else self.async_driver
        return URL.create(
            drivername=f"{self.dialect}+{driver}",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=db,
        ).render_as_string(hide_password=False)


class PgServer(DatabaseServer):
    dialect: str = "postgresql"
    sync_driver: str = "psycopg2"
    async_driver: str = "asyncpg"


class Database(DatabaseServer):
    db: str

    @property
    def sync_dsn(self) -> str:
        return super().get_dsn(self.db)

    @property
    def async_dsn(self) -> str:
        return super().get_dsn(self.db, sync=False)


class Postgres(PgServer, Database):
    pass
