from dataclasses import dataclass, field


@dataclass
class SlackBotConfig:
    """
    Slack secrets
    """
    slack_bot_token: str
    # Optional, token used for websocket mode
    slack_app_token: str = ""
    # Optional, token used for non-websocket mode
    slack_signing_secret: str = ""

    """
    Runtime configs
    """
    debug: bool = False

    """
    Database
    """
    # database name, default for in-memory sqlite db
    db_name: str = ":memory:"

    # hostname/ip of the database, empty for local sqlite
    db_hostname: str = ""

    # Optional, for prod mysql database
    db_username: str = ""
    db_password: str = ""

    db_url: str = field(init=False)

    def __post_init__(self):
        if not self.db_hostname or self.db_hostname.lower() == "localhost":
            self.db_url = f"sqlite://{self.db_name}"
        else:
            self.db_url = f"mysql://{self.db_username}:{self.db_password}@{self.db_hostname}/{self.db_name}"

    def db_in_prod(self) -> bool:
        return self.db_url.startswith("mysql")
