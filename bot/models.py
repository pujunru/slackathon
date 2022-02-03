import datetime
from dataclasses import dataclass
from typing import Union, Optional, Sequence, List
from datetime import tzinfo

from pytz import BaseTzInfo
from slack_sdk.models.blocks import PlainTextObject, Block, ButtonElement, ActionsBlock
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
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Availability*\nFrom  -  To  -  Status"
                }
            },
            action_time(0),
            actions(elements=[
                button(t="Add a time", action_id="add_available_time", value="add_available_time")]),

            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": " "
                },
                "accessory": {
                    "type": "button",
                    # "style": "primary",
                    "text": {
                        "type": "plain_text",
                        "text": "Update",
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "action_id": "75.actionId-2"
                }
            }
        ]
    }
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
                },ButtonElement(
                    text="submit",
                    style="primary",
                    action_id="10.actionId-2",
                )
            ])
        ]
    }


def hardcode_available():
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":white_check_mark:*Available*"
        }
    },{
        "type": "actions",
        "block_id": f"11.actionId-2",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "10:00a.m. - 10:30a.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"12.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "10:30a.m. - 11:00a.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"13.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "11:00a.m. - 11:30a.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"14.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "11:30a.m. - 12:00p.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"15.actionId-2"
            }
        ]
    },
    {
        "type": "actions",
        "block_id": f"24.actionId-2",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "12:00p.m. - 12:30p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"16.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "12:30p.m. - 01:00p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"17.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "02:00p.m. - 02:30p.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"18.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "02:30p.m. - 03:00p.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"19.actionId-2"
            }
        ]
    },
    {
        "type": "actions",
        "block_id": f"25.actionId-2",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "03:00p.m. - 03:30p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"20.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "03:30p.m. - 04:00p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"21.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "04:30p.m. - 05:00p.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"22.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "05:30p.m. - 06:00p.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"23.actionId-2"
            }

        ]
    }]


def hardcode_tentative():
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":thinking_face:*Tentative*"
        }
    },{
        "type": "actions",
        "block_id": f"30.actionId-2",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "01:00p.m. - 01:30.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"31.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "01:30p.m. - 02:00p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"32.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "05:00p.m. - 05:30p.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"33.actionId-2"
            }
        ]
    }]


def hardcode_unavailable():
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":x:*Unavailable*"
        }
    },{
        "type": "actions",
        "block_id": f"40.actionId-2",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "11:30a.m. - 12:00p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"41.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "04:00p.m. - 04:30p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"42.actionId-2"
            }]
    }]


def hardcode():
    return[*hardcode_available(),
    *hardcode_tentative(),
    *hardcode_unavailable()]


def hardcode_available_after():
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":white_check_mark:*Available*"
        }
    },{
        "type": "actions",
        "block_id": f"11.actionId-2",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "10:00a.m. - 10:30a.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"12.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "10:30a.m. - 11:00a.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"13.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "11:00a.m. - 11:30a.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"14.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "11:30a.m. - 12:00p.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"15.actionId-2"
            }
        ]
    },
        {
            "type": "actions",
            "block_id": f"24.actionId-2",
            "elements": [

                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "02:00p.m. - 02:30p.m.",
                        "emoji": True
                    },
                    "value":  " ",
                    "action_id": f"18.actionId-2"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "02:30p.m. - 03:00p.m.",
                        "emoji": True
                    },
                    "value":  " ",
                    "action_id": f"19.actionId-2"
                }
            ]
        },
        {
            "type": "actions",
            "block_id": f"25.actionId-2",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "03:00p.m. - 03:30p.m.",
                        "emoji": True
                    },
                    "value": " ",
                    "action_id": f"20.actionId-2"
                },

                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "04:30p.m. - 05:00p.m.",
                        "emoji": True
                    },
                    "value":  " ",
                    "action_id": f"22.actionId-2"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "05:30p.m. - 06:00p.m.",
                        "emoji": True
                    },
                    "value":  " ",
                    "action_id": f"23.actionId-2"
                }

            ]
        }]


def hardcode_tentative_after():
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":thinking_face:*Tentative*"
        }
    },{
        "type": "actions",
        "block_id": f"30.actionId-2",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "01:00p.m. - 01:30.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"31.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "01:30p.m. - 02:00p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"32.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "03:30p.m. - 04:00p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"21.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "05:00p.m. - 05:30p.m.",
                    "emoji": True
                },
                "value":  " ",
                "action_id": f"33.actionId-2"
            }
        ]
    }]


def hardcode_unavailable_after():
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":x:*Unavailable*"
        }
    },{
        "type": "actions",
        "block_id": f"40.actionId-2",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "11:30a.m. - 12:00p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"41.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "12:00p.m. - 12:30p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"16.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "12:30p.m. - 01:00p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"17.actionId-2"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "04:00p.m. - 04:30p.m.",
                    "emoji": True
                },
                "value": " ",
                "action_id": f"42.actionId-2"
            }]
    }]


def hardcode_after():
    return[*hardcode_available_after(),
           *hardcode_tentative_after(),
           *hardcode_unavailable_after()]


def hardcode_meeting():
    return [{
            "type": "divider"
        },{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Weekly Sync*"
        }},context("11:30AM - 12:00PM"),
        context("02/04/2022"),{
            "type": "actions",
            "block_id": f"54.actionId-2",
            "elements": [
                {
                    "type": "button",
                    "style": "primary",
                    "text": {
                        "type": "plain_text",
                        "text": "Yes",
                        "emoji": True
                    },
                    "value": " ",
                    "action_id": f"53.actionId-2"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Maybe",
                        "emoji": True
                    },
                    "value": " ",
                    "action_id": f"52.actionId-2"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "No",
                        "emoji": True
                    },
                    "value": " ",
                    "action_id": f"51.actionId-2"
                }]},{
            "type": "divider"
        }
    ]

def hardcode_message_meeting(user):
    return {"blocks":[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<@{user}> scheduled a meeting\n"
                        f"\tMonday, February 8, 2022\n"
                        f"\tTeam check-in for *Weekly Sync*\n"
                        f"\t10:30AM - 11:00AM (Pacific Time - Los Angeles"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\t*Going?*"
            }
        },{
            "type": "actions",
            "block_id": f"54.actionId-2",
            "elements": [
                {
                    "type": "button",
                    "style": "primary",
                    "text": {
                        "type": "plain_text",
                        "text": "Yes",
                        "emoji": True
                    },
                    "value": " ",
                    "action_id": f"63.actionId-2"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Maybe",
                        "emoji": True
                    },
                    "value": " ",
                    "action_id": f"62.actionId-2"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "No",
                        "emoji": True
                    },
                    "value": " ",
                    "action_id": f"61.actionId-2"
                }]},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\t*Status*"
            }
        },
        context("\t:white_check_mark: Confirm: @Jiazhen Zhao\n\t:x: Not coming:\n\t:question: Maybe: @Adam\n\t:grey_question: Waiting for response: @Mandy, @Alan, @Doris")
    ]}