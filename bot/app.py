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

from listeners import ListenerRegister, listen_events, listen_commands, listen_messages, listen_actions, listen_views, \
    listen_user_flow, listen_shortcuts

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
        self.init_database()

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
            listen_views,
            listen_user_flow,
            listen_shortcuts,
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
        # raise NotImplementedError("Database Initialization not yet implemented!")

    # Start/Close mode for server-ful modes, e.g. local WS based testing
    def start(self, socket_mode=False):
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
        db_name=os.environ.get("DB_NAME"),
        db_hostname=os.environ.get("DB_HOSTNAME"),
        db_username=os.environ.get("DB_USERNAME"),
        db_password=os.environ.get("DB_PASSWORD"),
    )
    bolt_app = SlackBoltApp(
        token=app_config.slack_bot_token,
        process_before_response=True,
    )

    app = SlackBotApp(config=app_config, bolt_app=bolt_app)
    logging.info("Starting slack bot app with lambda...")
    return app.start_lambda(event, context)


if __name__ == '__main__':
    logging.warning(msg=str(os.path.curdir))
    _app_config = SlackBotConfig(
        slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"),
        slack_signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    )

    _bolt_app = SlackBoltApp(
        token=_app_config.slack_bot_token,
        process_before_response=True,
    )
    _app = SlackBotApp(config=_app_config, bolt_app=_bolt_app)
    _app.start(socket_mode=False)

    atexit.register(_app.close)

