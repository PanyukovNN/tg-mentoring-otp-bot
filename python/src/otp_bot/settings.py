from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    bot_token: str = Field(..., alias="TG_BOT_TOKEN")
    bot_name: str = Field("", alias="TG_BOT_NAME")

    kafka_bootstrap_servers: str = Field(..., alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_group_id: str = Field("tg-mentoring-otp-bot", alias="KAFKA_GROUP_ID")
    kafka_send_otp_enabled: bool = Field(True, alias="KAFKA_SEND_OTP_ENABLED")
    kafka_topic_in: str = Field("Send.Otp.IN.V1", alias="KAFKA_TOPIC_IN")
    kafka_topic_out: str = Field("Send.Otp.OUT.V1", alias="KAFKA_TOPIC_OUT")

    server_port: int = Field(8011, alias="SERVER_PORT")
    timezone: str = Field("Europe/Moscow", alias="TZ")
