# Revisión de simplicidad del Proyecto II

Revisión de ChatGPT/Codex del **12/11/2026**, solicitada y autorizada por Gonzalo. Se leyeron las líneas de código añadidas y los archivos completos del núcleo, scripts, pruebas, configuración y documentación del II. El alcance son los **61 archivos** incorporados o modificados entre `f8edcff` (base del I) y `d3ff586` (II publicado), incluidas las modificaciones del I necesarias para el II. No es una auditoría de todos los ejercicios históricos de la asignatura.

## Dictamen

La estructura es razonable para los requisitos de sklearn, IA, pruebas y automatización. Había duplicación y algunas expresiones innecesariamente indirectas; se simplificaron. Las funciones de entrenamiento, inferencia y errores siguen separadas para poder seguir su recorrido y comprobarlas sin red.

Este es un dictamen técnico con comprobaciones reproducibles. No demuestra que exista una única implementación mínima, que el programa no tenga errores ni que el alumno comprenda ya todas las líneas. La revisión y los cambios los hizo Codex y se declaran en [AI_USAGE.md](../AI_USAGE.md).

## Cambios concretos

1. **Una cadena de ejecución:** PowerShell y Bash llaman a `run_pipeline.py` en lugar de repetir inferencia, comprobación y marcador.
2. **Una clase menos:** se elimina `FailOnceClient`; el primer fallo simulado queda dentro del bucle que ya controlaba los reintentos.
3. **Tests con imports normales:** se elimina el cargador basado en `importlib` de los ejercicios.
4. **Pasos visibles:** batch, partición por clases y selección del comando HTTP dejan de esconder pasos dentro de expresiones densas o despacho dinámico.
5. **Validación más legible:** máscaras en varias líneas, una función con nombre para el límite de int64 y eliminación del cálculo de duplicados que se sobrescribía después. Se mantiene el orden de los motivos de rechazo.
6. **Documentación:** voz más natural, ayuda de IA explícita, CI publicado actualizado, reflexión del E5 completada y registros históricos separados del estado local actual.

No se cambiaron las 13 variables predictoras, semilla 42, partición por paciente, regresión logística, pesos de clase ni umbral 0,5. Tampoco se eliminaron casos de prueba para hacer pasar la suite.

## Qué complejidad se conserva y por qué

| Elemento | Motivo |
| --- | --- |
| sklearn Pipeline | Guarda preprocesamiento y estimador juntos, evitando reajustar en test/inferencia |
| GroupShuffleSplit | Separa pacientes, no simplemente filas |
| CompletionClient y AIResponse | Contrato pequeño y tipado para mock y OpenAI, pedido por el enunciado |
| DeferredClient | Retrasa la configuración IA hasta que el job ha invalidado salidas antiguas |
| RetryingClient y errores tipados | Reintentos acotados solo para fallos temporales |
| Contextos de job y escritura temporal | Evitan repetir limpieza/logs y publicar archivos truncados |
| Tests parametrizados y fixtures | Prueban varios bordes sin copiar funciones enteras |
| Cadena Bash de ventas | Ejercicio E4 literal; no se confunde con otra implementación del pipeline hospitalario |

Se descartó unir todo en un script gigante, quitar comprobaciones o sustituir el ML para reducir líneas. Más líneas de formato pueden hacer una expresión más fácil de leer sin añadir comportamiento.

## Validación local después de los cambios

| Comprobación | Resultado |
| --- | --- |
| Suite completa antes | 145 passed; 95,95 % |
| Suite completa después | **145 passed; 96.02 %** (820/854 sentencias) |
| Cobertura mínima | 60 %, superada; no se rebajó el umbral |
| Scores del holdout antes/después | Exactamente iguales, sin tolerancia numérica |
| Metadatos de entrenamiento e informe de calidad | Exactamente iguales |
| Demo train → run → batch mock | Correcta; cinco registros JSONL |
| Métricas de la demo frente al histórico | Exactamente iguales: F1 0,2538; ROC-AUC 0,6120 |
| PowerShell 7: éxito y fallo de métricas | Exit 0/1 y marcador correcto |
| Git Bash: éxito y fallo de métricas | Exit 0/1 y marcador correcto |
| Cadena ventas: éxito, gate y mínimo de filas | Exit 0/1; sin publicación ni marcador tras los fallos |
| Dependencias | pip check correcto |

