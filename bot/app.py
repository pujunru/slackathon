import atexit
import logging
import os
from typing import Optional

from peewee import Database
from slack_bolt import App as SlackBoltApp
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from config import SlackBotConfig
from db.database import conn_sqlite_database, conn_mysql_database
from db.utils import init_db_if_not
from middlewares import MiddlewareRegister, global_middlewares
from listeners import ListenerRegister, listen_events, listen_commands, listen_messages, listen_actions, listen_views\
    # , listen_shortcuts
from runtime import SlackBotRuntime

logging.basicConfig(level=logging.DEBUG)


class SlackBotApp:
    def __init__(self, config: SlackBotConfig,
                 bolt_app: SlackBoltApp):
        self.config = config
        self.bolt_app = bolt_app  # Note DI for better testing

        self._socket_mode_handler: Optional[SocketModeHandler] = None
        self._lambda_mode_handler: Optional[SlackRequestHandler] = None

        self.logger = None  # TODO!

        # Init database
        if not self.config.db_in_prod():
            self.db: Database = conn_sqlite_database(config.db_name)
        else:
            self.db: Database = conn_mysql_database(config.db_url)
        # self.init_database()

        self._runtime = SlackBotRuntime(self.db)

        # Register Slack middlewares
        self.register_middlewares(
            global_middlewares,
        )

        # Register Slack event listeners
        self.register_listeners(
            listen_events,
            listen_commands,
            listen_messages,
            listen_actions,
            # listen_shortcuts,
            listen_views
        )

    # Global registration of listeners for each event type/business category
    def register_listeners(self, *listener_register: ListenerRegister):
        for register in listener_register:
            register(self.bolt_app, self._runtime)

    def register_middlewares(self, *middleware_register: MiddlewareRegister):
        for register in middleware_register:
            register(self.bolt_app)

    def init_database(self):
        assert self.db
        self.db.connect()

        init_db_if_not(self.db)

        # TODO: Init database schema when obsolete
        raise NotImplementedError("Database Initialization not yet implemented!")

    # Start/Close mode for server-ful modes, e.g. local WS based testing
    def start(self, socket_mode=True):
        if socket_mode:
            self._socket_mode_handler = SocketModeHandler(self.bolt_app, self.config.slack_app_token)
            self._socket_mode_handler.start()
        else:
            from flask import Flask, request
            from slack_bolt.adapter.flask import SlackRequestHandler

            flask_app = Flask(__name__)
            handler = SlackRequestHandler(self.bolt_app)

            @flask_app.route("/slack/events", methods=["POST"])
            def slack_events():
                return handler.handle(request)

            @flask_app.route("/slack/interactive-endpoint", methods=["POST"])
            def slack_interactive():
                return handler.handle(request)

            @flask_app.after_request
            def after(response):
                logging.debug(response.status)
                logging.debug(response.headers)
                logging.debug(response.get_data())
                return response

            @flask_app.before_request
            def before():
                logging.debug(request.headers)
                logging.debug(request.get_data())
                pass

            logging.debug("Starting slack bot app within flask...")
            # Run `ngrok http 3000` to establish a tunnel
            flask_app.run(debug=True, port=3000)

    def close(self):
        if self._socket_mode_handler:
            self._socket_mode_handler.close()
        self.db.close()

    def start_lambda(self, event, context):
        lambda_mode_handler = SlackRequestHandler(self.bolt_app)
        return lambda_mode_handler.handle(event, context)


def lambda_handler(event, context):
    app_config = SlackBotConfig(
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),
        slack_signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
        # db_name=os.environ.get("DB_NAME"),
        db_name="slackathon_staging",
        db_hostname="http://slackathon-app-db-prod.cacyqztjkxq5.us-west-1.rds.amazonaws.com/",
        db_username="berkeley_mds_up",
        db_password="testslackathon",
        # db_hostname=os.environ.get("DB_HOSTNAME"),
        # db_username=os.environ.get("DB_USERNAME"),
        # db_password=os.environ.get("DB_PASSWORD"),
    )
    bolt_app = SlackBoltApp(
        token=app_config.slack_bot_token,
        process_before_response=True,
    )

    app = SlackBotApp(config=app_config, bolt_app=bolt_app)
    logging.info("Starting slack bot app with lambda...")
    return app.start_lambda(event, context)


