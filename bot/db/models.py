from peewee import Model, CharField, PrimaryKeyField

from db.database import database_runtime


class BaseModel(Model):
    class Meta:
        database = database_runtime

    id = PrimaryKeyField()


class User(BaseModel):
    slack_uid = CharField(unique=True)
