# Auditoría de la entrega por temas

**Fecha:** 11/11/2026. **Alcance:** Proyecto II y los huecos del Proyecto I que condicionan su continuidad. Revisión basada en los archivos locales entregados, no en supuestas instrucciones adicionales del aula.

## Fuentes y estado inicial

Clon del profesor: `dsia-26-27`, HEAD `a9ccfd3`. Repositorio personal: `dsia-26-27-VizosoMarchena-Gonzalo`, HEAD previo `f8edcff`. Ambos estaban sin cambios locales al iniciar la revisión.

Se contrastaron los enunciados de I, II y III; guías/ejercicios de pytest y CI; data flows, E4 y ejemplos; clientes API y E5; uso de asistentes, catálogo de prompts y E6/E7; arquitectura, robustez, despliegue y E8/E8b/E9. En tu repo se revisaron los módulos y tests de ventas/diabetes, configuración, datos de muestra, diseño y documentación principal.

El punto de partida tenía **42 tests pasando**, las dos aplicaciones del Proyecto I y la muestra pública de diabetes. No contenía entrenamiento/inferencia sklearn, cliente generativo, workflow de CI, requirements global ni tests de las dos CLI. No equivalía todavía a un Proyecto II.

## Tema 1 — programación y datos

| Requisito / observación | Antes | Solución / evidencia |
| --- | --- | --- |
| Dos pipelines, ventas y dominio propio | Implementados | Se conservan ambos paquetes y sus entradas |
| Diseño modular y contratos | Repository/Protocol, loader/validator/metrics/CLI | Reutilización como paquetes instalables en `pyproject.toml` |
| Validación | Reglas específicas de dominio, pero aceptaba algunos vacíos/conteos incorrectos | Espacios, celdas vacías, IDs inválidos, decimales e infinitos rechazados; tests parametrizados |
| Exportación a un directorio nuevo | CLI fallaba si no existía | `mkdir(parents=True, exist_ok=True)` y smoke tests |
| Trazabilidad de datos | Fuente/licencia, pero fecha de descarga en blanco | Se elimina el placeholder; se declara honestamente que no consta y se registra hash del input |
| Continuidad | Solo métricas descriptivas | Nuevo pipeline reutiliza las mismas reglas; no copia el validador |

Las exclusiones de fallecimiento/hospicio son criterios de elegibilidad del objetivo, no solo suciedad de datos. Por simplicidad docente, el gate cuenta todas las filas rechazadas; el JSON desglosa sus motivos. En un producto podría separarse elegibilidad de errores de calidad.

## Tema 2 — tests, entornos y CI

| Requisito / ejercicio | Qué faltaba | Entregado |
| --- | --- | --- |
| E3: fixtures, assert/AAA, raises y parametrize | Existían en el I | Se amplían a datos, modelo, clientes y jobs |
| Tests loader/validator/metrics/CLI en ambas apps | Faltaban CLI | `1_programacion_avanzada_python/tests/test_cli.py` |
| Integración real de datos | Existía validación de CSV | Se añade entrenamiento → joblib → inferencia → mock sobre la muestra real |
| Test de carga/inferencia del modelo | No existía modelo | Roundtrip joblib, clases/categorías nuevas, ausencia de etiqueta y versiones incompatibles |
| Dependencias y entorno | Instalación manual de pandas/pytest | `requirements.txt`, `requirements-verified.txt`, `pyproject.toml`, `.env.example` |
| CI con gate ≥60 % | No había workflow | `.github/workflows/ci.yml`, cobertura y demo de ambos proyectos |
| Actions verde | Sin evidencia para los cambios nuevos | Pendiente de push y ejecución remota; no se sustituye por el resultado local |

El gate mide código de ventas, diabetes y readmission conjuntamente, sin excluir líneas difíciles para inflar la cifra. Los scripts de ejercicio tienen pruebas funcionales aunque no se incluyen en ese denominador. El porcentaje y el resultado medidos se detallan en `EVIDENCIA.md`.

## Tema 3 — automatización, sklearn y APIs

