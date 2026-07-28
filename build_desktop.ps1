param(
    [string]$Python = "python",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $repoRoot

if (-not $SkipInstall) {
    & $Python -m pip install -r requirements-desktop.txt
    if ($LASTEXITCODE -ne 0) { throw "Desktop dependency installation failed." }
}

& $Python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed; EXE was not built." }

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "ITR-status-Desktop" `
    --paths "src" `
    --collect-all openpyxl `
    --add-data "public;public" `
    --add-data "sample_data;sample_data" `
    "desktop_app.py"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

$artifact = Join-Path $repoRoot "dist\ITR-status-Desktop.exe"
if (-not (Test-Path -LiteralPath $artifact)) { throw "Expected EXE was not created: $artifact" }
Write-Host "Built: $artifact"
