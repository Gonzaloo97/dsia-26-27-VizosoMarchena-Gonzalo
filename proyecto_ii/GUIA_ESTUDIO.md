# Guía para entender y defender el Proyecto II

## Qué has construido

En el Proyecto I cargabas encuentros hospitalarios, separabas los que cumplían las reglas y calculabas estadísticas. En el II utilizas esos datos para **entrenar un modelo, guardarlo, volver a cargarlo y obtener predicciones**, además de generar un resumen mediante una interfaz de IA. Todo puede ejecutarse desde terminal y comprobarse con tests.

La pregunta del modelo es: **«Con la información disponible al finalizar este ingreso, ¿este encuentro pertenece a la clase de reingreso en menos de 30 días?»**. Es un ejercicio con datos históricos; no una herramienta asistencial validada.

## El recorrido de una ejecución

1. **Leer:** `data.read_data` utiliza el loader del Proyecto I. Una fila es un ingreso/encuentro, no necesariamente un paciente distinto.
2. **Validar:** se comprueban columnas, nulos, valores permitidos, rangos, IDs y elegibilidad. Las filas rechazadas conservan un motivo. Se mantiene `None` como categoría de prueba no realizada.
3. **Aplicar el gate:** si se rechaza más del porcentaje configurado, se detiene el job. No se llama a IA ni se publican predicciones de esa ejecución.
4. **Entrenar o inferir:** el comando `train` aprende el modelo; `run` carga un modelo que ya existe y lo aplica.
5. **Resumir:** el cliente IA recibe números agregados. En mock no hay un LLM: la respuesta está programada y claramente identificada.
6. **Guardar señales:** CSV de resultados, JSON de métricas, estado del job y log. El código de salida permite que otro script sepa si debe continuar.

Hay dos usos distintos de “pipeline”: el **pipeline de aplicación** organiza todo el flujo, mientras que `sklearn.pipeline.Pipeline` encadena preprocesamiento y clasificador. Se complementan.

## Lo que entra y lo que no entra al modelo

| Variable / grupo | Uso |
| --- | --- |
| `readmitted` | Respuesta que queremos aprender; `<30` se convierte en 1 y el resto en 0 |
| `patient_nbr` | Agrupar pacientes para separar train/test y detectar solapamiento |
| `encounter_id` | Relacionar cada predicción con su encuentro de origen |
| Estancia, procedimientos, medicamentos y visitas previas | Variables numéricas predictoras |
| Edad, sexo, diagnóstico, HbA1c y glucosa | Variables categóricas predictoras |
| `discharge_disposition_id` | Excluir encuentros fuera de la población elegida; no entra como predictor |
| Resto de columnas del CSV | Conservadas en la entrada/limpieza, pero excluidas de la lista de variables del modelo |

El momento de predicción importa: la estancia completa no se conoce al entrar en el hospital. Por eso el proyecto habla de predicción **al alta**.

## Evitar fuga de información

**Mismo paciente:** si un paciente tiene dos ingresos y uno aparece en train y otro en test, la evaluación puede resultar demasiado optimista. `GroupShuffleSplit` asigna todos sus encuentros a un solo lado. En la ejecución documentada hay 3.783 pacientes en train, 946 en test y cero compartidos.

**Preprocesamiento:** la media del escalado, los valores para imputar y las categorías del encoder se aprenden solo con train. Guardar todo dentro de una Pipeline impide tener que recalcularlos a mano al predecir.

**Objetivo:** `readmitted` nunca se incluye en X. Un test cambia la etiqueta real y comprueba que las predicciones permanecen iguales. La inferencia también funciona si el CSV no contiene esa columna.

**Decisiones posteriores:** cambiar el umbral o escoger la semilla que mejor sale en test también contaminaría la evaluación. Este proyecto utiliza decisiones fijas; para optimizar haría falta otra validación dentro del entrenamiento.

## Leer los resultados reales

El holdout contiene **968 encuentros: 123 positivos y 845 negativos**. La matriz del modelo es:

| Real / predicho | Predicho negativo | Predicho positivo |
| --- | --- | --- |
| No reingresa <30 días | 514 | 331 |
| Sí reingresa <30 días | 57 | 66 |

- **Recall = 66/123 = 53,66 %:** detecta aproximadamente la mitad de los positivos reales.
- **Precision = 66/(66+331) = 16,62 %:** de todos los positivos predichos, una parte pequeña es positiva realmente.
- **F1 = 0,2538:** combina precision y recall.
- **Accuracy = 59,92 %:** porcentaje de aciertos totales al umbral 0,5.
- **ROC-AUC = 0,6120:** el orden de los scores contiene señal, pero la discriminación es modesta.
- **Average precision = 0,2481:** se compara con una frecuencia positiva de 0,1271, la referencia de un score constante.

La referencia Dummy predice siempre la clase mayoritaria con este umbral y logra **87,29 % de accuracy**, pero **recall y F1 de 0** para el reingreso. Esto explica por qué no seleccionamos un modelo usando solo accuracy.

