import datetime
import re
from typing import Callable, NoReturn

import pytz
from pytz import timezone
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import DividerBlock, ButtonElement

from db.models import User, UserProfile, TimeSlot
from models import set_personal_profiles_modal, create_meeting_modal, action_time, TimeSlotInfo, button, actions, hardcode_message_meeting
from runtime import SlackBotRuntime
from views.home import HomeView, HomeEditAvailabilityModal
from views.meeting import CreateMeetingModal, MeetingParticipantView, MeetingParticipantSummaryView, \
    MeetingParticipantActionView, CreateMeetingTimeSuggestionModal
from views.users import SetProfileModal, NewUserMessage

ListenerRegister = Callable[[App, SlackBotRuntime], NoReturn]


def listen_events(app: App, runtime: SlackBotRuntime):
    @app.event("url_verification")
    def endpoint_url_validation(event, say):
        pong_msg = event["challenge"]
        say(pong_msg)


    @app.event("app_home_opened")
    def home_opened(event, say, client, logger):
        user_id = event["user"]

        try:
            # Call the views.publish method using the WebClient passed to listeners
            logger.debug("home start")
            result = client.views_publish(
                user_id=user_id,
                view=HomeView()
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error fetching home page")

        # say({
        #     "blocks": [
        #         {
        #             "type": "divider"
        #         },
        #         {
        #             "type": "section",
        #             "text": {
        #                 "type": "mrkdwn",
        #                 "text": f":wave:*Hi <@{user_id}>, you have added AlignUp into this workspace!*\nYour default working hours is\n\t*Working Hours:* 10:AM - 6:00PM\n\t*Working Days:* Monday - Friday\n\t*Timezone:* (GMT-8:00) Pacific Time - Los Angeles"
        #             }
        #         }, actions([button(t="Update my availability", action_id="set_personal_profiles", value="set_personal_profiles"),])
        #     ]
        # })

    @app.event("team_join")
    def team_join(event, say, client, logger):
        user_id = event["user"]
        say({
            "blocks": [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":wave:*Hi <@{user_id}>, you have added AlignUp into this workspace!*\nYour default working hours is\n\t*Working Hours:* 10:AM - 6:00PM\n\t*Working Days:* Monday - Friday\n\t*Timezone:* (GMT-8:00) Pacific Time - Los Angeles"
                    }
                }, actions([button(t="Update my availability", action_id="set_personal_profiles", value="set_personal_profiles"),])
            ]
        })


def listen_messages(app: App, runtime: SlackBotRuntime):
    @app.message(":wave:")
    def example_wave_back(message, say):
        user = message['user']
        say(text=f"Hola, <@{user}>!")

    @app.message("app install")
    def app_install(message, say):
        user_id = message['user']
        say({
            "blocks": [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":wave:*Hi <@{user_id}>, you have added AlignUp into this workspace!*\nYour default working hours is\n\t*Working Hours:* 10:AM - 6:00PM\n\t*Working Days:* Monday - Friday\n\t*Timezone:* (GMT-8:00) Pacific Time - Los Angeles"
                    }
                }, actions([button(t="Update my availability", action_id="set_personal_profiles", value="set_personal_profiles"),])
            ]
        })

    @app.message("update")
    def app_install(message, say):
        user_id = message['user']
        say({
            "blocks": [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":wave:Good Afternoon <@{user_id}>! It is almost the end of the week. Before you wrap up this week's work, don't forget to update you schedule for next week."
                                f"The will let your team members know the most up-to-date information about when you will be available next week."
                    }
                }, actions([button(t="Update my availability", action_id="set_personal_profiles", value="set_personal_profiles"),])
            ]
        })

    @app.message("meeting")
    def app_install(message, say):
        user_id = message['user']
        say(hardcode_message_meeting(user_id))

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
            view=CreateMeetingModal()
        )


def listen_commands(app: App, runtime: SlackBotRuntime):
    pass


