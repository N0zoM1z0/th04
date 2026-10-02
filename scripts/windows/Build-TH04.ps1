param(
    [string]$RepoPath = '@REPO_PATH@',
    [switch]$CheckOnly,
    [switch]$Launch,
    [switch]$Cold
)

$ErrorActionPreference = 'Stop'
$PackagePath = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildDir = '.analysis/build/th04-invincible'

function Invoke-TH04Step {
    param([string]$Label, [string[]]$Arguments, [switch]$Brief)
    Write-Host "`n$Label" -ForegroundColor Cyan
    $ErrorLog = Join-Path $env:TEMP ('th04-build-' + [guid]::NewGuid().ToString('N') + '.log')
    $OutputLog = Join-Path $env:TEMP ('th04-build-' + [guid]::NewGuid().ToString('N') + '.out')
    $PreviousErrorAction = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        if ($Brief) {
            & wsl.exe --cd $RepoPath --exec @Arguments > $OutputLog 2> $ErrorLog
        } else {
            & wsl.exe --cd $RepoPath --exec @Arguments 2> $ErrorLog
        }
        $StepExit = $LASTEXITCODE
        $ErrorActionPreference = $PreviousErrorAction
        if ($StepExit -ne 0) {
            if ($Brief) { Get-Content $OutputLog | Write-Host }
            Get-Content $ErrorLog | Write-Host
            throw "$Label failed with exit code $StepExit."
        }
        if ($Brief) {
            $Pass = Select-String -Path $OutputLog -Pattern '^preflight: PASS$' -Quiet
            if (-not $Pass) { throw "$Label did not report a preflight pass." }
            Write-Host 'Target identity and repository preflight: PASS' -ForegroundColor Green
        }
    } finally {
        $ErrorActionPreference = $PreviousErrorAction
        Remove-Item $ErrorLog -ErrorAction SilentlyContinue
        Remove-Item $OutputLog -ErrorAction SilentlyContinue
    }
}

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw 'Windows Subsystem for Linux is required for the attested 16-bit toolchain.'
}

Write-Host 'TH04 Reconstruction | Windows source build' -ForegroundColor Green
Write-Host 'Sources: src/main, src/op, src/maine, src/zun, src/shared'
Write-Host 'Tools: attested Turbo C++ 4.0J, TASM, TLINK, and DIET'
Write-Host 'Mode: invincible gameplay test build; the original game data is preserved'
if ($Cold) { Write-Host 'Build: complete cold source build' }
else { Write-Host 'Build: verified incremental source build (cold on first run)' }
Write-Host "Repository: $RepoPath"
Write-Host "Package: $PackagePath"

Invoke-TH04Step '1/3  Verify targets and build environment' @(
    'python3', 'scripts/preflight.py'
) -Brief
if ($CheckOnly) {
    Write-Host "`nBuild environment: READY" -ForegroundColor Green
    exit 0
}

if (Get-Process -Name 'DOSBox-X' -ErrorAction SilentlyContinue) {
    throw 'Close DOSBox-X before rebuilding the playable image.'
}

$PreviousErrorAction = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$PackageLinux = (& wsl.exe --exec wslpath -a -u $PackagePath 2>$null).Trim()
$ErrorActionPreference = $PreviousErrorAction
if ($LASTEXITCODE -ne 0 -or -not $PackageLinux) {
    throw 'Could not resolve the Windows package path in WSL.'
}

$BuildArgs = @('python3', 'scripts/build.py', '--invincible-main', '--progress',
               '--output-dir', $BuildDir)
$ExistingReceipt = Join-Path $PackagePath 'package.json'
if (-not $Cold -and (Test-Path $ExistingReceipt)) {
    $BuildArgs += @('--incremental-from', ($PackageLinux + '/package.json'))
}
Invoke-TH04Step '2/3  Compile, assemble, link, and audit four source products' $BuildArgs
Invoke-TH04Step '3/3  Verify executables and refresh the saved Windows image' @(
    'python3', 'scripts/export_windows_play.py', '--update',
    '--build-dir', $BuildDir, '--output-dir', $PackageLinux
)

Write-Host "`nTH04 source build: PASS" -ForegroundColor Green
Write-Host "Playable package: $PackagePath"
Write-Host 'Launch with start-th04.bat.'
if ($Launch) {
    Start-Process -FilePath (Join-Path $PackagePath 'start-th04.bat')
}
