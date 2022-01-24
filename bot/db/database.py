from peewee import Database, DatabaseProxy, SqliteDatabase

database_runtime = DatabaseProxy()


def use_database(db: Database):
    database_runtime.initialize(db)


def new_sqlite_database(db_name: str) -> SqliteDatabase:
    return SqliteDatabase(
        db_name, pragmas={
            'journal_mode': 'wal',
            'cache_size': -1 * 64000,  # 64MB
            'foreign_keys': 1,
            'ignore_check_constraints': 0,
            'synchronous': 0}
    )
