# Uso de herramientas de IA

Declaración del uso de IA generativa en este repositorio, siguiendo las indicaciones de la asignatura sobre citación del uso de IA.

## Herramienta

- **Claude** (Anthropic), a través de claude.ai.
- **ChatGPT / Codex** (OpenAI), para la continuación del Proyecto II el 11/11/2026.

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

## Proyecto II — intervención del 11/11/2026

### Alcance real de la asistencia

ChatGPT/Codex examinó el clon local del profesor y el repositorio personal, contrastó los requisitos de Proyectos I/II/III y propuso e implementó la continuación. La asistencia abarca **una parte sustancial del código, los tests y la documentación nuevos**, no solo correcciones de estilo. También ejecutó las comprobaciones locales registradas en `proyecto_ii/EVIDENCIA.md`.

Se reutilizan el dominio, los datos y los paquetes del Proyecto I. Se añadieron `readmission_app`, tests, scripts de automatización, configuración del entorno, workflow de GitHub Actions y documentación. El alumno debe revisar, comprender y poder explicar lo entregado antes de subirlo/defenderlo; esta declaración no atribuye esa revisión humana a una acción que no se ha observado.

### Decisiones y alternativas

| Decisión implementada | Motivo |
| --- | --- |
| Reutilizar `diabetes_app` mediante instalación de paquetes | Evitar dos copias divergentes de las reglas del Proyecto I |
| Separación por `patient_nbr` | Evitar encuentros de un mismo paciente a ambos lados de train/test |
| Preprocesamiento dentro de sklearn Pipeline | Ajustar imputación, escalado y categorías solo en entrenamiento |
| Modelo sencillo y DummyClassifier | Tener una referencia verificable antes de ampliar en el III |
| Mock explícito y OpenAI opcional | Demo y CI sin pago, red ni claves; adaptador real preparado |
| Agregados con lista cerrada para el prompt del pipeline | No enviar filas individuales, IDs ni diagnósticos |
| No ajustar semilla/umbral buscando mejor test | Mantener la evaluación interpretable y reproducible |
| No crear API/dashboard todavía | Son entregables del Proyecto III, no requisitos mínimos del II |

### Ejercicio de revisión/refactor de Tema 4

**Código explicado:** `diabetes_app/cli.py` carga argumentos, obtiene datos con el repositorio CSV, aplica las reglas del validador, calcula agregaciones y exporta datos e informe. Las operaciones de disco están en la CLI; las reglas se mantienen en módulos independientes. Su estructura se reutiliza desde el Proyecto II. El fallo observado es que la exportación suponía que el directorio de destino ya existía.

**Plan breve:** (1) crear el directorio de destino antes de exportar; (2) completar pruebas de ambas CLI; (3) revisar validaciones que podrían truncar conteos o fallar al convertir infinitos. Se implementó primero la creación del directorio (una línea por CLI) y se cubrió con pruebas de salida a una carpeta inexistente. Los cambios de validación se justifican y prueban por separado.

**Tres hallazgos reales corregidos:** faltaban tests de las CLI; los campos vacíos/espacios y algunos IDs mal formados podían pasar la validación; los conteos decimales se truncaban y los infinitos podían romper la conversión. Además, el diseño nuevo comprueba errores transitorios/permanentes del proveedor y evita fuga entre pacientes. No se afirma que se hayan completado los endpoints ni el RC del taller E7: pertenecen al III.

No se han fabricado diálogos con otras herramientas, revisiones humanas, commits históricos, resultados de API real ni Actions verdes. Las propuestas se aceptaron o ajustaron mediante lectura de los contratos y comprobaciones automatizadas por el asistente. Queda pendiente la revisión personal del alumno.

### IA durante la ejecución

- Proveedor efectivamente ejecutado: **mock**, offline y determinista.
- Proveedor implementado: **OpenAI Chat Completions**, HTTPX, configurado por entorno, con timeout y reintentos limitados. Contrato probado con respuestas simuladas; **no se ha realizado una llamada de pago**.
- Función: redactar un resumen de métricas agregadas; no sustituye el entrenamiento ni emite decisiones clínicas.
- No se han leído ni usado claves reales ni enviado encuentros hospitalarios a una API durante las comprobaciones.

Comandos de evidencia desde la raíz, tras instalar el proyecto:

```powershell
python scripts/run_demo.py
python -m readmission_app ai --provider mock --batch proyecto_ii/prompts.txt --output proyecto_ii/output/respuestas.jsonl
python -m readmission_app ai --provider mock --prompt "Explica recall" --fail-once
python -m pytest --cov=ventas_app --cov=diabetes_app --cov=readmission_app --cov-fail-under=60
```

### Referencias contrastadas

- Material de la asignatura: clon local `dmartincc/dsia-26-27`, commit `a9ccfd3`.
- scikit-learn: https://scikit-learn.org/stable/common_pitfalls.html
- Partición por grupos: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html
- API OpenAI: https://platform.openai.com/docs/api-reference/chat/create
- Dataset UCI: https://doi.org/10.24432/C5230J
