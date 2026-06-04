import sqlite3
import threading
from pathlib import Path


DB_PATH = (
    Path(__file__)
    .resolve()
    .parent
    / "cosmo.db"
)


class Database:

    def __init__(self):

        self.lock = threading.Lock()
        self.path = DB_PATH
        self.connection = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self._configure()

    def _configure(self):

        with self.lock:

            cursor = self.connection.cursor()

            cursor.execute(
                "PRAGMA foreign_keys = ON;"
            )

            cursor.execute(
                "PRAGMA journal_mode = WAL;"
            )

            cursor.execute(
                "PRAGMA synchronous = NORMAL;"
            )

            self.connection.commit()

    def execute(
        self,
        query,
        params=()
    ):

        with self.lock:

            cursor = self.connection.cursor()

            cursor.execute(
                query,
                params
            )

            self.connection.commit()

            return cursor

    def fetchone(
        self,
        query,
        params=()
    ):

        with self.lock:

            cursor = self.connection.cursor()

            cursor.execute(
                query,
                params
            )

            return cursor.fetchone()

    def fetchall(
        self,
        query,
        params=()
    ):

        with self.lock:

            cursor = self.connection.cursor()

            cursor.execute(
                query,
                params
            )

            return cursor.fetchall()


db = Database()