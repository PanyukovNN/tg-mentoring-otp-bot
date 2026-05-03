import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from .bot import build_dispatcher
from .kafka_listener import SendOtpKafkaListener
from .kafka_producer import SendOtpKafkaProducer
from .processor import SendTgMessageProcessor
from .settings import Settings


async def _run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stdout,
    )
    log = logging.getLogger(__name__)

    settings = Settings()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    producer: SendOtpKafkaProducer | None = None
    listener: SendOtpKafkaListener | None = None
    if settings.kafka_send_otp_enabled:
        producer = SendOtpKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            topic_out=settings.kafka_topic_out,
        )
        await producer.start()
        log.info("Kafka producer запущен")

        processor = SendTgMessageProcessor(bot=bot, producer=producer)
        listener = SendOtpKafkaListener(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            topic_in=settings.kafka_topic_in,
            processor=processor,
        )
        await listener.start()
    else:
        log.info("Kafka send-otp выключен (KAFKA_SEND_OTP_ENABLED=false)")

    dispatcher = build_dispatcher()
    http_app = _build_http_app()
    runner = web.AppRunner(http_app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=settings.server_port)
    await site.start()
    log.info("HTTP сервер запущен на порту %s", settings.server_port)

    try:
        await dispatcher.start_polling(bot, handle_signals=True)
    finally:
        log.info("Остановка приложения...")
        if listener is not None:
            await listener.stop()
        if producer is not None:
            await producer.stop()
        await runner.cleanup()
        await bot.session.close()


def _build_http_app() -> web.Application:
    async def health_handler(_request: web.Request) -> web.Response:
        return web.json_response({"status": "UP"})

    app = web.Application()
    app.router.add_get("/actuator/health", health_handler)
    return app


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
