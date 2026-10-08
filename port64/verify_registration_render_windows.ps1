param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$SourceManifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$reference = (Resolve-Path -LiteralPath $ReferenceDirectory).ProviderPath
$executables = (Resolve-Path -LiteralPath $ExecutableDirectory).ProviderPath
$font = (Resolve-Path -LiteralPath $FontBitmap).ProviderPath
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Use a new output directory.' }
$out = (New-Item -ItemType Directory -Path $OutputDirectory).FullName
function Hash([string]$path) { return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
$proof = Get-Content -Raw -LiteralPath (Join-Path $reference 'receipt.json') | ConvertFrom-Json
if (!$proof.passed -or $proof.snapshots.Count -lt 90 -or $proof.load_segments.Count -ne 2) { throw 'Original graphics reference is incomplete.' }
foreach ($pair in @(@('fixtures.txt',$proof.fixture_sha256),@('original.bin',$proof.original_sha256))) {
    if ((Hash (Join-Path $reference $pair[0])) -cne $pair[1]) { throw 'Original graphics reference changed.' }
}
if ((Hash $font) -cne $proof.font_sha256) { throw 'Font bitmap identity changed.' }
$assets = Join-Path $reference 'assets'
foreach ($name in @('HI01.PI','SCNUM2.BFT','GAMEFT.BFT')) {
    if ((Hash (Join-Path $assets $name)) -cne $proof.assets.$name) { throw "Graphics asset identity changed: $name" }
}
$products = @{}
$contracts = @(Get-ChildItem -LiteralPath $executables -Filter '*contracts.exe' | Sort-Object Name)
if ($contracts.Count -ne 33) { throw 'Expected 33 native contract executables.' }
$completed = 0
foreach ($contract in $contracts) {
    Write-Progress -Activity 'TH04 native x64 registration graphics verification' -Status $contract.Name -PercentComplete (100*$completed/34)
    $lines = @(& $contract.FullName 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Native contract failed: $($contract.Name): $lines" }
    $products[$contract.Name] = Hash $contract.FullName
    $completed++
    Write-Host "PASS [$completed/34] $($contract.Name)"
}
$exe = Join-Path $executables 'th04-port64-registration-contracts.exe'
$native = Join-Path $out 'native.bin'
Write-Progress -Activity 'TH04 native x64 registration graphics verification' -Status 'Pages, text RAM and RGB differential' -PercentComplete (100*33/34)
& $exe --render (Join-Path $reference 'fixtures.txt') (Join-Path $assets 'HI01.PI') (Join-Path $assets 'SCNUM2.BFT') (Join-Path $assets 'GAMEFT.BFT') $font $proof.message_hex $native
if ($LASTEXITCODE -ne 0) { throw 'Native graphics capture failed.' }
if ((Hash $native) -cne $proof.original_sha256) { throw 'Graphics/text RAM/RGB outputs differ.' }
@{
    passed=$true; observed_utc=[DateTime]::UtcNow.ToString('o'); host='actual-Windows-AMD64';
    snapshots=$proof.snapshots.Count; contracts=33; source_manifest=$SourceManifest; reference_producer_manifest=$proof.source_manifest;
    executable_sha256=(Hash $exe); native_sha256=(Hash $native); products=$products;
    reference_receipt_sha256=(Hash (Join-Path $reference 'receipt.json'));
    scope='Original helper/kernel/TRAM reference consumer; software video adapters and emulator-source RGB corroboration. No scene timing, host score persistence, GUI integration or DOS exactness claim.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Progress -Activity 'TH04 native x64 registration graphics verification' -Completed
Write-Host "PASS [34/34] $($proof.snapshots.Count) original graphics controls."
