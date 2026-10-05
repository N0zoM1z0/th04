param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$exeDirectory = (Resolve-Path $ExecutableDirectory).ProviderPath
$reference = (Resolve-Path $ReferenceDirectory).ProviderPath
New-Item -ItemType Directory -Force $OutputDirectory | Out-Null
$output = (Resolve-Path $OutputDirectory).ProviderPath
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Hash([string]$path) { return (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant() }
function Run([string]$exe, [string[]]$arguments, [string]$destination) {
    $lines = @(& $exe @arguments)
    if ($LASTEXITCODE -ne 0) { throw "Native executable failed: $exe" }
    [IO.File]::WriteAllText($destination, (($lines -join "`n") + "`n"), $utf8)
}
$receipt = Get-Content -Raw (Join-Path $reference 'receipt.json') | ConvertFrom-Json
if (!$receipt.passed -or $receipt.cases -ne 916 -or $receipt.clock_cases -ne 10) {
    throw 'Original verdict reference is incomplete'
}
foreach ($pair in @(
    @('fixtures.txt', $receipt.fixture_sha256), @('_UDE.TXT', $receipt.commentary_sha256),
    @('original.txt', $receipt.original_sha256), @('clock-original.txt', $receipt.clock_original_sha256)
)) {
    if ((Hash (Join-Path $reference $pair[0])) -ne $pair[1]) { throw "Reference differs: $($pair[0])" }
}
$contracts = @(Get-ChildItem -LiteralPath $exeDirectory -Filter 'th04-port64*contracts.exe' | Sort-Object Name)
if ($contracts.Count -ne 32) { throw "Expected 32 contract executables; found $($contracts.Count)" }
$products = @{}
foreach ($contract in $contracts) {
    Run $contract.FullName @() (Join-Path $output ($contract.BaseName + '.txt'))
    $products[$contract.Name] = Hash $contract.FullName
    Write-Host "PASS $($contract.Name)"
}
$exe = Join-Path $exeDirectory 'th04-port64-cutscene-contracts.exe'
$trace = Join-Path $output 'native.txt'
Run $exe @('--verdict-trace', (Join-Path $reference 'fixtures.txt'), (Join-Path $reference '_UDE.TXT')) $trace
if ((Hash $trace) -ne $receipt.original_sha256) { throw 'Windows verdict requests/state differ' }
$clock = Join-Path $output 'clock-native.txt'
Run $exe @('--verdict-clock', (Join-Path $reference '_UDE.TXT')) $clock
# Palette snapshots are collected after each native scheduler call. Compare
# their clock and tone separately from ordered requests, as the Python Oracle
# does; this changes no timestamps, values, payload bytes or request order.
$groups = New-Object 'System.Collections.Generic.List[object]'
$current = New-Object 'System.Collections.Generic.List[string]'
foreach ($line in [IO.File]::ReadAllLines($clock)) {
    if ($line.StartsWith('CLOCK ') -and $current.Count -gt 0) {
        $groups.Add($current.ToArray())
        $current.Clear()
    }
    $current.Add($line)
}
if ($current.Count -gt 0) { $groups.Add($current.ToArray()) }
$canonical = New-Object 'System.Collections.Generic.List[string]'
foreach ($group in $groups) {
    foreach ($line in $group) { if (!$line.StartsWith('PALETTE ') -and !$line.StartsWith('STOP ')) { $canonical.Add($line) } }
    foreach ($line in $group) { if ($line.StartsWith('PALETTE ')) { $canonical.Add($line) } }
    foreach ($line in $group) { if ($line.StartsWith('STOP ')) { $canonical.Add($line) } }
}
$canonicalPath = Join-Path $output 'clock-native-canonical.txt'
[IO.File]::WriteAllText($canonicalPath, (($canonical.ToArray() -join "`n") + "`n"), $utf8)
if ((Hash $canonicalPath) -ne $receipt.clock_original_sha256) { throw 'Windows verdict input/palette clock differs' }
$result = @{
    passed = $true; cases = 916; clock_cases = 10; contracts = $contracts.Count;
    source_manifest = $receipt.source_manifest;
    executable_sha256 = Hash $exe; products = $products;
    original_sha256 = $receipt.original_sha256; native_sha256 = Hash $trace;
    clock_original_sha256 = $receipt.clock_original_sha256; clock_native_sha256 = Hash $canonicalPath;
    platform = 'Actual Windows AMD64 execution'; utc = [DateTime]::UtcNow.ToString('o')
}
[IO.File]::WriteAllText((Join-Path $output 'receipt.json'), ($result | ConvertTo-Json -Depth 6), $utf8)
Write-Host 'Actual Windows verdict: 916 original state/request cases, 10 input/palette clocks and 32 contracts PASS'
