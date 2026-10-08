param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$SourceManifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $OutputDirectory) {throw 'Use a fresh output directory.'}
$out=(New-Item -ItemType Directory -Path $OutputDirectory).FullName
$executables=(Resolve-Path -LiteralPath $ExecutableDirectory).ProviderPath
function Hash([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function SaveLines([string]$path,[object[]]$lines) {
    [IO.File]::WriteAllText($path,(($lines -join "`n")+"`n"),(New-Object Text.UTF8Encoding($false)))
}
$contracts=@(Get-ChildItem -LiteralPath $executables -Filter '*contracts.exe' | Sort-Object Name)
if($contracts.Count -ne 34) {throw 'Expected 34 contract executables.'}
$products=@{}
foreach($contract in $contracts) {
    $lines=@(& $contract.FullName 2>&1)
    if($LASTEXITCODE -ne 0) {throw "Contract failed: $($contract.Name): $lines"}
    SaveLines (Join-Path $out ($contract.BaseName+'.txt')) $lines
    $products[$contract.Name]=Hash $contract.FullName
}
$exe=Join-Path $executables 'th04-port64-live-contracts.exe'
$scenes=Join-Path $out 'scenes'
$lines=@(& $exe --lifecycle-join $scenes 2>&1)
if($LASTEXITCODE -ne 0) {throw "Native lifecycle integration failed: $lines"}
$trace=Join-Path $out 'trace.txt';SaveLines $trace $lines
$outputs=@{}
Get-ChildItem -LiteralPath $scenes -Recurse -File | ForEach-Object {
    $relative=$_.FullName.Substring($scenes.Length+1).Replace('\','/')
    $outputs[$relative]=Hash $_.FullName
}
if($outputs.Count -ne 3 -or !$outputs.ContainsKey('continued/GENSOU.SCR') -or
   !$outputs.ContainsKey('ranked/GENSOU.SCR') -or !$outputs.ContainsKey('failed')) {throw 'Unexpected host files.'}
@{
    passed=$true;observed_utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';
    contracts=34;source_manifest=$SourceManifest;products=$products;
    executable_sha256=(Hash $exe);trace_sha256=(Hash $trace);outputs=$outputs;
    scope='Explicit native player checkpoints; MAIN suffix/Game Over clocks, real Continue writer-close, ten sections, restart and failed-write invariants. No natural route, original joined-CPU, frontend graphics, physical timing or audio acceptance.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS actual Windows 34 contracts, MAIN lifecycle integration and host files.'
