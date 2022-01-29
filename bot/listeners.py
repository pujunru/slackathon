from typing import Callable, NoReturn

import slack_sdk
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from peewee import Database
from models import set_personal_profiles_model, home_model
from db.utils import create_user

ListenerRegister = Callable[[App, Database], NoReturn]
from runtime import SlackBotRuntime

ListenerRegister = Callable[[App, SlackBotRuntime], NoReturn]


def listen_events(app: App, db: Database):
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

    @app.event("app_home_opened")
    def home_opened(event, client, logger):
        user_id = event["user"]
        home_view = home_model()

        try:
            # Call the views.publish method using the WebClient passed to listeners
            result = client.views_publish(
                user_id=user_id,
                view=home_view
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error fetching home page")


def listen_messages(app: App, db: Database):
def listen_messages(app: App, runtime: SlackBotRuntime):
    @app.message(":wave:")
    def example_wave_back(message, say):
        user = message['user']
        say(text=f"Hola, <@{user}>!")

    @app.message("hello")
    def ask_who(message, say):
        say("_Who's there?_")


def listen_commands(app: App, db: Database):
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


def listen_actions(app: App, db: Database):
    @app.action("set_personal_profiles")
    def set_personal_profiles(ack, action, body, client, logger):
        ack()
        print(body)
        if body["type"] == "block_actions":
            view = set_personal_profiles_model()
            try:
                result = client.views_open(
                    trigger_id=body["trigger_id"],
                    view=view
                )
                logger.info(result)

            except SlackApiError as e:
                logger.error("Error setting profile: {}".format(e))


def listen_views(app: App, db: Database):
    @app.view("personal_profile")
    def personal_profile(ack, body, client, view, logger):
        print(body)
        values = view["state"]["values"]
        working_hours_start = values["working_hours_start"]["timepicker-action"]["selected_time"]
        working_hours_end = values["working_hours_end"]["timepicker-action"]["selected_time"]
        errors = {}
        if working_hours_start >= working_hours_end:
            errors["working_hours_start"] = "Working hours start time must be earlier than the end time."
        if len(errors) > 0:
            ack(response_action="errors", errors=errors)
            return
        days = values["working_days"]["checkboxes-action"]["selected_options"]
        work_days = [day["value"] for day in days]
        timezone = values["timezone"]["static_select-action"]["selected_option"]["value"]
        print(f"{working_hours_start}...{working_hours_end}...{work_days}...{timezone}")
        ack()

        user = body["user"]["id"]
        return create_user(db, user, working_hours_start, working_hours_end, work_days, timezone, logger)



    # @app.action("new_meeting")
    # def new_meeting(ack, action, body, client, logger):
    #     ack()
    #     print(action)
    #     priority = ["High", "Middle", "Low"]
    #     meeting = {
    #         "type": "modal",
    #         "title": text("Create meeting"),
    #         "submit": text("Create"),
    #         "close": text("Cancel"),
    #         "blocks": [
    #             {
    #                 "type": "divider"
    #             },
    #             inputs(select_time(), "Working Hours"),
    #             inputs(select_time(), "-"),
    #             inputs(checkbox(options=[option(priority[i], i) for i in range(3)]), "Meeting Priority"),
    #             context("\nYou can always update your profile later.")
    #         ]
    #     }
    #
    #     try:
    #         result = client.views_update(
    #             view_id=body["view"]["id"],
    #             hash=body["view"]["hash"],
    #             view=meeting
    #         )
    #         logger.info(result)
    #
    #     except SlackApiError as e:
    #         logger.error("Error setting profile: {}".format(e))

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
