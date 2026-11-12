# Proyecto II — Automatización e integración de servicios

**Gonzalo Vizoso Marchena · DSIA 2026–2027 · Continuación del Proyecto I y base del III.**

Mi proyecto continúa el pipeline de calidad de ingresos hospitalarios del Proyecto I con un proceso reproducible: **CSV → validación → modelo sklearn persistido → inferencia → resumen con IA → CSV/JSON/logs**. Incluye un modo offline completo y un adaptador HTTP real para OpenAI.

## 1. Instalación y demo

Todos los comandos de esta guía se ejecutan desde la **raíz de tu repositorio personal**, no desde el clon del profesor. Python de referencia: **3.12**.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
.venv\Scripts\python.exe scripts/run_demo.py
```

Si `.venv` ya existe, puedes conservarlo y ejecutar los dos comandos de instalación. Para los comandos siguientes, activa el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, utiliza `.venv\Scripts\python.exe` en lugar de `python`, como en la demo inicial. No hace falta cambiar la política de ejecución. En Git Bash se activa con `source .venv/Scripts/activate`; en Linux/macOS, con `source .venv/bin/activate`.

La demo entrena, ejecuta inferencia sobre pacientes reservados y genera cinco respuestas JSONL en modo mock, incluyendo un fallo transitorio simulado. No necesita cuenta, clave, pago ni descarga de datos. Los ficheros de salida se regeneran en cada ejecución.

## 2. Dominio, datos y objetivo

| Elemento | Decisión |
| --- | --- |
| Dominio que continuará en el III | Análisis académico de reingresos hospitalarios en pacientes con diabetes |
| Dataset | Diabetes 130-US Hospitals for Years 1999-2008, UCI |
| Fuente | https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008 |
| DOI y licencia | https://doi.org/10.24432/C5230J · CC BY 4.0 |
| Cita | Clore, J., Cios, K., DeShazo, J. y Strack, B. (2014). *Diabetes 130-US Hospitals for Years 1999-2008* [Dataset]. UCI Machine Learning Repository. |
| Datos versionados | `1_programacion_avanzada_python/Datos/diabetic_data_muestra.csv`: 5.000 encuentros, muestra del Proyecto I con semilla 42 |
| Fecha y trazabilidad | Reutilización/verificación: 11/11/2026. La fecha exacta de descarga original no quedó registrada; no se inventa. El SHA-256 del fichero usado queda en cada informe de entrenamiento. |
| Objetivo binario | `readmitted == '<30'` frente a `NO` o `>30` |
| Momento de predicción | Al alta: la estancia y los procedimientos del ingreso ya son conocidos |
| Motivación | Continuar el dominio de salud y reutilizar el pipeline existente, añadiendo un ciclo ML/IA comprobable |

Los datos son históricos de EE. UU. Este proyecto no demuestra utilidad clínica ni representa el funcionamiento de un hospital actual. El resumen de IA sirve para documentar métricas, no para recomendar tratamientos.

La muestra contiene **4.867 encuentros elegibles y 133 rechazados** según las reglas del Proyecto I, incluidas las exclusiones de fallecimiento y hospicio. El pipeline conserva el motivo de rechazo. Los códigos 11, 19, 20 y 21 figuran como fallecimiento en el `IDS_mapping.csv` local; 13 y 14 corresponden a hospicio.

Para usar el dataset completo, descarga el archivo de UCI, guarda `diabetic_data.csv` en `1_programacion_avanzada_python/Datos/` y cambia `--input`. No es necesario para ejecutar la entrega. El archivo completo está excluido de Git.

## 3. Entrenamiento y evaluación

```powershell
python -m readmission_app train --input 1_programacion_avanzada_python/Datos/diabetic_data_muestra.csv --output-dir proyecto_ii/artifacts --seed 42 --test-size 0.2 --max-error-rate 0.1
```

Se utiliza regresión logística con pesos de clase equilibrados y un umbral didáctico fijo de 0,5. Una `Pipeline` de sklearn incorpora imputación, escalado numérico y codificación one-hot; todos los parámetros del preprocesamiento se ajustan solo con entrenamiento.

- **Partición por paciente:** `GroupShuffleSplit` reserva el 20 % de los grupos `patient_nbr`. El porcentaje de filas puede diferir ligeramente del 20 %. Ningún paciente comparte entrenamiento y test.
- **Variables:** 8 conteos/duraciones y 5 categóricas: edad, sexo, diagnóstico principal, HbA1c y glucosa. La lista exacta está en `readmission_app/model.py` y en el informe.
- **Excluidas del modelo:** `readmitted`, `encounter_id`, `patient_nbr` y cualquier columna no incluida en la lista cerrada. `discharge_disposition_id` determina elegibilidad, no es predictor.
- **Comparación:** `DummyClassifier(strategy='prior')` sirve de referencia. Se reportan accuracy, balanced accuracy, precision, recall, F1, ROC-AUC, average precision y matriz de confusión `[[TN, FP], [FN, TP]]`.
- **Configuración fija:** el código no incluye búsqueda de hiperparámetros, semillas ni umbrales. Si train o test no contienen ambas clases, detiene el entrenamiento y pide más datos. Esto describe la implementación; el código por sí solo no demuestra cuándo se tomó cada decisión.
- **Scores:** al utilizar pesos de clase, el score no se presenta como probabilidad clínica calibrada.

Resultados concretos y versiones verificadas: [EVIDENCIA.md](EVIDENCIA.md). La evaluación puede variar ligeramente entre versiones/plataformas; el informe registra versiones, semilla y hash de entrada. Para reproducir el entorno observado, se incluye `requirements-verified.txt` en la raíz.

| Salida de entrenamiento | Contenido |
| --- | --- |
| `model.joblib` | Preprocesamiento + estimador + metadatos + IDs de pacientes de train para detectar solapamientos |
| `training_metrics.json` | Métricas de test y baseline, partición, versiones, semilla, hash y limitaciones |
| `holdout.csv` | Encuentros reservados para comprobar la demo; nunca usados en fit |
| `holdout_predictions.csv` | Etiqueta real y score/clase predicha del holdout |
| `quality.json`, `status.json`, `run.log` | Calidad de entrada, estado del job y registro operativo |

El modelo entrenado se guarda en la carpeta local. Se excluye de Git junto con el resto de artefactos regenerables: el enunciado permite entregar instrucciones claras de reentrenamiento. Solo se deben cargar `joblib` propios o de confianza; su formato puede ejecutar código al deserializar. Si cambia la versión de sklearn, reentrena.

## 4. Inferencia integrada e IA

```powershell
python -m readmission_app run --input proyecto_ii/artifacts/holdout.csv --model-path proyecto_ii/artifacts/model.joblib --output-dir proyecto_ii/output --provider mock
```

La inferencia no reentrena y **funciona sin la columna `readmitted`**. Si esta existe, se validan sus valores y se calculan métricas descriptivas del lote. Estas métricas no se confunden con una nueva evaluación independiente. El informe indica cuántas filas pertenecen a pacientes usados en entrenamiento.

La salida incluye `clean.csv`, `rejected.csv`, `predictions.csv`, `quality.json`, `metrics.json`, `ai_summary.json`, `summary.md`, `run.log` y `status.json`. El CSV de predicciones contiene los identificadores locales, el score y la clase binaria. El proveedor IA recibe **solo agregados**, nunca IDs ni filas individuales. El modo `mock` se identifica explícitamente como simulación y no intenta aparentar una llamada real.

### Proveedor real opcional: OpenAI

```powershell
Copy-Item .env.example .env
# Edita .env e introduce OPENAI_API_KEY. No subas este fichero.
python -m readmission_app run --input proyecto_ii/artifacts/holdout.csv --provider openai
```

| Configuración | Valor por defecto / uso |
| --- | --- |
| `AI_PROVIDER` | `mock`; también `openai` |
| `OPENAI_API_KEY` | Vacía; obligatoria solo para OpenAI |
| `OPENAI_MODEL` | `gpt-4o-mini`; ajustable con `--model` a un modelo disponible para tu cuenta |
| `HF_TOKEN` | Vacía y reservada conforme a la plantilla vigente; no se utiliza ni activa un adaptador HF |
| `AI_TIMEOUT_SECONDS` | 20 segundos por intento, máximo configurable 120 |
| `AI_MAX_RETRIES` | 2 reintentos: hasta 3 intentos; configurable 0–5 |
| `--env-file` | Ruta explícita opcional; por defecto `.env` del directorio actual |

Los flags prevalecen sobre el entorno; las variables ya definidas en el sistema prevalecen sobre `.env`. El adaptador implementa `POST https://api.openai.com/v1/chat/completions` mediante HTTPX, con límite de salida y `store=false`. Este parámetro no constituye una garantía de retención cero del proveedor. No se ejecutó una llamada real de pago; el contrato HTTP se prueba con respuestas simuladas. El enunciado permite mock + diseño listo cuando no hay clave.

