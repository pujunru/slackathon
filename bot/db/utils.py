from peewee import Database, IntegrityError
from db.models import User, UserProfile, WeekDays, TimeSlot
from db.database import use_database


def init_db_if_not(db: Database):
    if not db.table_exists(User):
        db.create_tables(
            [User, UserProfile, WeekDays, TimeSlot]
        )


def create_user(db: Database, user, start_time, end_time, weekdays, timezone, logger):
    try:
        with db.atomic():
            # Attempt to create the user. If the username is taken, due to the
            # unique constraint, the database will raise an IntegrityError.
            user = User.create(
                slack_uid=user)
            UserProfile.create(user=user, timezone=int(timezone))
            for weekday in weekdays:
                WeekDays.create(user=user, day=int(weekday))
            TimeSlot.create(user=user, start=start_time, end=end_time, label="A")
            print("ss")
        return

    except IntegrityError:
        logger.error("User already existed.")
