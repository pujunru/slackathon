"""
timezone: UTC-12 - UTC+12 -> [0,24] in db
WeekDays: Monday - Sunday -> [0, 6]
"""
from peewee import Model, CharField, PrimaryKeyField, BooleanField, IntegerField, DateTimeField, ForeignKeyField

from db.database import database_runtime


class BaseModel(Model):
    class Meta:
        database = database_runtime

    id = PrimaryKeyField()


class User(BaseModel):
    slack_uid = CharField(unique=True)


class UserProfile(BaseModel):
    user = ForeignKeyField(User)
    timezone = IntegerField


class WeekDays(BaseModel):
    user = ForeignKeyField(User)
    day = IntegerField


class TimeSlot(BaseModel):
    user = ForeignKeyField(User)
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
