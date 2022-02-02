import datetime
from dataclasses import dataclass
from typing import Union, Optional, Sequence, List

from datetime import tzinfo

from pytz import BaseTzInfo
from slack_sdk.models.blocks import PlainTextObject, Block
from slack_sdk.models.views import View

from db.models import User


@dataclass
class TimeSlotInfo:
    time_slot_id: str  # timeslot.primary_key in db
    start_time: datetime.datetime  # In UTC
    end_time: datetime.datetime   # In UTC
    timezone: BaseTzInfo  # pytz supported timezone str
    available_users: List[User]
    tentative_users: List[User]
    unavailable_users: List[User]


class Modal(View):
    def __init__(self, title: Optional[Union[str, dict, PlainTextObject]],
                 blocks: Optional[Sequence[Union[dict, Block]]], **kwargs):
        super().__init__(
            type="modal",
            title=title,
            blocks=blocks,
            **kwargs
        )


def text(t):
    return {
        "type": "plain_text",
        "text": t,
        "emoji": True
    }


def button(t, action_id, value="click_me_123"):
    return {
        "type": "button",
        "text": text(t),
        "value": value,
        "action_id": action_id
    }


def option(t, value):
    return {
        "text": text(t),
        "value": value
    }


def inputs(id, element, label):
    return {
        "type": "input",
        "block_id": id,
        "element": element,
        "label": text(label)
    }


def actions(elements):
    return {
        "type": "actions",
        "elements": elements
    }

def select_time():
    return {
        "type": "timepicker",
        "initial_time": "12:00",
        "placeholder": text("Select time"),
        "action_id": "timepicker-action"
    }


def checkbox(options):
    return {
        "type": "checkboxes",
        "options": options,
        "action_id": "checkboxes-action"
    }


def static_select(name, options):
    return {
        "type": "static_select",
        # "object_id": name,
        "placeholder": text("Select an item"),
        "options": options,
        "action_id": name
    }


def context(t):
    return {
        "type": "context",
        "elements": [
            text(t)
        ]
    }


def date_picker():
    return {
        "type": "datepicker",
        "initial_date": "2022-01-31",
        "placeholder": {
            "type": "plain_text",
            "text": "Select a date",
            "emoji": True
        },
        "action_id": "datepicker-action"
    }


def select_users():
    return {
        "type": "multi_users_select",
        "placeholder": {
            "type": "plain_text",
            "text": "Select users",
            "emoji": True
        },
        "action_id": "multi_users_select-action"
    }


def radio_button(options):
    return {
        "type": "radio_buttons",
        "options": options,
        "action_id": "radio_buttons-action"
    }


def action_time(index):
    # availability = ["available", "tentative", "unavailable"]
    # return [
    # inputs(f"{index}.from", select_time(), "From"),
    # inputs(f"{index}.to", select_time(), "To"),
    # inputs(f"{index}.availability", static_select("availability", options=[option(availability[i], availability[i]) for i in range(3)]), "availability"),
    # actions(elements=[button("X", f"{index}.X")])]
    return {
        "type": "actions",
        "block_id": f"{index}",
        "elements": [
            {
                "type": "timepicker",
                "initial_time": "14:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select time",
                    "emoji": True
                },
                "action_id": f"{index}.actionId-0"
            },
            {
                "type": "timepicker",
                "initial_time": "15:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select time",
                    "emoji": True
                },
                "action_id": f"{index}.actionId-1"
            },
            {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Status",
                    "emoji": True
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Available",
                            "emoji": True
                        },
                        "value": "Available"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tentative",
                            "emoji": True
                        },
                        "value": "Tentative"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Unavailable",
                            "emoji": True
                        },
                        "value": "Unavailable"
                    }
                ],
                "action_id": f"{index}.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "X",
                    "emoji": True
                },
                "value": str(index),
                "action_id": f"{index}.actionId-3"
            }
        ]
    }


def set_personal_profiles_modal(counter=1):
    week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timezones = [f"UTC{i}" for i in range(-12, 0)] + ["UTC"] + [f"UTC+{i}" for i in range(1, 13)]

    result = {
        "type": "modal",
        "callback_id": "personal_profile",
        "title": text("My availability"),
        "submit": text("Submit"),
        "close": text("Cancel"),
        "blocks": [
            {
                "type": "divider"
            },
            inputs("timezone", static_select("timezone", options=[option(timezones[i], str(i)) for i in range(25)]), "Timezone"),
            inputs("working_days", checkbox(options=[option(week[i], str(i)) for i in range(7)]), "Working Days"),
            inputs("working_hours_start", select_time(), "Working Hours"),
            inputs("working_hours_end", select_time(), "-"),
            context("Availability"),
            context("From  -  To  -  Status")
        ]
    }
    for i in range(counter):
        result["blocks"].append(action_time(i))
    result["blocks"].append(actions(elements=[
        button(t="Add a time", action_id="add_available_time", value="add_available_time")]))
    return result


def plain_text_input():
    return {
        "type": "plain_text_input",
        "action_id": "plain_text_input-action"
    }


def create_meeting_modal(organizer, picked_times, default="Suggest a time"):
    importance = ["High", "Middle", "Low"]
    return {
        "type": "modal",
        "callback_id": "create_meeting",
        "title": text("Create a meeting"),
        "submit": text(default),
        "close": text("Cancel"),
        "blocks": [
            context("Arrange a meeting between members."),
            {
                "type": "divider"
            },
            inputs("title", plain_text_input(), "Title"),
            inputs("date", date_picker(), "Date"),
            inputs("select_users", select_users(), "Participants"),
            inputs("meeting_time", static_select("meeting_time", options=[option(picked_times[i], picked_times[i]) for i in range(len(picked_times))]), "Meeting time"),
            inputs("priority", radio_button(options=[option(importance[i], str(i)) for i in range(3)]), "Priority"),
            context(f"Organized by @{organizer}")
        ]
    }


def update_availability_modal():
    week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return {
        "type": "modal",
        "callback_id": "update_availability",
        "title": text("Update your availability"),
        "submit": text("Update"),
        "close": text("Cancel"),
        "blocks": [
            {
                "type": "divider"
            },
            inputs("working_days", checkbox(options=[option(week[i], str(i)) for i in range(7)]), "Working Days"),

        ]
    }


def home_modal():
    timezones = [f"UTC{i}" for i in range(-12, 0)] + ["UTC"] + [f"UTC+{i}" for i in range(1, 13)]
    return {
        "type": "home",
        "callback_id": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Smart meeting-time schedule app."
                }
            },
            {
                "type": "divider"
            },

            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": " "
                },
                "accessory": button(t="Update my availability", action_id="set_personal_profiles", value="set_personal_profiles")
            },
            inputs("timezone", static_select("timezone_1", options=[option(timezones[i], str(i)) for i in range(25)]), "Timezone"),
            actions(elements=[
                {
                    "type": "datepicker",
                    "initial_date": "2022-01-31",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True
                    },
                    "action_id": "10.actionId-0"
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Status",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Available",
                                "emoji": True
                            },
                            "value": "Available"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Tentative",
                                "emoji": True
                            },
                            "value": "Tentative"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Unavailable",
                                "emoji": True
                            },
                            "value": "Unavailable"
                        }
                    ],
                    "action_id": "9.actionId-2"
                },
                button("submit", "10.actionId-2", "submit")
            ])
        ]
    }
