# Cierre de la auditoría del Proyecto II

Mi entrega publicada `d3ff586` incorpora las correcciones del 11/11/2026 y superó [145 pruebas con 95,95 % de cobertura en GitHub Actions](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514). La demo y la subida de artefactos también terminaron correctamente. Ya no está pendiente publicar ese cierre.

La documentación y las simplificaciones del 12/11/2026 son una revisión posterior **todavía local**. Su alcance y validación se recogen en [REVISION_SIMPLICIDAD.md](REVISION_SIMPLICIDAD.md); el run de `d3ff586` no acredita esos cambios nuevos.

## Etapas y registros

| Etapa | Resultado | Registro |
| --- | --- | --- |
| Preparación inicial del 11/11 | 106 tests y 95,06 % en local | [verification.json](evidence/verification.json) |
| Publicación de `b4217ad` | CI verde de esa versión | [Run anterior](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43041031910) |
| Correcciones y E5, antes del siguiente commit | 145 tests y 95,95 %, wrappers y APIs | [verification_followup.json](evidence/verification_followup.json) |
| Validación previa a publicar `d3ff586` | Suite, demo y cadena Bash | [validation_final.json](evidence/validation_final.json) |
| Publicación de `d3ff586` | CI verde, 145 tests y 95,95 % | [Run actual publicado](https://github.com/Gonzaloo97/dsia-26-27-VizosoMarchena-Gonzalo/actions/runs/43087452514) |
| Revisión del 12/11 | Simplificación y documentación | [Revisión por archivo](REVISION_SIMPLICIDAD.md) |

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

La cobertura publicada es de líneas: 805 de 839 sentencias, sin medir ramas. No prueba que no existan otros errores. Los resultados de las simplificaciones posteriores deben consultarse por separado.

## Pendientes auténticos

1. Publicar la revisión local del 12/11 y comprobar su nuevo run, cuando se decida hacerlo.
2. Completar mi lectura y comprensión personal antes de la defensa. Codex hizo las revisiones y comprobaciones automatizadas descritas.
3. Mantener el historial auténtico: los commits de octubre corresponden principalmente al I; ML/IA/CI entraron en noviembre. Su valoración temporal corresponde al profesor.
4. Continuar el III con API, interfaz, despliegue, monitorización y RC. No se han instalado tareas periódicas ni desplegado servicios.

La fecha original de descarga sigue sin constar. El hash permite identificar la muestra utilizada. [EVIDENCIA.md](EVIDENCIA.md) reúne los resultados y [AUDITORIA_TEMAS.md](AUDITORIA_TEMAS.md) relaciona la entrega con los requisitos.
