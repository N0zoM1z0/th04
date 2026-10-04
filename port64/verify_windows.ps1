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
           'orange-contracts', 'dialog-contracts', 'bonus-contracts', 'score-contracts', 'transition-contracts', 'session-contracts', 'midboss2-contracts', 'kurumi-contracts', 'midboss3-contracts', 'elly-contracts', 'midboss4-contracts')
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
$stage2Dir = (New-Item -ItemType Directory -Path (Join-Path $outDir 'stage2-frames')).FullName
Write-Host 'Running four natural Stage 2 resource and dialogue scenarios...'
$stage2Lines = @(& $mainExe --hdi $hdiFile --font-bmp $fontFile --stage2-screenshots $stage2Dir 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Stage 2 scenarios failed: $stage2Lines" }
$stage2Lines | Set-Content -LiteralPath (Join-Path $outDir 'stage2.log')
$stage2Images = @{}
Get-ChildItem -LiteralPath $stage2Dir -Filter '*.bmp' | ForEach-Object {
    $stage2Images[$_.Name] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
}
if ($stage2Images.Count -ne 32) { throw 'Missing Stage 2 visual checkpoints.' }
$stage2Counters = @($stage2Lines | ForEach-Object { "$_" -replace ' screenshot=.*$', '' } | Where-Object { $_ -like 'MAIN Stage2 *' })
if ($stage2Counters.Count -ne 36) { throw 'Missing Stage 2 scenario counters.' }
$kurumiDir = (New-Item -ItemType Directory -Path (Join-Path $outDir 'kurumi-frames')).FullName
Write-Host 'Running eight natural Kurumi battle and departure scenarios...'
$kurumiLines = @(& $mainExe --hdi $hdiFile --font-bmp $fontFile --kurumi-screenshots $kurumiDir 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Kurumi scenarios failed: $kurumiLines" }
$kurumiLines | Set-Content -LiteralPath (Join-Path $outDir 'kurumi.log')
$kurumiImages = @{}
Get-ChildItem -LiteralPath $kurumiDir -Filter '*.bmp' | ForEach-Object {
    $kurumiImages[$_.Name] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
}
if ($kurumiImages.Count -ne 72) { throw 'Missing Kurumi visual checkpoints.' }
$kurumiCounters = @($kurumiLines | ForEach-Object { "$_" -replace ' screenshot=.*$', '' } | Where-Object { $_ -like 'MAIN Kurumi *' })
if ($kurumiCounters.Count -ne 80) { throw 'Missing Kurumi scenario counters.' }
$stage3Dir = (New-Item -ItemType Directory -Path (Join-Path $outDir 'stage3-frames')).FullName
Write-Host 'Running eight natural Stage 3 midboss and dialogue scenarios...'
$stage3Lines = @(& $mainExe --hdi $hdiFile --font-bmp $fontFile --stage3-screenshots $stage3Dir 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Stage 3 scenarios failed: $stage3Lines" }
$stage3Lines | Set-Content -LiteralPath (Join-Path $outDir 'stage3.log')
$stage3Images = @{}
Get-ChildItem -LiteralPath $stage3Dir -Filter '*.bmp' | ForEach-Object {
    $stage3Images[$_.Name] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
}
if ($stage3Images.Count -ne 72) { throw 'Missing Stage 3 visual checkpoints.' }
$stage3Counters = @($stage3Lines | ForEach-Object { "$_" -replace ' screenshot=.*$', '' } | Where-Object { $_ -like 'MAIN Stage3 *' })
if ($stage3Counters.Count -ne 80) { throw 'Missing Stage 3 scenario counters.' }
$ellyDir = (New-Item -ItemType Directory -Path (Join-Path $outDir 'elly-frames')).FullName
Write-Host 'Running eight natural Elly battle and departure scenarios...'
$ellyLines = @(& $mainExe --hdi $hdiFile --font-bmp $fontFile --elly-screenshots $ellyDir 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Elly scenarios failed: $ellyLines" }
$ellyLines | Set-Content -LiteralPath (Join-Path $outDir 'elly.log')
$ellyImages = @{}
Get-ChildItem -LiteralPath $ellyDir -Filter '*.bmp' | ForEach-Object {
    $ellyImages[$_.Name] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
}
if ($ellyImages.Count -ne 96) { throw 'Missing Elly visual checkpoints.' }
$ellyCounters = @($ellyLines | ForEach-Object { "$_" -replace ' screenshot=.*$', '' } | Where-Object { $_ -like 'MAIN Elly *' })
if ($ellyCounters.Count -ne 104) { throw 'Missing Elly scenario counters.' }
$stage4Dir = (New-Item -ItemType Directory -Path (Join-Path $outDir 'stage4-frames')).FullName
Write-Host 'Running eight natural Stage4 resource, midboss and dialogue scenarios...'
$stage4Lines = @(& $mainExe --hdi $hdiFile --font-bmp $fontFile --stage4-screenshots $stage4Dir 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Stage4 scenarios failed: $stage4Lines" }
$stage4Lines | Set-Content -LiteralPath (Join-Path $outDir 'stage4.log')
$stage4Images = @{}
Get-ChildItem -LiteralPath $stage4Dir -Filter '*.bmp' | ForEach-Object {
    $stage4Images[$_.Name] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
}
if ($stage4Images.Count -ne 96) { throw 'Missing Stage4 visual checkpoints.' }
$stage4Counters = @($stage4Lines | ForEach-Object { "$_" -replace ' screenshot=.*$', '' } | Where-Object { $_ -like 'MAIN Stage4 *' })
if ($stage4Counters.Count -ne 104) { throw 'Missing Stage4 scenario counters.' }
$receipt = @{
    passed=$true; host='native Windows'; contracts=$contracts
    native_sha256=(Get-FileHash -LiteralPath $mainExe -Algorithm SHA256).Hash.ToLowerInvariant()
    hdi_sha256=(Get-FileHash -LiteralPath $hdiFile -Algorithm SHA256).Hash.ToLowerInvariant()
    font_sha256=(Get-FileHash -LiteralPath $fontFile -Algorithm SHA256).Hash.ToLowerInvariant()
    dialog_fixture_bmp_sha256=$images; dialog_fixture_counters=$counters
    stage2_fixture_bmp_sha256=$stage2Images; stage2_fixture_counters=$stage2Counters
    kurumi_fixture_bmp_sha256=$kurumiImages; kurumi_fixture_counters=$kurumiCounters
    stage3_fixture_bmp_sha256=$stage3Images; stage3_fixture_counters=$stage3Counters
    stage4_fixture_bmp_sha256=$stage4Images
    stage4_fixture_counters=$stage4Counters
    elly_fixture_bmp_sha256=$ellyImages; elly_fixture_counters=$ellyCounters
    observed_utc=[DateTime]::UtcNow.ToString('o')
    limits='Headless contract/scenario execution; no GUI frame pacing or complete game claim.'
}
$receipt | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $outDir 'receipt.json')
Write-Host ("PASS: {0} contracts and {1} natural visual checkpoints." -f $names.Count, ($images.Count + $stage2Images.Count + $kurumiImages.Count + $stage3Images.Count + $ellyImages.Count + $stage4Images.Count))
