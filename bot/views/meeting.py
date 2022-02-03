import datetime
from typing import List

import pytz
from slack_sdk.models.attachments import BlockAttachment
from slack_sdk.models.blocks import *
from slack_sdk.models.messages.message import Message
from slack_sdk.models.views import View

from models import TimeSlotInfo
from utils import utc_offset_to_common_timezone, tzname_to_abbr, tz_to_abbr
from views.commons import Blocks

PLACE_HOLDER_IMG = "https://cdn.pixabay.com/photo/2021/12/19/14/36/bird-6881277_1280.jpg"


class MeetingParticipantActionView(Blocks):
    modes = {"questionnaire", "status"}

    meeting_part_quest_yes = "meeting_part_quest_yes"
    meeting_part_quest_maybe = "meeting_part_quest_maybe"
    meeting_part_quest_no = "meeting_part_quest_no"

    meeting_part_summary_send_reminder = "meeting_part_summary_send_reminder"
    meeting_part_summary_reschedule = "meeting_part_summary_reschedule"
    meeting_part_summary_cancel = "meeting_part_summary_cancel"

    # Note assumes start_datatime and end_datetime have the timezone set and are equivalent
    def __init__(self, *,
                 mode: str,
                 attend_users: List[str] = None,
                 may_attend_users: List[str] = None,
                 wont_attend_users: List[str] = None,
                 pending_users: List[str] = None):

        if mode not in self.modes:
            raise NotImplementedError

        if mode == "questionnaire":
            section = [
                HeaderBlock(text="Going?"),
                ActionsBlock(
                    elements=[
                        ButtonElement(text="Yes", action_id=self.meeting_part_quest_yes),
                        ButtonElement(text="No", action_id=self.meeting_part_quest_no),
                        ButtonElement(text="Maybe", action_id=self.meeting_part_quest_maybe),
                    ]
                ),
            ]

            if attend_users:
                section.append(ContextBlock(elements=[
                    ImageElement(image_url=PLACE_HOLDER_IMG, alt_text="attend_users"),
                    PlainTextObject(
                        text=f"{len(attend_users)} team member{'s' if len(attend_users) > 1 else ''} will attend"),
                ]))

            if may_attend_users:
                section.append(ContextBlock(elements=[
                    ImageElement(image_url=PLACE_HOLDER_IMG, alt_text="may_attend_users"),
                    PlainTextObject(
                        text=f"{len(may_attend_users)} team member{'s' if len(may_attend_users) > 1 else ''} may attend"),
                ]))

            if wont_attend_users:
                section.append(ContextBlock(elements=[
                    ImageElement(image_url=PLACE_HOLDER_IMG, alt_text="attend_users"),
                    PlainTextObject(
                        text=f"{len(wont_attend_users)} team member{'s' if len(wont_attend_users) > 1 else ''} will not attend"),
                ]))

        else:
            section = [
                HeaderBlock(text="Status")
            ]
            if attend_users:
                section.append(ContextBlock(elements=[
                    ImageElement(image_url=PLACE_HOLDER_IMG, alt_text="attend_users"),
                    MarkdownTextObject(
                        text="Confirmed: " + ", ".join([f"<@{uid}>" for uid in attend_users])),
                ]))
            if may_attend_users:
                section.append(ContextBlock(elements=[
                    ImageElement(image_url=PLACE_HOLDER_IMG, alt_text="may_attend_users"),
                    MarkdownTextObject(
                        text="Maybe: " + ", ".join([f"<@{uid}>" for uid in may_attend_users])),
                ]))
            if wont_attend_users:
                section.append(ContextBlock(elements=[
                    ImageElement(image_url=PLACE_HOLDER_IMG, alt_text="wont_attend_users"),
                    MarkdownTextObject(
                        text="Not coming: " + ", ".join([f"<@{uid}>" for uid in wont_attend_users])),
                ]))
            if pending_users:
                section.append(ContextBlock(elements=[
                    ImageElement(image_url=PLACE_HOLDER_IMG, alt_text="pending_users"),
                    MarkdownTextObject(
                        text="Waiting for response: " + ", ".join([f"<@{uid}>" for uid in pending_users])),
                ]))

            section.append(
                HeaderBlock(text="Options")
            )
            section.append(
                ActionsBlock(
                    elements=[
                        ButtonElement(text="Send Reminder", action_id=self.meeting_part_summary_send_reminder),
                        ButtonElement(text="Reschedule", action_id=self.meeting_part_summary_reschedule),
                        ButtonElement(text="Cancel", action_id=self.meeting_part_summary_cancel),
                    ]
                ),
            )

        super().__init__(section)


