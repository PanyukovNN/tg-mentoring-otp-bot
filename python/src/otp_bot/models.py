from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SendMessageStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    telegram_chat_id: str | None = Field(None, alias="telegramChatId")
    message: str | None = None


class SendMessageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    status: SendMessageStatus
    error_message: str | None = Field(None, alias="errorMessage")

    def to_json(self) -> str:
        return self.model_dump_json(by_alias=True, exclude_none=True)
