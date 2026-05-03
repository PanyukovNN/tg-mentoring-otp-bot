# tg-mentoring-otp-bot — Python

Python-порт Java-версии. Цель — снизить потребление памяти на сервере (JVM-сервисы тяжёлые).

## Стек

- Python 3.12, src-layout, hatchling (pyproject.toml)
- aiogram 3 — Telegram-бот (long polling)
- aiokafka — consumer/producer для Kafka
- aiohttp — HTTP-эндпоинт `/actuator/health`
- pydantic 2 — валидация конфигов и DTO

## Структура

```
python/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── README.md
├── deploy/
│   ├── deploy.sh             # SSH-деплой на nvpnt
│   └── config.env.example
└── src/
    └── otp_bot/
        ├── __init__.py
        ├── __main__.py        # точка входа (console script `otp-bot`)
        ├── settings.py        # переменные окружения через pydantic-settings
        ├── models.py          # SendMessageRequest/Response, SendMessageStatus
        ├── bot.py             # Telegram dispatcher: /start
        ├── kafka_listener.py  # consumer Send.Otp.IN.V1
        ├── kafka_producer.py  # producer Send.Otp.OUT.V1
        └── processor.py       # отправка TG-сообщения и ответа в Kafka
```

## Соответствие Java-версии

| Java | Python |
| --- | --- |
| `TgBotApi` + `TgBotConfig` | `bot.build_dispatcher()` + `aiogram.Bot` в `__main__` |
| `StartCommand` | `bot.on_start` |
| `TgBotListener` | `bot.on_any_message` |
| `SendOtpKafkaListener` | `kafka_listener.SendOtpKafkaListener` |
| `SendOtpKafkaProducer` | `kafka_producer.SendOtpKafkaProducer` |
| `SendTgMessageProcessor` | `processor.SendTgMessageProcessor` |
| `SendMessageRequest/Response/Status` | `models.*` |
| `JsonUtil` | pydantic `model_validate_json` / `model_dump_json` |

## Запуск локально

```bash
cd python
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

cp deploy/config.env.example deploy/config.env  # заполнить
set -a; source deploy/config.env; set +a

otp-bot
```

## Запуск в Docker

```bash
cd python
cp deploy/config.env.example deploy/config.env  # заполнить
docker compose up -d --build
```

## Деплой на удалённый сервер

```bash
./python/deploy/deploy.sh
```

Скрипт по SSH (хост `nvpnt`, переопределяется через `REMOTE_HOST`) выполняет на сервере:
- если репозитория ещё нет — `git clone` (нужен `GIT_REPO_URL` или `origin`),
- иначе `git pull` → `docker compose down` → `docker compose up -d --build`.

Перед первым деплоем нужно один раз:
- создать локально `python/deploy/config.env` (см. `config.env.example`).
- В нём `KAFKA_BOOTSTRAP_SERVERS=81.30.105.54:29092` — Kafka на новом сервере.
- При необходимости положить `~/common-config/config.env` (например, через `COMMON_CONFIG=...`).

### Переменные окружения

| Переменная | Описание | Дефолт |
| --- | --- | --- |
| `TG_BOT_TOKEN` | токен Telegram-бота | — |
| `TG_BOT_NAME` | имя бота | `""` |
| `KAFKA_BOOTSTRAP_SERVERS` | `host:port` Kafka | — |
| `KAFKA_GROUP_ID` | group id consumer-а | `tg-mentoring-otp-bot` |
| `KAFKA_SEND_OTP_ENABLED` | включить consumer/producer | `true` |
| `KAFKA_TOPIC_IN` | входящий топик | `Send.Otp.IN.V1` |
| `KAFKA_TOPIC_OUT` | топик ответов | `Send.Otp.OUT.V1` |
| `SERVER_PORT` | порт `/actuator/health` | `8011` |
| `TZ` | таймзона | `Europe/Moscow` |
