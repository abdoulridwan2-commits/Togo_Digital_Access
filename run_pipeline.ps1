param(
    [switch]$SkipDashboard
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

Write-Host "1/5  Vérification des données brutes..."
& $Python "src\check_data.py"

Write-Host "2/5  Nettoyage des données..."
& $Python "src\clean_data.py"

Write-Host "3/5  Analyse géospatiale..."
& $Python "src\analyze_data.py"

Write-Host "4/5  Calcul du score de priorité..."
& $Python "src\score_priorite.py"

if ($SkipDashboard) {
    Write-Host "Pipeline terminé (dashboard ignoré)."
    exit 0
}

Write-Host "5/5  Lancement du dashboard Streamlit..."
& $Python -m streamlit run "app\main.py"