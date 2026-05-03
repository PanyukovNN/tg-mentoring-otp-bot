import logging

from aiokafka import AIOKafkaProducer

from .models import SendMessageResponse

log = logging.getLogger(__name__)


class SendOtpKafkaProducer:
    def __init__(self, bootstrap_servers: str, topic_out: str) -> None:
        self._topic = topic_out
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            acks="all",
            value_serializer=lambda v: v.encode("utf-8"),
            key_serializer=lambda v: v.encode("utf-8") if v is not None else None,
        )

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def send_response(self, response: SendMessageResponse) -> None:
        try:
            payload = response.to_json()
            metadata = await self._producer.send_and_wait(self._topic, payload)
            log.info("Ответ отправлен: %s", metadata)
        except Exception as e:
            log.error("Ошибка при отправке ответа в kafka: %s", e, exc_info=True)
