from peewee import Database, DatabaseProxy, SqliteDatabase, MySQLDatabase
from playhouse.db_url import connect

database_runtime = DatabaseProxy()


def use_database(db: Database):
    database_runtime.initialize(db)


def conn_sqlite_database(db_name: str) -> SqliteDatabase:
    return SqliteDatabase(
        db_name, pragmas={
            'journal_mode': 'wal',
            'cache_size': -1 * 64000,  # 64MB
            'foreign_keys': 1,
            'ignore_check_constraints': 0,
            'synchronous': 0}
    )


def conn_mysql_database(db_url: str) -> MySQLDatabase:
    db = connect(db_url)

    # Boldly assume connect will make Mysql connection
    assert type(db) is MySQLDatabase
    return db
