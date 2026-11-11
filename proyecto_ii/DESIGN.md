# Diseño y decisiones técnicas

## Responsabilidades y dependencias

La CLI interpreta argumentos y convierte excepciones de dominio en exit codes. `pipeline.py` orquesta jobs; `data.py` adapta la carga y validación del Proyecto I; `model.py` contiene sklearn; `ai_client.py` aísla el proveedor; `storage.py` limita las escrituras y gestiona logs. Ninguna función de validación llama a una API ni decide dónde guardar archivos.

La dependencia hacia el Proyecto I es explícita en `pyproject.toml`: instala `diabetes_app` y `ventas_app` desde sus ubicaciones originales. Esto conserva sus comandos y permite reutilizar código sin modificaciones manuales de `sys.path` en producción. `pytest.ini` incorpora las rutas para permitir pruebas de desarrollo.

## Contratos públicos

| Interfaz | Entrada | Salida / fallo |
| --- | --- | --- |
| `transform(frame, require_target=...)` | DataFrame con columnas obligatorias del I; etiqueta opcional solo en inferencia | DataFrame limpio, rechazados con motivo e informe; DataError si el schema es inválido |
| `grouped_split(frame, seed, test_size)` | Encuentros elegibles y etiqueta | Train/test con pacientes disjuntos y ambas clases; ModelError si no es posible |
| `fit_model(clean, source, ...)` | Datos validados y ruta para hash | Bundle sklearn, holdout, predicciones holdout |
| `load_model(path)` | joblib de confianza | Bundle con versión/schema comprobados; ModelError |
| `predict(bundle, clean)` | Modelo y encuentros, sin necesidad de target | IDs, score y predicción binaria |
| `CompletionClient.complete(prompt)` | Texto limitado | `AIResponse(provider, text, model)`; AIClientError o TransientAIError |
| `train_job(...)` / `run_job(...)` | Rutas, política y cliente inyectable | Informes y artefactos; fallos de dominio propagados |

## Decisiones ML

La unidad de observación es el encuentro, pero la partición usa el paciente. Solo se usan variables disponibles al alta, y los identificadores sirven para trazabilidad y separación, nunca como predictores. `readmitted` se utiliza exclusivamente como objetivo o para evaluación posterior.

La regresión logística ofrece una base rápida y reproducible. Los pesos de clase favorecen detectar la clase minoritaria, a costa de falsos positivos; esto se refleja en las métricas en lugar de ocultarlo con accuracy. No se afirma que el modelo sea adecuado para decisiones asistenciales.

El imputador, scaler y one-hot pertenecen al modelo persistido: inferencia aplica exactamente las transformaciones aprendidas. Las categorías nuevas no rompen la ejecución. El test automático altera deliberadamente el holdout para comprobar que la media del scaler no se ajusta a él.

No se hace selección de modelos ni ajuste de hiperparámetros. Si el III requiere optimización, debe incorporar validación por grupos dentro de train y reservar el test, calibrar los scores y justificar el umbral antes de evaluar el resultado final.

## Diseño del cliente IA

El pipeline depende del Protocol `CompletionClient`. `MockClient` y `OpenAIClient` cumplen el mismo contrato. `RetryingClient` es un envoltorio que decide qué errores reintentar; `FailOnceClient` permite demostrar el comportamiento sin red. No se necesita instalar un SDK de proveedor: el adaptador HTTP usa el contrato oficial.

El prompt del pipeline se construye mediante una lista cerrada de agregados numéricos. Las respuestas externas son texto no confiable: se guardan, no se ejecutan. No se registra la clave ni el prompt en logs operativos. `AIConfig.api_key` se excluye de la representación textual de configuración.

El timeout se aplica por intento HTTP. No es un plazo global estricto: la duración total incluye los intentos y sus esperas. Los reintentos pueden generar llamadas adicionales facturables en modo real. El máximo es acotado y los errores de autorización no se reintentan.

## Publicación de resultados y fallos

Se protege la entrada/modelo frente a un directorio de salida que los contenga. Las escrituras usan fichero temporal en el mismo directorio y reemplazo final; se evita un CSV/JSON truncado en su ruta definitiva.

`status.json` es el marcador para consumidores automáticos. Un job iniciado escribe `running`, elimina únicamente sus salidas regenerables conocidas y al finalizar escribe `success`. Un error esperado escribe `failed` y sale distinto de cero; un fallo inesperado conserva `running` y su traceback, nunca se declara éxito. Puede existir información diagnóstica o parte de las salidas en un fallo, por lo que no deben consumirse sin comprobar el estado.

Los jobs no ofrecen transacciones multiproceso ni bloqueo del directorio. Dos ejecuciones concurrentes necesitan destinos diferentes. Los wrappers por fecha se diseñan para ejecución secuencial. No se modifica `.git`, no se programan tareas reales ni se publican resultados automáticamente.

## Pruebas relevantes

Los tests verifican resultados conocidos, errores, contratos y propiedades con consecuencias reales: no filtrar pacientes, no incluir el target como feature, no recalibrar transformaciones en test, conservar predicciones tras serialización, no llamar a IA si el gate falla, limitar reintentos y no presentar resultados antiguos como una ejecución correcta.

Las fixtures sintéticas contienen señal sencilla para que las pruebas de infraestructura sean rápidas; **sus métricas no se presentan como rendimiento del dataset real**. La integración real usa la muestra de 5.000 filas y verifica el checkpoint de 4.867 válidas. Los informes publicados corresponden a esta última.

## Puente al III

La API podrá cargar el modelo al arrancar, validar su petición, llamar a `predict` y normalizar excepciones a HTTP. La web consumirá esa API. El cliente IA podrá inyectarse sin cambiar el núcleo. En esa etapa se decidirán el modelo de peticiones concurrentes, autenticación si procede, almacenamiento, monitorización y estrategia de despliegue; no se añaden dependencias web antes de necesitarlas.