Se reintentan timeout, fallos de conexión, HTTP 408/429 y 5xx con espera creciente y jitter. HTTP 400/401/403 y respuestas inválidas fallan directamente. El cliente nunca pasa silenciosamente de OpenAI a mock. El texto generado se guarda sin ejecutarlo. Recibe agregados del lote y métricas históricas del holdout; cada bloque está identificado en `ai_summary.json`. Las cifras del lote se contrastan con `metrics.json` y las de evaluación con `training_metrics.json`.

### Batch y retry del E5

```powershell
python -m readmission_app ai --provider mock --batch proyecto_ii/prompts.txt --output proyecto_ii/output/respuestas.jsonl
python -m readmission_app ai --provider mock --prompt "Explica recall" --fail-once
```

Cinco prompts producen cinco registros JSONL con `prompt`, `provider`, `text` y `model`. El comando de prompts genéricos envía exactamente lo que se le pasa si se elige un proveedor real; úsalo con contenido de práctica sin datos personales. La restricción a agregados está implementada en el pipeline de reingresos.

Un destino JSONL representa el intento actual: se elimina el resultado anterior antes de leer los prompts y configurar el proveedor. Si falla el batch no queda un JSONL antiguo ni un batch parcial. Se protegen el archivo de prompts y el archivo de entorno frente a su sobrescritura. La configuración del proveedor se evalúa dentro del job de inferencia: una clave o configuración inválida deja `status=failed`, sin predicciones anteriores.

