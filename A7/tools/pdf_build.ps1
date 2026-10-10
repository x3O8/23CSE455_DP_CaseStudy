param(
  [Parameter(Mandatory=$true)][string]$TectonicPath,
  [string]$JavaPath,
  [string]$PlantUmlPath,
  [switch]$OnlyCached
)
$ErrorActionPreference = 'Stop'
$teamRoot = Split-Path $PSScriptRoot -Parent
$evidenceRoot = Join-Path $teamRoot 'test_result'
New-Item -ItemType Directory -Force -Path $evidenceRoot | Out-Null
if ($JavaPath -and $PlantUmlPath) {
  $diagrams = @('Part1/pattern_architecture.puml',
    'Part2/diagrams/additional_services.puml',
    'Part2/diagrams/cancellation_strategy.puml',
    'Part2/diagrams/cancellation_sequence.puml',
    'Part2/diagrams/evolved_architecture.puml')
  foreach ($diagram in $diagrams) {
    & $JavaPath -jar $PlantUmlPath -Playout=smetana -tpng (Join-Path $teamRoot $diagram)
    if ($LASTEXITCODE -ne 0) { throw "Diagram rendering failed: $diagram" }
  }
}
Push-Location $teamRoot
try {
  foreach ($source in @('A7_Report.tex', 'A7_slide.tex')) {
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($source)
    $compileOptions = @('--keep-logs')
    if ($OnlyCached) { $compileOptions += '--only-cached' }
    $output = & $TectonicPath @compileOptions $source 2>&1
    $exitCode = $LASTEXITCODE
    @("Compiled: $(Get-Date -Format o)", "Compiler: $TectonicPath", $output) |
      Set-Content -LiteralPath (Join-Path $evidenceRoot "pdf_${stem}_build.txt") -Encoding utf8
    if ($exitCode -ne 0) { throw "LaTeX build failed: $source" }
  }
  foreach ($stem in @('A7_Report', 'A7_slide')) {
    Move-Item -LiteralPath (Join-Path $teamRoot "$stem.log") -Destination (Join-Path $evidenceRoot "pdf_$stem.log") -Force
  }
} finally { Pop-Location }
