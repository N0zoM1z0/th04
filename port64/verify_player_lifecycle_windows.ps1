param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$SourceManifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $OutputDirectory) {throw 'Use a fresh output directory.'}
$out=(New-Item -ItemType Directory -Path $OutputDirectory).FullName
$reference=(Resolve-Path -LiteralPath $ReferenceDirectory).ProviderPath
$executables=(Resolve-Path -LiteralPath $ExecutableDirectory).ProviderPath
function Hash([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function SaveLines([string]$path,[object[]]$lines) {
    [IO.File]::WriteAllText($path,(($lines -join "`n")+"`n"),(New-Object Text.UTF8Encoding($false)))
}
$proof=Get-Content -Raw -LiteralPath (Join-Path $reference 'receipt.json') | ConvertFrom-Json
if(!$proof.passed -or $proof.records -ne 10319 -or $proof.load_segments.Count -ne 2 -or $proof.source_manifest -cne $SourceManifest) {
    throw 'Current-source original lifecycle reference is incomplete.'
}
if((Hash (Join-Path $reference 'fixtures.txt')) -cne $proof.fixture_sha256 -or
   (Hash (Join-Path $reference 'original.txt')) -cne $proof.trace_sha256) {throw 'Original reference changed.'}
$contracts=@(Get-ChildItem -LiteralPath $executables -Filter '*contracts.exe' | Sort-Object Name)
if($contracts.Count -ne 34) {throw 'Expected 34 contract executables.'}
$products=@{}
foreach($contract in $contracts) {
    $lines=@(& $contract.FullName 2>&1)
    if($LASTEXITCODE -ne 0) {throw "Contract failed: $($contract.Name): $lines"}
    SaveLines (Join-Path $out ($contract.BaseName+'.txt')) $lines
    $products[$contract.Name]=Hash $contract.FullName
}
$exe=Join-Path $executables 'th04-port64-player-lifecycle-contracts.exe'
$lines=@(& $exe --vectors (Join-Path $reference 'fixtures.txt') 2>&1)
if($LASTEXITCODE -ne 0) {throw 'Native lifecycle vectors failed.'}
$native=Join-Path $out 'native.txt';SaveLines $native $lines
if((Hash $native) -cne $proof.trace_sha256) {throw 'Lifecycle state/request differential failed.'}
@{
    passed=$true;observed_utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';
    contracts=34;source_manifest=$SourceManifest;products=$products;records=$proof.records;
    executable_sha256=(Hash $exe);native_sha256=(Hash $native);
    reference_receipt_sha256=(Hash (Join-Path $reference 'receipt.json'));
    scope='Original player/miss/Bomb state producers with explicit fire/items/HUD/sound/game-over/character graphics adapters. Component, not live gameplay; no audio device.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: actual Windows 34 contracts and 10,319 original lifecycle records.'
