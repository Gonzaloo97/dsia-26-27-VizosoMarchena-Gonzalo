\# Sesión 01 — Autoevaluación



\## 1. Diferencia entre Python global y `.venv`.



El Python global es la instalación única de Python que hay en todo el sistema operativo, compartida por todos los proyectos y programas del ordenador. Un `.venv` es un entorno virtual: una copia aislada del intérprete de Python y de sus librerías, creada dentro de la carpeta de un proyecto concreto. Al activar el `.venv`, los comandos `python` y `pip` dejan de apuntar al Python global y apuntan a los ejecutables dentro de `.venv\\Scripts\\`. Esto permite que cada proyecto tenga sus propias versiones de librerías sin interferir entre sí ni con el sistema.



\## 2. ¿Para qué sirve `python -m pip` frente a llamar solo a `pip`?



En un ordenador puede haber varias instalaciones de Python a la vez (la global y la de cada `.venv`), y cada una trae su propio `pip` incorporado. Si se escribe solo `pip`, el sistema busca en el PATH y ejecuta el primer `pip.exe` que encuentre, sin garantía de que sea el correspondiente al entorno activado — podría instalar el paquete en el Python global por error, en vez de en el `.venv`. Con `python -m pip`, en cambio, se indica explícitamente a \*ese\* `python` (el que se tenga activo en ese momento) que ejecute su propio módulo `pip`, asegurando que la instalación va exactamente al entorno correcto. Por eso es la forma recomendada al trabajar con entornos virtuales.



\## 3. Explica working tree / staging / commit.



Son las tres zonas por las que pasa un cambio en Git antes de quedar guardado en el historial:



\- \*\*Working tree\*\* (árbol de trabajo): son los ficheros tal como están en la carpeta del proyecto en un momento dado, editables libremente. Cuando se modifica o crea un fichero, el cambio vive aquí primero, y Git lo marca como "untracked" (nuevo) o "modified" (modificado) al ejecutar `git status`.

\- \*\*Staging area\*\* (o "index"): es una zona intermedia donde se eligen qué cambios concretos se quieren incluir en el próximo commit, mediante `git add <fichero>`. Permite tener ficheros modificados en el working tree sin necesidad de incluirlos todos en el mismo commit.

\- \*\*Commit\*\*: es la fotografía definitiva de lo que hay en el staging area en ese momento, guardada de forma permanente en el historial del repositorio mediante `git commit -m "mensaje"`. Cada commit queda identificado de forma única y puede recuperarse en cualquier momento posterior.



El flujo habitual es: se edita en el working tree → `git add` traslada los cambios elegidos al staging area → `git commit` los registra en el historial.



\## 4. ¿Clone y pull son lo mismo? ¿Por qué?



No, son operaciones distintas aunque ambas descargan datos de un repositorio remoto:



\- \*\*`git clone`\*\* se usa una única vez, al principio: descarga una copia completa del repositorio remoto (todo el historial de commits, todas las ramas) y crea un repositorio local nuevo enlazado a ese remoto (`origin`). Es el punto de partida cuando aún no se tiene el proyecto en el ordenador.

\- \*\*`git pull`\*\* se usa repetidamente, una vez ya existe el repositorio local: descarga los cambios nuevos que otros han subido al remoto desde la última sincronización, y los combina (mediante \*merge\*) con la rama local actual.



En resumen, `clone` crea el repositorio local desde cero, mientras que `pull` actualiza un repositorio local que ya existe con los cambios más recientes del remoto.



\## 5. Lista cuatro cosas que no se suben a GitHub y justifica una.



Cuatro tipos de ficheros o contenidos que no deben subirse a un repositorio de GitHub:



1\. El entorno virtual (`.venv/`)

2\. Ficheros de variables de entorno con credenciales (`.env`)

3\. Ficheros de caché o compilados de Python (`\_\_pycache\_\_/`, `\*.pyc`)

4\. Ficheros de configuración específicos del editor o IDE (`.vscode/`, `.idea/`)



\*\*Justificación de `.env`:\*\* este fichero suele contener información sensible como claves de API, contraseñas o cadenas de conexión a bases de datos. Si se sube a un repositorio público (o incluso privado con varios colaboradores), esas credenciales quedan expuestas en el historial de Git de forma permanente — incluso si se borra el fichero en un commit posterior, seguiría siendo recuperable en commits anteriores. La forma correcta de compartir su estructura sin exponer los valores reales es mediante un fichero de ejemplo como `.env.example`, con las claves pero sin los valores sensibles.



\## 6. Reescribe a buen estilo: `update`, `fix final`, `cambios varios`.



Los mensajes originales son vagos y no indican qué cambió realmente. Una reescritura siguiendo buenas prácticas (verbo en imperativo, específico, mismo idioma en todo el repositorio) sería:



\- `update` → `feat: añade validación de entrada al formulario de registro`

\- `fix final` → `fix: corrige cálculo incorrecto de IVA en el total del pedido`

\- `cambios varios` → `refactor: separa la lógica de conexión a base de datos en un módulo aparte`



Un buen mensaje de commit debe responder a "¿qué cambia y por qué?" en una línea corta (idealmente menos de 50 caracteres en el título), permitiendo entender el historial del proyecto sin tener que abrir cada commit para ver el código modificado.



\## 7. ¿Qué haces si el IDE no importa `pandas` pero la terminal sí?



Este síntoma indica que el IDE (por ejemplo, VS Code o PyCharm) tiene seleccionado un intérprete de Python distinto al del `.venv` activo en la terminal — probablemente sigue usando el Python global, donde `pandas` no está instalado, mientras que la terminal sí apunta al `.venv` donde `pandas` se instaló mediante `pip install -r requirements.txt`.



La solución es indicarle explícitamente al IDE que use el intérprete del entorno virtual del proyecto:

\- En VS Code: `Ctrl+Shift+P` → "Python: Select Interpreter" → elegir la ruta que apunte a `.venv\\Scripts\\python.exe`.

\- En PyCharm: Settings → Project → Python Interpreter → seleccionar o añadir el intérprete de `.venv`.



Para confirmar cuál es la ruta correcta, se puede ejecutar en la terminal (con el venv activado) `python -c "import sys; print(sys.executable)"`, y usar esa misma ruta en el IDE.



\## 8. ¿Qué haces si subiste `.env` por error?



Si el `.env` se subió y se hizo push al remoto, borrarlo simplemente con `git rm .env` y hacer un nuevo commit \*\*no es suficiente\*\*, porque el fichero sigue siendo recuperable en el historial de commits anteriores. Los pasos correctos serían:



1\. \*\*Revocar y rotar inmediatamente las credenciales expuestas\*\* (claves de API, contraseñas, tokens) en el servicio correspondiente — este es el paso más urgente y prioritario, ya que hasta que no se invalidan, quedan comprometidas independientemente de lo que se haga con el repositorio.

2\. \*\*Eliminar el fichero del historial de Git\*\*, no solo del último commit, usando herramientas como `git filter-repo` (recomendada actualmente) o `BFG Repo-Cleaner`, que reescriben el historial completo eliminando toda referencia al fichero.

3\. \*\*Forzar el push\*\* de ese historial reescrito (`git push --force`), y avisar a cualquier colaborador para que vuelva a clonar el repositorio, ya que el historial reescrito es incompatible con sus copias locales antiguas.

4\. \*\*Añadir `.env` al `.gitignore`\*\* (si no estaba ya) para evitar que vuelva a subirse por error en el futuro.



El punto clave es que borrar el fichero del último commit no elimina el riesgo — la credencial ya expuesta debe considerarse comprometida y sustituirse.