Git Bash fallaba al arrancar dentro del entorno restringido; se comprobó con acceso normal y los ocho casos finales pasaron en Windows. No se modificó ninguna política de ejecución. No se certifica una ejecución de los wrappers en Linux.

Comando de la suite, desde la raíz y con el entorno activado:

```powershell
python -m pytest --cov=ventas_app --cov=diabetes_app --cov=readmission_app --cov-report=term-missing --cov-fail-under=60 -q
python scripts/run_demo.py
python -m pip check
```

## Medición de velocidad

Cinco repeticiones por versión, sobre la misma muestra y entorno. Se mide cada operación después de importar librerías y leer el CSV. Estas cifras son observaciones locales; la carga y las cachés varían, así que no justifican afirmar una mejora general de velocidad.

| Operación | Mediana antes | Mediana después |
| --- | ---: | ---: |
| Validación | 0.2854 s | 0.1559 s |
| Entrenamiento y evaluación | 0.2777 s | 0.1588 s |
| Predicción sobre holdout | 0.0356 s | 0.0174 s |

No se observó una regresión de velocidad en esta medición. La comprobación más fuerte es la igualdad exacta de resultados; los tiempos no son una garantía para otras máquinas.

## Revisión de cada archivo

“Conservado” significa que se revisó y no se encontró una simplificación que justificase cambiarlo. No implica que toda alternativa sea peor. Las instantáneas históricas se comprueban como datos, no se reescriben como si fueran ejecuciones nuevas.