if __name__ == '__main__':
    _app_config = SlackBotConfig(
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),


        slack_signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),

    )

    _bolt_app = SlackBoltApp(
        token=_app_config.slack_bot_token,
        process_before_response=True,
    )
    _app = SlackBotApp(config=_app_config, bolt_app=_bolt_app)
    _app.start(socket_mode=True)

    atexit.register(_app.close)


# {'id': 'V030RPEPXAR', 'team_id': 'T02V2ERJKFF', 'type': 'modal', 'blocks': [{'type': 'divider', 'block_id': 'q280A'},
#                                                                             {'type': 'input', 'block_id': 'timezone',
#                                                                              'label': {'type': 'plain_text', 'text': 'Timezone', 'emoji': True},
#                                                                              'optional': False, 'dispatch_action': False,
#                                                                              'element': {'type': 'static_select', 'action_id': 'static_select-action', 'placeholder': {'type': 'plain_text', 'text': 'Select an item', 'emoji': True}, 'options': [{'text': {'type': 'plain_text', 'text': 'UTC-12', 'emoji': True}, 'value': '0'}, {'text': {'type': 'plain_text', 'text': 'UTC-11', 'emoji': True}, 'value': '1'}, {'text': {'type': 'plain_text', 'text': 'UTC-10', 'emoji': True}, 'value': '2'}, {'text': {'type': 'plain_text', 'text': 'UTC-9', 'emoji': True}, 'value': '3'}, {'text': {'type': 'plain_text', 'text': 'UTC-8', 'emoji': True}, 'value': '4'}, {'text': {'type': 'plain_text', 'text': 'UTC-7', 'emoji': True}, 'value': '5'}, {'text': {'type': 'plain_text', 'text': 'UTC-6', 'emoji': True}, 'value': '6'}, {'text': {'type': 'plain_text', 'text': 'UTC-5', 'emoji': True}, 'value': '7'}, {'text': {'type': 'plain_text', 'text': 'UTC-4', 'emoji': True}, 'value': '8'}, {'text': {'type': 'plain_text', 'text': 'UTC-3', 'emoji': True}, 'value': '9'}, {'text': {'type': 'plain_text', 'text': 'UTC-2', 'emoji': True}, 'value': '10'}, {'text': {'type': 'plain_text', 'text': 'UTC-1', 'emoji': True}, 'value': '11'}, {'text': {'type': 'plain_text', 'text': 'UTC', 'emoji': True}, 'value': '12'}, {'text': {'type': 'plain_text', 'text': 'UTC+1', 'emoji': True}, 'value': '13'}, {'text': {'type': 'plain_text', 'text': 'UTC+2', 'emoji': True}, 'value': '14'}, {'text': {'type': 'plain_text', 'text': 'UTC+3', 'emoji': True}, 'value': '15'}, {'text': {'type': 'plain_text', 'text': 'UTC+4', 'emoji': True}, 'value': '16'}, {'text': {'type': 'plain_text', 'text': 'UTC+5', 'emoji': True}, 'value': '17'}, {'text': {'type': 'plain_text', 'text': 'UTC+6', 'emoji': True}, 'value': '18'}, {'text': {'type': 'plain_text', 'text': 'UTC+7', 'emoji': True}, 'value': '19'}, {'text': {'type': 'plain_text', 'text': 'UTC+8', 'emoji': True}, 'value': '20'}, {'text': {'type': 'plain_text', 'text': 'UTC+9', 'emoji': True}, 'value': '21'}, {'text': {'type': 'plain_text', 'text': 'UTC+10', 'emoji': True}, 'value': '22'}, {'text': {'type': 'plain_text', 'text': 'UTC+11', 'emoji': True}, 'value': '23'}, {'text': {'type': 'plain_text', 'text': 'UTC+12', 'emoji': True}, 'value': '24'}]}},
#                                                                             {'type': 'input', 'block_id': 'working_days',
#                                                                              'label': {'type': 'plain_text', 'text': 'Working Days', 'emoji': True},
#                                                                              'optional': False, 'dispatch_action': False,
#                                                                              'element': {'type': 'checkboxes', 'action_id': 'checkboxes-action', 'options': [{'text': {'type': 'plain_text', 'text': 'Monday', 'emoji': True}, 'value': '0'}, {'text': {'type': 'plain_text', 'text': 'Tuesday', 'emoji': True}, 'value': '1'}, {'text': {'type': 'plain_text', 'text': 'Wednesday', 'emoji': True}, 'value': '2'}, {'text': {'type': 'plain_text', 'text': 'Thursday', 'emoji': True}, 'value': '3'}, {'text': {'type': 'plain_text', 'text': 'Friday', 'emoji': True}, 'value': '4'}, {'text': {'type': 'plain_text', 'text': 'Saturday', 'emoji': True}, 'value': '5'}, {'text': {'type': 'plain_text', 'text': 'Sunday', 'emoji': True}, 'value': '6'}]}},
#                                                                             {'type': 'input', 'block_id': 'working_hours_start', 'label': {'type': 'plain_text', 'text': 'Working Hours', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'timepicker', 'action_id': 'timepicker-action', 'initial_time': '12:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}},
#                                                                             {'type': 'input', 'block_id': 'working_hours_end', 'label': {'type': 'plain_text', 'text': '-', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'timepicker', 'action_id': 'timepicker-action', 'initial_time': '12:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}},
#                                                                             {'type': 'context', 'block_id': 'PUNb3', 'elements': [{'type': 'plain_text', 'text': 'Availability', 'emoji': True}]}, {'type': 'context', 'block_id': '6sTQ', 'elements': [{'type': 'plain_text', 'text': 'From-To-Status', 'emoji': True}]},
#                                                                             {'type': 'actions', 'block_id': 'index', 'elements': [{'type': 'timepicker', 'action_id': 'actionId-0', 'initial_time': '14:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}},
#                                                                                                                                   {'type': 'timepicker', 'action_id': 'actionId-1', 'initial_time': '15:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}},
#                                                                                                                                   {'type': 'static_select', 'action_id': 'actionId-2', 'placeholder': {'type': 'plain_text', 'text': 'Select an item', 'emoji': True}, 'options': [{'text': {'type': 'plain_text', 'text': 'High', 'emoji': True}, 'value': 'High'}, {'text': {'type': 'plain_text', 'text': 'Middle', 'emoji': True}, 'value': 'Middle'}, {'text': {'type': 'plain_text', 'text': 'Low', 'emoji': True}, 'value': 'Low'}]},
#                                                                                                                                   {'type': 'button', 'action_id': 'actionId-3', 'text': {'type': 'plain_text', 'text': 'X', 'emoji': True}, 'value': '0'}]}],
#  'private_metadata': '', 'callback_id': 'personal_profile', 'state': {'values': {'timezone': {'static_select-action': {'type': 'static_select', 'selected_option': None}}, 'working_days': {'checkboxes-action': {'type': 'checkboxes', 'selected_options': []}}, 'working_hours_start': {'timepicker-action': {'type': 'timepicker', 'selected_time': '12:00'}}, 'working_hours_end': {'timepicker-action': {'type': 'timepicker', 'selected_time': '12:00'}}, 'index': {'actionId-0': {'type': 'timepicker', 'selected_time': '14:00'}, 'actionId-1': {'type': 'timepicker', 'selected_time': '15:00'}, 'actionId-2': {'type': 'static_select', 'selected_option': None}}}}, 'hash': '1643579225.b3Zio4nQ', 'title': {'type': 'plain_text', 'text': 'My availability', 'emoji': True}, 'clear_on_close': False, 'notify_on_close': False, 'close': {'type': 'plain_text', 'text': 'Cancel', 'emoji': True}, 'submit': {'type': 'plain_text', 'text': 'Submit', 'emoji': True}, 'previous_view_id': None, 'root_view_id': 'V030RPEPXAR', 'app_id': 'A030Q8QHSCR', 'external_id': '', 'app_installed_team_id': 'T02V2ERJKFF', 'bot_id': 'B0305FAJ694'}





