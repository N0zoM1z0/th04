param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$RegistrationReference,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$SourceManifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $OutputDirectory) {throw 'Use a fresh output directory.'}
$out=(New-Item -ItemType Directory -Path $OutputDirectory).FullName
function Hash([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function StreamHash($stream) {
    $algorithm=[Security.Cryptography.SHA256]::Create()
    try {return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}
    finally {$algorithm.Dispose()}
}
$proof=Get-Content -Raw -LiteralPath (Join-Path $ReferenceDirectory 'receipt.json') | ConvertFrom-Json
if(!$proof.passed -or !$proof.original_cpu_reexecuted -or $proof.source_manifest -cne $SourceManifest -or
   $proof.load_segments.Count -ne 2 -or !$proof.scene_reference_receipt_sha256) {throw 'Current-source two-load scene graphics reference is incomplete.'}
foreach($pair in @(@('fixtures.txt',$proof.fixture_sha256),@('original.gz',$proof.trace_gzip_sha256))) {
    if((Hash (Join-Path $ReferenceDirectory $pair[0])) -cne $pair[1]) {throw 'Original Game Over reference changed.'}
}
foreach($property in $proof.asset_sha256.PSObject.Properties) {
    if((Hash (Join-Path $ReferenceDirectory $property.Name)) -cne $property.Value) {throw 'Game Over asset changed.'}
}
$products=@{}
$contracts=@(Get-ChildItem -LiteralPath $ExecutableDirectory -Filter '*contracts.exe' | Sort-Object Name)
if($contracts.Count -ne 34) {throw 'Expected 34 contract executables.'}
foreach($contract in $contracts) {
    $lines=@(& $contract.FullName 2>&1)
    if($LASTEXITCODE -ne 0) {throw "Contract failed: $($contract.Name): $lines"}
    [IO.File]::WriteAllText((Join-Path $out ($contract.BaseName+'.txt')),(($lines -join "`n")+"`n"),(New-Object Text.UTF8Encoding($false)))
    $products[$contract.Name]=Hash $contract.FullName
}
$exe=(Resolve-Path -LiteralPath (Join-Path $ExecutableDirectory 'th04-port64-player-lifecycle-contracts.exe')).ProviderPath
$fixture=(Resolve-Path -LiteralPath (Join-Path $ReferenceDirectory 'fixtures.txt')).ProviderPath
$start=New-Object Diagnostics.ProcessStartInfo
$start.FileName=$exe;$start.Arguments='--gameover-render "'+$fixture+'"'
$start.UseShellExecute=$false;$start.RedirectStandardOutput=$true;$start.RedirectStandardError=$true;$start.CreateNoWindow=$true
$process=New-Object Diagnostics.Process;$process.StartInfo=$start
if(!$process.Start()) {throw 'Cannot launch Game Over renderer.'}
try {
    $digest=StreamHash $process.StandardOutput.BaseStream
    $errors=$process.StandardError.ReadToEnd();$process.WaitForExit()
    if($process.ExitCode -ne 0) {throw "Game Over renderer failed: $errors"}
    if($digest -cne $proof.trace_raw_sha256) {throw 'Complete Game Over graphics stream differs.'}
} finally {
    if(!$process.HasExited) {$process.Kill();$process.WaitForExit()}
    $process.Dispose()
}
# The shared text compositor changed. Consume the independent 158-snapshot
# registration reference as well, including both pages, palette, TRAM and RGB.
$registration=Get-Content -Raw -LiteralPath (Join-Path $RegistrationReference 'receipt.json') | ConvertFrom-Json
if(!$registration.passed -or $registration.snapshots.Count -ne 158 -or $registration.load_segments.Count -ne 2) {throw 'Registration reference is incomplete.'}
if((Hash $FontBitmap) -cne $registration.font_sha256) {throw 'Registration CGROM changed.'}
foreach($pair in @(@('fixtures.txt',$registration.fixture_sha256),@('original.bin',$registration.original_sha256))) {
    if((Hash (Join-Path $RegistrationReference $pair[0])) -cne $pair[1]) {throw 'Original registration reference changed.'}
}
$assets=Join-Path $RegistrationReference 'assets'
foreach($name in @('HI01.PI','SCNUM2.BFT','GAMEFT.BFT')) {
    if((Hash (Join-Path $assets $name)) -cne $registration.assets.$name) {throw 'Registration asset changed.'}
}
$regExe=Join-Path $ExecutableDirectory 'th04-port64-registration-contracts.exe'
$native=Join-Path $out 'registration-native.bin'
& $regExe --render (Join-Path $RegistrationReference 'fixtures.txt') (Join-Path $assets 'HI01.PI') (Join-Path $assets 'SCNUM2.BFT') (Join-Path $assets 'GAMEFT.BFT') $FontBitmap $registration.message_hex $native
if($LASTEXITCODE -ne 0 -or (Hash $native) -cne $registration.original_sha256) {throw 'Registration graphics regression failed.'}
$archive=Join-Path $out 'registration-native.gz'
$inputStream=[IO.File]::OpenRead($native);$outputStream=[IO.File]::Create($archive)
$gzip=New-Object IO.Compression.GZipStream($outputStream,[IO.Compression.CompressionMode]::Compress)
try {$inputStream.CopyTo($gzip)} finally {$gzip.Dispose();$outputStream.Dispose();$inputStream.Dispose()}
$inputStream=[IO.File]::OpenRead($archive)
$gzip=New-Object IO.Compression.GZipStream($inputStream,[IO.Compression.CompressionMode]::Decompress)
try {$readback=StreamHash $gzip} finally {$gzip.Dispose();$inputStream.Dispose()}
if($readback -cne $registration.original_sha256) {throw 'Compressed registration capture readback failed.'}
$retiredBytes=(Get-Item -LiteralPath $native).Length
Remove-Item -LiteralPath $native
@{
    passed=$true;observed_utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';
    source_manifest=$SourceManifest;contracts=34;products=$products;
    snapshots=$proof.snapshots;compared_bytes=$proof.compared_bytes;gameover_raw_sha256=$digest;
    gameover_reference_receipt_sha256=(Hash (Join-Path $ReferenceDirectory 'receipt.json'));
    registration_snapshots=158;registration_raw_sha256=$readback;registration_gzip_sha256=(Hash $archive);
    registration_reference_receipt_sha256=(Hash (Join-Path $RegistrationReference 'receipt.json'));
    registration_reference_producer_manifest=$registration.source_manifest;retired_raw_bytes=$retiredBytes;
    scope='Original two-load Game Over TRAM instructions and complete indexed/TRAM/RGB stream; prior independent registration graphics regression. CGROM/frozen graphics/palette and emulator video policy are adapters. No live MAIN, physical timing/audio or full-route acceptance.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: actual Windows 34 contracts, Game Over graphics, 158 registration snapshots.'
