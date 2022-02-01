import copy
import datetime
import re
from typing import Callable, NoReturn

import slack_sdk
from pytz import timezone
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from peewee import Database
from models import set_personal_profiles_modal, home_modal, create_meeting_modal, action_time
from db.utils import create_user
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

    @app.event("app_home_opened")
    def home_opened(event, client, logger):
        user_id = event["user"]

        try:
            # Call the views.publish method using the WebClient passed to listeners
            print("home start")
            result = client.views_publish(
                user_id=user_id,
                view=home_modal()
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error fetching home page")


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
    @app.action(re.compile("(\d+)\.actionId-3"))
    def close_available_time(ack, action, body, client, logger):
        ack()
        index = action["action_id"][0]
        print(index)
        print(len(body["view"]["blocks"]))
        for i in range(len(body["view"]["blocks"])):
            print(body["view"]["blocks"][i])
            if body["view"]["blocks"][i]["block_id"] == index:
                body["view"]["blocks"].pop(i)
                break
        new_view = set_personal_profiles_modal()
        new_view["blocks"] = body["view"]["blocks"]
        try:
            result = client.views_update(
                view_id=body["container"]["view_id"],
                # token=body["token"],
                view=new_view
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error setting profile: {}".format(e))

    @app.action("add_available_time")
    def add_available_time(ack, action, body, client, logger):
        ack()
        index = action["action_id"][0]

        counter = 0
        for i in range(len(body["view"]["blocks"])):
            if len(body["view"]["blocks"][i]["block_id"]) == 1:
                counter += 1
            continue
        body["view"]["blocks"].insert(-1, action_time(counter))
        new_view = set_personal_profiles_modal()
        new_view["blocks"] = body["view"]["blocks"]
        print(new_view["blocks"])
        try:
            result = client.views_update(
                view_id=body["container"]["view_id"],
                # token=body["token"],
                view=new_view
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error setting profile: {}".format(e))

    @app.action(re.compile("(\d+)\.actionId-0"))
    @app.action(re.compile("(\d+)\.actionId-1"))
    @app.action(re.compile("(\d+)\.actionId-2"))
    def no_move(ack, action, body, client, logger):
        ack()
        pass

    @app.action("set_personal_profiles")
    def set_personal_profiles(ack, action, body, client, logger):
        """ Entry for Update my availability"""
        ack()
        print(body)
        if body["type"] == "block_actions":
            view = set_personal_profiles_modal()
            print(view["blocks"][7])
            try:
                result = client.views_open(
                    trigger_id=body["trigger_id"],
                    view=view
                )
                logger.info(result)

            except SlackApiError as e:
                logger.error("Error setting profile: {}".format(e))

    # @app.action("update_availability")
    # def update_availability(ack, action, body, client, logger):
    #     ack()
    #     print(body)
    #     if body["type"] == "block_actions":
    #         view = update_availability_modal()
    #         try:
    #             result = client.views_open(
    #                 trigger_id=body["trigger_id"],
    #                 view=view
    #             )
    #             logger.info(result)
    #
    #         except SlackApiError as e:
    #             logger.error("Error setting profile: {}".format(e))

    @app.action("new_meeting")
    def new_meeting(ack, action, body, client, logger):
        ack()
        view = create_meeting_modal(body["user"]["username"], [" "])
        try:
            result = client.views_open(
                trigger_id=body["trigger_id"],
                view=view
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error setting profile: {}".format(e))

    # TODO: view_update for add_time, view_update for erase time, view; db parts for meeting and update_avail
    @app.action("test")
    def test(ack, action, body, client, logger):
        ack(response_action="update", view=create_meeting_modal(body["user"]["username"], [" "], "Create"))
        # view = create_meeting_modal(body["user"]["username"], [" "])
        # try:
        #     result = client.views_open(
        #         trigger_id=body["trigger_id"],
        #         view=view
        #     )
        #     logger.info(result)
        #
        # except SlackApiError as e:
        #     logger.error("Error setting profile: {}".format(e))

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


def listen_views(app: App, runtime: SlackBotRuntime):
    @app.view("personal_profile")
    def personal_profile(ack, body, client, view, logger):
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
        # timezone = values["timezone"]["static_select-action"]["selected_option"]["value"]
        # print(f"{working_hours_start}...{working_hours_end}...{work_days}...{timezone}")
        ack()

        user = body["user"]["id"]
        # return create_user(runtime.db, user, working_hours_start, working_hours_end, work_days, timezone, logger)

    # @app.view("create_meeting")
    # def personal_profile(ack, body, client, view, logger):
    #     print(view["state"]["values"])
    #     values = view["state"]["values"]
    #     update = values["meeting_time"]["static_select-action"]["selected_option"]["value"] == " "
    #     date = values["date"]["datepicker-action"]["selected_date"]
    #     selected_users = values["select_users"]["multi_users_select-action"]["selected_users"]
    #     print(date, selected_users)
    #     # TODO: find out the time based on date and selected users
    #     picked_times = ["15:00"]
    #     if update:
    #         ack(response_action="update", view=create_meeting_modal(body["user"]["username"], picked_times, "Create"))
    #     else:
    #         ack()
    #         # TODO: save meeting to db