def listen_actions(app: App, runtime: SlackBotRuntime):
    @app.action("meeting_create_meeting_duration")
    def handle_some_action(ack, body, logger):
        ack()
        logger.info(body)

    @app.action("meeting_create_meeting_frequency")
    def handle_some_action(ack, body, logger):
        ack()
        logger.info(body)

    @app.action("meeting_create_meeting_suggestion_push")
    def meeting_create_meeting_suggestion_push(ack, body, client, logger):
        ack()

        client.views_push(
            trigger_id=body["trigger_id"],
            view=CreateMeetingTimeSuggestionModal(
                time_slot_infos=[
                    TimeSlotInfo(
                        time_slot_id="test1",
                        start_time=datetime.datetime.now(timezone("UTC")),
                        end_time=datetime.datetime.now(timezone("UTC")) + datetime.timedelta(hours=1),
                        timezone=pytz.timezone("America/Los_Angeles"),
                        available_users=[],
                        tentative_users=[],
                        unavailable_users=[],
                    ),
                    TimeSlotInfo(
                        time_slot_id="test2",
                        start_time=datetime.datetime.now(timezone("UTC")),
                        end_time=datetime.datetime.now(timezone("UTC")) + datetime.timedelta(hours=1),
                        timezone=pytz.timezone("America/Los_Angeles"),
                        available_users=[],
                        tentative_users=[],
                        unavailable_users=[],
                    ),
                    TimeSlotInfo(
                        time_slot_id="test3",
                        start_time=datetime.datetime.now(timezone("UTC")),
                        end_time=datetime.datetime.now(timezone("UTC")) + datetime.timedelta(hours=1),
                        timezone=pytz.timezone("America/Los_Angeles"),
                        available_users=[],
                        tentative_users=[],
                        unavailable_users=[],
                    ),
                    TimeSlotInfo(
                        time_slot_id="test4",
                        start_time=datetime.datetime.now(timezone("UTC")),
                        end_time=datetime.datetime.now(timezone("UTC")) + datetime.timedelta(hours=1),
                        timezone=pytz.timezone("America/Los_Angeles"),
                        available_users=[],
                        tentative_users=[],
                        unavailable_users=[],
                    ),
                    TimeSlotInfo(
                        time_slot_id="test5",
                        start_time=datetime.datetime.now(timezone("UTC")),
                        end_time=datetime.datetime.now(timezone("UTC")) + datetime.timedelta(hours=1),
                        timezone=pytz.timezone("America/Los_Angeles"),
                        available_users=[],
                        tentative_users=[],
                        unavailable_users=[],
                    ),
                    TimeSlotInfo(
                        time_slot_id="test6",
                        start_time=datetime.datetime.now(timezone("UTC")),
                        end_time=datetime.datetime.now(timezone("UTC")) + datetime.timedelta(hours=1),
                        timezone=pytz.timezone("America/Los_Angeles"),
                        available_users=[],
                        tentative_users=[],
                        unavailable_users=[],
                    ),
                ]
            )
        )

    @app.action("home_header_schedule_meeting")
    def home_header_schedule_meeting(ack, body, client, logger):
        ack()

        client.views_open(
            trigger_id=body["trigger_id"],
            view=CreateMeetingModal(
            ),
        )

    @app.action("home_dropdown_menu_select")
    def handle_some_action(ack, body, client, logger):
        ack()

        user = User.get_or_none(slack_uid=body["user"]["id"])
        if not user:
            client.views_open(
                trigger_id=body["trigger_id"],
                view=SetProfileModal(),
            )
        else:
            profile: UserProfile = UserProfile.get(user=user)
            client.views_open(
                trigger_id=body["trigger_id"],
                view=SetProfileModal(
                    start_time=profile.working_hours_start,
                    end_time=profile.working_hours_end,
                    working_days_magics=profile.to_magics(),
                    timezone=profile.timezone,
                    update=True,
                ),
            )

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



    # @app.action("new_meeting")
    # def new_meeting(ack, action, body, client, logger):
    #     ack()
    #     view = create_meeting_modal(body["user"]["username"], [" "])
    #     try:
    #         result = client.views_open(
    #             trigger_id=body["trigger_id"],
    #             view=view
    #         )
    #         logger.info(result)
    #
    #     except SlackApiError as e:
    #         logger.error("Error setting profile: {}".format(e))
    #
    # # TODO: view_update for add_time, view_update for erase time, view; db parts for meeting and update_avail
    # @app.action("test")
    # def test(ack, action, body, client, logger):
    #     ack(response_action="update", view=create_meeting_modal(body["user"]["username"], [" "], "Create"))
    #     # view = create_meeting_modal(body["user"]["username"], [" "])
    #     # try:
    #     #     result = client.views_open(
    #     #         trigger_id=body["trigger_id"],
    #     #         view=view
    #     #     )
    #     #     logger.info(result)
    #     #
    #     # except SlackApiError as e:
    #     #     logger.error("Error setting profile: {}".format(e))

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

    @app.action("home_edit_availability_but_clicked")
    def home_edit_availability(ack, client, body, logger):
        ack()
        client.views_open(
            trigger_id=body["trigger_id"],
            view=HomeEditAvailabilityModal()
        )


