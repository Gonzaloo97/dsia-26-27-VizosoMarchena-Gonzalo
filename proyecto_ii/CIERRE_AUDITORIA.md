# Cierre técnico de la auditoría del Proyecto II

> **Validación final (11/11/2026):** se repitieron las 35 pruebas de auditoría/APIs y la suite completa: 145 passed, cobertura 95,95 %, mínimo 60 % superado. La [evidencia final](evidence/validation_final.json) registra esta ejecución, la demo y los lanzadores Bash. El texto siguiente conserva la fotografía histórica anterior a la publicación; las referencias a cambios locales o publicación pendiente pertenecen a ese momento. Para el estado remoto del commit entregado, consultar [Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/workflows/ci.yml).

**Fecha:** 11/11/2026. **Base:** `b4217ad231b11543a046180b404ac13aa5cebf09`. **Estado de este cierre:** cambios locales, sin commit/push. Referencia contrastada: [enunciado vigente del profesor](https://github.com/dmartincc/dsia-26-27/blob/1c2906e77c5235a04f820f4252dcb0760e240728/proyectos/proyecto_ii/README.md), commit `1c2906e`.

## Resultado y evidencia

Se han resuelto los cuatro defectos reproducidos y completado la práctica de APIs abiertas, la plantilla de entorno y la documentación desactualizada. La suite local contiene **145 pruebas pasando**, **805 de 839 sentencias cubiertas: 95,95 %**, gate 60 % superado. No es cobertura de ramas ni garantía de ausencia de otros errores.

- [Verificación nueva](evidence/verification_followup.json): resultados, gate positivo/negativo, demo y wrappers.
- [Smokes HTTP reales](evidence/open_api_smoke.json): weather, country, fx, github y país inexistente, con comandos, respuestas y fecha.
- [Práctica E5 explicada](E5_APIS_ABIERTAS.md): contrato APIResult/AIResponse, tabla de errores, encaje y citación.
- [Run remoto de la base b4217ad](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43041031910): 106 tests, cobertura 95,06 %, demo y artefactos correctos. Este run no ejecutó las correcciones locales posteriores.

La demo volvió a entrenar sobre la muestra de 5.000 filas, infirió sobre los 968 encuentros reservados y generó cinco respuestas mock con recuperación tras fallo simulado. El informe training_metrics.json generado coincide exactamente con el histórico versionado: se mantienen 4.867 encuentros elegibles, cero pacientes compartidos, F1 0,2538 y ROC-AUC 0,6120. No se ha ajustado el modelo para mejorar artificialmente el test.

## Matriz de cierre

| Requisito / hallazgo | Estado tras el cierre | Evidencia |
| --- | --- | --- |
| II.1: dominio, datos, origen, licencia y motivación | Completo documentalmente | README §2, muestra incluida y hash en métricas |
| II.2: CLI reproducible y logs | Verificado | Demo train/run/ai y logs |
| II.3: train sklearn, persistencia e inferencia | Verificado | Modelo reentrenado, joblib y ejecución holdout |
| II.3: métricas básicas | Verificado | Informe nuevo idéntico al versionado, baseline incluido |
| II.4: unitarios, integración y carga/inferencia | Verificado | 145 tests locales; integración sobre muestra real |
| II.5: mock y proveedor real documentado | Implementado conforme a alternativa sin clave | CompletionClient, OpenAI, stubs; sin llamada de pago |
| II.6: entorno/dependencias | Completo | requirements, `.env.example` con HF_TOKEN vacío y su alcance explicado |
| II.7: citación de IA | Actualizada | AI_USAGE declara asistencia sustancial y revisión humana pendiente |
| II.8: núcleo modular para el III | Conservado | Datos, modelo, jobs, IA y almacenamiento separados |
| H1: estado antiguo success tras configuración inválida | Corregido y probado | DeferredClient y tres regresiones de configuración |
| H2: JSONL antiguo tras fallo | Corregido y probado | Fallo de clave, input y mitad del batch sin destino anterior |
| H3: overflow de enteros de diabetes | Corregido y probado | Rechazo fuera de int64; límite máximo válido comprobado |
| H4: infinito/desbordamiento de ventas | Corregido y probado | Rechazo por fila y error de datos si desborda el agregado |
| E3: fixtures, bordes, integración y comandos | Conservado y ampliado | Suite de I y II |
| CI: gate ≥60 % | Verificado localmente y en base remota | 95,95 % nuevo; 95,06 % base publicada |
| CI: comprobar que el gate rechaza | Verificado localmente | Umbral 100 → exit 2; umbral 60 → exit 0 |
| CI: ensayo remoto rojo/restauración | No acreditado | No se ha publicado una rama de ensayo ni disparado ese run |
| CI: README con enlace real | Corregido | Enlace al run concreto y separación de versiones |
| CI: evidencia del batch | Preparada para siguiente run | Workflow ahora conserva JSONL y status de inferencia |
| E4: flags, checkpoint 140/10 y gate 0,05 | Verificado | Tests y ejecución Bash real |
| E4: cadena literal Bash / publicación condicionada | Verificado | run_cadena_ventas.sh: éxito, fallo del gate y fallo del paso de métricas |
| E4: wrappers | Verificados en Windows | PowerShell y Git Bash; .gitattributes conserva LF en .sh |
| E4: cron por fecha | Preparado, no instalado | Wrapper, log y línea de cron en README; el ejercicio no exige instalarlo |
| E5: APIs abiertas y source/data | Verificado con red real | Cuatro respuestas normalizadas guardadas |
| E5: tabla HTTP y error controlado | Completado | E5_APIS_ABIERTAS.md y país ZZ exit 1 |
| E5: mock, batch de cinco y fail-once | Verificado | Demo nueva, tests y JSONL generado |
| E5: HF real | Extensión opcional no realizada | OpenAI es la alternativa documentada admitida |
| Historial de octubre | Limitación temporal conservada | Base I en octubre; ML/IA/CI entran en noviembre |
| Revisión y defensa personal | Pendiente del alumno | GUIA_ESTUDIO y lectura del código |
| E6/E7, API, web, despliegue y RC | Continuación del III | No se presentan como entregados por este cierre |

## Qué cambió en el comportamiento

**Inferencia:** la creación/configuración del proveedor se difiere hasta `complete`, dentro del job. Si falta la clave, el archivo de entorno o la configuración es inválida, se registra failed y no quedan las predicciones/resumen del intento anterior. La entrada/modelo siguen protegidos frente a un destino inseguro. Si ni siquiera se puede acceder al destino, no puede garantizarse escribir un estado allí; el proceso termina distinto de cero.

**Batch:** el destino anterior se invalida antes de cargar los prompts o crear el proveedor. Un fallo a mitad no publica una salida parcial. El archivo de prompts y el entorno no pueden utilizarse como destino. Debe comprobarse el código de salida; no se mantiene un manifiesto independiente de batch.

**Diabetes:** los números finitos y enteros también se contrastan con el máximo representable antes de la conversión int64. Se comparan como enteros Python para no redondear el límite. No se impone un límite clínico arbitrario.

**Ventas:** se rechazan valores no finitos y productos no representables. La multiplicación se calcula en coma flotante para evitar wraparound de int64. Si el total de importes individuales finitos desborda, se informa error de datos (exit 2) y failed; ya no hay traceback por serialización JSON.

**API abierta:** cliente HTTPX con timeout, errores permanentes/transitorios, reintentos acotados y resultado normalizado. Los smokes reales son explícitos y quedan fuera de CI; pytest usa dobles sin red. Los datos de ese ejercicio no se incorporan como predictores del dominio hospitalario.

## Reproducir las comprobaciones

Desde la raíz y con el entorno activado:

```powershell
python -m pytest --cov=ventas_app --cov=diabetes_app --cov=readmission_app --cov-fail-under=60
python scripts/run_demo.py
python scripts/run_pipeline.py
./scripts/run_pipeline.ps1
python scripts/verify_open_apis.py
```

En Git Bash o Linux con el venv preparado:

```bash
bash scripts/run_pipeline.sh
bash scripts/run_cadena_ventas.sh
bash scripts/run_cadena_ventas.sh proyecto_ii/output_ventas_gate 0.05
bash scripts/run_cadena_ventas.sh proyecto_ii/output_ventas_min 0.1 999999
```

Los dos últimos deben fallar con exit 1 y sin publicación/marcador de éxito. Fueron verificados sobre Git Bash/Windows; no se afirma un ensayo en Linux. No se modificó ninguna política de ejecución ni se instaló cron o tarea programada.

Para comprobar el gate con una medición ya existente:

```powershell
python -m coverage report --fail-under=100
# Esperado con esta suite: exit 2 (95,95 % < 100 %).
python -m coverage report --fail-under=60
# Esperado: exit 0. No cambia ni debilita el workflow.
```

## Pendientes que este cierre no puede atribuirse

1. **Publicación y nuevo Actions:** los cambios están locales. El run de b4217ad sigue siendo evidencia válida de ese commit, no de estos archivos modificados. Tras su revisión, publicar y comprobar el nuevo run.
2. **Historial auténtico:** hay commits del 6 y 11 de octubre, principalmente de la base del I. No se ha fabricado trabajo de ML/IA durante octubre ni alterado fechas. La valoración temporal corresponde al profesor.
3. **Revisión personal:** el alumno debe leer los cambios, ejecutar los comandos y poder explicar los contratos, el modelo y el uso de IA. Escribir esta lista no certifica haberlo hecho.
4. **E6/E7 y III:** no se han creado commits de refactor, tag RC, RELEASE.md, API o dashboard para simular otra fase. Corresponden a la continuación del mismo proyecto.

La fecha original de descarga sigue declarada como desconocida; no se inventó. Los archivos EVIDENCIA.md y verification.json conservan su condición histórica anterior al push. Este documento y verification_followup.json describen el cierre posterior.
