# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the APK Decompilation & Audit project.

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-initial-architecture-stack.md) | Initial Architecture & Technology Stack | Accepted | 2026-04-25 |

## Управление модернизацией

Проект использует эволюционную архитектуру. Если вы хотите предложить изменение архитектуры (например, заменить Jadx на новый движок, изменить оркестратор или способ изоляции песочницы):
1. Скопируйте шаблон и создайте новый файл `NNNN-title.md`.
2. Опишите контекст, рассмотренные варианты и причины выбора.
3. Добавьте его в этот индекс.
4. Обновите `architecture.md` в соответствии с принятым решением.