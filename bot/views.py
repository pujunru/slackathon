import datetime
from typing import Union, Optional, Sequence, List

import colored
from colour import Color
from slack_sdk.models.attachments import BlockAttachment
from slack_sdk.models.blocks import *
from slack_sdk.models.messages.message import Message
from slack_sdk.models.views import View

PLACE_HOLDER_IMG = "https://cdn.pixabay.com/photo/2021/12/19/14/36/bird-6881277_1280.jpg"


class Modal(View):
    def __init__(self, title: Optional[Union[str, dict, PlainTextObject]],
                 blocks: Optional[Sequence[Union[dict, Block]]], **kwargs):
        super().__init__(
            type="modal",
            title=title,
            blocks=blocks,
            **kwargs
        )


# class MeetingParticipantSummaryView(Blocks):
#     def __init__(self,
#                  meeting_datatime: datetime.datetime,
#                  project_name: str,
#                  start_time: datetime.time,
#                  end_time: datetime.time,
#                  ):
#         super().__init__()
#         self.append_block(
#             ContextBlock(elements=[
#                 MarkdownTextObject(text=meeting_datatime.strftime(""))
#             ])
#         )
#         self.append_block(
#             ContextBlock(elements=[
#                 ImageElement(image_url="", alt_text=""),
#                 MarkdownTextObject(text=f"Team check-in for project {project_name}"),
#             ])
#         )
#         self.append_block(
#             ContextBlock(elements=[
#                 PlainTextObject(text=f"{start_time.strftime('')} - {end_time.strftime('')}(PST)"),  # TODO: TIMEZONE!
#             ])
#         )


class TestMessage(Message):
    def __init__(self, *, text: str):
        super().__init__(text=text)


class Blocks:
    def __init__(self, blocks: List[Block]):
        self.blocks = blocks

    def __iter__(self):
        return iter(self.blocks)


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


class CreateMeetingView(View):
    def __init__(self, **kwargs):
        super().__init__(
            type="modal",
            title=PlainTextObject(text="Create Meeting"),
            close=PlainTextObject(text="Cancel"),
            submit=PlainTextObject(text="Create"),
            blocks=[
                InputBlock(
                    label=PlainTextObject(text="Meeting Title"),
                    element=PlainTextInputElement(
                        placeholder=PlainTextObject(text="Enter Title"),
                    )
                ),
                InputBlock(
                    label=PlainTextObject(text="Select Channel to Create Meeting In"),
                    element=ChannelSelectElement(
                        placeholder=PlainTextObject(text="Channel Name/User Name"),
                    )
                ),
                SectionBlock(
                    text=PlainTextObject(text="Duration"),
                    accessory=StaticSelectElement(
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
                        options=[
                            Option(value="0", text="Never Repeat"),
                        ]
                    )
                ),
                SectionBlock(
                    text=PlainTextObject(text="Earliest Date"),
                    accessory=DatePickerElement(
                        placeholder=PlainTextObject(text="Pick a date")
                    )
                ),
                SectionBlock(
                    text=PlainTextObject(text="Latest Date"),
                    accessory=DatePickerElement(
                        placeholder=PlainTextObject(text="Pick a date")
                    )
                ),
                InputBlock(
                    label=PlainTextObject(text="Agenda (Optional)"),
                    element=PlainTextInputElement(
                        placeholder=PlainTextObject(text="Type in agenda"),
                        multiline=True,
                    )
                ),
            ]
        )
