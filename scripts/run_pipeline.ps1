# Wrapper para PowerShell/Programador de tareas. Requiere entrenar antes.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
$day = Get-Date -Format 'yyyy-MM-dd'
$outDir = Join-Path $repoRoot "proyecto_ii\output_daily\$day"
Push-Location $repoRoot
try {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $marker = Join-Path $outDir 'LAST_OK.txt'
    if (Test-Path -LiteralPath $marker) { Remove-Item -LiteralPath $marker }
    & $pythonExe -m readmission_app run --input proyecto_ii/artifacts/holdout.csv --provider mock --output-dir $outDir
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $pythonExe scripts/check_metrics.py --metrics (Join-Path $outDir 'metrics.json') --min-rows-out 100
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Set-Content -LiteralPath $marker -Value "PIPELINE_OK $day" -Encoding utf8
} finally {
    Pop-Location
}
