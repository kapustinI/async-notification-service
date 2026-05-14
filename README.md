# Async Notification Service
Сервис для асинхронной отправки уведомлений

## Архитектура

- **API**: Flask
- **Worker**: Celery
- **Broker**: Redis
- **DB**: PostgreSQL
- **Контейнеры**: Docker Compose

Поток обработки:
1. Клиент отправляет `POST /api/v1/notifications`.
2. API валидирует payload, сохраняет запись в БД со статусом `pending`.
3. API ставит задачу в очередь Redis.
4. Worker забирает задачу, имитирует отправку, обновляет статус:
   - `sent` при успехе
   - `failed` + `error_text` при ошибке

## Структура проекта

```text
app/
  __init__.py
  config.py
  extensions.py
  models.py
  tasks.py
  api/
    __init__.py
    notification.py
  utils/
    validators.py
tests/
  conftest.py
  test_validators.py
  test_api.py
  test_tasks.py
docker-compose.yml
Dockerfile
requirements.txt
.env.example
request.http
README.md
```

## Запуск
1. Скопировать env-шаблон: 
`Copy-Item .env.example .env`
2. Поднять сервисы:
`docker compose up --build`
3. Проверить health:
`curl http://localhost:8000/health`

### `POST /api/v1/notifications`

Создать уведомление и поставить задачу в очередь.

Пример запроса:

```json
{
  "type": "email",
  "recipient": "1@mail.com",
  "subject": "test",
  "message": "test",
  "channel_data": {
    "template_id": "test1"
  }
}
```
Пример ответа:
```json
{
  "id": "uuid",
  "status": "queued"
}
```

### `GET /api/v1/notifications/<id>`

Получить статус конкретного уведомления.

Пример ответа:

```json
{
  "id": "uuid",
  "status": "pending",
  "error": null
}
```

### `GET /api/v1/notifications?status=&limit=&offset=`

Получить список уведомлений с фильтром и пагинацией.

Пример запроса:

```text
GET /api/v1/notifications?status=failed&limit=10&offset=0
```

Пример ответа:

```json
[
  {
    "id": "9f85d9be-2f34-4f6f-84b0-756f3fcb7f7f",
    "status": "failed",
    "error": "error"
  },
  {
    "id": "fe3a09dc-ff22-4db3-8bc9-e4f4f45dcab0",
    "status": "failed",
    "error": "error"
  }
]
```

## Валидация

- Обязательные поля:
  - `type`
  - `recipient`
  - `message`
- Допустимые значения `type`:
  - `email`
  - `sms`
  - `telegram`
- Для `email` проверяется корректность email-адреса.
- Для `sms` и `telegram` проверяется телефон в формате `+` и 11 цифр (пример: `+79991234567`).
- `channel_data` (если передан) должен быть JSON-объектом.

## Просмотр логов

```bash
docker compose logs -f api
docker compose logs -f worker
```
## Тесты
Запуск всех тестов:
```bash
pytest -q
```
Запуск отдельных наборов:
```bash
pytest -q tests/test_validators.py
pytest -q tests/test_api.py
pytest -q tests/test_tasks.py
```