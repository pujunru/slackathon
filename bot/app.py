import atexit
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
from listeners import ListenerRegister, listen_events, listen_commands, listen_messages
from runtime import SlackBotRuntime


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
            raise NotImplementedError("SlackBotApp modes other than websocket not yet implemented")

    def close(self):
        if self._socket_mode_handler:
            self._socket_mode_handler.close()
        self.db.close()

    def start_lambda(self, event, context):
        self._lambda_mode_handler = SlackRequestHandler(self.bolt_app)
        self._lambda_mode_handler.handle(event, context)


def lambda_handler(event, context):
    _app_config = SlackBotConfig(
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),
        slack_signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
        db_name=os.environ.get("DB_NAME"),
        db_hostname=os.environ.get("DB_HOSTNAME"),
        db_username=os.environ.get("DB_USERNAME"),
        db_password=os.environ.get("DB_PASSWORD"),
    )
    _bolt_app = SlackBoltApp(
        token=_app_config.slack_bot_token,
        process_before_response=True,
    )

    _app = SlackBotApp(config=_app_config, bolt_app=_bolt_app)
    _app.start_lambda(event, context)
