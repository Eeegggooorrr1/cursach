# Course Adapt

## Описание проекта

## Возможности

## Структура проекта

Проект разделен на серверную часть, клиентскую часть и общий слой запуска.

```text
backend/              
  ai/                 интеграция с LLM, шаблоны и контракты генерации
  cli/                модуль cli-скриптов
  core/               конфиг, DI, настройки бд, auth, кэш, логи
  handlers/           HTTP-ручки FastAPI
  migration/          миграции
  models/             SQLAlchemy-модели
  repositories/       слой работы с бд
  schemas/            Pydantic-схемы
  seed/               начальные данные
  services/           бизнес-логика
  tests/              тесты

frontend/             
  nginx/              конфиг nginx для сборки
  src/                
    api/              клиентские запросы и типы API
    assets/           стили и статические ресурсы
    components/       переиспользуемые Vue-компоненты
    composables/      общая логика
    router/           роутинг
    stores/           хранилища
    utils/            вспомогательные функции
    views/            страницы приложения

logs/                 локальные файловые логи бэка
```

## Введение в эксплуатацию

### Требования

Для запуска проекта нужны Docker, Docker Compose и `make`.

### Настройка окружения

Перед первым запуском нужно создать env-файлы из шаблонов:

```bash
cp .env.example .env
cp .env.test.example .env.test
```

В `.env` указываются настройки основного приложения, в `.env.test` - настройки тестового окружения.

### Запуск приложения

Проект поднимается из корня одной командой:

```bash
make up
```

После запуска frontend будет доступен по адресу:

```text
http://localhost:8080
```

Backend будет доступен по адресу:

```text
http://localhost:8000
```

Если нужно остановить проект:

```bash
make down
```

Перезапуск выполняется так:

```bash
make restart
```

### Миграции и начальные данные

При обычном запуске миграции и начальные данные применяются автоматически. Если нужно выполнить эти шаги отдельно, можно использовать:

```bash
make migrate
make seed
```

Или одной командой:

```bash
make init
```

### Логи

Логи контейнеров доступны через:

```bash
make logs
```

Backend пишет файл логов в:

```text
logs/backend/backend.log
```

### Тесты

Полная проверка проекта запускается командой:

```bash
make test
```

Backend и frontend можно проверить отдельно:

```bash
make test-backend
make test-frontend
```

### Команды Makefile

```text
make build          собрать образы
make build-backend  собрать backend-образ
make up             поднять приложение
make down           остановить приложение
make restart        перезапустить приложение
make logs           смотреть логи
make migrate        применить миграции
make seed           загрузить начальные данные
make init           выполнить migrate и seed
make test           запустить все проверки
make test-backend   запустить backend-тесты
make test-frontend  запустить frontend-проверки
make test-down      остановить тестовый контур
make clean          удалить контейнеры и volumes
```
