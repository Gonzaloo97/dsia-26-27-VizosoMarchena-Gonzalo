# Desarrollo de Soluciones de IA — Gonzalo Vizoso Marchena

Repositorio personal de prácticas de la asignatura **Desarrollo de Soluciones de IA** (DSIA, curso 2026-2027), del Máster Universitario en IA Aplicada (ICAI, Universidad Pontificia Comillas).

## Estructura del repositorio

| Carpeta / fichero | Contenido |
| --- | --- |
| `1_programacion_avanzada_python/Datos/` | Datasets del curso (`ventas.csv`, `iris.csv`) y ficheros generados por el pipeline |
| `1_programacion_avanzada_python/ejercicios/` | Enunciados de los ejercicios y `solucion_e1.py` (E1 — pandas) |
| `1_programacion_avanzada_python/ventas_app/` | Paquete modular del pipeline de ventas (E2 — arquitectura, Clean Code y SOLID) |
| `1_programacion_avanzada_python/tests/` | Tests con pytest del paquete `ventas_app` (E3) |
| `doc/` | Explicaciones de cada práctica en PDF |

## Entorno de trabajo

```bash
python -m venv .venv
source .venv/Scripts/activate     # Git Bash en Windows (Linux/Mac: source .venv/bin/activate)
pip install pandas pytest
```

## Pipeline de ventas

Desde la carpeta `1_programacion_avanzada_python`:

```bash
python -m ventas_app.cli --input Datos/ventas.csv --output Datos/ventas_limpias.csv
```

Genera `Datos/ventas_limpias.csv` (filas válidas con la columna `importe`) y `Datos/calidad_datos.json` (resumen de calidad de los datos).

## Tests

Desde la carpeta `1_programacion_avanzada_python`:

```bash
pytest -q                        # todos los tests
pytest -q -m "not integration"   # solo tests unitarios (sin leer el CSV real)
```

## Uso de IA

Para la elaboración de este repositorio se ha utilizado Claude (Anthropic) como asistente de programación y apoyo en la explicación de conceptos, conforme a las indicaciones de la asignatura sobre citación del uso de IA.