# Uso de herramientas de IA

Declaración del uso de IA generativa en este repositorio, siguiendo las indicaciones de la asignatura sobre citación del uso de IA.

## Herramienta

- **Claude** (Anthropic), a través de claude.ai.

## Uso por práctica

| Práctica | Para qué se usó la IA | Revisión y trabajo propio |
| --- | --- | --- |
| E0 — Entornos y Git | Guía paso a paso de los comandos de `venv` y Git, y aclaración de conceptos (fork, clone, repo propio) | Creación del entorno, del repositorio y de la rama; verificación con `check_entorno.py --strict`; respuestas de `sesion01.md` |
| E1 — pandas (`ejercicios/solucion_e1.py`) | Propuesta del script y explicación de cada paso | Ejecución y comprobación del checkpoint (140 válidas / 10 inválidas); identificación de las filas inválidas a partir de la salida del diagnóstico |
| E2 — Arquitectura (`ventas_app/`) | Propuesta de la división en módulos, excepciones, CLI con `argparse` y `DESIGN.md` | Ejecución del CLI y comparación con los resultados de la E1; elección entre dos versiones del `loader` (ver abajo) |
| E3 — pytest (`tests/`, `pytest.ini`) | Propuesta de los tests y de la configuración de pytest | Ejecución de la batería (`pytest -q` y `-m "not integration"`); se rompió un test a propósito para interpretar el informe de fallo |
| Proyecto I — Parte B (`diabetes_app/`) | Propuesta de reglas de validación, métricas, código y tests a partir del dataset elegido | Elección del dataset (el mismo del proyecto de Machine Learning) y de la Parte B frente a la alternativa de usar la API del Oura Ring (descartada por tratarse de datos personales no públicos); revisión de las reglas frente al EDA previo; ejecución del pipeline con la muestra y con el dataset completo |
| Documentación (`README.md`, `doc/`) | Redacción de explicaciones teóricas de cada práctica para estudio | Lectura y contraste con el material de la asignatura |


## Buenas prácticas seguidas

- No se han compartido claves, contraseñas ni datos personales con la herramienta.
- Todo el código se ha ejecutado y probado localmente antes de subirlo.