$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$frontendDir = Join-Path $repoRoot "frontend"

Set-Location $frontendDir

Write-Host "Checking frontend setup for MarketMind..."
Write-Host "Frontend directory: $frontendDir"
Write-Host ""

Write-Host "Checking required frontend files..."
foreach ($path in @(
  (Join-Path $frontendDir "package.json"),
  (Join-Path $frontendDir "vite.config.js"),
  (Join-Path $frontendDir "src\main.jsx"),
  (Join-Path $frontendDir "src\App.jsx")
)) {
  if (Test-Path $path) {
    Write-Host "[OK] $path"
  } else {
    Write-Host "[MISSING] $path"
  }
}

Write-Host ""
Write-Host "Checking Node.js..."
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCommand) {
  Write-Host "[OK] node found at $($nodeCommand.Source)"
  node --version
} else {
  Write-Host "[MISSING] node is not on PATH"
}

Write-Host ""
Write-Host "Checking npm..."
$npmCommand = Get-Command npm -ErrorAction SilentlyContinue
if ($npmCommand) {
  Write-Host "[OK] npm found at $($npmCommand.Source)"
  npm --version
} else {
  Write-Host "[MISSING] npm is not on PATH"
}

Write-Host ""
Write-Host "Commands to install dependencies and start the Vite dev server:"
Write-Host "cd `"$frontendDir`""
Write-Host "npm install"
Write-Host "npm run dev"

Write-Host ""
Write-Host "This script only checks local frontend setup. It does not implement frontend features."
