from typing import List

from slack_sdk.models.blocks import Block, Option, OptionGroup

from utils import utc_offset_to_common_timezone


class Blocks:
    def __init__(self, blocks: List[Block]):
        self.blocks = blocks

    def __iter__(self):
        return iter(self.blocks)


class WeekdayOptionsMixin:
    working_days_options = [
        Option(value="1", text="Monday"),
        Option(value="2", text="Tuesday"),
        Option(value="4", text="Wednesday"),
        Option(value="8", text="Thursday"),
        Option(value="16", text="Friday"),
        Option(value="32", text="Saturday"),
        Option(value="64", text="Sunday"),
    ]

    @classmethod
    def to_working_days_option(cls, working_day_magic: int):
        working_day_magic = int(working_day_magic)
        for day in cls.working_days_options:
            if int(day.value) == working_day_magic:
                return day
        else:
            return None

    @classmethod
    def to_working_days_options(cls, working_day_magics: List[int]) -> List[Option]:
        return [cls.to_working_days_option(m) for m in working_day_magics]


class TimezoneOptionGroupsMixin:
    timezone_option_groups = [
        OptionGroup(
            label=f"UTC{offset}",
            options=[Option(label=tz, value=tz) for tz in tzs],
        )
        for offset, tzs in utc_offset_to_common_timezone().items()
    ]

    @classmethod
    def to_timezone_option(cls, timezone: str):
        for group in cls.timezone_option_groups:
            for option in group.options:
                if option.value == timezone:
                    return option
        else:
            return None
