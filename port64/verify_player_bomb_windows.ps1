param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$StateReference,
    [Parameter(Mandatory=$true)][string]$PixelReference,
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
$state=Get-Content -Raw -LiteralPath (Join-Path $StateReference 'receipt.json') | ConvertFrom-Json
$pixel=Get-Content -Raw -LiteralPath (Join-Path $PixelReference 'receipt.json') | ConvertFrom-Json
foreach($proof in @($state,$pixel)) {
    if(!$proof.passed -or $proof.source_manifest -cne $SourceManifest -or $proof.load_segments.Count -ne 2 -or !$proof.original_cpu_reexecuted) {throw 'Current-source original reference is incomplete.'}
}
if((Hash (Join-Path $StateReference 'fixtures.txt')) -cne $state.fixture_sha256 -or
   (Hash (Join-Path $StateReference 'original.txt')) -cne $state.trace_sha256 -or
   (Hash (Join-Path $PixelReference 'fixtures.txt')) -cne $pixel.fixture_sha256 -or
   (Hash (Join-Path $PixelReference 'original.gz')) -cne $pixel.trace_gzip_sha256) {throw 'Original reference changed.'}
foreach($property in $pixel.asset_sha256.PSObject.Properties) {
    if((Hash (Join-Path $PixelReference $property.Name)) -cne $property.Value) {throw 'Bomb asset changed.'}
}
$lines=@(& $exe '--bomb-vectors' (Join-Path $StateReference 'fixtures.txt') 2>&1)
if($LASTEXITCODE -ne 0) {throw 'Bomb state consumer failed.'}
$native=Join-Path $out 'native-state.txt';SaveLines $native $lines
if((Hash $native) -cne $state.trace_sha256) {throw 'Bomb state differential failed.'}
# Consume binary stdout directly. Do not allocate a second140MB pixel file.
$start=New-Object Diagnostics.ProcessStartInfo
$start.FileName=$exe
$fixture=(Resolve-Path -LiteralPath (Join-Path $PixelReference 'fixtures.txt')).ProviderPath
$start.Arguments='--bomb-pixels "'+$fixture+'"'
$start.UseShellExecute=$false;$start.RedirectStandardOutput=$true;$start.RedirectStandardError=$true;$start.CreateNoWindow=$true
$process=New-Object Diagnostics.Process;$process.StartInfo=$start
if(!$process.Start()) {throw 'Cannot launch Bomb pixel consumer.'}
$algorithm=[Security.Cryptography.SHA256]::Create()
try {
    $digest=([BitConverter]::ToString($algorithm.ComputeHash($process.StandardOutput.BaseStream))).Replace('-','').ToLowerInvariant()
    $errorText=$process.StandardError.ReadToEnd();$process.WaitForExit()
    if($process.ExitCode -ne 0) {throw "Bomb pixel consumer failed: $errorText"}
    if($digest -cne $pixel.trace_raw_sha256) {throw 'Bomb complete pixel stream differs.'}
} finally {
    if(!$process.HasExited) {$process.Kill();$process.WaitForExit()}
    $algorithm.Dispose();$process.Dispose()
}
@{
    passed=$true;observed_utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';
    source_manifest=$SourceManifest;contracts=34;products=$products;
    state_cases=$state.cases;state_records=$state.records;state_sha256=(Hash $native);
    pixel_cases=$pixel.cases;pixel_screens=$pixel.screens;pixel_raw_sha256=$digest;
    state_reference_receipt_sha256=(Hash (Join-Path $StateReference 'receipt.json'));
    pixel_reference_receipt_sha256=(Hash (Join-Path $PixelReference 'receipt.json'));
    scope='Complete character Bomb state/request and indexed pixel streams against two-load original controls. Explicit hardware/input/sound adapters; live MAIN and audio remain unaccepted.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: actual Windows 34 contracts and complete Bomb state/pixel streams.'
