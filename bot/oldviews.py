import datetime
from typing import Union, Optional, Sequence, List

import colored
from colour import Color
from slack_sdk.models.attachments import BlockAttachment
from slack_sdk.models.blocks import *
from slack_sdk.models.messages.message import Message
from slack_sdk.models.views import View

from views.commons import Blocks
from views.meeting import MeetingParticipantActionView



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





