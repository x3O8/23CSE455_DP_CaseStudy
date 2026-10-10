param(
    [Parameter(Mandatory=$true)][string]$RubyBin,
    [Parameter(Mandatory=$true)][string]$GemHome,
    [string]$BundlePath,
    [string]$DatabaseHost = '127.0.0.1',
    [int]$DatabasePort = 55432,
    [string]$DatabaseUser = 'codex_test'
)
$ErrorActionPreference = 'Stop'
$teamRoot = Split-Path $PSScriptRoot -Parent
$appRoot = Join-Path $teamRoot 'Part2/code'
$evidence = Join-Path $teamRoot 'test_result'
$ruby = Join-Path $RubyBin 'ruby.exe'
$env:PATH = "$RubyBin;$GemHome/bin;$env:PATH"
$env:GEM_HOME = $GemHome
$env:GEM_PATH = $GemHome
$env:BUNDLE_GEMFILE = Join-Path $appRoot 'Gemfile'
if ($BundlePath) { $env:BUNDLE_PATH = $BundlePath }
$env:RAILS_ENV = 'test'
$env:DATABASE_HOST = $DatabaseHost
$env:DATABASE_PORT = "$DatabasePort"
$env:DATABASE_USERNAME = $DatabaseUser
$env:DATABASE_PASSWORD = ''
$env:PAYMENT_CURRENCY = 'EUR'
$env:INTEGROMAT_BOOKING_HOOK = ''
$env:INTEGROMAT_BASE_URI = ''
$env:CANCELLATION_POLICY = 'flexible'

function Invoke-Evidence([string]$Name, [string[]]$Arguments) {
    $destination = Join-Path $evidence $Name
    $command = 'ruby ' + ($Arguments -join ' ')
    $output = & $ruby @Arguments 2>&1 | ForEach-Object { "$_" }
    $exitCode = $LASTEXITCODE
    if ($Arguments[0] -eq '-rbundler/setup' -and ($output -join "`n") -notmatch '(?m)^[1-9]\d* examples?, 0 failures?\s*$') {
        $exitCode = 1
    }
    @("Command: $command", "Environment: RAILS_ENV=test; PostgreSQL $DatabaseHost`:$DatabasePort; user $DatabaseUser", '', $output, '', "Exit code: $exitCode") | Set-Content -LiteralPath $destination -Encoding utf8
    Write-Output "$Name : exit $exitCode"
    if ($exitCode -ne 0) { throw "Check failed. Read $destination" }
}

Push-Location $appRoot
try {
    Invoke-Evidence 'bundle_check.txt' @('-S', 'bundle', 'check')
    Invoke-Evidence 'test_db_migrations.txt' @('bin/rails', 'db:drop', 'db:create', 'db:migrate')
    Invoke-Evidence 'test_db_migration_status.txt' @('bin/rails', 'db:migrate:status')
    $rspecEntry = @('-rbundler/setup', '-e', 'load Gem.bin_path("rspec-core", "rspec")', '--')
    Invoke-Evidence 'part2_rspec.txt' ($rspecEntry + @('spec', '--format', 'documentation'))
    Invoke-Evidence '../Part2/changes/Change1/test_result.txt' ($rspecEntry + @('spec/services/additional_service_pricing_spec.rb', '--format', 'documentation'))
    Invoke-Evidence '../Part2/changes/Change2/test_result.txt' ($rspecEntry + @('spec/services/room_upgrade_spec.rb', '--format', 'documentation'))
    Invoke-Evidence '../Part2/changes/Change3/test_result.txt' ($rspecEntry + @('spec/services/cancellation_service_spec.rb', 'spec/requests/booking_cancellations_spec.rb', '--format', 'documentation'))
    Invoke-Evidence 'rails_boot.txt' @('bin/rails', 'runner', 'Rails.application.eager_load!; puts "BOOT_OK Rails=#{Rails.version} env=#{Rails.env} tables=#{ActiveRecord::Base.connection.tables.length}"')
} finally {
    Pop-Location
}
