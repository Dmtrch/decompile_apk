# Findings & Research

## Architectural Decisions
1. **Language/Backend**: Рекомендуется Python (FastAPI + Celery) для легкой интеграции с инструментами безопасности.
2. **Sandbox**: Docker-Android обеспечивает необходимую изоляцию.
3. **Network Isolation**: Использование `iptables` внутри песочницы для форвардинга 80/443 портов на локальный `mitmproxy` + кастомный эмулятор сервера.
4. **Resilience Strategy**: Если приложение использует SSL Pinning, Frida должна автоматически внедрять скрипты для его обхода, чтобы `mitmproxy` мог анализировать трафик.

## Tools & Libraries
- **Jadx**: Автоматизация декомпиляции.
- **Frida**: Для динамического анализа и **Runtime Patching** (обход проверок сервера).
- **mitmproxy**: Для перехвата, модификации и перенаправления HTTP/S трафика.
- **Semgrep**: Поиск уязвимостей в коде.

## Known Challenges (Mitigation strategies)
...
- **Server Connectivity Dependency**: Приложение может уходить в "бесконечную загрузку" или закрываться без связи. Решение: Интеллектуальный Mock-сервер, который на любой POST/GET запрос возвращает HTTP 200 OK с корректным (валидным по формату) пустым JSON/XML.
- **Anti-Debugging/Anti-VM**: Приложение может определять, что оно в песочнице. Решение: Скрипты для скрытия следов Frida и эмулятора (MagiskHide-like подходы).