class MeetingParticipantSummaryView(Blocks):
    # Note assumes start_datatime and end_datetime have the timezone set and are equivalent
    def __init__(self, *,
                 project_name: str,
                 start_datetime: datetime.datetime,
                 end_datetime: datetime.datetime):
        super().__init__([
            ContextBlock(elements=[
                MarkdownTextObject(text=start_datetime.strftime("%A, %B %-m, %Y"))
            ]),
            ContextBlock(elements=[
                ImageElement(
                    image_url=PLACE_HOLDER_IMG,
                    alt_text="fi"),
                MarkdownTextObject(text=f"Team check-in for project {project_name}"),
            ]),
            ContextBlock(elements=[
                PlainTextObject(
                    text=f"{start_datetime.time().strftime('%-I:%M%p')} - {end_datetime.time().strftime('%-I:%M%p')}"
                         f" ({start_datetime.tzname()})"),
            ]),
        ])


class MeetingParticipantView(Message):
    def __init__(self, *,
                 scheduler_uid: str,
                 scheduler_avatar_url: str,
                 meeting_summary: MeetingParticipantSummaryView,
                 meeting_action: MeetingParticipantActionView):
        super().__init__(
            text="",
            blocks=[
                ContextBlock(elements=[
                    ImageElement(image_url=scheduler_avatar_url, alt_text=scheduler_uid),
                    MarkdownTextObject(text=f"<@{scheduler_uid}> scheduled a meeting"),
                ])
            ],
            attachments=[
                BlockAttachment(
                    blocks=[
                        *meeting_summary,
                        DividerBlock(),
                        *meeting_action,
                    ]
                ),
                DividerBlock(),
                BlockAttachment(
                    blocks=[
                        *meeting_summary,
                        DividerBlock(),
                        *meeting_action,
                    ]
                ),
            ]
        )


class CreateMeetingModal(View):
    def __init__(self, **kwargs):
        super().__init__(
            type="modal",
            title=PlainTextObject(text="Create Meeting"),
            close=PlainTextObject(text="Cancel"),
            submit=PlainTextObject(text="Next"),
            callback_id="meeting_create_meeting_submit",
            blocks=[
                InputBlock(
                    label=PlainTextObject(text="Meeting Title"),
                    element=PlainTextInputElement(
                        action_id="meeting_create_meeting_title",
                        placeholder=PlainTextObject(text="Enter Title"),
                    )
                ),
                InputBlock(
                    label=PlainTextObject(text="Select Channel to Create Meeting In"),
                    element=ConversationMultiSelectElement(
                        action_id="meeting_create_meeting_participants",
                        placeholder=PlainTextObject(text="Channel Name/User Name"),
                    )
                ),
                ContextBlock(
                    elements=[PlainTextObject(text="Or type names to create a new channel")]
                ),
                SectionBlock(
                    text=PlainTextObject(text="Duration"),
                    accessory=StaticSelectElement(
                        action_id="meeting_create_meeting_duration",
                        options=[
                            Option(value="0.5h", text="30 Mins"),
                            Option(value="1h", text="1 Hour"),
                            Option(value="2h", text="2 Hours"),
                            Option(value="3h", text="3 Hours"),
                            Option(value="4h", text="4 Hours"),
                        ]
                    )
                ),
                SectionBlock(
                    text=PlainTextObject(text="Frequency"),
                    accessory=StaticSelectElement(
                        action_id="meeting_create_meeting_frequency",
                        options=[
                            Option(value="0", text="Never Repeat"),
                        ],
                        initial_option=Option(value="0", text="Never Repeat"),
                    ),
                ),
                InputBlock(
                    label=PlainTextObject(text="Meeting Date"),
                    element=DatePickerElement(
                        action_id="meeting_create_meeting_date",
                        placeholder=PlainTextObject(text="Pick a date"),
                        initial_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                    ),
                ),
                # SectionBlock(
                #     text=PlainTextObject(text="Latest Date"),
                #     accessory=DatePickerElement(
                #         placeholder=PlainTextObject(text="Pick a date")
                #     )
                # ),
                InputBlock(
                    label=PlainTextObject(text="Agenda (Optional)"),
                    element=PlainTextInputElement(
                        action_id="meeting_create_meeting_agenda",
                        placeholder=PlainTextObject(text="Type in agenda"),
                        multiline=True,
                    )
                ),
                SectionBlock(
                    text=PlainTextObject(text="See"),
                    accessory=ButtonElement(
                        action_id="meeting_create_meeting_suggestion_push",
                        text="Show me"
                    )
                ),
            ]
        )


