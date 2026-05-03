import logging

from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

log = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        try:
            await message.answer(f"Привет, твой идентификатор в телеграм: {message.chat.id}")
        except Exception as e:
            log.error(
                "Exception at start command %s: %s",
                message.chat.id,
                e,
                exc_info=True,
            )

    @dp.message()
    async def on_any_message(message: Message) -> None:
        log.info("Update: %s", message.model_dump_json(exclude_none=True))

    return dp