El enunciado vigente recomienda Hugging Face pero admite otro proveedor documentado, incluido OpenAI. Aquí la tarea es generación de texto (`Chat Completions`) y el modelo por defecto es `gpt-4o-mini`. No se afirma haber implementado HF. Las llamadas públicas independientes del E5, su contrato y la tabla de errores están en [E5_APIS_ABIERTAS.md](E5_APIS_ABIERTAS.md).

## 5. Automatización y códigos de salida

| Código | Significado |
| --- | --- |
| 0 | Job completado |
| 1 | No se cumple el umbral de calidad o no quedan filas válidas |
| 2 | Entrada, configuración, argumentos o acceso a ficheros incorrectos |
| 3 | Entrenamiento/modelo ausente o incompatible |
| 4 | Fallo del cliente de IA |

El `status.json` de un job iniciado pasa por `running`, `success` o `failed`. La publicación se considera válida solo con `success` y exit 0. Antes de regenerar salidas se eliminan únicamente los nombres de artefactos propios de ese job, evitando que una ejecución fallida parezca conservar predicciones válidas anteriores. Cada fichero se escribe de forma atómica. **No ejecutar dos jobs concurrentes contra el mismo directorio**: utiliza un destino distinto por ejecución concurrente.

La idempotencia se refiere a salidas de datos sin duplicados: los logs/duraciones varían y una llamada al proveedor real puede generar un texto distinto o consumir cuota nuevamente.

Lanzador portable, sin instalar tareas en el equipo:

```powershell
python scripts/run_pipeline.py
```

También se incluyen `scripts/run_pipeline.ps1` y `bash scripts/run_pipeline.sh`. Ambos llaman a `run_pipeline.py`, que concentra la cadena: inferencia → comprobar métricas → escribir `LAST_OK.txt` solo si todo pasa. Salida por fecha en `proyecto_ii/output_daily/`. Ambos wrappers se ejecutaron correctamente durante el cierre del 11/11/2026, el segundo con Git Bash en Windows. El Bash busca `.venv/bin/python` y admite `.venv/Scripts/python.exe`; no se ha ensayado aún en Linux. No se cambiaron políticas de ejecución. Ejemplo didáctico de cron, **no instalado**:

```cron
15 2 * * * /bin/bash /ruta/al/repo/scripts/run_pipeline.sh
```

### E4 de ventas, conservando el checkpoint del profesor