class CreateMeetingTimeSuggestionModal(View):
    def __init__(self,
                 time_slot_infos: List[TimeSlotInfo] = None):

        blocks = [
            SectionBlock(
                text=MarkdownTextObject(text="*Suggested Time Slots*"),
                accessory=RadioButtonsElement(
                    action_id="meeting_create_meeting_time_suggestion_suggest_select",
                    options=[
                        Option(
                            value=t.time_slot_id,
                            description=MarkdownTextObject(
                                text=f"Unavailable: {len(t.unavailable_users)} users",
                            ),
                            text=MarkdownTextObject(
                                text=f"*{t.start_time.astimezone(t.timezone).strftime('%-I:%M%p')} - {t.end_time.astimezone(t.timezone).strftime('%-I:%M%p')} ({tz_to_abbr(t.timezone)})*\n"
                                     f"Available: {len(t.available_users)} users \n"
                                # f"{self.render_users_list(t.available_users)}\n"
                                     f"Tentative: {len(t.tentative_users)} users \n"
                                # f"{self.render_users_list(t.tentative_users)}\n"
                                     f"Unavailable: {len(t.unavailable_users)} users"
                                # f"{self.render_users_list(t.unavailable_users)}\n"
                            )
                        )
                        for t in time_slot_infos[: 2 if len(time_slot_infos) > 2 else len(time_slot_infos)]
                    ]
                )
            ) if time_slot_infos else SectionBlock(text=MarkdownTextObject(
                text="Oh oh, seems like there's no handy time we can suggest for you :disappointed:"
            )),
        ]

        if len(time_slot_infos) > 2:
            blocks.append(
                InputBlock(
                    optional=True,
                    label=PlainTextObject(text="Or Choose Another Time Slot"),
                    element=StaticSelectElement(
                        action_id="meeting_create_meeting_another_time_slot_select",
                        options=[
                            Option(
                                value=t.time_slot_id,
                                # text= " test"
                                text=f"{t.start_time.astimezone(t.timezone).strftime('%-I:%M%p')} - {t.end_time.astimezone(t.timezone).strftime('%-I:%M%p')} ({tz_to_abbr(t.timezone)})\n"
                            )
                            for t in time_slot_infos[2:]
                        ]
                    )
                ),
            )
        super().__init__(
            type="modal",
            title=PlainTextObject(text="Meeting Time"),
            close=PlainTextObject(text="Back"),
            submit=PlainTextObject(text="Confirm"),
            callback_id="meeting_create_meeting_suggest_time_submit",
            blocks=blocks,
        )

    @staticmethod
    def render_users_list(uids: List[str]) -> str:
        if not uids:
            return ""

        return ", ".join([f"<@{uid}>" for uid in uids])
