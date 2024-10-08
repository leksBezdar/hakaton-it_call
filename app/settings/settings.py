from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TEST_MODE: bool = Field(default=False)

    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int

    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str
    TEST_DB_HOST: str
    TEST_DB_PORT: int

    KAFKA_URL: str = Field(default="kafka:29092")
    user_subscribed_event_topic: str = Field(default="user_subscribed_topic")
    user_unsubscribed_event_topic: str = Field(default="user_unsubscribed_topic")

    CONFIRM_URL: str
    UNSUBSCRIBE_URL: str
    MAIN_PAGE_URL: str

    SEND_TIME: str = Field(default="12:00")

    SENDER_MAIL: str
    SMTP_APP_PASSWORD: str
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)

    @property
    def SMTP_URL(self) -> tuple[str, int]:
        return (self.SMTP_HOST, self.SMTP_PORT)

    REDIS_HOST: str = Field(default="redis-it_call")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:"
            f"{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )

    ALLOWED_CORS_ORIGINS: list[str] = Field(default=["*"])
    ALLOWED_CORS_ORIGIN_REGEX: str


settings = Settings()
