# Diseño y decisiones técnicas

Mi proyecto separa cinco tareas: leer y validar datos, entrenar/predecir, llamar a IA, coordinar la ejecución y guardar resultados. Cada módulo tiene una responsabilidad concreta.

## Recorrido del código

| Archivo | Qué hace |
| --- | --- |
| `cli.py` | Lee argumentos y devuelve el código de salida |
| `data.py` | Reutiliza la carga y validación del I; permite inferencia sin etiqueta |
| `model.py` | Define variables, separa pacientes, entrena, evalúa, guarda/carga y predice |
| `config.py` | Lee y comprueba la configuración IA |
| `ai_client.py` | Devuelve mock o texto de OpenAI, con reintentos limitados |
| `pipeline.py` | Ordena train/run y construye los agregados para IA |
| `storage.py` | Guarda archivos y configura el log |
| `errors.py` | Relaciona errores esperados con códigos de salida |
| `open_api_client.py` | Ejercicio E5 independiente: APIs abiertas |

`pyproject.toml` instala los tres paquetes. No hace falta copiar las reglas del I ni cambiar `sys.path` a mano. Los scripts se usan desde el repositorio; no se incluyen como paquetes de la aplicación instalada.

## Modelo

La unidad de observación es el ingreso, pero train/test se separan por `patient_nbr`. Los IDs y `readmitted` no entran como predictores. Se usan datos disponibles al alta.

`build_model` crea imputación, escalado, one-hot y regresión logística. Guardar esta Pipeline completa conserva las transformaciones aprendidas con train. El test modifica el holdout y comprueba que el scaler no vuelve a ajustarse.

La configuración es fija; no hay búsqueda de hiperparámetros ni del umbral. Se compara con DummyClassifier y se muestra el coste en falsos positivos. El score no es una probabilidad clínica calibrada. Si el III incorpora optimización, necesitará validación por grupos dentro de train y una evaluación final reservada.

## Cliente IA

`CompletionClient` describe una única operación: `complete(prompt) -> AIResponse`. `MockClient` y `OpenAIClient` cumplen ese contrato. El Protocol ayuda a comprobar que ambos pueden usarse en el pipeline; no es un sistema de plugins.

`RetryingClient` repite solo errores temporales. El flag `fail_once` simula el primer fallo dentro del mismo bucle, sin una clase adicional. El límite de intentos y la espera evitan un bucle infinito. El timeout es por intento, no un plazo total.

`DeferredClient` crea el cliente cuando se llama por primera vez. Se conserva porque configurar el proveedor antes de iniciar el job dejaría resultados antiguos si falta una clave o el entorno es inválido. Su función es retrasar ese paso hasta después de invalidar las salidas anteriores.

`summary_payload` envía una lista cerrada de agregados del lote y métricas históricas del holdout/modelo de referencia. Los bloques están identificados; el resumen no constituye una evaluación nueva del lote. No envía filas, IDs ni diagnósticos. La respuesta es texto: se guarda sin ejecutarla. El CLI `ai`, en cambio, permite prompts genéricos y no aplica esa selección de agregados.

## Guardar resultados y tratar fallos

Los jobs usan el contexto `job`: abrir log → escribir `running` → invalidar salidas anteriores → ejecutar pasos → escribir `success` o `failed`. Compartir este código evita repetirlo en train, run y ventas.

La escritura temporal seguida de reemplazo evita publicar un CSV/JSON truncado. Esto protege cada archivo por separado; no es una transacción de todo el job. Los consumidores deben comprobar `status=success` y exit 0. Un fallo inesperado puede dejar `running` y un traceback, nunca un éxito nuevo.

Se rechazan destinos que contengan la entrada o el modelo. Un directorio inaccesible puede impedir incluso guardar el estado. No hay bloqueo multiproceso: dos jobs concurrentes necesitan destinos distintos.

## Automatización y continuidad

`run_pipeline.py` concentra inferencia → comprobación de métricas → marcador local. PowerShell y Bash llaman a esa misma cadena. `run_cadena_ventas.sh` se conserva como ejercicio E4 literal de limpiar, comprobar y copiar resultados.

La API del III podrá cargar el modelo y llamar a `predict`/`run_job`; el cliente IA se puede sustituir sin copiar la lógica. Autenticación, concurrencia, almacenamiento y despliegue se decidirán en esa etapa.

La revisión por archivo y los cambios de legibilidad están en [REVISION_SIMPLICIDAD.md](REVISION_SIMPLICIDAD.md). Las comprobaciones de resultados están en [EVIDENCIA.md](EVIDENCIA.md).