| Archivo | Decisión | Justificación |
| --- | --- | --- |
| `.env.example` | Simplificado / aclarado | Aclara mock/OpenAI y HF reservado; conserva las variables y no incluye claves. |
| `.gitattributes` | Conservado | Una regla LF para los scripts Bash; se conserva. |
| `.github/workflows/ci.yml` | Conservado | Cadena directa de instalar, probar, demo y artefactos; se conserva. |
| `.gitignore` | Conservado | Excluye entorno, claves y resultados regenerables; se conserva. |
| `1_programacion_avanzada_python/diabetes_app/cli.py` | Conservado | La creación del directorio evita un fallo real; sin otra capa añadida. |
| `1_programacion_avanzada_python/diabetes_app/loader.py` | Conservado | Se mantiene el Repository del I y su tratamiento de None/vacíos; no se duplica. |
| `1_programacion_avanzada_python/diabetes_app/validator.py` | Simplificado / aclarado | Máscaras separadas, función con nombre en lugar de lambda larga y un único cálculo de duplicados; orden de motivos conservado. |
| `1_programacion_avanzada_python/tests/test_cli.py` | Simplificado / aclarado | Los CSV de ejemplo se dividen en fragmentos legibles; mismas pruebas y resultados. |
| `1_programacion_avanzada_python/ventas_app/cli.py` | Conservado | Se conserva la creación de directorios antes de exportar. |
| `1_programacion_avanzada_python/ventas_app/validator.py` | Conservado | Se conservan finitud y producto float para evitar overflow; el cálculo ya es directo. |
| `AI_USAGE.md` | Simplificado / aclarado | Primera persona, ayuda sustancial declarada y etapas consolidadas; revisión personal sin certificar. |
| `README.md` | Simplificado / aclarado | Entrada al II con run actual y acceso a citación y revisión. |
| `proyecto_ii/AUDITORIA_TEMAS.md` | Simplificado / aclarado | Matriz breve: mínimos, ejercicios, extras y limitaciones temporales. |
| `proyecto_ii/CIERRE_AUDITORIA.md` | Simplificado / aclarado | Una cronología sustituye pendientes repetidos y estados contradictorios. |
| `proyecto_ii/DESIGN.md` | Simplificado / aclarado | Explica cada módulo y por qué se conservan las pocas abstracciones necesarias. |
| `proyecto_ii/E5_APIS_ABIERTAS.md` | Simplificado / aclarado | Añade propuesta concreta de API abierta y extensión 7.2; distingue evidencia de comprensión. |
| `proyecto_ii/EVIDENCIA.md` | Simplificado / aclarado | Estado publicado al principio; resultados iniciales claramente históricos. |
| `proyecto_ii/GUIA_ESTUDIO.md` | Simplificado / aclarado | CI actual y lenguaje sin atribuir comprensión personal; conserva explicación de métricas. |
| `proyecto_ii/README.md` | Simplificado / aclarado | Activación explícita, cadena compartida y afirmaciones limitadas a lo comprobable. |
| `proyecto_ii/evidence/ai_summary.json` | Conservado | Instantánea histórica mock; preservada sin regenerarla. |
| `proyecto_ii/evidence/inference_metrics.json` | Conservado | Instantánea histórica de inferencia; preservada. |
| `proyecto_ii/evidence/open_api_smoke.json` | Cambio previo preservado | Tenía un cambio local del usuario antes de la revisión; no se modifica ni se revierte. |
| `proyecto_ii/evidence/quality.json` | Conservado | Checkpoint histórico de 4.867/133 y motivos; preservado. |
| `proyecto_ii/evidence/respuestas.jsonl` | Conservado | Cinco registros mock históricos; preservados. |
| `proyecto_ii/evidence/training_metrics.json` | Conservado | Hash, split, métricas y baseline históricos; comparación exacta con la demo actual. |
| `proyecto_ii/evidence/validation_final.json` | Conservado | Registro previo a publicar d3ff586; se conserva su fecha/alcance. |
| `proyecto_ii/evidence/verification.json` | Conservado | Primera verificación local de 106 pruebas; no se reescribe como resultado actual. |
| `proyecto_ii/evidence/verification_followup.json` | Conservado | Registro histórico posterior de 145 pruebas; conservado. |
| `proyecto_ii/prompts.txt` | Conservado | Cinco frases de práctica sin datos personales; no necesita simplificación. |
| `pyproject.toml` | Conservado | Instala tres paquetes desde sus rutas y un comando; evita manipular sys.path. |
| `pytest.ini` | Conservado | Rutas y marcador de integración sencillos; se conserva. |
| `readmission_app/__init__.py` | Conservado | Solo descripción y versión; se conserva. |
| `readmission_app/__main__.py` | Conservado | Entrada mínima a la CLI; se conserva. |
| `readmission_app/ai_client.py` | Simplificado / aclarado | Elimina FailOnceClient; el fallo simulado queda en el bucle de reintentos. Mantiene contrato, mock, adaptador y creación diferida. |
| `readmission_app/cli.py` | Simplificado / aclarado | Batch en pasos explícitos: leer, completar y publicar; mantiene exclusión mutua de prompt/batch y protecciones. |
| `readmission_app/config.py` | Conservado | Dataclass de configuración y validaciones directas; se conserva. |
| `readmission_app/data.py` | Simplificado / aclarado | Captura solo el error ya normalizado por el loader, sin repetir sus capturas internas. |
| `readmission_app/errors.py` | Conservado | Pequeña jerarquía que permite códigos de salida estables; se conserva. |
| `readmission_app/model.py` | Simplificado / aclarado | Entradas y comprobación de clases en pasos separados; mismo algoritmo, variables y parámetros. |
| `readmission_app/open_api_client.py` | Simplificado / aclarado | Despacho explícito de los cuatro comandos en lugar de getattr/expansión dinámica. |
| `readmission_app/pipeline.py` | Simplificado / aclarado | Nombres intermedios y líneas más legibles; se conserva el contexto común de estado/log. |
| `readmission_app/storage.py` | Conservado | Escritura temporal, limpieza en finally y logs con cierre; no se elimina esta protección. |
| `requirements-verified.txt` | Conservado | Snapshot histórico de versiones; no se presenta como entorno limpio probado de nuevo. |
| `requirements.txt` | Conservado | Ocho dependencias directas con rangos; sin framework adicional. |
| `scripts/check_metrics.py` | Conservado | CLI pequeña: leer, comprobar estructura y aplicar umbrales; se conserva. |
| `scripts/open_api_client.py` | Conservado | Entrada de siete líneas al cliente E5; se conserva. |
| `scripts/pipeline_ventas.py` | Conservado | Reutiliza el I y el contexto de job; conserva control de finitud del total. |
| `scripts/run_cadena_ventas.sh` | Conservado | Cadena literal del E4; se conserva y comprueba éxito y dos fallos. |
| `scripts/run_demo.py` | Conservado | Tres comandos secuenciales que paran al fallar; se conserva. |
| `scripts/run_pipeline.ps1` | Simplificado / aclarado | De 19 a 7 líneas: llama a la cadena Python y propaga su salida. |
| `scripts/run_pipeline.py` | Conservado | Único lugar que coordina inferencia, métricas y marcador para ambos wrappers. |
| `scripts/run_pipeline.sh` | Simplificado / aclarado | De 19 a 16 líneas: conserva venv/log y llama a la misma cadena Python. |
| `scripts/verify_open_apis.py` | Conservado | Pruebas reales explícitas y resultado JSON; conserva la separación de pytest/CI. |
| `tests/conftest.py` | Conservado | Fixtures pequeñas reutilizables y entorno mock aislado; se conserva. |
| `tests/test_ai_contract.py` | Simplificado / aclarado | Adapta fail-once y comprueba que no se repite en la segunda llamada; mantiene errores, HTTP simulado y agregados. |
| `tests/test_audit_regressions.py` | Conservado | Conserva todos los casos de resultados antiguos, configuración y overflow. |
| `tests/test_data_contract.py` | Conservado | Conserva pureza, etiqueta opcional, validación y gate. |
| `tests/test_exercises.py` | Simplificado / aclarado | Imports normales sustituyen importlib y su cargador dinámico; mismos casos funcionales. |
| `tests/test_jobs.py` | Simplificado / aclarado | Argumentos largos repartidos en líneas; misma integración y comprobación de fallos. |
| `tests/test_model_contract.py` | Conservado | Conserva fuga, serialización, categorías nuevas y métricas conocidas. |
| `tests/test_open_api_client.py` | Simplificado / aclarado | Datos de prueba legibles y comprobación del JSON de los cuatro comandos públicos, sin red. |

Esta revisión añade dos archivos de apoyo: `REVISION_SIMPLICIDAD.md` (este informe) y [evidence/simplicity_review.json](evidence/simplicity_review.json) (resultados, alcance y hashes del código/scripts revisados). Ambos se comprobaron como documentación de esta intervención, además de los 61 archivos anteriores. Las mediciones temporales de trabajo quedan en `output_revision/`, ignorado por Git.

## Estado de publicación y lectura

La versión publicada `d3ff586` tiene [run verde de 145 pruebas y 95,95 %](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514). Los cambios de esta revisión **son locales, sin commit ni push y sin un nuevo run remoto**. No se realizó una llamada real a OpenAI ni se repitieron las APIs públicas. La modificación local de `open_api_smoke.json` que existía al empezar se mantiene intacta.

Para estudiar el código, recomiendo leer `data.py` → `model.py` → `ai_client.py` → `pipeline.py` → `cli.py`. `config.py`, `errors.py` y `storage.py` son los apoyos de ese recorrido. [GUIA_ESTUDIO.md](GUIA_ESTUDIO.md) explica las métricas. Esta guía y la revisión de Codex no sustituyen la lectura personal antes de defender el trabajo.
