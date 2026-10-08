param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$Hdi,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$SourceManifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $OutputDirectory) {throw 'Use a fresh output directory.'}
$out=(New-Item -ItemType Directory -Path $OutputDirectory).FullName
function Hash([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
$proof=Get-Content -Raw -LiteralPath (Join-Path $ReferenceDirectory 'receipt.json') | ConvertFrom-Json
if(!$proof.passed -or !$proof.original_cpu_reexecuted -or !$proof.muted -or $proof.scenes -ne 20 -or
   $proof.load_segments.Count -ne 2) {throw 'Attested two-load integration reference is incomplete.'}
$producer=Get-Content -Raw -LiteralPath (Join-Path $ReferenceDirectory 'source-manifest.json') | ConvertFrom-Json
if($producer.sha256 -cne $proof.source_manifest) {throw 'Original producer manifest changed.'}
if((Hash $Hdi) -cne $proof.hdi_sha256 -or (Hash $FontBitmap) -cne $proof.font_sha256 -or
   (Hash (Join-Path $ReferenceDirectory 'original.gz')) -cne $proof.trace_gzip_sha256) {throw 'Original integration inputs changed.'}
foreach($property in $proof.outputs.PSObject.Properties) {
    if((Hash (Join-Path (Join-Path $ReferenceDirectory 'scenes') $property.Name)) -cne $property.Value) {throw 'Original fixture input changed.'}
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
$exe=(Resolve-Path -LiteralPath (Join-Path $ExecutableDirectory 'th04-port64.exe')).ProviderPath
$products['th04-port64.exe']=Hash $exe
$scenes=Join-Path $out 'scenes'
$disk=(Resolve-Path -LiteralPath $Hdi).ProviderPath
$font=(Resolve-Path -LiteralPath $FontBitmap).ProviderPath
$start=New-Object Diagnostics.ProcessStartInfo
$start.FileName=$exe
$start.Arguments='--hdi "'+$disk+'" --font-bmp "'+$font+'" --mute --gameover-checks "'+$scenes+'"'
$start.UseShellExecute=$false;$start.RedirectStandardOutput=$true;$start.RedirectStandardError=$true;$start.CreateNoWindow=$true
$process=New-Object Diagnostics.Process;$process.StartInfo=$start
if(!$process.Start()) {throw 'Cannot launch muted Game Over frontend.'}
$algorithm=[Security.Cryptography.SHA256]::Create()
try {
    # Hash every indexed/TRAM/RGB byte without another raw capture on disk.
    $digest=([BitConverter]::ToString($algorithm.ComputeHash($process.StandardOutput.BaseStream))).Replace('-','').ToLowerInvariant()
    $errors=$process.StandardError.ReadToEnd();$process.WaitForExit()
    if($process.ExitCode -ne 0) {throw "Game Over frontend failed: $errors"}
    if($digest -cne $proof.trace_raw_sha256) {throw 'Complete Game Over frontend display stream differs.'}
} finally {
    if(!$process.HasExited) {$process.Kill();$process.WaitForExit()}
    $algorithm.Dispose();$process.Dispose()
}
$outputs=@{}
Get-ChildItem -LiteralPath $scenes -Recurse -File | ForEach-Object {
    $relative=$_.FullName.Substring($scenes.Length+1).Replace('\','/')
    $outputs[$relative]=Hash $_.FullName
}
if($outputs.Count -ne @($proof.outputs.PSObject.Properties).Count) {throw 'Unexpected frontend output files.'}
foreach($property in $proof.outputs.PSObject.Properties) {
    if(!$outputs.ContainsKey($property.Name) -or $outputs[$property.Name] -cne $property.Value) {throw "Frontend file differs: $($property.Name)"}
}
@{
    passed=$true;observed_utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';
    source_manifest=$SourceManifest;contracts=34;products=$products;outputs=$outputs;muted=$true;
    scenes=$proof.scenes;snapshots=$proof.snapshots;compared_bytes=$proof.compared_bytes;
    trace_raw_sha256=$digest;reference_receipt_sha256=(Hash (Join-Path $ReferenceDirectory 'receipt.json'));
    reference_producer_manifest=$proof.source_manifest;
    scope='Actual OP selection and finite STD enemy contact drive MAIN; complete frozen graphics/TRAM/RGB and scene/file outputs agree with two-load original request/TRAM controls. Display/CGROM/hardware and life/bomb HUD/audio/DOS score-I/O adapters remain. Quit ends at pending score-only MAINE; no full route or physical timing acceptance.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: actual Windows 34 contracts, twenty live Game Over scenes and complete display/file streams.'
