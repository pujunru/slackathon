from typing import Callable, NoReturn
from slack_bolt import App

MiddlewareRegister = Callable[[App], NoReturn]


def global_middlewares(app: App):
    @app.use
    def global_log_request(logger, body, next):
        logger.info(body)
        return next()

    @app.error
    def global_err_handler(error, body, logger):
        logger.exception(f"Error: {error}")
        logger.info(f"Request body: {body}")