```powershell
python scripts/pipeline_ventas.py --input 1_programacion_avanzada_python/Datos/ventas.csv --output-dir proyecto_ii/output_ventas --max-error-rate 0.1
python scripts/check_metrics.py --metrics proyecto_ii/output_ventas/metrics.json --min-rows-out 100
python scripts/pipeline_ventas.py --input 1_programacion_avanzada_python/Datos/ventas.csv --output-dir proyecto_ii/output_ventas_gate --max-error-rate 0.05
```

El primer comando produce **140 válidas / 10 rechazadas**; el último termina con exit 1. En PowerShell consulta `$LASTEXITCODE` inmediatamente después. No hay que cambiar código para endurecer la política.

La cadena literal de Bash del E4 está en `scripts/run_cadena_ventas.sh`: limpiar → comprobar métricas → copiar a `publicado/` y escribir `LAST_OK.txt`. Se verificaron éxito, gate rojo y fallo del segundo paso, sin conservar publicación ni marcador antiguos. Desde Git Bash/Linux:

```bash
bash scripts/run_cadena_ventas.sh
bash scripts/run_cadena_ventas.sh proyecto_ii/output_ventas_gate 0.05
bash scripts/run_cadena_ventas.sh proyecto_ii/output_ventas_min 0.1 999999
```

Los dos últimos comandos deben terminar con código 1. Los destinos de ejemplo están ignorados por Git. Las entradas no finitas y los importes que desbordan se rechazan; un agregado total no representable produce error de datos controlado.

## 6. Tests y CI

```powershell
python -m pytest -q
python -m pytest -q -m "not integration"
python -m pytest --cov=ventas_app --cov=diabetes_app --cov=readmission_app --cov-report=term-missing --cov-fail-under=60
```

Los tests cubren el Proyecto I y el II: validación, CLI, contrato de datos, aislamiento por paciente, preprocesamiento ajustado solo en train, serialización/inferencia, categorías nuevas, errores de modelo, ausencia de etiqueta, idempotencia, gate de calidad, batch, timeout, 401/429/503 y agotamiento de reintentos. Los tests HTTP no salen a internet.

Workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). Instala Python 3.12, ejecuta toda la suite con cobertura ≥60 %, corre la demo y conserva informes como artefactos. Se dispara con push a main/master y con PR. [Abrir Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/workflows/ci.yml).

**Versión publicada comprobada:** [run 43087452514](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514), commit `d3ff586`, **145 pruebas y 95,95 % de cobertura**. El run anterior de `b4217ad` tenía 106 pruebas y 95,06 %. Las simplificaciones del 12/11/2026 aún son locales; sus comprobaciones están en [REVISION_SIMPLICIDAD.md](REVISION_SIMPLICIDAD.md). El [cierre de auditoría](CIERRE_AUDITORIA.md) recoge los defectos corregidos y las limitaciones pendientes.

## 7. Organización y continuidad

| Ruta | Responsabilidad |
| --- | --- |
| `1_programacion_avanzada_python/` | Proyecto I conservado; se reutiliza `diabetes_app` como dependencia local instalable |
| `readmission_app/data.py` | Adaptador de lectura y reglas existentes; inferencia sin etiqueta |
| `readmission_app/model.py` | Variables, split, sklearn, métricas, persistencia, predict |
| `readmission_app/ai_client.py` | Contrato de IA, proveedores y reintentos |
| `readmission_app/pipeline.py` | Orquestación train/run y agregado que se envía a IA |
| `readmission_app/config.py`, `errors.py`, `storage.py` | Configuración, fallos, logs y escritura |
| `readmission_app/cli.py` | Entrada por terminal |
| `tests/`, `scripts/` | Pruebas nuevas, demo y automatización |
| `proyecto_ii/AUDITORIA_TEMAS.md` | Qué faltaba en cada tema y evidencia que lo resuelve |
| `proyecto_ii/GUIA_ESTUDIO.md` | Explicación del funcionamiento y preguntas para defenderlo |
| `AI_USAGE.md` | Ayuda recibida de IA y revisión personal pendiente |

En el Proyecto III se añadirá una API con `/health`, predicción y análisis, una web/dashboard que consuma ese backend, despliegue verificable, monitorización por petición y demo de 5–7 minutos. `predict`, `run_job` y `CompletionClient` se reutilizan; la API no tendrá que copiar la lógica a un endpoint. La web, el servidor y el despliegue **todavía no forman parte de esta entrega II**.

Diseño detallado: [DESIGN.md](DESIGN.md). Revisión por temas: [AUDITORIA_TEMAS.md](AUDITORIA_TEMAS.md).
