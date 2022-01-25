from peewee import Model, CharField, PrimaryKeyField, BooleanField, IntegerField, DateTimeField

from db.database import database_runtime


class BaseModel(Model):
    class Meta:
        database = database_runtime

    id = PrimaryKeyField()


class User(BaseModel):
    slack_uid = CharField(unique=True)


class UserProfile(BaseModel):
    pass


class TimeSlot(BaseModel):
    user = User
    start = DateTimeField
    end = DateTimeField
    label = CharField


class Meeting(BaseModel):
    epoch = IntegerField


class MeetingOption(BaseModel):
    meeting = Meeting
    text = CharField
    epoch = IntegerField


class MeetingOptionUser(BaseModel):
    user = User
    checked = BooleanField
