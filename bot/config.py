from dataclasses import dataclass


@dataclass
class SlackBotConfig:
    """
    Slack secrets
    """
    slack_bot_token: str
    slack_app_token: str

    """
    Runtime configs
    """
    debug: bool = False

    """
    Database
    """
    db_name: str = ":memory:"