Los pesos de clase ayudan a detectar positivos, pero generan muchos falsos positivos. No significa que el modelo sea clínicamente útil. El score tampoco se presenta como una probabilidad calibrada de riesgo individual.

## Qué hace la IA generativa

El modelo clásico produce los scores. La IA generativa produce **texto sobre las métricas**, no esos scores. Son dos componentes distintos con funciones diferentes.

En modo `mock`, la clase devuelve texto determinista sin red. Esto permite desarrollar y comprobar el sistema sin claves. `OpenAIClient` utiliza el mismo contrato para una llamada real: la aplicación recibe `AIResponse` en ambos casos. El pipeline no necesita conocer los detalles HTTP.

Un timeout o un 503 puede desaparecer al repetir; un 401 por clave incorrecta normalmente no. Por eso `RetryingClient` solo reintenta errores temporales y tiene un límite. `--fail-once` demuestra ese comportamiento con una primera llamada fallida simulada.

## Qué prueban realmente los tests

- Casos pequeños con respuestas conocidas: una agregación, una matriz de confusión, una fila inválida.
- Errores esperados: falta de archivos/columnas/modelo/clave.
- Propiedades del diseño: pacientes disjuntos, target fuera de X, estado de preprocessing sin cambios en test.
- Contratos externos: cuerpo HTTP, timeout, formatos inválidos y códigos de error, todos simulados.
- Integración: CSV público → validación → entrenamiento → joblib → inferencia → resumen mock → archivos.

**95,06 % de cobertura** significa que se ejecutó esa proporción de líneas medibles de los paquetes incluidos. No significa 95,06 % de precisión del modelo ni ausencia total de errores. Las pruebas comprueban comportamientos concretos y la métrica de cobertura ayuda a localizar huecos.

## Demo de 4–5 minutos

1. Abre `proyecto_ii/README.md` y explica objetivo, origen de datos y continuidad con el I.
2. Ejecuta `python scripts/run_demo.py`. Identifica train, run y batch mock.
3. Abre `proyecto_ii/artifacts/training_metrics.json`: muestra pacientes disjuntos, comparación Dummy/modelo y limitaciones.
4. Abre `proyecto_ii/output/predictions.csv`, `metrics.json` y `summary.md`. Explica que el proveedor utilizado es mock.
5. Ejecuta `python -m pytest -q` y señala un test de fuga, uno de carga del modelo y uno de errores de API.
6. Explica la ampliación del III: backend, dashboard, despliegue y monitorización.

El tiempo de arranque de Python/sklearn puede variar en Windows. No confundas ese arranque con el tiempo de entrenamiento registrado dentro del job.

## Preguntas que deberías poder responder

| Pregunta | Respuesta breve |
| --- | --- |
| ¿Por qué regresión logística? | Es una base supervisada sencilla y reproducible para un objetivo binario. No se afirma que sea el mejor modelo posible. |
| ¿Para qué guardar con joblib? | Para reutilizar el estimador y su preprocesamiento sin volver a entrenar. |
| ¿Por qué no introducir patient_nbr en X? | Es un identificador, no una característica explicativa adecuada; se usa para separar grupos. |
| ¿Por qué el 20 % de test no coincide exactamente con el 20 % de filas? | Se reserva el 20 % de pacientes; cada paciente puede aportar distinto número de encuentros. |
| ¿Dónde se controla la fuga del scaler? | En sklearn Pipeline ajustada solo con X_train, y en un test que modifica deliberadamente test. |
| ¿Qué sucede con una categoría nueva? | El encoder admite categorías desconocidas sin fallar. |
| ¿Puede ejecutarse sin conocer readmitted? | Sí, `run` admite ausencia de etiqueta; `train` la necesita. |
| ¿Por qué mock es suficiente aquí? | El enunciado permite mock + proveedor real preparado sin clave; hace CI independiente de la red y de pagos. |
| ¿Se han probado llamadas reales a OpenAI? | No. Se implementó el adaptador y se comprobó su contrato con simulaciones. |
| ¿Por qué un fallo de calidad termina con 1? | Para detener la cadena automática y evitar publicar resultados de un lote que no cumple la política. |
| ¿Qué es idempotencia en esta entrega? | Repetir no duplica registros ni nombres de salida; el último estado identifica si el job terminó correctamente. |
| ¿Qué añade CI respecto a pytest local? | Ejecuta los checks en otro entorno al subir cambios o abrir un PR y aplica el gate de cobertura. |
| ¿Ya hay un run verde en GitHub? | Debe comprobarse después de subir estos cambios; la evidencia registrada aquí es local. |
| ¿Qué falta para el III? | API, web/dashboard conectado, despliegue, monitorización y exposición. |

Antes de entregar: revisa `AI_USAGE.md`, lee el código de las piezas principales y comprueba que puedes explicar estas respuestas con tus propias palabras.
