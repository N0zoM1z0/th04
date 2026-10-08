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
$contracts=@(Get-ChildItem -LiteralPath $executables -Filter '*contracts.exe' | Sort-Object Name)
if($contracts.Count -ne 34) {throw 'Expected 34 contract executables.'}
$products=@{}
foreach($contract in $contracts) {
    $lines=@(& $contract.FullName 2>&1)
    if($LASTEXITCODE -ne 0) {throw "Contract failed: $($contract.Name): $lines"}
    SaveLines (Join-Path $out ($contract.BaseName+'.txt')) $lines
    $products[$contract.Name]=Hash $contract.FullName
}
$cases=@(
    @('menu-linux-final','th04-port64-player-lifecycle-contracts.exe','--gameover-menu'),
    @('scene-linux-final','th04-port64-player-lifecycle-contracts.exe','--gameover-scene'),
    @('main-score-linux-final','th04-port64-score-file-contracts.exe','--main-trace')
)
$controls=@{}
foreach($case in $cases) {
    $ref=Join-Path $reference $case[0]
    $proof=Get-Content -Raw -LiteralPath (Join-Path $ref 'receipt.json') | ConvertFrom-Json
    if(!$proof.passed -or $proof.load_segments.Count -ne 2 -or $proof.source_manifest -cne $SourceManifest) {
        throw "Current-source original reference is incomplete: $($case[0])"
    }
    if((Hash (Join-Path $ref 'fixtures.txt')) -cne $proof.fixture_sha256 -or
       (Hash (Join-Path $ref 'original.txt')) -cne $proof.trace_sha256) {throw 'Original reference changed.'}
    $exe=Join-Path $executables $case[1]
    $lines=@(& $exe $case[2] (Join-Path $ref 'fixtures.txt') 2>&1)
    if($LASTEXITCODE -ne 0) {throw "Native control failed: $($case[0])"}
    $native=Join-Path $out ($case[0]+'.txt');SaveLines $native $lines
    if((Hash $native) -cne $proof.trace_sha256) {throw "Differential failed: $($case[0])"}
    $controls[$case[0]]=@{
        cases=$proof.cases;records=$proof.records;executable_sha256=(Hash $exe);
        native_sha256=(Hash $native);reference_receipt_sha256=(Hash (Join-Path $ref 'receipt.json'))
    }
}
@{
    passed=$true;observed_utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';
    contracts=34;source_manifest=$SourceManifest;products=$products;controls=$controls;
    scope='Original Game Over/menu clocks and MAIN Continue byte-store controls. Explicit consumer/hardware adapters; component only, no audio device.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: actual Windows 34 contracts, Game Over clocks and MAIN Continue file controls.'
