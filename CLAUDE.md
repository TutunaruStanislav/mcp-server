# Translation MCP Server

MCP-сервер для перевода текстов между английским, русским и украинским языками
через публичное бесплатное API MyMemory (без API-ключа).

Полная документация пользователя и инструкции по интеграции с IDE (Claude Code,
VS Code + Cline) — в **`translation-server/README.md`**.

## Структура

```
mcp-local/
├── translation-server/
│   ├── src/
│   │   ├── server.py       # MCP-сервер: setup_logging, create_server, main
│   │   ├── tools.py        # 5 tools + валидация входных данных
│   │   ├── api_client.py   # MyMemoryAPIClient: translate, detect_language, check_health
│   │   └── __init__.py
│   ├── run.py              # Точка входа (asyncio.run(main))
│   ├── test_tools.py       # Проверка tools напрямую (6 кейсов)
│   ├── verify_mcp.py       # E2E-проверка через реальный MCP-транспорт
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md           # Документация пользователя
├── .claude/mcp.json        # Конфиг MCP-сервера для Claude Code
├── REPORT.md               # Отчёт: принципы MCP, ссылки на код, контракт
└── CLAUDE.md
```

## Архитектура

- `server.py` — создаёт `Server('translation-server')`, регистрирует
  `list_tools` и `call_tool`, маршрутизирует вызовы в функции из `tools.py`,
  запускается через `stdio_server()` + `server.run(...)`.
- `tools.py` — определения tools (`get_tools`) и их реализация. Валидирует коды
  языков и совпадение source/target до обращения к API. Каждый tool возвращает
  структурированный объект; `server._json_content` сериализует его в JSON
  (`ensure_ascii=False`).
- `api_client.py` — HTTP-клиент MyMemory. `detect_language` использует
  эвристику по алфавиту (латиница → ENG; кириллица с `і/ї/є/ґ` → UKR; иначе RUS),
  т.к. у MyMemory нет эндпоинта детекции.

## Tools

1. `translate_text` — перевод с явным указанием языков.
2. `translate_with_detection` — перевод с авто-определением языка источника.
3. `detect_language` — определение языка текста.
4. `get_supported_languages` — список поддерживаемых языков.
5. `check_api_health` — проверка доступности API.

Коды языков: `ENG`, `RUS`, `UKR`.

## Запуск и проверка

```bash
cd translation-server
python -m venv venv && venv\Scripts\activate   # Windows; см. README для Linux/macOS
pip install -r requirements.txt
python test_tools.py                            # ожидается 6/6 passed
```

В IDE сервер запускается автоматически по конфигу (`.claude/mcp.json` для
Claude Code). Команды активации venv и настройка Cline — в README.

## Логирование

Логи пишутся в stderr в формате
`YYYY-MM-DD HH:MM:SS - module - LEVEL - message`. Уровень задаётся переменной
`LOG_LEVEL` (по умолчанию `INFO`). Каждый tool логирует вызов, статус и результат.

## Требования к коду

- PEP8, type hints, краткие docstrings.
- Обработка исключений в каждом tool и в API-клиенте.
- Секреты не коммитятся (`.gitignore`); API-ключи не используются.

## Возможные улучшения

- [ ] Unit-тесты (pytest) вместо/в дополнение к `test_tools.py`.
- [ ] Кэширование переводов.
- [ ] Расширение списка языков.
- [ ] Batch-перевод.
