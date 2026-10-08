param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$executables = (Resolve-Path -LiteralPath $ExecutableDirectory).ProviderPath
$reference = (Resolve-Path -LiteralPath $ReferenceDirectory).ProviderPath
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Use a new output directory.' }
$out = (New-Item -ItemType Directory -Path $OutputDirectory).FullName
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Hash([string]$path) { return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
$proof = Get-Content -Raw -LiteralPath (Join-Path $reference 'receipt.json') | ConvertFrom-Json
if (!$proof.passed -or $proof.cases -lt 1000 -or $proof.load_segments.Count -ne 2) { throw 'Original score-file reference is incomplete.' }
foreach ($pair in @(@('fixtures.txt',$proof.fixture_sha256),@('original.txt',$proof.original_sha256))) {
    if ((Hash (Join-Path $reference $pair[0])) -cne $pair[1]) { throw 'Original reference bytes changed.' }
}
$contracts = @(Get-ChildItem -LiteralPath $executables -Filter '*contracts.exe' | Sort-Object Name)
if ($contracts.Count -ne 34) { throw 'Expected 34 native contract executables.' }
$products = @{}
$completed = 0
foreach ($contract in $contracts) {
    Write-Progress -Activity 'TH04 native x64 score-file verification' -Status $contract.Name -PercentComplete (100*$completed/35)
    $lines = @(& $contract.FullName 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Native contract failed: $($contract.Name): $lines" }
    [IO.File]::WriteAllText((Join-Path $out ($contract.BaseName+'.txt')), (($lines -join "`n")+"`n"), $utf8)
    $products[$contract.Name] = Hash $contract.FullName
    $completed++
    Write-Host "PASS [$completed/35] $($contract.Name)"
}
Write-Progress -Activity 'TH04 native x64 score-file verification' -Status 'Original cipher, files and ranking differential' -PercentComplete (100*34/35)
$exe = Join-Path $executables 'th04-port64-score-file-contracts.exe'
$lines = @(& $exe --trace (Join-Path $reference 'fixtures.txt') 2>&1)
if ($LASTEXITCODE -ne 0) { throw 'Native score-file differential failed.' }
$trace = Join-Path $out 'native.txt'
[IO.File]::WriteAllText($trace, (($lines -join "`n")+"`n"), $utf8)
if ((Hash $trace) -cne $proof.original_sha256) { throw 'Complete score file/work/RNG/I-O/ranking outputs differ.' }
$receipt = @{
    passed=$true; observed_utc=[DateTime]::UtcNow.ToString('o'); host='actual-Windows-AMD64';
    cases=$proof.cases; contracts=34; source_manifest=$proof.source_manifest;
    executable_sha256=(Hash $exe); native_sha256=(Hash $trace); products=$products;
    reference_receipt_sha256=(Hash (Join-Path $reference 'receipt.json'));
    scope='Original-instruction score-file reference consumer. Success-only guarded byte-store file adapters; no registration GUI, host score persistence or DOS exactness claim.'
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Progress -Activity 'TH04 native x64 score-file verification' -Completed
Write-Host "PASS [35/35] $($proof.cases) original score-file controls."
