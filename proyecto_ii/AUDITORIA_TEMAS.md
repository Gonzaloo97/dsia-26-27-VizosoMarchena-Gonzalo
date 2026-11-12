# Revisión de requisitos del Proyecto II

Mi proyecto continúa la base de diabetes del I y prepara el mismo núcleo para el III. Esta revisión distingue los requisitos de entrega de los ejercicios y mejoras adicionales.

**Fuentes:** [Proyecto II](https://github.com/dmartincc/dsia-26-27/blob/1c2906e77c5235a04f820f4252dcb0760e240728/proyectos/proyecto_ii/README.md) y [E5](https://github.com/dmartincc/dsia-26-27/blob/1c2906e77c5235a04f820f4252dcb0760e240728/3_automatizacion_e_ia/ejercicios/E5_apis_ia.md), commit `1c2906e`. La primera auditoría del 11/11 usó el clon local `a9ccfd3`; posteriormente se contrastó la versión vigente.

**Estado:** la revisión de código y documentación del 12/11 está publicada en `cebdb27` y tiene [GitHub Actions correcto](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43268309498). La revisión local obtuvo 145 pruebas y 96,02 % de cobertura; el detalle está en [REVISION_SIMPLICIDAD.md](REVISION_SIMPLICIDAD.md). El commit anterior `d3ff586` queda como evidencia histórica ([run del 11/11](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514)).

## Ocho mínimos del enunciado

| Mínimo obligatorio | Dónde se encuentra | Estado |
| --- | --- | --- |
| 1. Dominio, datos, origen, licencia y motivación | README §2 | Documentado |
| 2. Pipeline reproducible con logs | CLI train/run, demo y `run.log` | Implementado y probado |
| 3. sklearn: train, persistencia, inferencia y métricas | `model.py`, `pipeline.py`, README §3–4 | Implementado y probado |
| 4. Tests unitarios, integración y carga/inferencia | `tests/`, especialmente modelo/jobs | Implementado y probado |
| 5. Cliente tipado, mock y proveedor real documentado | `ai_client.py`, README §4 | Mock y OpenAI; contrato HTTP simulado, sin llamada real |
| 6. `.env.example` y dependencias | Raíz; incluye `HF_TOKEN=` y sklearn | Presente; HF no implementado |
| 7. Uso y citación de IA | `../AI_USAGE.md` | Declara aportación sustancial y revisión personal pendiente |
| 8. Modularidad para continuar en el III | Datos/modelo/IA/jobs/CLI separados | Conservada |

El enunciado recomienda HF y admite otro proveedor documentado. OpenAI es la alternativa de texto utilizada en el diseño; el proveedor ejecutado en demo/tests es mock. No se exige subir el modelo si hay instrucciones claras de reentrenamiento.

## Entrega y limitaciones

| Condición | Estado |
| --- | --- |
| Mismo repositorio para el Trabajo Final | Se mantiene este repositorio y dominio |
| Historial a lo largo de octubre | Hay base del I en octubre; ML/IA/CI se incorporan el 11 de noviembre. Limitación temporal real |
| README con datos → train → inferencia → IA → III | Documentado |
| Fecha original de descarga | No registrada; se conserva la muestra y se informa su hash |
| Comprensión y defensa personal | Pendiente de completar; la revisión de Codex no la sustituye |

## Ejercicios y comprobaciones por tema

| Bloque | Evidencia | Clasificación respecto a esta revisión |
| --- | --- | --- |
| Tema 1: reutilización de ventas/diabetes | Paquetes del I y tests de sus CLI | Base conservada y reforzada |
| Tema 2: pytest e integración | Casos de datos, modelo, IA y jobs | Parte del mínimo II.4 |
| CI y umbral de cobertura del 60 % | Workflow y run publicado | Calidad/ejercicio de CI; el enunciado II no enumera ese porcentaje entre sus ocho mínimos |
| E4: ventas y gate | 140 válidas/10 rechazadas; gate 0,05 → exit 1 | Ejercicio de automatización |
| E4: cadena y repetición | Lanzador Python, wrappers y cadena Bash de ventas | Ejercicio y apoyo a la reproducibilidad |
| Programación periódica | Ejemplo de cron en README | Preparado; no se ha instalado una tarea |
| E5 partes 1–2 | Cuatro APIs abiertas, contrato, tabla de errores y país ZZ | Núcleo obligatorio del E5 |
| E5 partes 3–5 | Mock, batch de cinco y fail-once/retry | Núcleo obligatorio del E5 |
| E5 parte 6 | AI_USAGE con proveedor, tarea, modelo y comandos | Cierre obligatorio del E5 |
| E5 parte 7.2 | Tests mock sin red | Extensión deseable realizada |
| HF real | No realizado | Alternativa/extensión recomendada; no requisito exclusivo |
| Tema 4: explicación y refactor con IA | AI_USAGE y guía de estudio | Ayuda declarada; no acredita mi comprensión personal |

El gate cuenta todas las filas rechazadas, incluidas las exclusiones por fallecimiento/hospicio. `quality.json` desglosa motivos. En un producto podría separarse elegibilidad de calidad; aquí se conserva la política docente existente.

## Qué continúa en el III

API de servicio, web/dashboard conectado, manejo HTTP, monitorización, despliegue verificable, release candidate y exposición. El proyecto no presenta esos elementos como ya entregados. Los ejercicios E6/E7 y los de API/despliegue deben evaluarse según su propio alcance; no se añaden automáticamente a los ocho mínimos del II.

Los documentos DESIGN, EVIDENCIA, cierre, guía de estudio y revisión de simplicidad ayudan a explicar y comprobar el proyecto; el enunciado no exige todos esos nombres de archivo por separado.
