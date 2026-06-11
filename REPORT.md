# Отчёт: Translation MCP Server

Отчёт по заданию: реализация MCP-сервера переводов, интеграция с IDE,
проверочные вызовы инструментов, ссылки на код. Пользовательская инструкция
(установка, запуск, интеграция с Claude Code и VS Code + Cline) — в
`translation-server/README.md`.

## 1. Принципы MCP

**Как IDE/агент подключается к серверу.** IDE (Claude Code, VS Code + Cline и
т.п.) выступает MCP-клиентом. По конфигу (`.claude/mcp.json` для Claude Code или
`cline_mcp_settings.json` для Cline) клиент запускает сервер как дочерний процесс
(`command` + `args`) и общается с ним по транспорту **stdio**: сообщения
MCP (JSON-RPC) идут через stdin/stdout, а логи — в stderr. При старте выполняется
рукопожатие (`initialize`), после чего клиент запрашивает список инструментов
(`tools/list`) и вызывает их (`tools/call`). Агент сам решает, какой инструмент и
с какими аргументами вызвать, опираясь на их описания и схемы.

**Что считается «tool».** В этом сервере tool — это именованная операция,
объявленная в `get_tools()` с человекочитаемым описанием и JSON Schema входных
параметров (`inputSchema`); за каждым tool стоит отдельная Python-функция-
реализация. Tool возвращает **структурированный JSON-объект** (а не свободный
текст), что позволяет агенту надёжно разбирать результат. Реализовано 5 tools:
`translate_text`, `translate_with_detection`, `detect_language`,
`get_supported_languages`, `check_api_health`.

## 2. Реализация — ссылки на код

### Поднятие сервера и регистрация инструментов

- **Поднятие сервера:** `translation-server/src/server.py:L114–L128` —
  `main()`: транспорт `stdio_server()` + `server.run(...)`.
- **Создание сервера и регистрация tools:** `src/server.py:L47–L111` —
  `create_server()`: `Server('translation-server')` (L51), регистрация
  `list_tools` (L53–L58) и `call_tool` (L60–L108).
- **Объявление инструментов (имена, описания, `inputSchema`):**
  `src/tools.py:L11–L100` — `get_tools()`.
- **Единый формат результата (JSON):** `src/server.py:L39–L44` —
  `_json_content()` (`json.dumps(..., ensure_ascii=False)`).

### Инструменты

| Tool | Реализация | Строки логов | Пример вывода |
|------|-----------|--------------|---------------|
| `translate_text` | `tools.py:L103–L152` | вызов `L111–L117`, результат `L134–L138` | `verification.log:L21–L29` |
| `translate_with_detection` | `tools.py:L155–L206` | вызов `L162–L167`, детекция `L178`, результат `L187–L192` | `verification.log:L31–L40` |
| `detect_language` | `tools.py:L209–L232` | вызов `L213–L216`, результат `L227–L230` | `verification.log:L42–L48` |
| `get_supported_languages` | `tools.py:L235–L250` | вызов `L239`, результат `L243–L248` | `verification.log:L16–L19` |
| `check_api_health` | `tools.py:L253–L270` | вызов `L257`, результат `L266–L269` | `verification.log:L10–L14` |

Диспетчеризация вызовов и логирование статуса success/error —
`src/server.py:L69–L108`.

### API-клиент (MyMemory)

- `src/api_client.py:L45–L102` — `translate()` (HTTP-запрос к MyMemory).
- `src/api_client.py:L104–L130` — `detect_language()` (эвристика по алфавиту:
  латиница → ENG, кириллица с `і/ї/є/ґ` → UKR, иначе RUS).
- `src/api_client.py:L31–L43` — `check_health()`.

## 3. Tool outputs contract

Каждый tool возвращает `TextContent(type='text', text=<JSON>)`, где `<JSON>` —
сериализованный объект (`server.py:_json_content`, L39–L44). Контракт по tool:

```jsonc
// translate_text
{"source_lang":"ENG","target_lang":"RUS",
 "original_text":"Hello, world!","translated_text":"Привет, мир!"}

// translate_with_detection
{"detected_source_lang":"ENG","target_lang":"RUS",
 "original_text":"Good morning","translated_text":"Доброе утро"}

// detect_language
{"detected_language":"UKR","supported_languages":["ENG","RUS","UKR"]}

// get_supported_languages
{"ENG":"English","RUS":"Russian","UKR":"Ukrainian"}

// check_api_health
{"api_available":true,"status":"healthy"}

// любая ошибка
{"status":"error","tool":"<name>","error":"<message>"}
```

## 4. Проверочные запросы и подтверждение вызовов

Все запросы воспроизводятся скриптом `translation-server/verify_mcp.py` через
реальный MCP-транспорт (stdio). Трейс серверных логов сохранён в
`translation-server/verification.log`.

| # | Запрос пользователя | Ожидаемый tool | Подтверждение (лог) | Результат |
|---|---------------------|----------------|---------------------|-----------|
| 1 | «Проверь, доступен ли API перевода» | `check_api_health` | `verification.log:L10–L14` | `{"api_available":true,"status":"healthy"}` |
| 2 | «Какие языки поддерживаются?» | `get_supported_languages` | `verification.log:L16–L19` | `{"ENG":"English","RUS":"Russian","UKR":"Ukrainian"}` |
| 3 | «Переведи "Hello, world!" с английского на русский» | `translate_text` | `verification.log:L21–L29` | `…"translated_text":"Привет, мир!"` |
| 4 | «Переведи на русский: Good morning» | `translate_with_detection` | `verification.log:L31–L40` (detected=ENG, L36) | `…"translated_text":"Доброе утро"` |
| 5 | «Определи язык текста "Привіт, світ"» | `detect_language` | `verification.log:L42–L48` (detected=UKR, L46) | `{"detected_language":"UKR",…}` |

**Итого:** 5 проверочных запросов, все 5 приводят к реальному вызову MCP-tool
(по заданию требуется ≥5 запросов и ≥3 вызова).

## 5. Логи / отладочный вывод (фрагмент `verification.log`)

Логи пишутся в stderr и показывают имя tool, входные параметры (без секретов) и
статус success/error:

```
2026-06-11 19:55:48 - src.server - INFO - Tool execution started: name=translate_text, arguments={
  "text": "Hello, world!",
  "source_lang": "ENG",
  "target_lang": "RUS"
}
2026-06-11 19:55:48 - src.tools - INFO - Tool called: translate_text | text_length=13, source_lang=ENG, target_lang=RUS
2026-06-11 19:55:48 - src.api_client - INFO - Translation request: text_length=13, lang_pair=eng|rus
2026-06-11 19:55:48 - src.tools - INFO - Tool result: translate_text | status=success, is_translated=True
2026-06-11 19:55:48 - src.server - INFO - Tool execution succeeded: name=translate_text
```

## 6. Безопасность

Инструменты **не выполняют команд оболочки и не читают файлы** — они делают
только HTTP-запросы к публичному API MyMemory, поэтому ограничение файловой
области не требуется. API-ключ не нужен; `.env` исключён в `.gitignore`; входные
данные валидируются (коды языков, совпадение source/target).

## 7. Как воспроизвести

```bash
cd translation-server
venv\Scripts\activate           # Linux/macOS: source venv/bin/activate
python verify_mcp.py            # печатает JSON-результаты, пишет verification.log
python test_tools.py            # 6/6 passed
```
