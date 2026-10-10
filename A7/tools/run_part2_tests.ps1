param(
  [Parameter(Mandatory=$true)][string]$Ruby,
  [string]$GemHome,
  [string]$DatabaseHost = '127.0.0.1',
  [int]$DatabasePort = 5432,
  [string]$DatabaseUser = 'postgres',
  [ValidateSet('original','Change1','Change2','Change3','final','all')][string]$Stage = 'all'
)
$ErrorActionPreference = 'Stop'
$teamRoot = Split-Path $PSScriptRoot -Parent
$receiptRoot = Join-Path $teamRoot 'Part2/verification'
New-Item -ItemType Directory -Force $receiptRoot | Out-Null
$env:RAILS_ENV = 'test'
$env:DISABLE_BOOTSNAP = '1'
if ($GemHome) { $env:GEM_HOME = $GemHome; $env:GEM_PATH = $GemHome }
$selectedStages = if ($Stage -eq 'all') { @('original','Change1','Change2','Change3','final') } else { @($Stage) }
foreach ($checkpointStage in $selectedStages) {
  $sourceRoot = if ($checkpointStage -eq 'final') { Join-Path $teamRoot 'Part2/code' } else { Join-Path $teamRoot "Part2/checkpoints/$checkpointStage" }
  $env:BUNDLE_GEMFILE = Join-Path $sourceRoot 'Gemfile'
  $schemaPath = Join-Path $sourceRoot 'db/schema.rb'
  $schemaBytes = [System.IO.File]::ReadAllBytes($schemaPath)
  $lockPath = Join-Path $sourceRoot 'Gemfile.lock'
  $lockBytes = [System.IO.File]::ReadAllBytes($lockPath)
  # Distinct test database per checkpoint; never drop an existing database.
  $env:DATABASE_URL = "postgresql://${DatabaseUser}@${DatabaseHost}:${DatabasePort}/a7_part2_${checkpointStage}_test"
  $logPath = Join-Path $receiptRoot "${checkpointStage}_rails.txt"
  "Checkpoint: $checkpointStage`nSource: $sourceRoot`nDatabase: a7_part2_${checkpointStage}_test`nExecuted at: $(Get-Date -Format o)`nRuntime: $Ruby`nBundle: checkpoint's own Gemfile/lockfile" | Set-Content $logPath
  Push-Location $sourceRoot
  try {
    foreach ($task in @('db:create','db:migrate')) {
      "Command: ruby bin/rails $task" | Add-Content $logPath
      & $Ruby bin/rails $task 2>&1 | Out-File -Append -Encoding utf8 $logPath
      $resultCode = $LASTEXITCODE
      "Exit code: $resultCode" | Add-Content $logPath
      if ($resultCode -ne 0) { throw "$checkpointStage $task failed; see $logPath" }
    }
    'Command: ruby -rbundler/setup -e load Gem.bin_path("rspec-core", "rspec") -- spec --format documentation' | Add-Content $logPath
    & $Ruby '-rbundler/setup' '-e' 'load Gem.bin_path("rspec-core", "rspec")' '--' 'spec' '--format' 'documentation' 2>&1 | Out-File -Append -Encoding utf8 $logPath
    $resultCode = $LASTEXITCODE
    "Exit code: $resultCode" | Add-Content $logPath
    if ($resultCode -ne 0) { throw "$checkpointStage RSpec failed; see $logPath" }
    if (-not ((Get-Content $logPath -Raw) -match '[1-9][0-9]* examples, 0 failures')) { throw "${checkpointStage}: no successful nonempty RSpec result" }
    Write-Output "${checkpointStage}: Rails migrations and RSpec exit zero ($logPath)"
  } finally {
    [System.IO.File]::WriteAllBytes($schemaPath, $schemaBytes)
    [System.IO.File]::WriteAllBytes($lockPath, $lockBytes)
    Pop-Location
  }
}