def listen_views(app: App, runtime: SlackBotRuntime):
    @app.action("users_set_profile_start_time_select")
    @app.action("users_set_profile_end_time_select")
    def noop(ack):
        ack()

    @app.view("meeting_create_meeting_suggest_time_submit")
    def meeting_create_meeting_suggest_time_submit(ack, client, body, ):
        ack()

        # Should store a timeslot
        print(body)

    @app.view("meeting_create_meeting_submit")
    def meeting_create_meeting_submit(ack, client, body, ):
        ack()

        values = body["view"]["state"]["values"]

        title = None
        convs = []
        duration = None
        frequency = None
        date = None
        agenda = None
        for block_name, block in values.items():
            for action_name, action in block.items():
                if action_name == "meeting_create_meeting_title":
                    title = action["value"]
                    pass
                elif action_name == 'meeting_create_meeting_participants':
                    for conv in action['selected_conversations']:
                        convs.append(conv)
                elif action_name == 'meeting_create_meeting_duration':
                    duration = action['selected_option']['value']
                elif action_name == 'meeting_create_meeting_frequency':
                    frequency = action['selected_option']['value']
                elif action_name == 'meeting_create_meeting_date':
                    date = action['selected_date']
                elif action_name == 'meeting_create_meeting_agenda':
                    agenda = action['value']

        # Filter the convs list as there might be channels or apps
        # for uid in convs:
        #     if uid.startswith("C"):
        #         client.conversations_info(channel=uid)

        # with runtime.db.atomic() as transaction:
        #     for user_or_chan in convs:
        #         pass
        client.views_push(
            trigger_id=body["trigger_id"],
            view=CreateMeetingTimeSuggestionModal()
        )

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

        view = HomeView(False)
        try:
            result = client.views_update(
                external_id="home",
                # token=body["token"],
                view=view
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error updating home: {}".format(e))
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


def listen_user_flow(app: App, runtime: SlackBotRuntime):
    """
    Message new user with a button to create profile
    """

    @app.message("new")
    def new_user(message, say):
        user = message['user']

        msg = NewUserMessage(user)
        say(
            text="",
            blocks=msg.blocks,
        )

    """
    Open page for new user profile
    """

    @app.action("new_user_msg_set_profile")
    def new_user_msg_set_profile(ack, action, body, client, logger, say):
        ack()

        user = User.get_or_none(slack_uid=body["user"]["id"])
        if user:
            say(
                text=f"Dada <@{body['user']['id']}>, you have already set up your profile!"
            )
            return
        client.views_open(
            trigger_id=body["trigger_id"],
            view=SetProfileModal(),
        )

    """
    Set new user profile submitted (create/update)
    """

    @app.view("user_set_profile_submitted")
    def user_set_profile_submitted(ack, client, body, logger):
        ack()

        uid = body.get("user").get("id")

        values = body["view"]["state"]["values"]

        # Parse the response, which is hideous :)
        tz = None
        start_time = None
        end_time = None
        working_days = []
        for block_name, block in values.items():
            for action_name, elem in block.items():
                if action_name == 'users_set_profile_timezone_select':
                    tz = elem["selected_option"]['value']
                elif action_name == 'users_set_profile_working_days_multi_select':
                    for option in elem["selected_options"]:
                        working_days.append(option["value"])
                elif action_name == 'users_set_profile_start_time_select':
                    start_time = datetime.datetime.strptime(elem['selected_time'], "%H:%M")
                elif action_name == 'users_set_profile_end_time_select':
                    end_time = datetime.datetime.strptime(elem['selected_time'], "%H:%M")

        # Create user if not
        user = User.get_or_none(slack_uid=uid)
        if not user:
            with runtime.db.atomic() as xaction:
                try:
                    user = User.create(
                        slack_uid=uid
                    )
                    user_profile = UserProfile(
                        user=user,
                        timezone=tz,
                        working_hours_start=start_time,
                        working_hours_end=end_time,
                    )

                    user_profile.update_workdays(*working_days)
                    user_profile.save()
                except Exception:
                    xaction.rollback()
                    raise RuntimeError("Fail in creation user and user profiles")

    """
    Open edit availability modal
    """

    @app.action("home_edit_availability_but_clicked")
    def home_edit_availability(ack, client, body, logger):
        ack()
        client.views_open(
            trigger_id=body["trigger_id"],
            view=HomeEditAvailabilityModal()
        )

    """
    Switch weekdays
    """

    @app.action("user_edit_availability_weekday_selected")
    def user_edit_availability_weekday_selected(ack, client, action, body, logger):
        ack()

        client.views_update(
            view_id=body["view"]["id"],
            view=HomeEditAvailabilityModal(
                selected_weekday_magic=action["selected_option"]["value"]
            )
        )

    @app.action("user_edit_availability_add_time_clicked")
    def user_edit_availability_add_time_clicked(ack, client, action, body, logger):
        ack(response_action="errors", errors=Exception())

    """
    Update availability (submission)
    """

    @app.action("user_edit_availability_update_time_clicked")
    def user_edit_availability_update_time_clicked(ack, client, action, body, logger):
        ack()

        uid = body["user"]["id"]
        user = User.get(slack_uid=uid)
        user_tz = timezone(user.profile.get().timezone)

        state = body["view"]["state"]["values"]

        start = None
        end = None
        status = None
        for block_name, block in state.items():
            for action_name, act in block.items():
                if action_name == 'user_edit_availability_available_time_start':
                    start = act['selected_time']
                elif action_name == 'user_edit_availability_available_time_start':
                    end = act['selected_time']
                elif action_name == 'user_edit_availability_available_time_status':
                    status = act['selected_option']

        if start and end and status:
            TimeSlot.create(
                user=user,
                type="availability",
                start=user_tz.localize(datetime.datetime.strptime(start, "%-I:%M%p")).astimezone(timezone('UTC')),
                end=user_tz.localize(datetime.datetime.strptime(end, "%-I:%M%p")).astimezone(timezone('UTC')),
                status_label=status.lower(),
            )
