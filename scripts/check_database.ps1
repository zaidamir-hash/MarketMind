$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$schemaFile = Join-Path $repoRoot "database\marketmind_schema_v2_postgresql.sql"
$verificationFile = Join-Path $repoRoot "database\verification_queries.sql"
$seedFile = Join-Path $repoRoot "database\seed_assets.sql"

$defaultUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "postgres" }
$defaultDatabase = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "marketmind" }
$bootstrapDatabase = if ($env:POSTGRES_BOOTSTRAP_DB) { $env:POSTGRES_BOOTSTRAP_DB } else { "postgres" }
$defaultHost = if ($env:POSTGRES_HOST) { $env:POSTGRES_HOST } else { "localhost" }
$defaultPort = if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "5432" }

Write-Host "Checking local database setup for MarketMind..."
Write-Host "Repository root: $repoRoot"
Write-Host "Default PostgreSQL host: $defaultHost"
Write-Host "Default PostgreSQL port: $defaultPort"
Write-Host "Default PostgreSQL user: $defaultUser"
Write-Host "Default PostgreSQL database: $defaultDatabase"
Write-Host "Bootstrap database for first-time schema run: $bootstrapDatabase"
Write-Host ""

Write-Host "Checking required database files..."
foreach ($path in @($schemaFile, $verificationFile, $seedFile)) {
  if (Test-Path $path) {
    Write-Host "[OK] $path"
  } else {
    Write-Host "[MISSING] $path"
  }
}

Write-Host ""
Write-Host "Checking for psql..."
$psqlCommand = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlCommand) {
  Write-Host "[OK] psql found at $($psqlCommand.Source)"
} else {
  Write-Host "[MISSING] psql is not on PATH"
  Write-Host "Add PostgreSQL's bin folder to PATH, for example:"
  Write-Host "C:/Program Files/PostgreSQL/17/bin"
}

Write-Host ""
Write-Host "This script checks:"
Write-Host "- schema file presence"
Write-Host "- verification query file presence"
Write-Host "- seed file presence"
Write-Host "- whether psql is available on PATH"

Write-Host ""
Write-Host "Run the schema manually with:"
Write-Host "psql -h $defaultHost -p $defaultPort -U $defaultUser -d $bootstrapDatabase -f `"$($schemaFile -replace '\\','/')`""

Write-Host ""
Write-Host "Run the verification queries with:"
Write-Host "psql -h $defaultHost -p $defaultPort -U $defaultUser -d $defaultDatabase -f `"$($verificationFile -replace '\\','/')`""

Write-Host ""
Write-Host "Run the seed asset inserts with:"
Write-Host "psql -h $defaultHost -p $defaultPort -U $defaultUser -d $defaultDatabase -f `"$($seedFile -replace '\\','/')`""

Write-Host ""
Write-Host "Password is not hardcoded. If PostgreSQL prompts for one, enter it there."
