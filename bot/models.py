from typing import Union, Optional, Sequence

from slack_sdk.models.blocks import PlainTextObject, Block
from slack_sdk.models.views import View


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


def static_select(options):
    return {
        "type": "static_select",
        "placeholder": text("Select an item"),
        "options": options,
        "action_id": "static_select-action"
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


def set_personal_profiles_modal():
    week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timezones = [f"UTC{i}" for i in range(-12, 0)] + ["UTC"] + [f"UTC+{i}" for i in range(1, 13)]
    return {
        "type": "modal",
        "callback_id": "personal_profile",
        "title": text("Set your profile"),
        "submit": text("Create"),
        "close": text("Cancel"),
        "blocks": [
            {
                "type": "divider"
            },
            inputs("working_hours_start", select_time(), "Working Hours"),
            inputs("working_hours_end", select_time(), "-"),
            inputs("working_days", checkbox(options=[option(week[i], str(i)) for i in range(7)]), "Working Days"),
            inputs("timezone", static_select(options=[option(timezones[i], str(i)) for i in range(25)]), "Timezone"),
            context("\nYou can always update your profile later.")
        ]
    }


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
            inputs("meeting_time", static_select(options=[option(picked_times[i], picked_times[i]) for i in range(len(picked_times))]), "Meeting time"),
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
    return {
        "type": "home",
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
            actions(elements=[
                button(t="Set Personal Profile", action_id="set_personal_profiles", value="set_personal_profiles"),
                button(t="Update Availability", action_id="update_availability", value="update_availability"),
                button(t="New Meeting", action_id="new_meeting", value="new_meeting"),
            ])
        ]
    }
