# Uso de herramientas de IA

He utilizado IA como ayuda para desarrollar y documentar este repositorio. La aportación es sustancial: incluye código, pruebas y explicaciones, además de correcciones de estilo.

## Herramientas y etapas

- **Claude (Anthropic), mediante claude.ai:** ayuda en las prácticas y el Proyecto I.
- **ChatGPT/Codex (OpenAI):** continuación y auditoría del Proyecto II el 11/11/2026; revisión documental y simplificación del código el 12/11/2026.

El registro anterior del Proyecto I describía estas actividades:

| Práctica | Ayuda de IA | Actividades recogidas en el registro original |
| --- | --- | --- |
| E0 | Explicaciones de venv, Git, fork y clone | Creación del entorno/repositorio y comprobación con `check_entorno.py --strict` |
| E1 | Propuesta de script y explicación | Ejecución del checkpoint de 140 válidas / 10 inválidas |
| E2 | Módulos, excepciones, CLI y diseño | Comparación con E1 y elección de una versión del loader |
| E3 | Tests y configuración de pytest | Ejecución de tests y ensayo de un fallo intencionado |
| Proyecto I, diabetes | Validación, métricas, código y tests | Uso del dataset de ML, contraste con el EDA y ejecuciones con muestra/dataset completo |
| Documentación | Explicaciones teóricas para estudio | Lectura y contraste con el material del curso |

Esta tabla conserva lo declarado entonces. La revisión automática del 12/11 no vuelve a acreditar esas actividades personales ni demuestra que yo haya leído o entendido cada archivo. La elección del dataset y la alternativa descartada de Oura Ring constaban en ese registro; no se ha añadido ahora un relato nuevo de trabajo propio.

## Proyecto II: qué aportó el asistente

Codex examinó el material del profesor y el repositorio, implementó una parte sustancial de `readmission_app`, scripts, tests y documentación, y ejecutó las comprobaciones registradas. Mi proyecto reutiliza los datos y paquetes del Proyecto I.

| Propuesta incorporada | Para qué sirve |
| --- | --- |
| Reutilizar `diabetes_app` como paquete | Mantener una sola versión de las reglas |
| Separar train/test por paciente | Evitar pacientes compartidos entre ambos conjuntos |
| Guardar preprocesamiento y regresión logística juntos | Aplicar en inferencia lo aprendido con train |
| Comparar con DummyClassifier | Interpretar el resultado con una referencia sencilla |
| Mock y adaptador OpenAI | Desarrollar sin red y tener una alternativa real preparada |
| Enviar solo agregados desde el pipeline | Evitar transmitir filas e identificadores |
| Estados de ejecución y escrituras temporales | Distinguir éxito, fallo y resultados incompletos |

Se descartó introducir llamadas públicas reales en pytest/CI, añadir predictores meteorológicos sin una unión de datos justificada o exigir HF como único proveedor. La implementación no incluye búsqueda de semillas, hiperparámetros o umbrales. No se han añadido API web, dashboard ni despliegue: quedan para el III.

El refactor del 11/11 añadió la creación de directorios en las CLI del I y corrigió validaciones de vacíos, IDs, decimales, infinitos y desbordamientos. La auditoría posterior corrigió estados antiguos de inferencia y JSONL conservados tras un fallo. Los cambios y sus comprobaciones se conservan en el historial de Git.

El 12/11 pedí una revisión de cada archivo incorporado al II y una simplificación del código. Codex unificó los lanzadores, eliminó una clase de simulación innecesaria, sustituyó cargas dinámicas en tests por imports normales y aclaró pasos densos. Esa revisión superó 145 pruebas en local y el código simplificado pasó GitHub Actions. Esta revisión sigue siendo asistencia de IA; no equivale a mi revisión personal.

## IA durante la ejecución del programa

| Campo | Implementación |
| --- | --- |
| Proveedor ejecutado | `mock`, offline y determinista |
| Proveedor real implementado | OpenAI Chat Completions mediante HTTPX |
| Tarea | Generar texto sobre agregados del lote y métricas del holdout |
| Modelo por defecto | `gpt-4o-mini`, configurable con `OPENAI_MODEL` o `--model` |
| Hugging Face | No implementado; `HF_TOKEN=` conserva el campo de la plantilla |
| Validación del adaptador real | Respuestas HTTP simuladas, sin una llamada real a OpenAI |

El pipeline solo envía agregados; el CLI de prompts genéricos envía el texto que se le entregue. Las comprobaciones documentadas del II usan mock o claves ficticias en tests. Los archivos de entorno están ignorados por Git. Esto describe el programa y estas comprobaciones, sin afirmar una auditoría completa de todo lo compartido históricamente en chats.

## Evidencia y procedencia

La revisión de simplificación y documentación del 12/11 se publicó en `cebdb27`, con [GitHub Actions correcto](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43268309498). La revisión local registró 145 pruebas y un 96,02 % de cobertura; la versión anterior `d3ff586` también había superado [Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514) con 145 pruebas y 95,95 %. La carpeta `proyecto_ii/evidence/` conserva métricas, ejemplos de inferencia e IA y resultados de las APIs. Los registros internos de auditoría se pueden consultar en el historial de Git. Para futuras ejecuciones, consultar [el historial de Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/workflows/ci.yml).

Los contratos `APIResult(source, data)`, endpoints y normalización de las APIs abiertas se adaptaron del [ejemplo del profesor](https://github.com/dmartincc/dsia-26-27/blob/1c2906e77c5235a04f820f4252dcb0760e240728/3_automatizacion_e_ia/ejemplos/open_api_client.py) a HTTPX, con errores tipados y tests sin red. El enunciado y el E5 se contrastaron en `1c2906e`; la primera revisión local había usado `a9ccfd3`.

Comandos desde la raíz, con el entorno activado:

```powershell
python scripts/run_demo.py
python -m readmission_app ai --provider mock --batch proyecto_ii/prompts.txt --output proyecto_ii/output/respuestas.jsonl
python -m readmission_app ai --provider mock --prompt "test" --fail-once
python scripts/open_api_client.py weather --lat 40.4168 --lon -3.7038
python -m pytest --cov=ventas_app --cov=diabetes_app --cov=readmission_app --cov-fail-under=60
```

La tabla de APIs, los comandos y las reflexiones del E5 están en el [README del Proyecto II](proyecto_ii/README.md). `python scripts/verify_open_apis.py` ejecuta red real y actualiza su instantánea; no forma parte de pytest/CI.

Referencias: [UCI](https://doi.org/10.24432/C5230J), [prevención de fuga](https://scikit-learn.org/stable/common_pitfalls.html), [GroupShuffleSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html) y [contrato de chat](https://developers.openai.com/api/reference/resources/chat).

Antes de la defensa me queda completar la lectura y comprensión personal del código. Las pruebas automáticas y esta declaración no sustituyen ese trabajo. La fecha original de descarga no consta y la incorporación de ML/IA/CI ocurrió en noviembre; se mantienen las fechas auténticas del historial.
