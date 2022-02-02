"""
timezone: UTC-12 - UTC+12 -> [0,24] in db
WeekDays: Monday - Sunday -> [0, 6]
"""
from peewee import Model, CharField, PrimaryKeyField, BooleanField, IntegerField, DateTimeField, ForeignKeyField, \
    BitField

from db.database import database_runtime


class BaseModel(Model):
    class Meta:
        database = database_runtime

    id = PrimaryKeyField()


class User(BaseModel):
    slack_uid = CharField(unique=True)


class UserProfile(BaseModel):
    user = ForeignKeyField(User, backref="profile", unique=True)
    timezone = CharField()  # pytz supported timezone chars
    workdays = BitField()
    working_hours_start = DateTimeField()
    working_hours_end = DateTimeField()

    selected_monday = workdays.flag(1)
    selected_tuesday = workdays.flag(2)
    selected_wednesday = workdays.flag(4)
    selected_thursday = workdays.flag(8)
    selected_friday = workdays.flag(16)
    selected_saturday = workdays.flag(32)
    selected_sunday = workdays.flag(64)

    def update_workdays(self, *workdays):
        for workday in workdays:
            self.workdays |= int(workday)

    def to_magics(self):
        res = []
        for i in range(7):
            m = self.workdays & 2 ** i
            if m:
                res.append(m)
        return res


class WeekDays(BaseModel):
    user = ForeignKeyField(User)
    day = IntegerField


class TimeSlot(BaseModel):
    user = ForeignKeyField(User, backref="timeslots")
    type = CharField(choices=[
        "availability",
    ])
    start = DateTimeField()
    end = DateTimeField()
    status_label = CharField(choices=[
        "available",
        "tentative",
        "unavailable",
    ])


class Meeting(BaseModel):
    epoch = IntegerField()
    title = CharField(max_length=100)
    meeting_start = DateTimeField(help_text="In UTC")
    meeting_end = DateTimeField(help_text="In UTC")
    frequency = CharField()


class MeetingParticipant(BaseModel):
    user = ForeignKeyField(User)
    meeting = ForeignKeyField(Meeting)


class MeetingOption(BaseModel):
    meeting = Meeting
    text = CharField
    epoch = IntegerField


class MeetingOptionUser(BaseModel):
    user = User
    checked = BooleanField
