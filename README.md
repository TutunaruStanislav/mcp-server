# Translation MCP Server

MCP (Model Context Protocol) сервер для перевода текстов между английским,
русским и украинским языками через публичное бесплатное API
[MyMemory](https://mymemory.translated.net/doc/spec.php). API-ключ не требуется.

## Поддерживаемые языки

| Код | Язык |
|-----|------|
| `ENG` | English |
| `RUS` | Russian |
| `UKR` | Ukrainian |

## Инструменты (tools)

| Tool | Параметры | Назначение |
|------|-----------|------------|
| `translate_text` | `text`, `source_lang`, `target_lang` | Перевод с явным указанием языков |
| `translate_with_detection` | `text`, `target_lang` | Перевод с авто-определением языка источника |
| `detect_language` | `text` | Определение языка текста (ENG/RUS/UKR) |
| `get_supported_languages` | — | Список поддерживаемых языков |
| `check_api_health` | — | Проверка доступности API |

Языки в `source_lang` / `target_lang` задаются кодами `ENG`, `RUS`, `UKR`.
Определение языка (`detect_language` и `translate_with_detection`) работает по
эвристике на основе алфавита: латиница → `ENG`, кириллица с украинскими буквами
`і/ї/є/ґ` → `UKR`, прочая кириллица → `RUS`.

## Установка

Требуется **Python 3.8+**.

```bash
# Linux / macOS
cd translation-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```cmd
:: Windows
cd translation-server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

> Команда активации venv — единственное отличие между ОС:
> `source venv/bin/activate` (Linux/macOS) против `venv\Scripts\activate`
> (Windows). Деактивация везде — `deactivate`.

## Проверка установки

```bash
python test_tools.py
```

Ожидаемый результат — `Total: 6/6 tests passed`. Тест обращается к реальному
API, поэтому нужен интернет.

## Конфигурация (опционально)

Скопируйте `.env.example` в `.env` и при необходимости измените значения:

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `MYMEMORY_API_URL` | `https://api.mymemory.translated.net/get` | URL API |
| `TRANSLATION_TIMEOUT` | `10` | Timeout запроса, сек |
| `LOG_LEVEL` | `INFO` | Уровень логов: DEBUG / INFO / WARNING / ERROR |

## Интеграция с IDE

MCP-сервер запускается клиентом (IDE) как дочерний процесс и общается с ним
через stdio. Запускать `run.py` вручную для повседневной работы не нужно — это
делает IDE. Ниже — настройка для Claude Code и для VS Code + Cline.

> **Важно:** в `command` указывайте Python **из venv** (где установлены
> зависимости), а не системный `python`. Иначе клиент не найдёт пакет `mcp`.
> Путь к venv-интерпретатору:
> - Windows: `...\translation-server\venv\Scripts\python.exe`
> - Linux/macOS: `.../translation-server/venv/bin/python`

### Claude Code

Конфиг уже готов в `.claude/mcp.json` в корне репозитория:

```json
{
  "mcpServers": {
    "translation": {
      "command": "C:\\WORK\\3\\otus\\mcp-server\\translation-server\\venv\\Scripts\\python.exe",
      "args": ["C:\\WORK\\3\\otus\\mcp-server\\translation-server\\run.py"],
      "cwd": "C:\\WORK\\3\\otus\\mcp-server"
    }
  }
}
```

Поправьте пути под свою машину и перезапустите Claude Code. Проверить
подключение: команда `/mcp` должна показать сервер `translation` со статусом
`connected` и 5 инструментов.

### VS Code + Cline

[Cline](https://cline.bot) — расширение VS Code с поддержкой MCP.

1. Установите расширение **Cline** из Marketplace VS Code и откройте его панель.
2. В панели Cline нажмите иконку **MCP Servers** (стек серверов на верхней
   панели) → вкладка **Installed** / **Configure** → кнопку
   **Configure MCP Servers**. Откроется файл `cline_mcp_settings.json`.
3. Добавьте сервер `translation` и сохраните файл:

```json
{
  "mcpServers": {
    "translation": {
      "command": "C:\\WORK\\3\\otus\\mcp-server\\translation-server\\venv\\Scripts\\python.exe",
      "args": ["C:\\WORK\\3\\otus\\mcp-server\\translation-server\\run.py"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

   На Linux/macOS используйте прямые слэши и путь
   `.../translation-server/venv/bin/python`.
4. Cline перезапустит сервер автоматически после сохранения. В разделе
   **MCP Servers** напротив `translation` должен загореться зелёный индикатор,
   а ниже — появиться список из 5 инструментов.

> Cline не поддерживает поле `cwd`. Файл `.env` (если используется) Cline
> читать не будет — задавайте настройки через блок `env` в конфиге, например
> `"env": { "TRANSLATION_TIMEOUT": "20" }`. Значений по умолчанию достаточно
> для работы без `.env`.

### Проверка работы в IDE

Откройте чат агента и отправьте запросы — агент сам вызовет нужный tool.
Каждый tool возвращает структурированный JSON:

| Запрос | Tool | Результат (JSON) |
|--------|------|------------------|
| «Проверь, доступен ли API перевода» | `check_api_health` | `{"api_available": true, "status": "healthy"}` |
| «Какие языки поддерживаются?» | `get_supported_languages` | `{"ENG": "English", "RUS": "Russian", "UKR": "Ukrainian"}` |
| «Переведи "Hello, world!" с английского на русский» | `translate_text` | `{"source_lang": "ENG", "target_lang": "RUS", "original_text": "Hello, world!", "translated_text": "Привет, мир!"}` |
| «Переведи на русский: Good morning» | `translate_with_detection` | `{"detected_source_lang": "ENG", "target_lang": "RUS", ...}` |
| «Определи язык текста "Привіт, світ"» | `detect_language` | `{"detected_language": "UKR", "supported_languages": ["ENG", "RUS", "UKR"]}` |

Полный контракт результатов и трейс реальных вызовов — в `../REPORT.md` и
`verification.log` (генерируется скриптом `verify_mcp.py`).

Если инструменты не появились: проверьте путь к Python в конфиге, что
зависимости установлены (`pip list | findstr mcp`) и перезапустите IDE.

## Запуск вручную (для отладки)

```bash
python run.py
```

Сервер слушает stdio и пишет логи в stderr в формате
`YYYY-MM-DD HH:MM:SS - module - LEVEL - message`. Каждый вызов tool логирует
параметры, статус и результат. Перенаправление логов в файл:

```bash
python run.py 2> server.log
```

Сервер ждёт сообщения MCP по stdin, поэтому в пустом терминале он просто висит —
это нормально, им управляет IDE.

## Устранение неполадок

| Проблема | Решение |
|----------|---------|
| `ModuleNotFoundError: mcp` | Активируйте venv и `pip install -r requirements.txt`; в конфиге IDE укажите venv-Python |
| Сервер не подключается к IDE | Проверьте абсолютные пути в конфиге и `python --version` (≥ 3.8), перезапустите IDE |
| Tools не видны | Проверьте валидность JSON в конфиге, посмотрите логи MCP в IDE |
| Перевод падает с ошибкой | Проверьте интернет и что коды языков — только `ENG`, `RUS`, `UKR` |
| Медленный первый запрос | Норма: первое обращение к API инициализирует соединение |

## Структура

```
translation-server/
├── src/
│   ├── server.py        # MCP-сервер: регистрация и роутинг tools
│   ├── tools.py         # Реализация 5 tools + валидация
│   ├── api_client.py    # Клиент MyMemory API + детекция языка
│   └── __init__.py
├── run.py               # Точка входа
├── test_tools.py        # Проверка tools напрямую (6 кейсов)
├── verify_mcp.py        # E2E-проверка через реальный MCP-транспорт
├── requirements.txt
└── .env.example
```

Отчёт по заданию (принципы MCP, ссылки на код, контракт результатов,
проверочные запросы) — в `../REPORT.md`.

## Безопасность и лицензия

- API-ключи не используются (публичное API); `.env` исключён в `.gitignore`.
- Входные данные валидируются (коды языков, совпадение source/target).
- Лицензия: MIT.
