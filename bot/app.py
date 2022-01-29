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
from listeners import ListenerRegister, listen_events, listen_commands, listen_messages, listen_actions, listen_views
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



if __name__ == '__main__':
    _app_config = SlackBotConfig(
        # slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),
        slack_bot_token="xoxb-2988501631525-3024827153457-VJaaPBMI5c5tLYsWp7KtPhBg",
        # slack_app_token=os.environ.get("SLACK_APP_TOKEN"),
        slack_app_token="xapp-1-A030Q8QHSCR-3035935418416-11bc253051d4dda96d0c33817792c67bc0214972a204893da568e146740553ac",
        debug=True,  # Turning on debug now
        db_name=":memory:",  # Use memory for now
    )

    _bolt_app = SlackBoltApp(
        token=_app_config.slack_bot_token,
        process_before_response=True,
    )
    _app = SlackBotApp(config=_app_config, bolt_app=_bolt_app)
    _app.start()

    atexit.register(_app.close)
