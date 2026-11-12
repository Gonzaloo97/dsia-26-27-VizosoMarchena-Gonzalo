# Wrapper para PowerShell/Programador de tareas. Requiere entrenar antes.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
# La cadena y el marcador se gestionan en un solo sitio.
& $pythonExe (Join-Path $PSScriptRoot 'run_pipeline.py') @args
exit $LASTEXITCODE
