import copy
import datetime
import re
from typing import Callable, NoReturn

import slack_sdk
from pytz import timezone
from slack_bolt import App
from slack_sdk.models.attachments import Attachment, BlockAttachment
from slack_sdk.models.blocks import ContextBlock, MarkdownTextObject, ImageBlock, PlainTextObject, ImageElement, \
    DividerBlock, ActionsBlock, ButtonElement

from views import MeetingParticipantView, MeetingParticipantSummaryView, TestMessage, MeetingParticipantActionView, \
    CreateMeetingView
from runtime import SlackBotRuntime

ListenerRegister = Callable[[App, SlackBotRuntime], NoReturn]


def listen_events(app: App, runtime: SlackBotRuntime):
    @app.event("url_verification")
    def endpoint_url_validation(event, say):
        pong_msg = event["challenge"]
        say(pong_msg)

    @app.event("team_join")
    def example_team_joined(event, say):
        user_id = event["user"]
        text = f"Welcome to the team, <@{user_id}>! 🎉 boba tea is on you next time!"
        say(text=text, channel="#general")

    @app.event("message")
    def handle_message_events(body, logger):
        logger.info(body)


def listen_messages(app: App, runtime: SlackBotRuntime):
    @app.message(":wave:")
    def example_wave_back(message, say):
        user = message['user']
        say(text=f"Hola, <@{user}>!")

    @app.message("test!")
    def test_view(message, say, client):
        uid = message['user']

        user = client.users_profile_get(user=uid)

        view = MeetingParticipantView(
            scheduler_uid=uid,
            scheduler_avatar_url=user['profile']['image_24'],
            meeting_summary=MeetingParticipantSummaryView(
                project_name="TODO:",
                start_datetime=datetime.datetime.now(tz=timezone("America/Los_Angeles")),
                end_datetime=datetime.datetime.now(tz=timezone("America/Los_Angeles")),
            ),
            meeting_action=MeetingParticipantActionView(
                mode="questionnaire",
                attend_users=[uid],
                may_attend_users=[uid],
                wont_attend_users=[uid],
                pending_users=[uid],
            ),
        )
        say(
            blocks=view.blocks,
            attachments=view.attachments,
        )

        status_view = MeetingParticipantView(
            scheduler_uid=uid,
            scheduler_avatar_url=user['profile']['image_24'],
            meeting_summary=MeetingParticipantSummaryView(
                project_name="TODO:",
                start_datetime=datetime.datetime.now(tz=timezone("America/Los_Angeles")),
                end_datetime=datetime.datetime.now(tz=timezone("America/Los_Angeles")),
            ),
            meeting_action=MeetingParticipantActionView(
                mode="status",
                attend_users=[uid],
                may_attend_users=[uid],
                wont_attend_users=[uid],
                pending_users=[uid],
            ),
        )
        say(
            blocks=status_view.blocks,
            attachments=status_view.attachments,
        )


def listen_shortcuts(app: App, runtime: SlackBotRuntime):
    @app.shortcut("open_modal")
    def create_meeting(shortcut, ack, client):
        ack()
        # Call the views_open method using the built-in WebClient
        client.views_open(
            trigger_id=shortcut["trigger_id"],
            # A simple view payload for a modal
            view=CreateMeetingView()
        )


def listen_commands(app: App, runtime: SlackBotRuntime):
    @app.command("/come")
    def example_come(ack, client: slack_sdk.web.client.WebClient, command, body, say, logger):
        ack()
        print(logger)
        print(body)
        print(command)
        channel_id = command["channel_id"]
        # client.conversations_join(channel=channel_id)
        # say(text=f"What's up?", channel=channel_id)


def listen_actions(app: App, runtime: SlackBotRuntime):
    @app.action(re.compile("meeting_part.*"))
    @app.action("hnrB")
    def process_meeting_part(ack, action, body, say, client):
        ack(
            # "???"
        )
        attachments = body['message']['attachments']
        attachments.append(DividerBlock())
        client.chat_update(
            channel=body['channel']['id'],
            ts=body['message']['ts'],
            text=body['message']['text'],
            blocks=body['message']['blocks'],
            attachments=attachments,
        )
        print(body)
        print(action)

        say(
        )

# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
# @app.message(":wave:")
# def message_hello(message, say):
#     # say() sends a message to the channel where the event was triggered
#     say(f"Hey there <@{message['user']}>!")
#
#
# @app.message("knock knock")
# def ask_who(message, say):
#     say("_Who's there?_")
#
#
# @app.command("/hello-bolt-python")
# def handle_command(body, ack, respond, client, logger):
#     logger.info(body)
#     ack(
#         text="Accepted!",
#         blocks=[
#             {
#                 "type": "section",
#                 "block_id": "b",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": ":white_check_mark: Accepted!",
#                 },
#             }
#         ],
#     )
#
#     respond(
#         blocks=[
#             {
#                 "type": "section",
#                 "block_id": "b",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": "You can add a button alongside text in your message. ",
#                 },
#                 "accessory": {
#                     "type": "button",
#                     "action_id": "a",
#                     "text": {"type": "plain_text", "text": "Button"},
#                     "value": "click_me_123",
#                 },
#             }
#         ]
#     )
#
#     res = client.views_open(
#         trigger_id=body["trigger_id"],
#         view={
#             "type": "modal",
#             "callback_id": "view-id",
#             "title": {
#                 "type": "plain_text",
#                 "text": "My App",
#             },
#             "submit": {
#                 "type": "plain_text",
#                 "text": "Submit",
#             },
#             "close": {
#                 "type": "plain_text",
#                 "text": "Cancel",
#             },
#             "blocks": [
#                 {
#                     "type": "input",
#                     "element": {"type": "plain_text_input"},
#                     "label": {
#                         "type": "plain_text",
#                         "text": "Label",
#                     },
#                 },
#                 {
#                     "type": "input",
#                     "block_id": "es_b",
#                     "element": {
#                         "type": "external_select",
#                         "action_id": "es_a",
#                         "placeholder": {"type": "plain_text", "text": "Select an item"},
#                         "min_query_length": 0,
#                     },
#                     "label": {"type": "plain_text", "text": "Search"},
#                 },
#                 {
#                     "type": "input",
#                     "block_id": "mes_b",
#                     "element": {
#                         "type": "multi_external_select",
#                         "action_id": "mes_a",
#                         "placeholder": {"type": "plain_text", "text": "Select an item"},
#                         "min_query_length": 0,
#                     },
#                     "label": {"type": "plain_text", "text": "Search (multi)"},
#                 },
#             ],
#         },
#     )
#     logger.info(res)
