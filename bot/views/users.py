import datetime
from typing import List

import pytz
from slack_sdk.models.blocks import *
from slack_sdk.models.messages.message import Message
from slack_sdk.models.views import View

from utils import utc_offset_to_common_timezone
from views.commons import WeekdayOptionsMixin, TimezoneOptionGroupsMixin


class NewUserMessage(Message):
    def __init__(self, uid: str):
        super().__init__(
            text=f":wave: Hi <@{uid}>\nLet's set up your first personal profile in less than a minute!\nThis will let "
                 f"your team members know when you are available for meetings! ",
            markdown=True,
            blocks=[
                SectionBlock(
                    text=MarkdownTextObject(
                        text=f":wave: Hi <@{uid}>\nLet's set up your first personal profile in less than a minute!\nThis will let "
                             f"your team members know when you are available for meetings! ", )
                ),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text="Set your profile",
                            action_id="new_user_msg_set_profile"
                        )
                    ]
                )
            ]
        )


class SetProfileModal(View, WeekdayOptionsMixin, TimezoneOptionGroupsMixin):
    def __init__(self,
                 start_time: datetime.time = None,
                 end_time: datetime.time = None,
                 working_days_magics: List[int] = None,
                 timezone: str = None,
                 update: bool = False):
        super().__init__(
            type="modal",
            title=f"{'Set' if not update else 'Update'} your profile",
            submit="Create" if not update else 'Update',
            close="Cancel",
            callback_id="user_set_profile_submitted",
            blocks=[
                HeaderBlock(text=PlainTextObject(text="Working Hours")),
                ActionsBlock(
                    elements=[
                        TimePickerElement(
                            placeholder="Start time",
                            action_id="users_set_profile_start_time_select",
                            initial_time=start_time.strftime("%H:%M") if start_time else None,

                        ),
                        TimePickerElement(
                            placeholder="End time",
                            action_id="users_set_profile_end_time_select",
                            initial_time=end_time.strftime("%H:%M") if end_time else None,
                        ),
                    ]
                ),
                InputBlock(
                    label="Working Days",
                    element=StaticMultiSelectElement(
                        action_id="users_set_profile_working_days_multi_select",
                        options=self.working_days_options,
                        initial_options=[self.to_working_days_option(m) for m in
                                         working_days_magics] if working_days_magics else None
                    ),
                ),
                InputBlock(
                    label="Your timezone",
                    element=StaticSelectElement(
                        action_id="users_set_profile_timezone_select",
                        option_groups=self.timezone_option_groups,
                        initial_option=self.to_timezone_option(timezone) if timezone else None
                    )
                ),
                ContextBlock(
                    elements=[MarkdownTextObject(text="You can always update your profile later")]
                )
            ]
        )
