# Diseño de ventas_app

## Principios SOLID aplicados

- **SRP (Responsabilidad única)** — `loader.py`, `validator.py`, `metrics.py` y `cli.py`. Cada módulo tiene un único motivo para cambiar: `loader` solo lee ficheros, `validator` solo decide qué filas son válidas, `metrics` solo calcula agregaciones y `cli` solo orquesta el flujo y lee los argumentos.
- **OCP (Abierto/cerrado)** — `validator.py`, lista `COLUMNAS_POSITIVAS`. La función `validar_ventas` recorre la lista en un bucle, así que para exigir que otra columna numérica sea positiva basta con añadirla a la lista, sin modificar la lógica de la función.
- **DIP (Inversión de dependencias)** — `loader.py`, `Protocol` `SalesRepository`. La función `load()` trabaja con la abstracción `SalesRepository` (cualquier objeto con un método `load()` que devuelva un DataFrame), no con un formato concreto. Las implementaciones `CsvSalesRepository` y `JsonSalesRepository` se eligen según la extensión del fichero. Además, `validator.py` y `metrics.py` solo reciben un `DataFrame`, así que no dependen de la fuente de datos.
- **ISP (Segregación de interfaces)** — `loader.py`, `Protocol` `SalesRepository`. La interfaz solo exige un método, `load()`. Quien implementa un repositorio de lectura no está obligado a implementar métodos que no necesita (guardar, sincronizar...).

## Extensión: JsonSalesRepository

Se ha añadido `JsonSalesRepository` en `loader.py` y se ha registrado en el diccionario `REPOSITORIOS`. **No ha sido necesario modificar `metrics.py`, `validator.py` ni `cli.py`.** Esto cumple a la vez OCP (se amplía añadiendo código nuevo, sin tocar el existente) y DIP (el resto del programa depende de la interfaz, no del formato).

## Clean Code

- **Nombres descriptivos:** `importe_por_region`, `clientes_recurrentes`, `comprobar_columnas`... en lugar de nombres crípticos como `df2` o `res`.
- **Sin números mágicos:** los valores fijos tienen nombre (`VALOR_MINIMO`, `NUM_TOP_PRODUCTOS`, `MIN_COMPRAS_RECURRENTE`, `NOMBRE_INFORME_CALIDAD`).
- **Sin `print` de depuración:** los mensajes se emiten con `logging`, que indica el nivel (`INFO`, `ERROR`) y se puede desactivar o redirigir sin tocar el código.
- **Errores propios:** `DataLoadError` y `ValidationError` dan mensajes claros en lugar de trazas de error de pandas.
- **Comentarios del porqué, no del qué:** el código se explica con nombres y docstrings; los comentarios solo justifican decisiones no evidentes (por ejemplo, por qué `NaN > 0` deja fuera los vacíos o por qué el importe se convierte a `float` antes de escribir el JSON).
- **I/O en los bordes:** solo `loader.py` lee ficheros y solo `cli.py` escribe. `validator.py` y `metrics.py` no tienen efectos laterales, por eso se pueden testear con DataFrames en memoria.