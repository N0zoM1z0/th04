param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$Hdi,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$SourceManifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $OutputDirectory) {throw 'Use fresh score-route outputs.'}
$out=(New-Item -ItemType Directory -Path $OutputDirectory).FullName
function Hash([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
$proof=Get-Content -Raw -LiteralPath (Join-Path $ReferenceDirectory 'receipt.json') | ConvertFrom-Json
$producer=Get-Content -Raw -LiteralPath (Join-Path $ReferenceDirectory 'source-manifest.json') | ConvertFrom-Json
if(!$proof.passed -or !$proof.muted -or !$proof.original_cpu_reexecuted -or
   $proof.natural_bounded_routes -ne 24 -or $proof.failed_writer_routes -ne 4 -or
   $proof.load_segments.Count -ne 2 -or $proof.source_manifest -cne $producer.sha256) {
    throw 'Independent two-load MAINE reference is incomplete.'
}
if((Hash $Hdi) -cne $proof.hdi_sha256 -or (Hash $FontBitmap) -cne $proof.font_sha256 -or
   (Hash (Join-Path $ReferenceDirectory 'original.json')) -cne $proof.original_sha256) {
    throw 'Reference identity changed.'
}
foreach($property in $proof.outputs.PSObject.Properties) {
    if((Hash (Join-Path (Join-Path $ReferenceDirectory 'scenes') $property.Name)) -cne $property.Value) {
        throw 'Reference frontend outputs changed.'
    }
}
$contracts=@(Get-ChildItem -LiteralPath $ExecutableDirectory -Filter '*contracts.exe' | Sort-Object Name)
if($contracts.Count -ne 34) {throw 'Expected34 contracts.'}
$products=@{}
foreach($contract in $contracts) {
    $lines=@(& $contract.FullName 2>&1)
    if($LASTEXITCODE -ne 0) {throw "Contract failed: $($contract.Name): $lines"}
    [IO.File]::WriteAllText((Join-Path $out ($contract.BaseName+'.txt')),(($lines -join "`n")+"`n"),(New-Object Text.UTF8Encoding($false)))
    $products[$contract.Name]=Hash $contract.FullName
}
$exe=(Resolve-Path -LiteralPath (Join-Path $ExecutableDirectory 'th04-port64.exe')).ProviderPath
$products['th04-port64.exe']=Hash $exe
$scenes=Join-Path $out 'scenes'
$start=New-Object Diagnostics.ProcessStartInfo
$start.FileName=$exe
$start.Arguments='--hdi "'+(Resolve-Path -LiteralPath $Hdi).ProviderPath+'" --font-bmp "'+
    (Resolve-Path -LiteralPath $FontBitmap).ProviderPath+'" --mute --score-route-checks "'+$scenes+'"'
$start.UseShellExecute=$false;$start.RedirectStandardOutput=$true;$start.RedirectStandardError=$true;$start.CreateNoWindow=$true
$process=New-Object Diagnostics.Process;$process.StartInfo=$start
if(!$process.Start()) {throw 'Cannot launch muted score-route frontend.'}
try {
    $stdout=$process.StandardOutput.ReadToEnd();$errors=$process.StandardError.ReadToEnd();$process.WaitForExit()
    if($process.ExitCode -ne 0) {throw "Score-route frontend failed: $errors"}
    $lines=$stdout -split "\r?\n"
    if(@($lines | Where-Object {$_ -match '^SCORE_ROUTE '}).Count -ne 24 -or
       @($lines | Where-Object {$_ -match '^SCORE_ROUTE_FAILED '}).Count -ne 4) {throw 'Missing natural route/failure controls.'}
    [IO.File]::WriteAllText((Join-Path $out 'native.txt'),($stdout.Replace("`r`n","`n")),(New-Object Text.UTF8Encoding($false)))
} finally {if(!$process.HasExited) {$process.Kill();$process.WaitForExit()};$process.Dispose()}
$outputs=@{}
Get-ChildItem -LiteralPath $scenes -Recurse -File | ForEach-Object {
    $relative=$_.FullName.Substring($scenes.Length+1).Replace('\','/')
    $outputs[$relative]=Hash $_.FullName
}
if($outputs.Count -ne @($proof.outputs.PSObject.Properties).Count) {throw 'Unexpected output count.'}
foreach($property in $proof.outputs.PSObject.Properties) {
    if(!$outputs.ContainsKey($property.Name) -or $outputs[$property.Name] -cne $property.Value) {
        throw "Complete frontend file differs: $($property.Name)"
    }
}
@{
    passed=$true;observed_utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';muted=$true;
    source_manifest=$SourceManifest;reference_producer_manifest=$proof.source_manifest;
    reference_receipt_sha256=(Hash (Join-Path $ReferenceDirectory 'receipt.json'));
    contracts=34;products=$products;outputs=$outputs;natural_bounded_routes=24;failed_writer_routes=4;
    scope='Actual OP/STD contact and shot kills -> Quit -> registration -> verdict -> fresh OP -> second MAIN. Original MAINE dispatch/delay reference has guarded child-duration/init/sound/exec adapters. Full native files agree; no complete natural game route, physical timing or audio acceptance.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS actual Windows34 contracts,24 bounded score routes and4 real failed writers; muted.'
