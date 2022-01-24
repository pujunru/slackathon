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
