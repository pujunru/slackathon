from peewee import Database

from db.models import User


def init_db_if_not(db: Database):
    if not db.table_exists(User):
        db.create_tables(
            User,
        )
