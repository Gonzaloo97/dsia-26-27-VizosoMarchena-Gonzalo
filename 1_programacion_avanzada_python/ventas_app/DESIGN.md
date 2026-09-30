# Diseño de ventas_app

## Principios SOLID aplicados

- **SRP (Responsabilidad única)** — `loader.py`, `validator.py`, `metrics.py` y `cli.py`. Cada módulo tiene un único motivo para cambiar: `loader` solo lee ficheros, `validator` solo decide qué filas son válidas, `metrics` solo calcula agregaciones y `cli` solo orquesta el flujo y lee los argumentos.
- **OCP (Abierto/cerrado)** — `validator.py`, lista `COLUMNAS_POSITIVAS`. La función `validar_ventas` recorre la lista en un bucle, así que para exigir que otra columna numérica sea positiva basta con añadirla a la lista, sin modificar la lógica de la función.
- **DIP (Inversión de dependencias)** — `validator.py` y `metrics.py`. Ambos reciben un `DataFrame` y no dependen de un fichero ni de un formato concreto. La procedencia de los datos queda aislada en `loader.py`. Por eso añadir la lectura de JSON (extensión) solo ha requerido cambiar `loader.py`, sin tocar `metrics.py`.

## Clean Code

- **Nombres descriptivos:** `importe_por_region`, `clientes_recurrentes`, `comprobar_columnas`... en lugar de nombres crípticos como `df2` o `res`.
- **Sin números mágicos:** los valores fijos tienen nombre (`VALOR_MINIMO`, `NUM_TOP_PRODUCTOS`, `MIN_COMPRAS_RECURRENTE`, `NOMBRE_INFORME_CALIDAD`).
- **Sin `print` de depuración:** los mensajes se emiten con `logging`, que indica el nivel (`INFO`, `ERROR`) y se puede desactivar o redirigir sin tocar el código.
- **Errores propios:** `DataLoadError` y `ValidationError` dan mensajes claros en lugar de trazas de error de pandas.