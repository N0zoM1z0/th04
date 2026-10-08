param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$Hdi,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$GraphicsReference,
    [Parameter(Mandatory=$true)][string]$SourceManifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Use a fresh output directory.' }
$out = (New-Item -ItemType Directory -Path $OutputDirectory).FullName
$executables = (Resolve-Path -LiteralPath $ExecutableDirectory).ProviderPath
$reference = (Resolve-Path -LiteralPath $GraphicsReference).ProviderPath
$image = (Resolve-Path -LiteralPath $Hdi).ProviderPath
$font = (Resolve-Path -LiteralPath $FontBitmap).ProviderPath
function Hash([string]$path) { return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
function SaveLines([string]$path,[object[]]$lines) {
    [IO.File]::WriteAllText($path, (($lines -join "`n")+"`n"), (New-Object Text.UTF8Encoding($false)))
}
$proof = Get-Content -Raw -LiteralPath (Join-Path $reference 'receipt.json') | ConvertFrom-Json
if (!$proof.passed -or (Hash $image) -cne $proof.hdi_sha256 -or (Hash $font) -cne $proof.font_sha256) {
    throw 'Registration data/font reference identity changed.'
}
$assets = Join-Path $reference 'assets'
foreach ($name in @('HI01.PI','SCNUM2.BFT','GAMEFT.BFT')) {
    if ((Hash (Join-Path $assets $name)) -cne $proof.assets.$name) { throw "Asset identity changed: $name" }
}
$imageBefore = Hash $image
$contracts = @(Get-ChildItem -LiteralPath $executables -Filter '*contracts.exe' | Sort-Object Name)
if ($contracts.Count -ne 33) { throw "Expected 33 contracts; found $($contracts.Count)" }
$products = @{}
foreach ($contract in $contracts) {
    $lines = @(& $contract.FullName 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Contract failed: $($contract.Name): $lines" }
    SaveLines (Join-Path $out ($contract.BaseName+'.txt')) $lines
    $products[$contract.Name] = Hash $contract.FullName
}
$scene = Join-Path $executables 'th04-port64-registration-scene-contracts.exe'
$lines = @(& $scene --assets $assets $font $proof.message_hex 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Real-asset scene controls failed: $lines" }
SaveLines (Join-Path $out 'scene-real-assets.txt') $lines
$lines = @(& $scene --fade-clock 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Scene clock capture failed: $lines" }
SaveLines (Join-Path $out 'fade-clock.txt') $lines
$game = Join-Path $executables 'th04-port64.exe'
$front = Join-Path $out 'front-end'
$lines = @(& $game --hdi $image --font-bmp $font --registration-checks $front --mute 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Headless frontend controls failed: $lines" }
SaveLines (Join-Path $out 'front-end.txt') $lines
if (@($lines | Where-Object { "$_" -match '^REGISTRATION fixture=' }).Count -ne 30) {
    throw 'Expected 30 seeded registration/fresh-OP/second-MAIN frontend controls.'
}
if ((Hash $image) -cne $imageBefore) { throw 'Read-only source HDI changed.' }
$captures = @{}
foreach ($file in @(Get-ChildItem -LiteralPath $front -Recurse -File)) {
    $relative = $file.FullName.Substring($front.Length+1).Replace([char]92,[char]47)
    $captures[$relative] = Hash $file.FullName
}
@{
    passed=$true; observed_utc=[DateTime]::UtcNow.ToString('o'); host='actual-Windows-AMD64';
    contracts=33; source_manifest=$SourceManifest; products=$products;
    game_sha256=(Hash $game); scene_sha256=(Hash $scene); captures=$captures;
    hdi_sha256=$imageBefore; font_sha256=(Hash $font);
    scope='Seeded child registration/save/reload/fresh OP/second MAIN; explicit mute. No natural full-game route or audio acceptance.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: 33 contracts, real assets, 30 seeded frontend saves/restarts; muted.'
