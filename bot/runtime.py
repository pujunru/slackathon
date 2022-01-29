from peewee import Database


class SlackBotRuntime:
    def __init__(self, db: Database):
        self._db = db

    @property
    def db(self) -> Database:
        return self._db

    @db.setter
    def db(self, database: Database):
        return