# {'id': 'V031JE34KR6', 'team_id': 'T02V2ERJKFF', 'type': 'modal',
#  'blocks': [{'type': 'divider', 'block_id': 'bmE7f'},
#             {'type': 'input', 'block_id': 'timezone', 'label': {'type': 'plain_text', 'text': 'Timezone', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'static_select', 'action_id': 'static_select-action', 'placeholder': {'type': 'plain_text', 'text': 'Select an item', 'emoji': True}, 'options': [{'text': {'type': 'plain_text', 'text': 'UTC-12', 'emoji': True}, 'value': '0'}, {'text': {'type': 'plain_text', 'text': 'UTC-11', 'emoji': True}, 'value': '1'}, {'text': {'type': 'plain_text', 'text': 'UTC-10', 'emoji': True}, 'value': '2'}, {'text': {'type': 'plain_text', 'text': 'UTC-9', 'emoji': True}, 'value': '3'}, {'text': {'type': 'plain_text', 'text': 'UTC-8', 'emoji': True}, 'value': '4'}, {'text': {'type': 'plain_text', 'text': 'UTC-7', 'emoji': True}, 'value': '5'}, {'text': {'type': 'plain_text', 'text': 'UTC-6', 'emoji': True}, 'value': '6'}, {'text': {'type': 'plain_text', 'text': 'UTC-5', 'emoji': True}, 'value': '7'}, {'text': {'type': 'plain_text', 'text': 'UTC-4', 'emoji': True}, 'value': '8'}, {'text': {'type': 'plain_text', 'text': 'UTC-3', 'emoji': True}, 'value': '9'}, {'text': {'type': 'plain_text', 'text': 'UTC-2', 'emoji': True}, 'value': '10'}, {'text': {'type': 'plain_text', 'text': 'UTC-1', 'emoji': True}, 'value': '11'}, {'text': {'type': 'plain_text', 'text': 'UTC', 'emoji': True}, 'value': '12'}, {'text': {'type': 'plain_text', 'text': 'UTC+1', 'emoji': True}, 'value': '13'}, {'text': {'type': 'plain_text', 'text': 'UTC+2', 'emoji': True}, 'value': '14'}, {'text': {'type': 'plain_text', 'text': 'UTC+3', 'emoji': True}, 'value': '15'}, {'text': {'type': 'plain_text', 'text': 'UTC+4', 'emoji': True}, 'value': '16'}, {'text': {'type': 'plain_text', 'text': 'UTC+5', 'emoji': True}, 'value': '17'}, {'text': {'type': 'plain_text', 'text': 'UTC+6', 'emoji': True}, 'value': '18'}, {'text': {'type': 'plain_text', 'text': 'UTC+7', 'emoji': True}, 'value': '19'}, {'text': {'type': 'plain_text', 'text': 'UTC+8', 'emoji': True}, 'value': '20'}, {'text': {'type': 'plain_text', 'text': 'UTC+9', 'emoji': True}, 'value': '21'}, {'text': {'type': 'plain_text', 'text': 'UTC+10', 'emoji': True}, 'value': '22'}, {'text': {'type': 'plain_text', 'text': 'UTC+11', 'emoji': True}, 'value': '23'}, {'text': {'type': 'plain_text', 'text': 'UTC+12', 'emoji': True}, 'value': '24'}]}}, {'type': 'input', 'block_id': 'working_days', 'label': {'type': 'plain_text', 'text': 'Working Days', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'checkboxes', 'action_id': 'checkboxes-action', 'options': [{'text': {'type': 'plain_text', 'text': 'Monday', 'emoji': True}, 'value': '0'}, {'text': {'type': 'plain_text', 'text': 'Tuesday', 'emoji': True}, 'value': '1'}, {'text': {'type': 'plain_text', 'text': 'Wednesday', 'emoji': True}, 'value': '2'}, {'text': {'type': 'plain_text', 'text': 'Thursday', 'emoji': True}, 'value': '3'}, {'text': {'type': 'plain_text', 'text': 'Friday', 'emoji': True}, 'value': '4'}, {'text': {'type': 'plain_text', 'text': 'Saturday', 'emoji': True}, 'value': '5'}, {'text': {'type': 'plain_text', 'text': 'Sunday', 'emoji': True}, 'value': '6'}]}}, {'type': 'input', 'block_id': 'working_hours_start', 'label': {'type': 'plain_text', 'text': 'Working Hours', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'timepicker', 'action_id': 'timepicker-action', 'initial_time': '12:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}}, {'type': 'input', 'block_id': 'working_hours_end', 'label': {'type': 'plain_text', 'text': '-', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'timepicker', 'action_id': 'timepicker-action', 'initial_time': '12:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}}, {'type': 'context', 'block_id': 'zGClF', 'elements': [{'type': 'plain_text', 'text': 'Availability', 'emoji': True}]}, {'type': 'context', 'block_id': 'T=1', 'elements': [{'type': 'plain_text', 'text': 'From-To-Status', 'emoji': True}]},
#             {'type': 'actions', 'block_id': '0', 'elements': [{'type': 'timepicker', 'action_id': '0.actionId-0', 'initial_time': '14:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}, {'type': 'timepicker', 'action_id': '0.actionId-1', 'initial_time': '15:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}, {'type': 'static_select', 'action_id': '0.actionId-2', 'placeholder': {'type': 'plain_text', 'text': 'Select an item', 'emoji': True}, 'options': [{'text': {'type': 'plain_text', 'text': 'High', 'emoji': True}, 'value': 'High'}, {'text': {'type': 'plain_text', 'text': 'Middle', 'emoji': True}, 'value': 'Middle'}, {'text': {'type': 'plain_text', 'text': 'Low', 'emoji': True}, 'value': 'Low'}]}, {'type': 'button', 'action_id': '0.actionId-3', 'text': {'type': 'plain_text', 'text': 'X', 'emoji': True}, 'value': '0'}]},
#             {'type': 'actions', 'block_id': '1', 'elements': [{'type': 'timepicker', 'action_id': '1.actionId-0', 'initial_time': '14:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}, {'type': 'timepicker', 'action_id': '1.actionId-1', 'initial_time': '15:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}, {'type': 'static_select', 'action_id': '1.actionId-2', 'placeholder': {'type': 'plain_text', 'text': 'Select an item', 'emoji': True}, 'options': [{'text': {'type': 'plain_text', 'text': 'High', 'emoji': True}, 'value': 'High'}, {'text': {'type': 'plain_text', 'text': 'Middle', 'emoji': True}, 'value': 'Middle'}, {'text': {'type': 'plain_text', 'text': 'Low', 'emoji': True}, 'value': 'Low'}]}, {'type': 'button', 'action_id': '1.actionId-3', 'text': {'type': 'plain_text', 'text': 'X', 'emoji': True}, 'value': '1'}]}, {'type': 'actions', 'block_id': '2', 'elements': [{'type': 'timepicker', 'action_id': '2.actionId-0', 'initial_time': '14:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}, {'type': 'timepicker', 'action_id': '2.actionId-1', 'initial_time': '15:00', 'placeholder': {'type': 'plain_text', 'text': 'Select time', 'emoji': True}}, {'type': 'static_select', 'action_id': '2.actionId-2', 'placeholder': {'type': 'plain_text', 'text': 'Select an item', 'emoji': True}, 'options': [{'text': {'type': 'plain_text', 'text': 'High', 'emoji': True}, 'value': 'High'}, {'text': {'type': 'plain_text', 'text': 'Middle', 'emoji': True}, 'value': 'Middle'}, {'text': {'type': 'plain_text', 'text': 'Low', 'emoji': True}, 'value': 'Low'}]}, {'type': 'button', 'action_id': '2.actionId-3', 'text': {'type': 'plain_text', 'text': 'X', 'emoji': True}, 'value': '2'}]}], 'private_metadata': '', 'callback_id': 'personal_profile', 'state': {'values': {'0': {'0.actionId-0': {'type': 'timepicker', 'selected_time': '14:00'}, '0.actionId-1': {'type': 'timepicker', 'selected_time': '15:00'}, '0.actionId-2': {'type': 'static_select', 'selected_option': None}}, '1': {'1.actionId-0': {'type': 'timepicker', 'selected_time': '14:00'}, '1.actionId-1': {'type': 'timepicker', 'selected_time': '15:00'}, '1.actionId-2': {'type': 'static_select', 'selected_option': None}}, '2': {'2.actionId-0': {'type': 'timepicker', 'selected_time': '14:00'}, '2.actionId-1': {'type': 'timepicker', 'selected_time': '15:00'}, '2.actionId-2': {'type': 'static_select', 'selected_option': None}}, 'timezone': {'static_select-action': {'type': 'static_select', 'selected_option': None}}, 'working_days': {'checkboxes-action': {'type': 'checkboxes', 'selected_options': []}}, 'working_hours_start': {'timepicker-action': {'type': 'timepicker', 'selected_time': '12:00'}}, 'working_hours_end': {'timepicker-action': {'type': 'timepicker', 'selected_time': '12:00'}}}}, 'hash': '1643580806.JerRAZO0', 'title': {'type': 'plain_text', 'text': 'My availability', 'emoji': True}, 'clear_on_close': False, 'notify_on_close': False, 'close': {'type': 'plain_text', 'text': 'Cancel', 'emoji': True}, 'submit': {'type': 'plain_text', 'text': 'Submit', 'emoji': True}, 'previous_view_id': None, 'root_view_id': 'V031JE34KR6', 'app_id': 'A030Q8QHSCR', 'external_id': '', 'app_installed_team_id': 'T02V2ERJKFF', 'bot_id': 'B0305FAJ694'}