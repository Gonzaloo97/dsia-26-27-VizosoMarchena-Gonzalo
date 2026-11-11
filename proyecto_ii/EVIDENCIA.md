# Evidencia local de ejecución

> **Validación final (11/11/2026):** se repitieron las 35 pruebas de auditoría/APIs y la suite completa: 145 passed, cobertura 95,95 %, mínimo 60 % superado. El texto siguiente conserva la fotografía histórica anterior a la publicación; las referencias a cambios locales o publicación pendiente pertenecen a ese momento. Para el estado remoto del commit entregado, consultar [Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/workflows/ci.yml).

> **Foto histórica inicial:** las secciones siguientes y `evidence/verification.json` describen la preparación anterior al push de `b4217ad`. Posteriormente se verificó [su run verde remoto](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43041031910). Las correcciones nuevas se registran en [CIERRE_AUDITORIA.md](CIERRE_AUDITORIA.md), [verification_followup.json](evidence/verification_followup.json) y [open_api_smoke.json](evidence/open_api_smoke.json): 145 tests y cobertura 95,95 % local. Estas correcciones aún no tienen un run remoto propio. Se preserva la evidencia inicial sin atribuirle comprobaciones posteriores.

**Fecha:** 11/11/2026. **Entorno:** Windows, Python 3.12.5. **Proveedor de IA ejecutado:** mock. Esta evidencia corresponde al código preparado en la carpeta personal; no acredita todavía un run de GitHub Actions.

## Verificación automatizada

Comando ejecutado desde la raíz:

```powershell
python -m pytest --cov=ventas_app --cov=diabetes_app --cov=readmission_app --cov-report=term-missing --cov-report=xml --cov-fail-under=60 -q
```

Resultado final: **106 passed**, **95,06 % de cobertura de líneas**, umbral **60 % superado**. Se midieron 709 sentencias y quedaron 35 sin ejecutar en esta medición. Incluye todos los tests originales y los nuevos. Los paquetes contienen también algunos puntos de entrada y el generador de muestras del I que no fueron ejecutados por esta suite; no se excluyeron para mejorar el porcentaje.

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

Matriz de confusión del modelo: `[[514, 331], [57, 66]]` (filas reales 0/1; columnas predichas 0/1). El modelo detecta parte de los positivos pero produce numerosos falsos positivos. La referencia tiene accuracy alta porque no detecta ningún positivo al umbral elegido. Los resultados son modestos y se muestran sin seleccionar una semilla favorable ni presentar el sistema como clínicamente validado.

## Demo y ejercicios

`python scripts/run_demo.py` completó las tres etapas: entrenamiento, inferencia sobre el holdout y batch mock de cinco prompts con recuperación tras el fallo simulado.

- La inferencia produjo 968 predicciones y reportó cero filas de pacientes de entrenamiento.
- Las métricas descriptivas del lote holdout coincidieron con las del entrenamiento.
- El JSONL contiene cinco registros y declara `provider=mock`.
- `python scripts/run_pipeline.py` completó la cadena de inferencia, comprobación de métricas y marcador local. Los tests verifican también que el primer o segundo fallo detiene la cadena y elimina un marcador de éxito anterior. La ejecución del wrapper `.ps1` fue bloqueada por la política local; no se cambió esa política. El `.sh` no se ejecutó en Windows.
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

## Límites de esta verificación

No se ha hecho push ni observado Actions para estos cambios. No se ha ejecutado el proveedor real de pago, ni desplegado API/dashboard. Los scripts no instalan una tarea periódica. No se puede acreditar retrospectivamente un historial de commits durante octubre ni la fecha exacta de la descarga original. Estas cuestiones se distinguen de los requisitos técnicos ya implementados y comprobados localmente.
