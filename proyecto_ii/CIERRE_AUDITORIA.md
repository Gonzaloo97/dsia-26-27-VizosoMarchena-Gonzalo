# Cierre de la auditoría del Proyecto II

El cierre del 11/11/2026 se publicó en `d3ff586` y superó [145 pruebas con 95,95 % de cobertura en GitHub Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514). Posteriormente, la simplificación del 12/11 se publicó en `cebdb27` y [superó GitHub Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43268309498). La revisión local de esta última registró 145 pruebas y 96,02 % de cobertura.

La documentación y las simplificaciones del 12/11/2026 ya están publicadas. Su alcance y validación local se recogen en [REVISION_SIMPLICIDAD.md](REVISION_SIMPLICIDAD.md). El run de `d3ff586` acredita la versión anterior, mientras que el de `cebdb27` corresponde al código simplificado.

## Etapas y registros

| Etapa | Resultado | Registro |
| --- | --- | --- |
| Preparación inicial del 11/11 | 106 tests y 95,06 % en local | [verification.json](evidence/verification.json) |
| Publicación de `b4217ad` | CI verde de esa versión | [Run anterior](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43041031910) |
| Correcciones y E5, antes del siguiente commit | 145 tests y 95,95 %, wrappers y APIs | [verification_followup.json](evidence/verification_followup.json) |
| Validación previa a publicar `d3ff586` | Suite, demo y cadena Bash | [validation_final.json](evidence/validation_final.json) |
| Publicación de `d3ff586` | CI verde, 145 tests y 95,95 % | [Run del 11/11](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514) |
| Revisión y publicación del 12/11 | Código simplificado, documentación actualizada, 145 pruebas locales, 96,02 % de cobertura local y CI correcto | [Revisión por archivo](REVISION_SIMPLICIDAD.md) · [Run de `cebdb27`](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43268309498) |

Los JSON conservan el estado que tenían al generarse. Por ejemplo, un campo de CI pendiente en un registro previo al push no describe el estado remoto actual. No se cambian retrospectivamente esos resultados.

## Defectos corregidos el 11/11

| Defecto | Cambio y comprobación |
| --- | --- |
| Configuración IA inválida dejaba un éxito anterior | Cliente creado dentro del job; regresiones de clave, entorno y timeout incorrectos |
| Batch fallido dejaba JSONL anterior | Invalidación previa y publicación tras completar todo el batch; tests de configuración, entrada y fallo intermedio |
| Enteros de diabetes fuera de int64 | Rechazo antes de convertir; se comprueban máximo válido y valores superiores |
| Ventas admitía infinitos/desbordamientos | Finitud de entrada, producto y total; error controlado si el agregado desborda |

Se mantiene la protección de entrada/modelo frente a una salida que los contenga. El archivo de prompts y el entorno tampoco pueden usarse como destino del batch. Si el directorio es inaccesible, puede no ser posible guardar `status.json`; hay que comprobar también el código de salida.

## Otras comprobaciones del cierre

- Reentrenamiento sobre 5.000 filas: 4.867 elegibles, 133 rechazadas y cero pacientes compartidos entre train/test.
- Inferencia sobre 968 encuentros reservados y cinco respuestas mock con recuperación del fallo simulado.
- Informes de entrenamiento coincidentes con la evidencia histórica: F1 0,2538 y ROC-AUC 0,6120.
- Cuatro APIs abiertas y error controlado del país ZZ, documentados en [E5_APIS_ABIERTAS.md](E5_APIS_ABIERTAS.md).
- Gate local de cobertura: umbral 100 → exit 2; umbral 60 → exit 0. No se acredita un ensayo remoto rojo intencionado.
- Wrappers PowerShell y Git Bash ejecutados en Windows. No se afirma un ensayo de esos wrappers en Linux.
- Cadena Bash de ventas: éxito, fallo del gate y fallo de comprobación de métricas; sin publicación ni marcador antiguos tras fallar.

La cobertura del cierre del 11/11 fue de líneas: 805 de 839 sentencias (95,95 %), sin medir ramas. La revisión local de la versión simplificada midió 820 de 854 (96,02 %) y su workflow remoto terminó correctamente. Estas cifras no garantizan la ausencia de otros errores.

## Pendientes auténticos

1. Sincronizar mi copia local con los últimos cambios documentales de GitHub antes de entregar y verificar que no queden modificaciones sin revisar.
2. Completar mi lectura y comprensión personal antes de la defensa. Codex hizo las revisiones y comprobaciones automatizadas descritas.
3. Mantener el historial auténtico: los commits de octubre corresponden principalmente al I; ML/IA/CI entraron en noviembre. Su valoración temporal corresponde al profesor.
4. Continuar el III con API, interfaz, despliegue, monitorización y RC. No se han instalado tareas periódicas ni desplegado servicios.

La fecha original de descarga sigue sin constar. El hash permite identificar la muestra utilizada. [EVIDENCIA.md](EVIDENCIA.md) reúne los resultados y [AUDITORIA_TEMAS.md](AUDITORIA_TEMAS.md) relaciona la entrega con los requisitos.
