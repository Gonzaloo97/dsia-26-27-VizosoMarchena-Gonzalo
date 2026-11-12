# Evidencia de ejecución

El código simplificado se publicó el 12/11/2026 en `cebdb27` y [superó GitHub Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43268309498) con 145 pruebas; el workflow también ejecutó la demo y guardó artefactos. La cobertura local documentada para esa revisión es del 96,02 %. La versión anterior `d3ff586` había superado [145 pruebas y 95,95 %](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514) el 11/11/2026.

La revisión de simplicidad del 12/11 está documentada en [REVISION_SIMPLICIDAD.md](REVISION_SIMPLICIDAD.md) y su código ya está publicado. Los registros anteriores se conservan como evidencia histórica, sin atribuirles las pruebas del commit nuevo.

| Registro | Qué acredita |
| --- | --- |
| [verification.json](evidence/verification.json) | Primera ejecución local: 106 tests, 95,06 % |
| [verification_followup.json](evidence/verification_followup.json) | Correcciones posteriores: 145 tests, 95,95 %, wrappers y APIs |
| [validation_final.json](evidence/validation_final.json) | Última comprobación local antes de publicar `d3ff586` |
| [Run 43087452514](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514) | Ejecución histórica de `d3ff586`: 145 tests, 95,95 % |
| [Run 43268309498](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43268309498) | Validación remota de `cebdb27`: tests, demo y artefactos correctos; revisión local 145 tests y 96,02 % |
| [open_api_smoke.json](evidence/open_api_smoke.json) | Instantánea de APIs reales; su campo `checked_at_utc` indica cuándo se regeneró |

Los JSON se conservan con sus resultados y fechas. La instantánea de APIs puede cambiar al ejecutar explícitamente `verify_open_apis.py`; no es una salida fija del modelo ni de pytest.

## Primera verificación local: registro histórico del 11/11

Entorno: Windows, Python 3.12.5; proveedor ejecutado: mock. El detalle siguiente corresponde a la primera preparación, anterior a las correcciones y al push.

### Comando y resultado inicial

Comando ejecutado desde la raíz:

```powershell
python -m pytest --cov=ventas_app --cov=diabetes_app --cov=readmission_app --cov-report=term-missing --cov-report=xml --cov-fail-under=60 -q
```

Resultado de esa primera ejecución: **106 passed**, **95,06 % de cobertura de líneas**, umbral **60 % superado**. Se midieron 709 sentencias y quedaron 35 sin ejecutar en esta medición. Incluye todos los tests originales y los nuevos. La medición incluye el generador de muestras del I aunque no se ejecutara en esa suite; no mide cobertura de ramas.

El comando de instalación editable del paquete se ejecutó correctamente. Para resolver la ausencia de acceso a PyPI en el entorno de trabajo se reutilizaron instalaciones locales disponibles de las herramientas de construcción/cobertura. No se modificaron otros proyectos. La instalación nueva estándar queda descrita en el README; no se afirma haber descargado todas las dependencias en un entorno limpio conectado.

Versiones relevantes:

| Componente | Versión |
| --- | --- |
| Python | 3.12.5 |
| pandas | 3.0.6 |
| NumPy | 2.5.3 |
| scikit-learn | 1.9.1 |
| joblib | 1.6.0 |
| pytest | 9.1.1 |
| pytest-cov | 7.1.0 |
| coverage | 7.16.1 |

Las versiones exactas instaladas y sus dependencias transitivas están en `requirements-verified.txt`; `requirements.txt` expresa los rangos del proyecto. El snapshot es una referencia del entorno medido, no una comprobación de disponibilidad futura en un índice de paquetes.

## Entrenamiento sobre la muestra pública

| Dato | Resultado |
| --- | --- |
| Filas iniciales | 5.000 |
| Filas elegibles | 4.867 |
| Filas rechazadas | 133 (2,66 %) |
| Train | 3.899 encuentros / 3.783 pacientes |
| Holdout | 968 encuentros / 946 pacientes |
| Pacientes compartidos | **0** |
| Positivos en holdout | 123 (12,71 %) |
| Semilla | 42 |
| Umbral | 0,5 fijado de antemano |

