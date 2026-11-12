# E5 — APIs abiertas y borde de IA

Ejecución técnica registrada el 11/11/2026. Documento revisado el 12/11/2026. Referencia: [E5 del profesor, versión contrastada](https://github.com/dmartincc/dsia-26-27/blob/1c2906e77c5235a04f820f4252dcb0760e240728/3_automatizacion_e_ia/ejercicios/E5_apis_ia.md). El contrato y los endpoints se adaptan del [ejemplo de aula](https://github.com/dmartincc/dsia-26-27/blob/1c2906e77c5235a04f820f4252dcb0760e240728/3_automatizacion_e_ia/ejemplos/open_api_client.py), con HTTPX y pruebas offline propias.

## Comandos y evidencia real

Desde la raíz, con el entorno instalado y activado:

```powershell
python scripts/open_api_client.py weather --lat 40.4168 --lon -3.7038
python scripts/open_api_client.py country --code ES
python scripts/open_api_client.py fx --base EUR --symbols USD,GBP
python scripts/open_api_client.py github --owner dmartincc --repo dsia-26-27
python scripts/open_api_client.py country --code ZZ
```

Los cuatro primeros terminaron con exit 0. El último produjo `ERROR: Pais sin resultados o formato inesperado de World Bank.` y exit 1, sin traceback. [Respuestas y comandos observados](evidence/open_api_smoke.json). Las APIs públicas se llamaron sin claves; los valores son una instantánea, no resultados fijos de un test.

| Comando | `source` | Campos normalizados de `data` |
| --- | --- | --- |
| weather | open-meteo | lat, lon, time, temperature_c, wind_kmh |
| country | worldbank | id, iso2, name, capital |
| fx | frankfurter | base, date, rates |
| github | github | full_name, html_url, language, stars |

`APIResult(source, data)` identifica la procedencia y evita que el núcleo dependa del JSON particular del proveedor. Cada método traduce el formato externo a campos conocidos; un cambio de API se resuelve en ese borde. `transform` sigue siendo una función de datos, sin HTTP.

Como posible ampliación usaría la **API pública de GitHub** para mostrar metadatos del repositorio y facilitar la trazabilidad de la entrega. Sería una función auxiliar, aún no integrada en el pipeline hospitalario. Las APIs practicadas no se usan como predictores de salud. El borde de modelos sí está integrado para resumir métricas agregadas; cumple una función distinta.

## Estrategias de error

| Caso | ¿Reintentar? | Motivo y comportamiento |
| --- | --- | --- |
| Timeout/conexión | Sí, acotado | Puede ser transitorio; `TransientOpenAPIError` |
| 404 | No | Ruta o recurso inexistente; `OpenAPIError` |
| 401/403 | No | Revisar autenticación/permisos; repetir no los corrige |
| 429 | Sí, con espera | Saturación o cuota temporal; nunca bucle ilimitado |
| 408 / 5xx | Sí, acotado | Petición agotada o fallo temporal del servidor |
| JSON inválido / contrato distinto | No | Es un error de respuesta que necesita revisión |
| País sin datos | No | Error de dominio tras HTTP correcto; caso `ZZ` |

Se aplica timeout de 15 segundos por petición y hasta 2 reintentos con espera creciente. No es un plazo total de 15 segundos para toda la operación. Los errores no imprimen el cuerpo externo. El test de 429 no espera realmente y comprueba el número de intentos.

## Analogía con IA y práctica mock

`APIResult(source, data)` y `AIResponse(provider, text, model)` son resultados tipados en dos bordes distintos. El primero normaliza datos públicos estructurados; el segundo permite intercambiar un mock determinista y el proveedor OpenAI para texto.

```powershell
python -m readmission_app ai --provider mock --prompt "Di hola en una frase"
python -m readmission_app ai --provider mock --batch proyecto_ii/prompts.txt --output proyecto_ii/output/respuestas.jsonl
python -m readmission_app ai --provider mock --prompt "test" --fail-once
python -m pytest tests/test_open_api_client.py tests/test_ai_contract.py -q
```

El smoke devuelve `provider=mock` y texto con prefijo `[mock]`. El batch genera cinco registros con prompt/provider/text/model y `--fail-once` recupera el primer error transitorio. La parte 7.2 deseable está cubierta por los tests del cliente mock sin red. Mock es obligatorio en CI para que pruebas y demo no dependan de una cuenta, cuota, red o disponibilidad del proveedor. El HTTP abierto se prueba con respuestas simuladas en pytest. Los smokes reales se ejecutan **solo explícitamente**, fuera de la suite y del workflow offline:

```powershell
python scripts/verify_open_apis.py
```

Ese comando actualiza la instantánea de respuestas reales; si una dependencia falla, registra el fallo y termina distinto de cero. No confunde un fallo de red con el caso negativo esperado de `ZZ`. El smoke HF es una extensión deseable no realizada: la alternativa documentada de modelos es OpenAI y no se ha hecho una llamada de pago.

La implementación y las comprobaciones contaron con ayuda sustancial de Codex, descrita en [AI_USAGE.md](../AI_USAGE.md). Me queda completar la revisión y comprensión personal antes de defenderlo.
