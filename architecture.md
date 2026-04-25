# Детальная архитектура: Decompile & Audit APK

В основе архитектуры лежат принципы **Clean Architecture** и **Domain-Driven Design (DDD)**. Система разделена на независимые слои, что позволяет легко заменять или модернизировать отдельные компоненты (например, движки декомпиляции или анализаторы безопасности) без влияния на остальную систему.

## 1. High-Level Architecture (C4: Container Level)

Система состоит из следующих основных контейнеров:

1. **Web UI (SPA: Vue/React)**
   *   Точка входа для аналитиков безопасности.
   *   Загрузка APK, мониторинг статуса задач, просмотр отчетов (Security Scorecard).
2. **API Gateway / Backend (FastAPI / Python)**
   *   Принимает REST запросы от UI.
   *   Валидирует входные данные (APK файлы).
   *   Управляет Domain Models: `Job`, `Report`, `ApkAsset`.
3. **Orchestrator / Task Queue (Celery + RabbitMQ/Redis)**
   *   Управляет жизненным циклом тяжелых задач (декомпиляция, статический анализ, сборка, динамический анализ).
   *   Обеспечивает масштабируемость (возможность добавления новых worker-узлов).
4. **Decompilation Worker (Python/Java)**
   *   Отвечает за распаковку, деобфускацию и декомпиляцию.
   *   Интегрирует Jadx, Apktool.
5. **Security Scanning Worker (SAST)**
   *   Выполняет статический анализ кода с помощью Semgrep.
6. **Sandbox Manager Worker (DAST)**
   *   Управляет эфемерными контейнерами Docker-Android.
   *   Поднимает Mock-сервер для "Air-Gap" перехвата трафика.
   *   Внедряет Frida-скрипты для обхода SSL Pinning и блокировок (Resilience).
7. **Storage (PostgreSQL + MinIO/S3)**
   *   **PostgreSQL**: Хранение метаданных задач, результатов сканирования, конфигураций.
   *   **MinIO**: Объектное хранилище для оригинальных APK, декомпилированного кода и сгенерированных отчетов.

## 2. Domain-Driven Design (Ограниченные контексты - Bounded Contexts)

### 2.1. APK Processing Context
Отвечает за трансформацию бинарного APK в анализируемый исходный код и обратно.
*   **Entities**: `ApkArchive`, `DecompiledProject`, `RebuiltApk`.
*   **Value Objects**: `Checksum`, `DexSignature`.
*   **Services**: `ApkDecompiler`, `ProjectBuilder`.

### 2.2. Security Auditing Context
Отвечает за анализ кода и поведения.
*   **Entities**: `Vulnerability`, `AuditReport`, `NetworkTrace`.
*   **Value Objects**: `SeverityScore` (CVSS), `CweId`.
*   **Services**: `StaticAnalyzer` (SAST), `DynamicAnalyzer` (DAST).

### 2.3. Sandbox Execution Context
Отвечает за изолированное выполнение и эмуляцию сети.
*   **Entities**: `SandboxSession`, `MockRoute`.
*   **Services**: `DeviceEmulator`, `TrafficInterceptor`, `AntiLockoutPatcher`.

## 3. Процесс модернизации архитектуры (Architecture Decision Records)

Для обеспечения непрерывной модернизации и прозрачности принятия решений вводится обязательное использование **ADR (Architecture Decision Records)**.

### Правила работы с архитектурой:
1. **Любое значимое изменение** (смена базы данных, выбор нового инструмента декомпиляции, изменение межсервисного взаимодействия) должно фиксироваться в виде ADR.
2. ADR хранятся в директории `docs/adr/`.
3. Прежде чем внедрять новую технологию, необходимо проверить существующие решения (Library-First Approach) и обосновать выбор в ADR.
4. Устаревшие решения помечаются статусом `Deprecated` или `Superseded`.

Это позволит архитектуре эволюционировать вместе с развитием технологий безопасности, сохраняя при этом понятную историю изменений для команды.