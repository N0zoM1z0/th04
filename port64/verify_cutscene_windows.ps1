param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$GalleryDirectory,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
# Run the AMD64 products on actual Windows. The Python oracle separately
# attests the original CPU references; this consumer compares their complete
# request/page/font outputs, without claiming a physical PC-98 capture.
$ErrorActionPreference = 'Stop'
$exeDir = (Resolve-Path -LiteralPath $ExecutableDirectory).ProviderPath
$refs = (Resolve-Path -LiteralPath $ReferenceDirectory).ProviderPath
$gallery = (Resolve-Path -LiteralPath $GalleryDirectory).ProviderPath
$font = (Resolve-Path -LiteralPath $FontBitmap).ProviderPath
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Use a new output directory.' }
$out = (New-Item -ItemType Directory -Path $OutputDirectory).FullName
$exe = Join-Path $exeDir 'th04-port64-cutscene-contracts.exe'
$cases = (Get-Content -Raw -LiteralPath (Join-Path $refs 'receipt.json') | ConvertFrom-Json).cases
if ($cases.Count -ne 72) { throw 'The original control reference is incomplete.' }
$contracts = @()
foreach ($program in Get-ChildItem -LiteralPath $exeDir -Filter '*contracts.exe') {
    $lines = @(& $program.FullName 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Contract failed: $($program.Name): $lines" }
    $contracts += @{ name=$program.Name; sha256=(Get-FileHash -LiteralPath $program.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
}
if ($contracts.Count -ne 34) { throw 'Expected thirty-four native contracts.' }
Write-Host 'PASS: 34 native AMD64 contracts.'
for ($i=0; $i -lt $cases.Count; $i++) {
    $inputFile = Join-Path $refs ('{0:d3}.txt' -f $i)
    $expected = (Get-Content -Raw -LiteralPath (Join-Path $refs ('{0:d3}-trace.txt' -f $i))) -replace "`r", ''
    $lines = @(& $exe --trace $inputFile ($cases[$i].held) 2>&1)
    if ($LASTEXITCODE -ne 0 -or (($lines -join "`n").TrimEnd() -cne $expected.TrimEnd())) { throw "Script trace $i differs." }
    $lines | Set-Content -LiteralPath (Join-Path $out ('{0:d3}-trace.txt' -f $i)) -Encoding UTF8
}
Write-Host 'PASS: 72 original script request streams.'
function Compare-Bytes([string]$actual, [string]$reference) {
    $hash = (Get-FileHash -LiteralPath $actual -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -cne (Get-FileHash -LiteralPath $reference -Algorithm SHA256).Hash.ToLowerInvariant()) { throw "Byte comparison failed: $actual" }
    return $hash
}
$assets = Join-Path $gallery 'assets'
$decodes = @{}
foreach ($picture in Get-ChildItem -LiteralPath $assets -Filter '*.PI') {
    $decoded = Join-Path $out ($picture.Name + '.raw')
    & $exe --decode $picture.FullName $decoded
    if ($LASTEXITCODE -ne 0) { throw 'PI decode failed.' }
    $decodes[$picture.Name] = Compare-Bytes $decoded (Join-Path $assets ($picture.Name + '.raw'))
}
if ($decodes.Count -ne 17) { throw 'Expected seventeen Ending pictures.' }
$matrix = (New-Item -ItemType Directory -Path (Join-Path $out 'font-controls')).FullName
& $exe --glyphs $font (Join-Path $gallery 'font-controls/fixtures.txt') $matrix
if ($LASTEXITCODE -ne 0) { throw 'Graphics font controls failed.' }
$fontHashes = @{}
foreach ($frame in Get-ChildItem -LiteralPath $matrix -Filter '*.bin') {
    $fontHashes[$frame.Name] = Compare-Bytes $frame.FullName (Join-Path $gallery ('font-controls/' + $frame.Name))
}
if ($fontHashes.Count -ne 264) { throw 'Expected264 complete graphics font controls.' }
$pages = @{}
$palette = @{}
foreach ($script in Get-ChildItem -LiteralPath $assets -Filter '_ED*.TXT') {
    $route = (New-Item -ItemType Directory -Path (Join-Path $out $script.Name)).FullName
    $reference = Join-Path $gallery $script.Name
    & $exe --render $assets $script.Name 0 $font (Join-Path $reference 'checkpoints.txt') $route
    if ($LASTEXITCODE -ne 0) { throw "Ending render failed: $($script.Name)" }
    $state = (Get-Content -Raw -LiteralPath (Join-Path $route 'states.txt')) -replace "`r", ''
    $want = (Get-Content -Raw -LiteralPath (Join-Path $reference 'states.txt')) -replace "`r", ''
    if ($state -cne $want) { throw 'Ending page selection, scroll or palette clock differs.' }
    foreach ($frame in Get-ChildItem -LiteralPath $route -Filter '*.bin') {
        $pages[$script.Name + '/' + $frame.Name] = Compare-Bytes $frame.FullName (Join-Path $reference $frame.Name)
    }
    foreach ($frame in Get-ChildItem -LiteralPath $route -Filter '*.pal') {
        $palette[$script.Name + '/' + $frame.Name] = Compare-Bytes $frame.FullName (Join-Path $reference $frame.Name)
    }
}
if ($pages.Count -ne 192 -or $palette.Count -ne 96) { throw 'Ending gallery is incomplete.' }
@{
    passed=$true; observed_utc=[DateTime]::UtcNow.ToString('o'); platform='actual Windows AMD64'
    contracts=$contracts; cases=$cases.Count; pages=$pages; palettes=$palette; pi_decodes=$decodes; font_controls=$fontHashes
    font_sha256=(Get-FileHash -LiteralPath $font -Algorithm SHA256).Hash.ToLowerInvariant()
    original_reference_sha256=(Get-FileHash -LiteralPath (Join-Path $refs 'receipt.json') -Algorithm SHA256).Hash.ToLowerInvariant()
    original_gallery_sha256=(Get-FileHash -LiteralPath (Join-Path $gallery 'receipt.json') -Algorithm SHA256).Hash.ToLowerInvariant()
    limits='Component execution: original references use consumer adapters. No audio, staff roll, score registration, whole-game or DOS exact claim.'
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: eight Endings,192 complete pages,96 palettes,264 font controls and17 PI decodes.'
