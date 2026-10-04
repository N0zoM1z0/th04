param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$Hdi,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$exeDir = (Resolve-Path -LiteralPath $ExecutableDirectory).Path
$hdiFile = (Resolve-Path -LiteralPath $Hdi).Path
$fontFile = (Resolve-Path -LiteralPath $FontBitmap).Path
if (Test-Path -LiteralPath $OutputDirectory) {
    throw 'Use a new output directory to avoid mixing verification results.'
}
$outDir = (New-Item -ItemType Directory -Path $OutputDirectory).FullName
$names = @('contracts', 'live-contracts', 'shot-contracts', 'enemy-contracts',
           'bullet-contracts', 'effect-contracts', 'midboss-contracts',
           'orange-contracts', 'dialog-contracts', 'bonus-contracts', 'score-contracts', 'transition-contracts', 'session-contracts')
$contracts = @()
foreach ($name in $names) {
    $exe = Join-Path $exeDir ("th04-port64-$name.exe")
    Write-Host "Checking $name..."
    $text = @(& $exe 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "$name failed: $text" }
    $text | Set-Content -LiteralPath (Join-Path $outDir "$name.log")
    $contracts += @{ name=$name; sha256=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant() }
}
$framesDir = (New-Item -ItemType Directory -Path (Join-Path $outDir 'frames')).FullName
$mainExe = Join-Path $exeDir 'th04-port64.exe'
Write-Host 'Running eight natural Stage 1 dialogue scenarios...'
$lines = @(& $mainExe --hdi $hdiFile --font-bmp $fontFile --dialog-screenshots $framesDir 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Stage 1 dialogue scenarios failed: $lines" }
$lines | Set-Content -LiteralPath (Join-Path $outDir 'dialog.log')
$images = @{}
Get-ChildItem -LiteralPath $framesDir -Filter '*.bmp' | ForEach-Object {
    $images[$_.Name] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
}
if ($images.Count -ne 64) { throw "Expected 64 checkpoints, got $($images.Count)." }
$counters = @($lines | ForEach-Object { "$_" -replace ' screenshot=.*$', '' } | Where-Object { $_ -like 'MAIN dialog *' })
if ($counters.Count -ne 72) { throw 'Missing Stage 1 scenario counters.' }
$receipt = @{
    passed=$true; host='native Windows'; contracts=$contracts
    native_sha256=(Get-FileHash -LiteralPath $mainExe -Algorithm SHA256).Hash.ToLowerInvariant()
    hdi_sha256=(Get-FileHash -LiteralPath $hdiFile -Algorithm SHA256).Hash.ToLowerInvariant()
    font_sha256=(Get-FileHash -LiteralPath $fontFile -Algorithm SHA256).Hash.ToLowerInvariant()
    dialog_fixture_bmp_sha256=$images; dialog_fixture_counters=$counters
    observed_utc=[DateTime]::UtcNow.ToString('o')
    limits='Headless contract/scenario execution; no GUI frame pacing or complete game claim.'
}
$receipt | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $outDir 'receipt.json')
Write-Host 'PASS: thirteen contracts and 64 natural dialogue checkpoints.'