Hash SHA-256 de la muestra empleada:

```text
68160fe3f2835ee56eeb357b595de5723b8ad3be3dd42b599e5e6b37530c46e5
```

| Métrica holdout | Regresión logística | Dummy (prior) |
| --- | ---: | ---: |
| Accuracy | 0,5992 | 0,8729 |
| Balanced accuracy | 0,5724 | 0,5000 |
| Precision clase positiva | 0,1662 | 0,0000 |
| Recall clase positiva | 0,5366 | 0,0000 |
| F1 clase positiva | 0,2538 | 0,0000 |
| ROC-AUC | 0,6120 | 0,5000 |
| Average precision | 0,2481 | 0,1271 |

Matriz de confusión del modelo: `[[514, 331], [57, 66]]` (filas reales 0/1; columnas predichas 0/1). El modelo detecta parte de los positivos pero produce numerosos falsos positivos. La referencia tiene accuracy alta porque no detecta ningún positivo al umbral elegido. Los resultados son modestos. La implementación utiliza una semilla fija y no incluye búsqueda de la mejor semilla; no se presenta el sistema como clínicamente validado.

## Demo y ejercicios

`python scripts/run_demo.py` completó las tres etapas: entrenamiento, inferencia sobre el holdout y batch mock de cinco prompts con recuperación tras el fallo simulado.

- La inferencia produjo 968 predicciones y reportó cero filas de pacientes de entrenamiento.
- Las métricas descriptivas del lote holdout coincidieron con las del entrenamiento.
- El JSONL contiene cinco registros y declara `provider=mock`.
- `python scripts/run_pipeline.py` completó la cadena de inferencia, comprobación de métricas y marcador local. Los tests verifican también que el primer o segundo fallo detiene la cadena y elimina un marcador de éxito anterior. En esta primera ejecución no se verificaron los wrappers. El cierre posterior sí registró PowerShell y Git Bash en Windows, como muestra `verification_followup.json`.
- Los tests verificaron además el checkpoint E4 de ventas (140/10), el gate que termina con exit 1 y la repetición idempotente.
- La integración HTTP se verificó con stubs, incluidos timeouts, autorización, saturación, fallo del servidor y respuesta vacía; no se utilizó una clave real.

## Ficheros de evidencia versionables

| Fichero | Qué permite comprobar |
| --- | --- |
| [evidence/training_metrics.json](evidence/training_metrics.json) | Split, hash, versiones, métricas exactas, baseline y limitaciones |
| [evidence/quality.json](evidence/quality.json) | Cantidades y motivos de rechazo |
| [evidence/inference_metrics.json](evidence/inference_metrics.json) | Métricas del lote y ausencia de solapamiento con train |
| [evidence/ai_summary.json](evidence/ai_summary.json) | Proveedor mock, texto y agregados enviados al cliente |
| [evidence/respuestas.jsonl](evidence/respuestas.jsonl) | Cinco respuestas del E5 |
| [evidence/verification.json](evidence/verification.json) | Resumen de checks y cobertura local |

Estas copias pequeñas documentan la ejecución del 11/11/2026. La demo regenera los archivos de trabajo de `artifacts/` y `output/`, no sobrescribe automáticamente estas evidencias históricas. Si cambia código/datos y se quiere actualizar la evidencia, se debe volver a ejecutar y copiar los resultados correspondientes.

## Límites y estado actual

La publicación de `cebdb27` y su GitHub Actions están verificados. La revisión de simplicidad del 12/11 ya no está pendiente de publicar. No se ha ejecutado OpenAI real ni desplegado API/dashboard. Los scripts no instalan tareas periódicas. No consta la fecha exacta de descarga ni trabajo de ML/IA durante octubre; no se reconstruye retrospectivamente. Las comprobaciones técnicas realizadas por Codex no acreditan mi lectura y comprensión personal.
