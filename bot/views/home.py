import datetime
from typing import List

from slack_sdk.models.blocks import *
from slack_sdk.models.views import View

from views.commons import Blocks, WeekdayOptionsMixin
from models import button, inputs, static_select, option, hardcode, hardcode_after, hardcode_meeting

class HomeMyAvailabilityView(Blocks):
    def __init__(self, filter_availability_result: Blocks = None):
        timezones = [f"UTC{i}" for i in range(-12, 0)] + ["UTC"] + [f"UTC+{i}" for i in range(1, 13)]
        _blocks = [
            HeaderBlock(text=PlainTextObject(text="My availability")),
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": " "
                },
                "accessory":
                    ButtonElement(
                    text="Update my availability",
                    style="primary",
                    action_id="set_personal_profiles",
                ),
            },
            inputs("timezone", static_select("timezone_1", options=[option(timezones[i], str(i)) for i in range(25)]), "Timezone"),
            # SectionBlock(
            #     text=PlainTextObject(text="<placeholder>"),
            #     accessory=ButtonElement(
            #         text=PlainTextObject(text="Edit your availability"),
            #         action_id="home_edit_availability_but_clicked"
            #     )
            # ),
            ActionsBlock(
                elements=[
                    DatePickerElement(
                        initial_date=datetime.date.today().strftime("%Y-%m-%d")
                    ),
                    StaticSelectElement(
                        placeholder=PlainTextObject(text="Filter by status"),
                        options=[
                            Option(value="Available", text="Available"),
                            Option(value="Tentative", text="Tentative"),
                            Option(value="Unavailable", text="Unavailable"),
                        ]
                    ),ButtonElement(
                        text="Submit",
                        style="primary",
                        action_id="10.actionId-2",
                    )
                ]
            ),
        ]

        if filter_availability_result:
            _blocks = [
                *_blocks,
                *filter_availability_result,
            ]

        super().__init__(
            blocks=_blocks,
        )


class HomeEditAvailabilityModal(View, WeekdayOptionsMixin):
    def __init__(self,
                 blks=None,
                 state=None,
                 selected_weekday_magic: int = None,
                 working_days: List[int] = None):
        super().__init__(
            type="modal",
            title="Edit your availability",
            state=state if state else None,
            blocks=blks if blks else [
                SectionBlock(
                    text=MarkdownTextObject(text="*Working Days*")
                ),
                ActionsBlock(
                    elements=[StaticSelectElement(
                        placeholder="Select a day you want to edit",
                        action_id="user_edit_availability_weekday_selected",
                        options=self.working_days_options if not working_days else self.to_working_days_options(
                            working_days),
                        initial_option=self.to_working_days_option(
                            selected_weekday_magic) if selected_weekday_magic else None,
                    )]),
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text="*My available time slots*"),
                ),
                ActionsBlock(
                    elements=[
                        TimePickerElement(action_id="user_edit_availability_available_time_start", placeholder="From"),
                        TimePickerElement(action_id="user_edit_availability_available_time_end", placeholder="To"),
                        StaticSelectElement(
                            action_id="user_edit_availability_available_time_status",
                            placeholder=PlainTextObject(text="Filter by status"),
                            options=[
                                Option(value="Available", text="Available"),
                                Option(value="Tentative", text="Tentative"),
                                Option(value="Unavailable", text="Unavailable"),
                            ]
                        ),
                    ]
                ),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            action_id="user_edit_availability_add_time_clicked",
                            text="Add time",
                        ),
                        ButtonElement(
                            style='primary',
                            action_id="user_edit_availability_update_time_clicked",
                            text=f"Update{' ' + self.to_working_days_option(selected_weekday_magic).text if selected_weekday_magic else ''}",
                        ),
                    ]
                )
            ]
        )


class HomeView(View):
    def __init__(self, before=True):
        tmp = hardcode() if before else hardcode_after()
        super().__init__(
            external_id="home",
            type="home",
            callback_id="home",
            blocks=[
                HeaderBlock(
                    text=PlainTextObject(text=":wave: Hey! Welcome to AlignUp.")
                ),
                SectionBlock(
                    text="We make meeting scheduling simple and intuitive for global distributed teams.",
                ),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text="Schedule a meeting",
                            style="primary",
                            action_id="home_header_schedule_meeting",
                        ),
                        ButtonElement(
                            text="Edit a meeting",
                            action_id="home_header_edit_meeting",
                        ),
                        OverflowMenuElement(
                            action_id="home_dropdown_menu_select",
                            options=[
                                Option(value="EditMyProfile", text="Edit my profile"),
                                Option(value="...", text="..."),
                            ]
                        )
                    ]
                ),
                DividerBlock(),
                HeaderBlock(
                    text=PlainTextObject(text="Upcoming meetings"),
                ),
                *hardcode_meeting(),
                DividerBlock(),
                *HomeMyAvailabilityView(),
                *tmp
            ]
        )
