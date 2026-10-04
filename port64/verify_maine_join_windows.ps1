param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ControlReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$RouteReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$Hdi,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
# Actual Windows consumer of independently checked GNU/original CPU receipts.
# The Python consumer verifies the resulting complete indexed/RGB frames again.
$ErrorActionPreference = 'Stop'
$exeDir = (Resolve-Path -LiteralPath $ExecutableDirectory).ProviderPath
$control = (Resolve-Path -LiteralPath $ControlReferenceDirectory).ProviderPath
$routes = (Resolve-Path -LiteralPath $RouteReferenceDirectory).ProviderPath
$hdiFile = (Resolve-Path -LiteralPath $Hdi).ProviderPath
$font = (Resolve-Path -LiteralPath $FontBitmap).ProviderPath
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Use a new output directory.' }
$out = (New-Item -ItemType Directory -Path $OutputDirectory).FullName
$routeOut = (New-Item -ItemType Directory -Path (Join-Path $out 'routes')).FullName
$exe = Join-Path $exeDir 'th04-port64-cutscene-contracts.exe'
$main = Join-Path $exeDir 'th04-port64.exe'
$controlReceipt = Get-Content -Raw -LiteralPath (Join-Path $control 'receipt.json') | ConvertFrom-Json
$routeReceipt = Get-Content -Raw -LiteralPath (Join-Path $routes 'receipt.json') | ConvertFrom-Json
if (!$controlReceipt.passed -or !$routeReceipt.passed -or $routeReceipt.natural_routes -ne 24) {
    throw 'Reference controls/routes are incomplete.'
}
$contracts = @()
foreach ($program in Get-ChildItem -LiteralPath $exeDir -Filter '*contracts.exe') {
    $lines = @(& $program.FullName 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Contract failed: $($program.Name): $lines" }
    $contracts += @{ name=$program.Name; sha256=(Get-FileHash -LiteralPath $program.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
}
if ($contracts.Count -ne 30) { throw 'Expected thirty native contracts.' }
Write-Host 'PASS: 30 native AMD64 contracts.'
foreach ($kind in @('handoff', 'frame', 'fade')) {
    $expected = (Get-Content -Raw -LiteralPath (Join-Path $control ($kind+'-trace.txt'))) -replace "`r", ''
    if ($kind -eq 'fade') { $lines = @(& $exe --fade 2>&1) }
    else {
        $option = if ($kind -eq 'frame') { '--frames' } else { '--handoff' }
        $lines = @(& $exe $option (Join-Path $control ($kind+'-fixtures.txt')) 2>&1)
    }
    if ($LASTEXITCODE -ne 0 -or (($lines -join "`n").TrimEnd() -cne $expected.TrimEnd())) {
        throw "Original $kind controls differ."
    }
    $lines | Set-Content -LiteralPath (Join-Path $out ($kind+'-trace.txt')) -Encoding UTF8
}
Write-Host 'PASS: original resident copies, frame counters and 273-refresh fade.'
Get-ChildItem -LiteralPath $routes -Filter '*-checkpoints.txt' | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $routeOut $_.Name)
}
Write-Host 'Running 24 natural MAIN-to-MAINE Ending routes...'
$lines = @(& $main --hdi $hdiFile --font-bmp $font --ending-screenshots $routeOut 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Ending routes failed: $lines" }
$lines | Set-Content -LiteralPath (Join-Path $out 'routes.log') -Encoding UTF8
$actualRoutes = @($lines | Where-Object { "$_" -like 'MAINE Ending route=*' })
$expectedRoutes = @(Get-Content -LiteralPath (Join-Path $routes 'stdout.log') | Where-Object { $_ -like 'MAINE Ending route=*' })
if ($actualRoutes.Count -ne 24 -or ($actualRoutes -join "`n") -cne ($expectedRoutes -join "`n")) {
    throw 'Natural Ending counters differ from GNU.'
}
$files = @()
foreach ($file in Get-ChildItem -LiteralPath $routes -File) {
    if ($file.Extension -notin @('.bin', '.pal', '.bmp') -and $file.Name -notlike '*-states.txt') { continue }
    $actual = Join-Path $routeOut $file.Name
    if (!(Test-Path -LiteralPath $actual)) { throw "Missing Ending frame: $($file.Name)" }
    $expectedHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $actualHash = (Get-FileHash -LiteralPath $actual -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($file.Extension -eq '.txt') {
        # Native Windows text streams write CRLF; compare the integer state
        # records while keeping binary page/palette/BMP hashes strict.
        $expectedText = (Get-Content -Raw -LiteralPath $file.FullName) -replace "`r", ''
        $actualText = (Get-Content -Raw -LiteralPath $actual) -replace "`r", ''
        if ($actualText -cne $expectedText) { throw "Ending state differs: $($file.Name)" }
    } elseif ($actualHash -cne $expectedHash) { throw "Ending frame differs: $($file.Name)" }
    $files += @{ name=$file.Name; sha256=$actualHash }
}
if ($files.Count -ne 1176) { throw 'Incomplete page/palette/RGB/state comparisons.' }
$receipt = @{
    passed=$true; observed_utc=[DateTime]::UtcNow.ToString('o'); host='actual-Windows-AMD64';
    contracts=$contracts; natural_routes=24; compared_files=$files;
    source_manifest_sha256=$routeReceipt.source_manifest_sha256;
    executable_sha256=(Get-FileHash -LiteralPath $main -Algorithm SHA256).Hash.ToLowerInvariant();
    control_executable_sha256=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant();
    reference_receipt_sha256=(Get-FileHash -LiteralPath (Join-Path $routes 'receipt.json') -Algorithm SHA256).Hash.ToLowerInvariant();
    scope='Actual Windows consumer of original/GNU controls; natural MAIN-to-MAINE Ending, no physical PC-98 capture, audio synthesis, Staff Roll or saved-score claim.'
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: 24 routes, 576 complete indexed pages, 288 palettes and 288 RGB frames.'
