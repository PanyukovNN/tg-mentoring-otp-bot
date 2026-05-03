import logging

from aiogram import Bot

from .kafka_producer import SendOtpKafkaProducer
from .models import SendMessageRequest, SendMessageResponse, SendMessageStatus

log = logging.getLogger(__name__)


class SendTgMessageProcessor:
    def __init__(self, bot: Bot, producer: SendOtpKafkaProducer) -> None:
        self._bot = bot
        self._producer = producer

    async def process(self, request: SendMessageRequest) -> None:
        try:
            await self._bot.send_message(
                chat_id=request.telegram_chat_id,
                text=request.message,
            )
            response = SendMessageResponse(id=request.id, status=SendMessageStatus.SUCCESS)
            await self._producer.send_response(response)
        except Exception as e:
            log.warning(
                "Не удалось отправить сообщение в чат. Запрос: %s. Ошибка: %s",
                request.model_dump_json(exclude_none=True),
                e,
                exc_info=True,
            )
            response = SendMessageResponse(
                id=request.id,
                status=SendMessageStatus.ERROR,
                error_message=f"Не удалось отправить сообщение в чат: {e}",
            )
            await self._producer.send_response(response)
