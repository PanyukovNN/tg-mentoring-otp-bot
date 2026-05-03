#!/usr/bin/env bash
# Единоразовый скрипт деплоя Python-версии tg-mentoring-otp-bot на удалённый сервер по SSH.
# При первом запуске клонирует репозиторий на сервер, при последующих — pull + rebuild.
# Перед SSH-командами заливает локальный python/deploy/config.env на сервер.
#
# Использование: ./python/deploy/deploy.sh
#
# Переменные окружения (опционально):
#   REMOTE_HOST        — алиас SSH (по умолчанию: nvpnt)
#   REMOTE_PROJECT_DIR — путь к репозиторию на сервере, относительно $HOME (по умолчанию: tg-mentoring-otp-bot)
#   GIT_REPO_URL       — URL для первого клона (по умолчанию https://github.com/PanyukovNN/tg-mentoring-otp-bot.git)
#   COMMON_CONFIG      — путь до локального ~/common-config/config.env, если хочешь синхронизировать и его
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-nvpnt}"
REMOTE_PROJECT_DIR="${REMOTE_PROJECT_DIR:-tg-mentoring-otp-bot}"
GIT_REPO_URL="${GIT_REPO_URL:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_CONFIG="${SCRIPT_DIR}/config.env"

if [[ ! -f "${LOCAL_CONFIG}" ]]; then
    echo "ERROR: не найден ${LOCAL_CONFIG}" >&2
    echo "Создай его: cp ${SCRIPT_DIR}/config.env.example ${SCRIPT_DIR}/config.env и заполни" >&2
    exit 1
fi

echo "==> Проверяю наличие репозитория на ${REMOTE_HOST}:~/${REMOTE_PROJECT_DIR}"
if ! ssh "${REMOTE_HOST}" "[ -d ${REMOTE_PROJECT_DIR}/.git ]"; then
    GIT_REPO_URL="${GIT_REPO_URL:-https://github.com/PanyukovNN/tg-mentoring-otp-bot.git}"
    echo "==> Клонирую ${GIT_REPO_URL} в ~/${REMOTE_PROJECT_DIR}"
    ssh "${REMOTE_HOST}" "git clone ${GIT_REPO_URL} ${REMOTE_PROJECT_DIR}"
fi

echo "==> Заливаю креды на ${REMOTE_HOST}:~/${REMOTE_PROJECT_DIR}/python/deploy/config.env"
ssh "${REMOTE_HOST}" "mkdir -p ${REMOTE_PROJECT_DIR}/python/deploy"
scp -q "${LOCAL_CONFIG}" "${REMOTE_HOST}:${REMOTE_PROJECT_DIR}/python/deploy/config.env"
ssh "${REMOTE_HOST}" "chmod 600 ${REMOTE_PROJECT_DIR}/python/deploy/config.env"

if [[ -n "${COMMON_CONFIG:-}" ]]; then
    if [[ ! -f "${COMMON_CONFIG}" ]]; then
        echo "ERROR: указан COMMON_CONFIG=${COMMON_CONFIG}, но файл не найден" >&2
        exit 1
    fi
    echo "==> Заливаю common-config на ${REMOTE_HOST}:~/common-config/config.env"
    ssh "${REMOTE_HOST}" "mkdir -p common-config"
    scp -q "${COMMON_CONFIG}" "${REMOTE_HOST}:common-config/config.env"
    ssh "${REMOTE_HOST}" "chmod 600 common-config/config.env"
else
    echo "==> Создаю пустой ~/common-config/config.env, если отсутствует"
    ssh "${REMOTE_HOST}" "mkdir -p common-config && touch common-config/config.env && chmod 600 common-config/config.env"
fi

echo "==> Деплой tg-mentoring-otp-bot (python) на ${REMOTE_HOST}..."
ssh -o BatchMode=no "${REMOTE_HOST}" bash -s <<EOF
set -euo pipefail

if command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    DC="docker compose"
fi

cd ~/${REMOTE_PROJECT_DIR}
echo "==> git pull"
git pull --ff-only

cd python
echo "==> \${DC} down"
\${DC} down || true

echo "==> \${DC} up -d --build"
\${DC} up -d --build

echo "==> Текущий статус:"
docker ps --filter name=tg-mentoring-otp-bot-py --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
EOF

echo "==> Готово"
