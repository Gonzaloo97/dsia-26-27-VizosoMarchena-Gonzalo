# Diseño de diabetes_app (Parte B del Proyecto I)

## Adaptación al dominio (qué cambia respecto a ventas_app)

| Aspecto | ventas_app (Parte A) | diabetes_app (Parte B) |
| --- | --- | --- |
| Unidad de análisis | Una venta | Un encuentro hospitalario (ingreso) |
| Carga | CSV / JSON | CSV del formato UCI: `?` como nulo y `None` conservado como texto ("prueba no realizada") |
| Reglas | 2 columnas positivas | Nulos, rangos numéricos, valores categóricos permitidos, duplicados y exclusión de pacientes fallecidos |
| Errores | Filas inválidas tal cual | Filas inválidas con columna `motivo` + recuento por regla |
| Métricas | Importe por región/producto, clientes recurrentes | Distribución de reingresos, reingreso <30 días por edad y por HbA1c, estancia media, pacientes recurrentes |
| Informe de calidad | Filas e importe total | Filas, incumplimientos por regla, % de nulos por columna, columnas casi vacías, tasa de reingreso |

## Principios SOLID aplicados

- **SRP (Responsabilidad única)** — `loader.py`, `validator.py`, `metrics.py` y `cli.py`. Cada módulo tiene un único motivo para cambiar. Por ejemplo, si cambia el criterio clínico de qué encuentro es válido, solo se modifica `validator.py`.
- **OCP (Abierto/cerrado)** — `validator.py`. Las reglas están definidas como datos (`COLUMNAS_SIN_NULOS`, `RANGOS_NUMERICOS`, `VALORES_PERMITIDOS`, `CODIGOS_ALTA_FALLECIMIENTO`) y `construir_reglas()` las recorre en bucles. Para añadir una regla nueva basta con añadir una entrada a esos diccionarios o listas, sin modificar la lógica de validación.
- **DIP (Inversión de dependencias)** — `loader.py`, `Protocol` `EncounterRepository`. `load()` depende de la interfaz y no de una fuente concreta. `CsvEncounterRepository` se registra en `REPOSITORIOS`; para añadir otra fuente (por ejemplo, una API o un Parquet) se crea una clase nueva con `load()` sin modificar `validator.py`, `metrics.py` ni `cli.py`.

## Decisiones de dominio

- **`?` es nulo, `None` no lo es.** En `max_glu_serum` y `A1Cresult`, `None` significa que la prueba no se realizó y es información útil. pandas convierte `None` en `NaN` por defecto, así que se desactiva con `keep_default_na=False`.
- **Se excluyen los pacientes fallecidos** (códigos de alta 11, 19, 20 y 21 según `IDS_mapping.csv`): no pueden reingresar y sesgarían el análisis de reingresos.
- **`weight`, `payer_code` y `medical_specialty` tienen muchos nulos pero no invalidan filas.** No son necesarias para el análisis, así que se informan en el JSON de calidad (`columnas_casi_vacias`) en lugar de descartar el 97 % del dataset.
- **Varios encuentros por paciente son válidos** (un paciente puede ingresar varias veces). Se informan como métrica (`pacientes_recurrentes`).