| Bloque | Qué faltaba | Entregado / cómo comprobarlo |
| --- | --- | --- |
| E4: flags y control de calidad | CLI I sin umbral operativo | `scripts/pipeline_ventas.py`: 140/10, gate 0.05 → exit 1 |
| Señales del job | Logging básico | `metrics/quality.json`, `run.log`, `status.json`, códigos 0–4 |
| Idempotencia | No demostrada | Rerun con nombres estables, sin duplicados; un fallo invalida salidas antiguas; test automático |
| Cadena de scripts | Ausente | `check_metrics.py`, lanzador Python y wrappers PowerShell/Bash; marcador local de éxito |
| Programación periódica | Ausente | Wrappers preparados y ejemplo de cron documentado; no se instala una tarea real |
| Modelo sklearn | Ausente | LogisticRegression + Pipeline, semilla, split por grupos y baseline |
| Persistencia e inferencia | Ausente | joblib con contrato/versiones; `run` carga y predice sin reentrenar |
| Métricas ML | Ausentes | F1, recall, precision, ROC-AUC, AP, balanced accuracy, accuracy y confusión |
| Cliente generativo unificado | Ausente | `CompletionClient`, `AIResponse`, MockClient y OpenAIClient |
| E5: batch de 5 prompts | Ausente | `proyecto_ii/prompts.txt`, comando `ai --batch`, JSONL de cinco registros |
| E5: fail-once/retry | Ausente | Fallo simulado, hasta 2 reintentos por defecto, backoff+jitter y tests |
| Timeout, 401/429/5xx, respuesta vacía | Ausente | Clasificación de errores; no reintentar autorización ni ocultar fallos |
| Secretos y datos | Sin integración real | Clave desde entorno, repr sin clave, mensajes de error saneados, payload agregado |

La llamada real es opcional según el enunciado. El adaptador está implementado; la verificación real depende de una clave válida y cuota. La entrega no afirma haberlo probado contra OpenAI.

## Tema 4 — desarrollo asistido y documentación

| Requisito | Entregado | Límite honesto |
| --- | --- | --- |
| Citación del asistente | Ampliación detallada de `AI_USAGE.md` | Se declara aportación sustancial de ChatGPT/Codex |
| Explicar código existente | Resumen del flujo de la CLI y guía de estudio | El alumno debe leer y comprobar que lo entiende |
| Refactor pequeño con tests (E6) | Crear directorios de salida, tests y registro del motivo | No se inventa un commit/PR ni la asistencia a un taller |
| Revisión de riesgos | Fallos concretos de validación, fuga por paciente y gestión de API | Tests y decisiones explícitas, no garantías generales de producción |
| README reproducible | Instalación, entrenamiento, inferencia, IA, pruebas y automatización | Los comandos de API/web de E7 corresponden al III |
| Release Candidate (E7) | Plan de continuidad identificado | Tag RC, web, endpoints y demo final pendientes del III |

## Tema 5 — lo que pertenece al Proyecto III

No se debe confundir “Proyecto II completo en local” con “Trabajo Final completo”. La continuidad exige **el mismo repo, dominio, datos y núcleo ML/IA**. Queda por añadir:

1. API de servicio (`/health`, predicción y análisis) con contratos de entrada/salida.
2. Web o dashboard funcional que llame al backend y permita la demo.
3. Manejo HTTP de validación/dependencias, request_id, latencias y estado degradado.
4. Empaquetado/despliegue verificable, smoke y plan de rollback.
5. Evidencia de CI remoto, release candidate y exposición de 5–7 minutos.

E8 pide la primera API; E8b añade robustez; E9 preparación de despliegue. E6/E7 se sitúan en el taller del III aunque el Proyecto II ya exige documentar el uso de IA. Estos entregables futuros no se marcan como realizados.

## Comprobación de los ocho mínimos del Proyecto II

| Mínimo literal del enunciado | Ubicación |
| --- | --- |
| 1. Dominio/datos para el III documentados | README, sección 2 |
| 2. Pipeline reproducible con logs | `python -m readmission_app train/run`, `pipeline.py` |
| 3. sklearn: entrenamiento, persistencia, inferencia y métricas | `model.py`, artefactos locales e informes versionables |
| 4. pytest unitario/integración y carga/inferencia | `tests/test_model_contract.py`, `test_jobs.py` y resto de suite |
| 5. Mock y proveedor real documentado | `ai_client.py`, `.env.example`, README |
| 6. requirements y .env.example | Raíz del repositorio |
| 7. AI_USAGE | `AI_USAGE.md` actualizado |
| 8. Modularidad preparada para API | Funciones y Protocol independientes de argparse/web |

## Pendientes que no se pueden fabricar con código

- **Publicación y Actions:** el usuario pidió preparar su carpeta. Los cambios quedan locales para revisión y subida; no hay un nuevo run remoto verificado.
- **Historial de octubre:** no es posible generar retroactivamente trabajo histórico auténtico. Los commits futuros deben llevar su fecha real.
- **Fecha de descarga original:** no consta; debe completarse solo si se conoce realmente. La muestra existente y sus hashes hacen reproducible esta ejecución.
- **Revisión/defensa del alumno:** leer `GUIA_ESTUDIO.md`, ejecutar la demo y saber explicar el diff antes de entregar, conforme a las indicaciones del profesor.
