param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$SourceManifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $OutputDirectory) {throw 'Use a fresh output directory.'}
$out=(New-Item -ItemType Directory -Path $OutputDirectory).FullName
function Hash([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function SaveLines([string]$path,[object[]]$lines) {
    [IO.File]::WriteAllText($path,(($lines -join "`n")+"`n"),(New-Object Text.UTF8Encoding($false)))
}
$products=@{}
$contracts=@(Get-ChildItem -LiteralPath $ExecutableDirectory -Filter '*contracts.exe' | Sort-Object Name)
if($contracts.Count -ne 34) {throw 'Expected 34 contract executables.'}
foreach($contract in $contracts) {
    $lines=@(& $contract.FullName 2>&1)
    if($LASTEXITCODE -ne 0) {throw "Contract failed: $($contract.Name): $lines"}
    SaveLines (Join-Path $out ($contract.BaseName+'.txt')) $lines
    $products[$contract.Name]=Hash $contract.FullName
}
$exe=(Resolve-Path -LiteralPath (Join-Path $ExecutableDirectory 'th04-port64-player-lifecycle-contracts.exe')).ProviderPath
$state=Get-Content -Raw -LiteralPath (Join-Path $ReferenceDirectory 'receipt.json') | ConvertFrom-Json
$pixel=Get-Content -Raw -LiteralPath (Join-Path $ReferenceDirectory 'receipt.json') | ConvertFrom-Json
foreach($proof in @($state,$pixel)) {
    if(!$proof.passed -or $proof.source_manifest -cne $SourceManifest -or $proof.load_segments.Count -ne 2 -or !$proof.original_cpu_reexecuted) {throw 'Current-source original reference is incomplete.'}
}
if((Hash (Join-Path $ReferenceDirectory 'state-fixtures.txt')) -cne $state.fixture_sha256[0] -or
   (Hash (Join-Path $ReferenceDirectory 'original.txt')) -cne $state.state_sha256 -or
   (Hash (Join-Path $ReferenceDirectory 'pixel-fixtures.txt')) -cne $pixel.fixture_sha256[1] -or
   (Hash (Join-Path $ReferenceDirectory 'original.gz')) -cne $pixel.trace_gzip_sha256) {throw 'Original reference changed.'}
foreach($property in $pixel.asset_sha256.PSObject.Properties) {
    if((Hash (Join-Path $ReferenceDirectory $property.Name)) -cne $property.Value) {throw 'player render asset changed.'}
}
$lines=@(& $exe '--player-render-vectors' (Join-Path $ReferenceDirectory 'state-fixtures.txt') 2>&1)
if($LASTEXITCODE -ne 0) {throw 'player render state consumer failed.'}
$native=Join-Path $out 'native-state.txt';SaveLines $native $lines
if((Hash $native) -cne $state.state_sha256) {throw 'player render state differential failed.'}
# Consume binary stdout directly without a second raw pixel capture.
$start=New-Object Diagnostics.ProcessStartInfo
$start.FileName=$exe
$fixture=(Resolve-Path -LiteralPath (Join-Path $ReferenceDirectory 'pixel-fixtures.txt')).ProviderPath
$start.Arguments='--player-render-pixels "'+$fixture+'"'
$start.UseShellExecute=$false;$start.RedirectStandardOutput=$true;$start.RedirectStandardError=$true;$start.CreateNoWindow=$true
$process=New-Object Diagnostics.Process;$process.StartInfo=$start
if(!$process.Start()) {throw 'Cannot launch player render pixel consumer.'}
$algorithm=[Security.Cryptography.SHA256]::Create()
try {
    $digest=([BitConverter]::ToString($algorithm.ComputeHash($process.StandardOutput.BaseStream))).Replace('-','').ToLowerInvariant()
    $errorText=$process.StandardError.ReadToEnd();$process.WaitForExit()
    if($process.ExitCode -ne 0) {throw "player render pixel consumer failed: $errorText"}
    if($digest -cne $pixel.trace_raw_sha256) {throw 'player render complete pixel stream differs.'}
} finally {
    if(!$process.HasExited) {$process.Kill();$process.WaitForExit()}
    $algorithm.Dispose();$process.Dispose()
}
@{
    passed=$true;observed_utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';
    source_manifest=$SourceManifest;contracts=34;products=$products;
    state_cases=$state.state_cases;state_records=$state.state_cases;state_sha256=(Hash $native);
    pixel_cases=$pixel.pixel_cases;pixel_screens=$pixel.screens;pixel_raw_sha256=$digest;
    state_reference_receipt_sha256=(Hash (Join-Path $ReferenceDirectory 'receipt.json'));
    pixel_reference_receipt_sha256=(Hash (Join-Path $ReferenceDirectory 'receipt.json'));
    scope='Complete player-render request and indexed pixel streams against two-load original controls. Explicit hardware/input/sound adapters; live MAIN and audio remain unaccepted.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: actual Windows 34 contracts and complete player render state/pixel streams.'
