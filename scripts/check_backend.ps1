$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$backendDir = Join-Path $repoRoot "backend"
$venvDir = Join-Path $backendDir ".venv"

Set-Location $backendDir

Write-Host "Checking backend setup for MarketMind..."
Write-Host "Backend directory: $backendDir"
Write-Host ""

Write-Host "Checking required backend files..."
foreach ($path in @(
  (Join-Path $backendDir "app\main.py"),
  (Join-Path $backendDir "app\core\config.py"),
  (Join-Path $backendDir "app\db\session.py"),
  (Join-Path $backendDir "requirements.txt")
)) {
  if (Test-Path $path) {
    Write-Host "[OK] $path"
  } else {
    Write-Host "[MISSING] $path"
  }
}

Write-Host ""
Write-Host "Checking Python..."
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) {
  Write-Host "[OK] python found at $($pythonCommand.Source)"
  python --version
} else {
  Write-Host "[MISSING] python is not on PATH"
}

Write-Host ""
Write-Host "Checking virtual environment..."
if (Test-Path $venvDir) {
  Write-Host "[OK] .venv exists at $venvDir"
} else {
  Write-Host "[MISSING] .venv does not exist in backend/"
}

Write-Host ""
Write-Host "Commands to create a virtual environment and install dependencies:"
Write-Host "cd `"$backendDir`""
Write-Host "python -m venv .venv"
Write-Host ".\.venv\Scripts\Activate.ps1"
Write-Host "pip install -r requirements.txt"

Write-Host ""
Write-Host "This script only checks local backend setup. It does not run the backend or implement features."
