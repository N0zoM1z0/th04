param([Parameter(Mandatory=$true)][string]$Plan)
$ErrorActionPreference = 'Stop'
$p = Get-Content -LiteralPath $Plan -Raw | ConvertFrom-Json
if ($p.version -ne 1 -or !$p.muted) { throw 'A muted version 1 plan is required.' }
if (Test-Path -LiteralPath $p.output) { throw 'Use a fresh output directory.' }
$controller = Join-Path $PSScriptRoot 'windows_background_controller.cs'
function Hash([string]$path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
$builds = @{
    '8257fbf8e952690ab8963844ba92f810399f9f67ca74db463ca006aaf3fbe750' = @{ iat=3308920; life=0; death=2797664 }
    '8a178d24c284e1703c4ffa71e0b68c4a4f0845481604b7e2655dae16c9752940' = @{ iat=3308920; life=0; death=2797664 }
    'c0d1ca7deaa6a22697fa3926dd1218c08a6b3a88efded89255b04945365b8adc' = @{ iat=3313016; life=0; death=2801760 }
    '2dfd38e8eafefde4f0f428633c6dc3c31c1dd1ca6ff1211bfedc8d6d37f2e4a2' = @{ iat=3313016; life=0; death=2801760 }
    '1b43c12e2f090daf0053576974571db9ea6c75a49eff1f6d085d9b3b8d920c7a' = @{ iat=0; life=0 }
    'ebb25a2bd91c6569030413def7c16f2de2469e2907d20fdcd9ee1545511a9be5' = @{ iat=0; life=0 }
    '22554b6500ceaa23986afe2cecde501acc3172b4e343b0e7d217930943051073' = @{ iat=3308920; life=0 }
    '768c429a899fcf00253dbfae9b3e61dbb49ee69475370086d29825d288a68a6b' = @{ iat=3308920; life=0 }
    'eaa05bdde3c21f702df7b6d9885aa78813216a18449d34e56b296f85fe437e3a' = @{ iat=3304824; life=916432 }
    '55dbe34d1edcf8b28b5d369c2b5ee686a346019c3ae698398aa5f718fe7d5d51' = @{ iat=3304824; life=916432 }
    'c11f516a7f7421274b9622388829665c40ce4fe958e260b68a44c961fa2efc13' = @{ iat=3300728; life=913744 }
    'b7aabad98c193ed1a425e5126bfa01a721b7f8f3dfa7949641b6270bd3493015' = @{ iat=3296560; life=910384 }
    'ad4b09d4671da41f3008c7d895f0fe43d1b541a3bbc790d122b6a53168fb8ca2' = @{ iat=3300728; life=910960 }
}
$candidate = Hash $p.exe
if (!$builds.ContainsKey($candidate)) { throw 'Unsupported candidate; never attach to an original game.' }
$build = $builds[$candidate]
if ((Hash $controller) -cne $p.controller_sha256) { throw 'Controller identity differs.' }
if (($p.mode -eq 'hook' -or $p.mode -eq 'music-room' -or $p.mode -like 'ui-*') -and $p.hook_iat_rva -ne $build.iat) { throw 'Unexpected foreground import.' }
foreach ($item in $p.inputs) {
    if ((Hash $item.path) -cne $item.sha256) { throw "Input identity differs: $($item.path)" }
}
if ($p.mode -eq 'ui-registration') { $env:TH04_UI_TEST_SCENE='registration' }
elseif ($p.mode -eq 'ui-ending') { $env:TH04_UI_TEST_SCENE='ending' }
else { Remove-Item Env:TH04_UI_TEST_SCENE -ErrorAction SilentlyContinue }
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition (Get-Content -LiteralPath $controller -Raw)
[Th04BackgroundController]::SetLifePatchRva([uint32]$build.life)
[Th04BackgroundController]::SetNoDeathRva([uint32]$build.death)
if ($p.pmd_driver -eq 'pmd86' -or $p.pmd_driver -eq 'pmdb2') {
    if ((Hash $p.opna_rom) -cne '53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8') { throw 'Unexpected OPNA ROM.' }
}
[Th04BackgroundController]::SetSoundProfile([string]$p.pmd_driver, [string]$p.opna_rom)
if ($p.cases) {
    [IO.Directory]::CreateDirectory($p.output) | Out-Null
    $prefix = [IO.Path]::GetFullPath($p.output).TrimEnd('\') + '\'
    foreach ($case in $p.cases) {
        if (![IO.Path]::GetFullPath($case.output).StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Case outputs must stay inside the owned suite directory.'
        }
        if (Test-Path -LiteralPath $case.output) { throw 'Case output already exists.' }
        [Th04BackgroundController]::Run($p.exe, $p.hdi, $p.font, $case.output,
            [string]$case.mode, [uint32]$p.hook_iat_rva, [bool]$p.no_life_loss,
            [string]$case.route_plan, [string]$case.initial_score)
        Write-Host "PASS $($case.mode)"
    }
} else {
    [Th04BackgroundController]::Run($p.exe, $p.hdi, $p.font, $p.output,
        [string]$p.mode, [uint32]$p.hook_iat_rva, [bool]$p.no_life_loss,
        [string]$p.route_plan, [string]$p.initial_score)
}
foreach ($item in $p.inputs) {
    if ((Hash $item.path) -cne $item.sha256) { throw "Final input differs: $($item.path)" }
}
if ((Hash $p.exe) -cne $candidate) { throw 'Candidate file changed.' }
@{
    passed = $true; host = 'actual-Windows-x64'; muted = $true
    pmd_driver = [string]$p.pmd_driver; opna_rom = [string]$p.opna_rom
    no_life_loss = [bool]$p.no_life_loss; cases = $p.cases; inputs = $p.inputs
    controller_sha256 = (Hash $controller); plan_sha256 = (Hash $Plan)
    scope = 'Owned inactive desktop; process-local input adapter and optional no-life-loss patch. Functional tests; no physical input/audio, difficulty/balance or DOS parity acceptance.'
} | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $p.output 'receipt.json')
