import asyncio
import logging
import uuid
from contextvars import ContextVar

from aiokafka import AIOKafkaConsumer

from .models import SendMessageRequest
from .processor import SendTgMessageProcessor

log = logging.getLogger(__name__)

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class SendOtpKafkaListener:
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topic_in: str,
        processor: SendTgMessageProcessor,
    ) -> None:
        self._topic = topic_in
        self._processor = processor
        self._consumer = AIOKafkaConsumer(
            topic_in,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=True,
            auto_offset_reset="latest",
            value_deserializer=lambda v: v.decode("utf-8"),
            key_deserializer=lambda v: v.decode("utf-8") if v is not None else None,
        )
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        await self._consumer.start()
        self._task = asyncio.create_task(self._run(), name="send-otp-kafka-listener")
        log.info("Kafka listener запущен на топике %s", self._topic)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self._consumer.stop()

    async def _run(self) -> None:
        try:
            async for record in self._consumer:
                request_id_var.set(str(uuid.uuid4()))
                try:
                    log.info(
                        "Получен запрос на отправку сообщения: topic=%s partition=%s offset=%s value=%s",
                        record.topic,
                        record.partition,
                        record.offset,
                        record.value,
                    )
                    request = SendMessageRequest.model_validate_json(record.value)
                    await self._processor.process(request)
                except Exception as e:
                    log.error("Ошибка обработки сообщения топика: %s", e, exc_info=True)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.error("Kafka listener аварийно остановлен: %s", e, exc_info=True)
            raise
