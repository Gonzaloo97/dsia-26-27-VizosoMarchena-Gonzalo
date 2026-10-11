# Desarrollo de Soluciones de IA — Gonzalo Vizoso Marchena

Repositorio personal de prácticas de la asignatura **Desarrollo de Soluciones de IA** (DSIA, curso 2026-2027), del Máster Universitario en IA Aplicada (ICAI, Universidad Pontificia Comillas).

## Estructura

| Carpeta / fichero | Contenido |
| --- | --- |
| `sesion01.md` | Notas y autoevaluación de la sesión 1 (E0 — entornos y Git) |
| `1_programacion_avanzada_python/Datos/` | Datasets (`ventas.csv` del curso y muestra de diabetes) y ficheros generados por los pipelines |
| `1_programacion_avanzada_python/ejercicios/` | Enunciados y `solucion_e1.py` (E1 — pandas) |
| `1_programacion_avanzada_python/ventas_app/` | Pipeline de ventas (E2) — **Proyecto I, Parte A** |
| `1_programacion_avanzada_python/diabetes_app/` | Pipeline de ingresos hospitalarios de pacientes diabéticos — **Proyecto I, Parte B** |
| `1_programacion_avanzada_python/tests/` | Tests con pytest (E3 y Proyecto I) |
| `doc/` | Explicaciones de cada práctica en PDF |
| `AI_USAGE.md` | Declaración del uso de IA |

## Entorno

```bash
python -m venv .venv
source .venv/Scripts/activate     # Git Bash en Windows (Linux/Mac: source .venv/bin/activate)
python -m pip install pandas pytest
```

Los comandos siguientes se ejecutan **desde la carpeta `1_programacion_avanzada_python`**.

## E1 — Script de pandas

```bash
python ejercicios/solucion_e1.py
```

## Proyecto I — Parte A: pipeline de ventas (`ventas_app`, E2)

```bash
python -m ventas_app.cli --input Datos/ventas.csv --output Datos/ventas_limpias.csv
```

- **Entrada:** CSV o JSON (lista de registros) con las columnas `fecha`, `region`, `producto`, `unidades`, `precio_unitario` y `cliente_id`.
- **Fila válida:** `unidades` y `precio_unitario` numéricos y mayores que 0.
- **Salidas:** `Datos/ventas_limpias.csv` (filas válidas con la columna `importe`) y `Datos/calidad_datos.json` (filas totales, válidas, inválidas e importe total).
- **Métricas:** importe por región, top 3 productos por importe y clientes con más de una compra.
- **Diseño:** principios SOLID y Clean Code en `ventas_app/DESIGN.md`.

## Proyecto I — Parte B: pipeline de ingresos hospitalarios de pacientes diabéticos

Pipeline de calidad de datos sobre registros de ingresos (encuentros) de pacientes diabéticos, orientado al análisis de **reingresos hospitalarios**.

### Dataset

| Campo | Valor |
| --- | --- |
| Nombre | Diabetes 130-US Hospitals for Years 1999-2008 |
| Origen | UCI Machine Learning Repository |
| URL | https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008 |
| DOI | 10.24432/C5230J |
| Licencia | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| Cita | Clore, J., Cios, K., DeShazo, J. y Strack, B. (2014). *Diabetes 130-US Hospitals for Years 1999-2008* [Dataset]. UCI Machine Learning Repository. |
| Fecha de descarga | DD/MM/2026 *(completar)* |
| Tamaño original | 101 766 encuentros × 50 columnas (~18 MB) |

**Datos en el repositorio:** solo se versiona una **muestra de 5 000 filas** (`Datos/diabetic_data_muestra.csv`). El fichero completo no se sube (está en `.gitignore`). Para regenerar la muestra, se descarga `diabetic_data.csv` de la URL anterior, se guarda en `Datos/` y se ejecuta:

```bash
python -m diabetes_app.crear_muestra --input Datos/diabetic_data.csv --output Datos/diabetic_data_muestra.csv
```

La muestra es reproducible (semilla fija).

También se incluye `Datos/IDS_mapping.csv` (del mismo origen), que traduce a texto los códigos numéricos de `admission_type_id`, `discharge_disposition_id` y `admission_source_id`.

### Ejecución

```bash
python -m diabetes_app.cli --input Datos/diabetic_data_muestra.csv --output Datos/diabetes_limpio.csv
```

El mismo comando funciona con el fichero completo (`--input Datos/diabetic_data.csv`).

**Salidas:**

- `Datos/diabetes_limpio.csv`: encuentros válidos.
- `Datos/calidad_diabetes.json`: filas totales, válidas e inválidas; incumplimientos por regla; porcentaje de nulos por columna; columnas casi vacías; porcentaje de nulos encubiertos (códigos "desconocido" de `IDS_mapping.csv`); pacientes únicos y tasa global de reingreso en menos de 30 días.

### Reglas de validación

| Regla | Detalle |
| --- | --- |
| Columnas obligatorias | Si falta alguna, se lanza `ValidationError` |
| Nulos | `encounter_id`, `patient_nbr`, `gender`, `age`, `diag_1` (diagnóstico principal) y `readmitted` no pueden estar vacíos |
| Tipos y rangos | `time_in_hospital` entre 1 y 14 días; `number_diagnoses` entre 1 y 16; conteos de procedimientos, medicamentos y visitas ≥ 0 |
| Valores permitidos | `gender` ∈ {Female, Male}; `age` en los 10 tramos de edad; `readmitted` ∈ {NO, >30, <30}; `A1Cresult` y `max_glu_serum` en sus categorías |
| Duplicados | `encounter_id` debe ser único |
| Pacientes fallecidos | Códigos de alta 11, 19, 20 y 21: se excluyen porque no pueden reingresar |

Los valores `?` del dataset se leen como nulos; `None` en `A1Cresult` / `max_glu_serum` se conserva, porque significa "prueba no realizada".

**Nulos encubiertos:** según `IDS_mapping.csv`, algunos códigos de ID significan "desconocido" (`NULL`, `Not Available`, `Not Mapped`, `Unknown/Invalid`). No invalidan la fila, pero su porcentaje se informa en el JSON de calidad. En el dataset completo afectan al 10,2 % de `admission_type_id`, al 4,6 % de `discharge_disposition_id` y al 6,9 % de `admission_source_id`.

### Métricas

1. Distribución de reingresos (% NO, >30 días, <30 días).
2. Tasa de reingreso en menos de 30 días por tramo de edad.
3. Tasa de reingreso en menos de 30 días según el resultado de HbA1c (incluido "no medida").
4. Estancia media (días) según la categoría de reingreso.
5. Pacientes con más de un encuentro.

**Diseño:** ver `diabetes_app/DESIGN.md`.

## Tests (E3 y Proyecto I)

```bash
pytest -q                        # todos los tests
pytest -q -m "not integration"   # solo unitarios (sin leer los datasets reales)
```

## Uso de IA

Ver `AI_USAGE.md`.