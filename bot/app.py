import atexit
import os
from typing import Optional

from peewee import SqliteDatabase
from slack_bolt import App as SlackBoltApp
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import SlackBotConfig
from db.database import new_sqlite_database
from db.utils import init_db_if_not
from middlewares import MiddlewareRegister, global_middlewares
from listeners import ListenerRegister, listen_events, listen_commands, listen_messages


class SlackBotApp:
    def __init__(self, config: SlackBotConfig,
                 bolt_app: SlackBoltApp):
        self.config = config
        self.bolt_app = bolt_app  # Note DI for better testing

        self._socket_mode_handler: Optional[SocketModeHandler] = None

        self.logger = None  # TODO!

        # Init database
        self.db: SqliteDatabase = new_sqlite_database(config.db_name)
        # self.init_database()

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
            register(self.bolt_app)

    def register_middlewares(self, *middleware_register: MiddlewareRegister):
        for register in middleware_register:
            register(self.bolt_app)

    def init_database(self):
        assert self.db
        self.db.connect()

        init_db_if_not(self.db)

        # TODO: Init database schema when obsolete
        raise NotImplementedError("Database Initialization not yet implemented!")

    def start(self, socket_mode=True):
        if socket_mode:
            self._socket_mode_handler = SocketModeHandler(self.bolt_app, self.config.slack_app_token)
            self._socket_mode_handler.start()

    def close(self):
        if self._socket_mode_handler:
            self._socket_mode_handler.close()
        self.db.close()


# Start your app
if __name__ == "__main__":
    _app_config = SlackBotConfig(
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),
        slack_app_token=os.environ.get("SLACK_APP_TOKEN"),
        debug=True,  # Turning on debug now
        db_name=":memory:",  # Use memory for now
    )

    _bolt_app = SlackBoltApp(
        token=_app_config.slack_bot_token,
    )

    _app = SlackBotApp(config=_app_config, bolt_app=_bolt_app)
    _app.start()

    atexit.register(_app.close)
