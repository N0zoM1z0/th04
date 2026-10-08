param(
    [Parameter(Mandatory=$true)][string]$ExecutableDirectory,
    [Parameter(Mandatory=$true)][string]$ControlReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$RouteReferenceDirectory,
    [Parameter(Mandatory=$true)][string]$Hdi,
    [Parameter(Mandatory=$true)][string]$FontBitmap,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [string]$StaffDirectory,
    [string]$VerdictDirectory,
    [string]$CongratulationsDirectory
)
# Actual Windows consumer of independently checked GNU/original CPU receipts.
# The Python consumer verifies the resulting complete indexed/RGB frames again.
$ErrorActionPreference = 'Stop'
$exeDir = (Resolve-Path -LiteralPath $ExecutableDirectory).ProviderPath
$control = (Resolve-Path -LiteralPath $ControlReferenceDirectory).ProviderPath
$routes = (Resolve-Path -LiteralPath $RouteReferenceDirectory).ProviderPath
$hdiFile = (Resolve-Path -LiteralPath $Hdi).ProviderPath
$font = (Resolve-Path -LiteralPath $FontBitmap).ProviderPath
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Use a new output directory.' }
$out = (New-Item -ItemType Directory -Path $OutputDirectory).FullName
$routeOut = (New-Item -ItemType Directory -Path (Join-Path $out 'routes')).FullName
$exe = Join-Path $exeDir 'th04-port64-cutscene-contracts.exe'
$main = Join-Path $exeDir 'th04-port64.exe'
$controlReceipt = Get-Content -Raw -LiteralPath (Join-Path $control 'receipt.json') | ConvertFrom-Json
$routeReceipt = Get-Content -Raw -LiteralPath (Join-Path $routes 'receipt.json') | ConvertFrom-Json
if (!$controlReceipt.passed -or !$routeReceipt.passed -or $routeReceipt.natural_routes -ne 24) {
    throw 'Reference controls/routes are incomplete.'
}
$contracts = @()
foreach ($program in Get-ChildItem -LiteralPath $exeDir -Filter '*contracts.exe') {
    $lines = @(& $program.FullName 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Contract failed: $($program.Name): $lines" }
    $contracts += @{ name=$program.Name; sha256=(Get-FileHash -LiteralPath $program.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
}
if ($contracts.Count -ne 34) { throw 'Expected thirty-four native contracts.' }
Write-Host 'PASS: 34 native AMD64 contracts.'
foreach ($kind in @('handoff', 'frame', 'fade')) {
    $expected = (Get-Content -Raw -LiteralPath (Join-Path $control ($kind+'-trace.txt'))) -replace "`r", ''
    if ($kind -eq 'fade') { $lines = @(& $exe --fade 2>&1) }
    else {
        $option = if ($kind -eq 'frame') { '--frames' } else { '--handoff' }
        $lines = @(& $exe $option (Join-Path $control ($kind+'-fixtures.txt')) 2>&1)
    }
    if ($LASTEXITCODE -ne 0 -or (($lines -join "`n").TrimEnd() -cne $expected.TrimEnd())) {
        throw "Original $kind controls differ."
    }
    $lines | Set-Content -LiteralPath (Join-Path $out ($kind+'-trace.txt')) -Encoding UTF8
}
Write-Host 'PASS: original resident copies, frame counters and 273-refresh fade.'
if ($StaffDirectory) {
    $staff = (Resolve-Path -LiteralPath $StaffDirectory).ProviderPath
    $staffReceipt = Get-Content -Raw -LiteralPath (Join-Path $staff 'receipt.json') | ConvertFrom-Json
    if (!$staffReceipt.passed -or $staffReceipt.cases.Count -ne 8 -or $staffReceipt.kernel_controls.Count -lt 240) {
        throw 'Original Staff Roll controls are incomplete.'
    }
    $assets = Join-Path $staff 'assets'
    foreach ($case in $staffReceipt.cases) {
        $trace = Join-Path $staff ('trace-{0:x}-{1}.txt' -f $case.load,$case.angle)
        $expected = (Get-Content -Raw -LiteralPath $trace) -replace "`r", ''
        $actual = @(& $exe --staff-trace $assets $case.angle 2>&1)
        if ($LASTEXITCODE -ne 0 -or (($actual -join "`n").TrimEnd() -cne $expected.TrimEnd())) {
            throw 'Original Staff Roll request stream differs.'
        }
    }
    foreach ($kind in @('pages','kernels')) {
        $destination = (New-Item -ItemType Directory -Path (Join-Path $out ('staff-'+$kind))).FullName
        if ($kind -eq 'pages') { & $exe --staff-render $assets (Join-Path $staff 'checkpoints.txt') $destination }
        else { & $exe --staff-kernels $assets (Join-Path $staff 'kernel-fixtures.txt') $destination }
        if ($LASTEXITCODE -ne 0) { throw 'Staff Roll renderer/kernel consumer failed.' }
        # Restored reference pages may retain their lossless .gz archives.
        # Compare the renderer's actual outputs, not the archive siblings.
        $referenceFiles = @(Get-ChildItem -LiteralPath (Join-Path $staff $kind) -File | Where-Object { $_.Extension -in @('.bin', '.pal', '.txt') })
        $expectedFiles = if ($kind -eq 'pages') { 499 } else { 268 }
        if ($referenceFiles.Count -ne $expectedFiles) { throw 'Restore all Staff Roll reference files before comparison.' }
        foreach ($file in $referenceFiles) {
            $actual = Join-Path $destination $file.Name
            if ($file.Extension -eq '.txt') {
                $actualText = (Get-Content -Raw -LiteralPath $actual) -replace "`r", ''
                $expectedText = (Get-Content -Raw -LiteralPath $file.FullName) -replace "`r", ''
                if ($actualText -cne $expectedText) { throw 'Staff Roll state differs.' }
            } else {
                if ((Get-FileHash -LiteralPath $actual -Algorithm SHA256).Hash -cne
                    (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash) { throw 'Staff Roll graphics differ.' }
            }
        }
    }
    Write-Host 'PASS: eight original Staff Roll request controls and complete graphics/kernel outputs.'
}
if ($VerdictDirectory) {
    $verdict = (Resolve-Path -LiteralPath $VerdictDirectory).ProviderPath
    $verdictReceipt = Get-Content -Raw -LiteralPath (Join-Path $verdict 'receipt.json') | ConvertFrom-Json
    if (!$verdictReceipt.passed -or $verdictReceipt.cases.Count -ne 80 -or $verdictReceipt.complete_pages -ne 160) {
        throw 'Original verdict graphics are incomplete.'
    }
    $destination = (New-Item -ItemType Directory -Path (Join-Path $out 'verdict-pages')).FullName
    & $exe --verdict-render (Join-Path $verdict 'assets') $font (Join-Path $verdict 'fixtures.txt') $destination
    if ($LASTEXITCODE -ne 0) { throw 'Verdict renderer failed.' }
    foreach ($file in Get-ChildItem -LiteralPath (Join-Path $verdict 'pages') -File) {
        $actual = Join-Path $destination $file.Name
        if ($file.Extension -eq '.txt') {
            if (((Get-Content -Raw -LiteralPath $actual) -replace "`r", '') -cne
                ((Get-Content -Raw -LiteralPath $file.FullName) -replace "`r", '')) { throw 'Verdict state differs.' }
        } elseif ((Get-FileHash -LiteralPath $actual -Algorithm SHA256).Hash -cne
                  (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash) { throw 'Verdict page differs.' }
    }
    Write-Host 'PASS: 80 original verdict graphics cases and 160 complete pages.'
}
if ($CongratulationsDirectory) {
    $congratulations = (Resolve-Path -LiteralPath $CongratulationsDirectory).ProviderPath
    $congratulationsReceipt = Get-Content -Raw -LiteralPath (Join-Path $congratulations 'receipt.json') | ConvertFrom-Json
    if (!$congratulationsReceipt.passed -or $congratulationsReceipt.complete_pages -ne 20 -or $congratulationsReceipt.clock_controls -ne 50) {
        throw 'Original congratulations controls are incomplete.'
    }
    # The component emits ordered requests, then palette samples/STOP inside
    # each clock group. Preserve all values and reorder only these observations
    # exactly as canonical_clock does in the independent Python Oracle.
    $lines = @(& $exe --congratulations-trace 2>&1)
    if ($LASTEXITCODE -ne 0) { throw 'Congratulations clock consumer failed.' }
    $groups = New-Object 'System.Collections.Generic.List[object]'
    $current = New-Object 'System.Collections.Generic.List[string]'
    foreach ($line in $lines) {
        if ($line.StartsWith('CLOCK ') -and $current.Count -gt 0) { $groups.Add($current.ToArray()); $current.Clear() }
        $current.Add($line)
    }
    if ($current.Count -gt 0) { $groups.Add($current.ToArray()) }
    $canonical = New-Object 'System.Collections.Generic.List[string]'
    foreach ($group in $groups) {
        foreach ($line in $group) { if (!$line.StartsWith('PALETTE ') -and !$line.StartsWith('STOP ')) { $canonical.Add($line) } }
        foreach ($line in $group) { if ($line.StartsWith('PALETTE ')) { $canonical.Add($line) } }
        foreach ($line in $group) { if ($line.StartsWith('STOP ')) { $canonical.Add($line) } }
    }
    $expected = (Get-Content -Raw -LiteralPath (Join-Path $congratulations 'native.txt')) -replace "`r", ''
    if (($lines -join "`n").TrimEnd() -cne $expected.TrimEnd()) { throw 'Congratulations requests/clock differ from accepted GNU.' }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText((Join-Path $out 'congratulations-native-canonical.txt'), (($canonical.ToArray() -join "`n") + "`n"), $utf8)
    if ((Get-FileHash -LiteralPath (Join-Path $out 'congratulations-native-canonical.txt') -Algorithm SHA256).Hash.ToLowerInvariant() -cne
        $congratulationsReceipt.native_canonical_sha256) { throw 'Canonical original congratulations clock differs.' }
    $destination = (New-Item -ItemType Directory -Path (Join-Path $out 'congratulations-pages')).FullName
    & $exe --congratulations-render (Join-Path $congratulations 'assets') $font $destination
    if ($LASTEXITCODE -ne 0) { throw 'Congratulations renderer failed.' }
    $referenceFiles = @(Get-ChildItem -LiteralPath (Join-Path $congratulations 'pages') -File | Where-Object { $_.Extension -in @('.bin', '.pal', '.txt') })
    if ($referenceFiles.Count -ne 31) { throw 'Expected twenty pages, ten palettes and one state file.' }
    foreach ($file in $referenceFiles) {
        $actual = Join-Path $destination $file.Name
        if ($file.Extension -eq '.txt') {
            if (((Get-Content -Raw -LiteralPath $actual) -replace "`r", '') -cne
                ((Get-Content -Raw -LiteralPath $file.FullName) -replace "`r", '')) { throw 'Congratulations page state differs.' }
        } elseif ((Get-FileHash -LiteralPath $actual -Algorithm SHA256).Hash -cne
                  (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash) { throw 'Congratulations page/palette differs.' }
    }
    Write-Host 'PASS: 50 original congratulations clocks and 20 complete pages.'
}
Get-ChildItem -LiteralPath $routes -Filter '*-checkpoints.txt' | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $routeOut $_.Name)
}
Write-Host 'Running 24 natural MAIN-to-MAINE Ending routes...'
$lines = @(& $main --hdi $hdiFile --font-bmp $font --ending-screenshots $routeOut 2>&1)
if ($LASTEXITCODE -ne 0) { throw "Ending routes failed: $lines" }
$lines | Set-Content -LiteralPath (Join-Path $out 'routes.log') -Encoding UTF8
$actualRoutes = @($lines | Where-Object { "$_" -like 'MAINE Ending route=*' })
$expectedRoutes = @(Get-Content -LiteralPath (Join-Path $routes 'stdout.log') | Where-Object { $_ -like 'MAINE Ending route=*' })
if ($actualRoutes.Count -ne 24 -or ($actualRoutes -join "`n") -cne ($expectedRoutes -join "`n")) {
    throw 'Natural Ending counters differ from GNU.'
}
$files = @()
foreach ($file in Get-ChildItem -LiteralPath $routes -File) {
    if ($file.Extension -notin @('.bin', '.pal', '.bmp') -and $file.Name -notlike '*-states.txt') { continue }
    $actual = Join-Path $routeOut $file.Name
    if (!(Test-Path -LiteralPath $actual)) { throw "Missing Ending frame: $($file.Name)" }
    $expectedHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $actualHash = (Get-FileHash -LiteralPath $actual -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($file.Extension -eq '.txt') {
        # Native Windows text streams write CRLF; compare the integer state
        # records while keeping binary page/palette/BMP hashes strict.
        $expectedText = (Get-Content -Raw -LiteralPath $file.FullName) -replace "`r", ''
        $actualText = (Get-Content -Raw -LiteralPath $actual) -replace "`r", ''
        if ($actualText -cne $expectedText) { throw "Ending state differs: $($file.Name)" }
    } elseif ($actualHash -cne $expectedHash) { throw "Ending frame differs: $($file.Name)" }
    $files += @{ name=$file.Name; sha256=$actualHash }
}
if ($StaffDirectory) {
    $staffRoutes = @($lines | Where-Object { "$_" -like 'MAINE Staff Roll route=*' })
    $expectedStaffRoutes = @(Get-Content -LiteralPath (Join-Path $routes 'stdout.log') | Where-Object { $_ -like 'MAINE Staff Roll route=*' })
    if ($staffRoutes.Count -ne 24 -or ($staffRoutes -join "`n") -cne ($expectedStaffRoutes -join "`n")) { throw 'Staff Roll route state differs.' }
}
if ($VerdictDirectory) {
    $actualVerdicts = @($lines | Where-Object { "$_" -like 'MAINE Verdict route=*' })
    $expectedVerdicts = @(Get-Content -LiteralPath (Join-Path $routes 'stdout.log') | Where-Object { $_ -like 'MAINE Verdict route=*' })
    if ($actualVerdicts.Count -ne 24 -or ($actualVerdicts -join "`n") -cne ($expectedVerdicts -join "`n")) { throw 'Verdict route state differs.' }
}
if ($CongratulationsDirectory) {
    $actualCongratulations = @($lines | Where-Object { "$_" -like 'MAINE Congratulations route=*' })
    $expectedCongratulations = @(Get-Content -LiteralPath (Join-Path $routes 'stdout.log') | Where-Object { $_ -like 'MAINE Congratulations route=*' })
    if ($actualCongratulations.Count -ne 24 -or ($actualCongratulations -join "`n") -cne ($expectedCongratulations -join "`n")) { throw 'Congratulations registration-entry state differs.' }
}
$expectedCount = if ($CongratulationsDirectory) { 1440 } elseif ($VerdictDirectory) { 1344 } elseif ($StaffDirectory) { 1248 } else { 1176 }
if ($files.Count -ne $expectedCount) { throw 'Incomplete page/palette/RGB/state comparisons.' }
$receipt = @{
    passed=$true; observed_utc=[DateTime]::UtcNow.ToString('o'); host='actual-Windows-AMD64';
    contracts=$contracts; natural_routes=24; compared_files=$files;
    source_manifest_sha256=$routeReceipt.source_manifest_sha256;
    executable_sha256=(Get-FileHash -LiteralPath $main -Algorithm SHA256).Hash.ToLowerInvariant();
    control_executable_sha256=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant();
    reference_receipt_sha256=(Get-FileHash -LiteralPath (Join-Path $routes 'receipt.json') -Algorithm SHA256).Hash.ToLowerInvariant();
    staff_control_cases=$(if ($StaffDirectory) { 8 } else { 0 });
    staff_kernel_cases=$(if ($StaffDirectory) { $staffReceipt.kernel_controls.Count } else { 0 });
    staff_routes=$(if ($StaffDirectory) { 24 } else { 0 });
    verdict_graphics_cases=$(if ($VerdictDirectory) { 80 } else { 0 });
    verdict_routes=$(if ($VerdictDirectory) { 24 } else { 0 });
    congratulations_routes=$(if ($CongratulationsDirectory) { 24 } else { 0 });
    congratulations_clock_cases=$(if ($CongratulationsDirectory) { 50 } else { 0 });
    scope='Actual Windows consumer of original/GNU controls; natural MAIN-to-MAINE Ending and optional Staff Roll/verdict/congratulations graphics and registration-entry delay. No physical PC-98 capture, audio synthesis or saved-score claim.'
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'receipt.json') -Encoding UTF8
Write-Host 'PASS: 24 routes, 576 complete indexed pages, 288 palettes and 288 RGB frames.'
