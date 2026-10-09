param([Parameter(Mandatory=$true)][string]$PlanFile)
$ErrorActionPreference='Stop'
$plan=Get-Content -Raw -LiteralPath $PlanFile | ConvertFrom-Json
if($plan.version -ne 1 -or !$plan.muted) {throw 'Expected a muted version1 host plan.'}
if(Test-Path -LiteralPath $plan.output) {throw 'Use fresh Windows outputs.'}
$out=(New-Item -ItemType Directory -Path $plan.output).FullName
$utf8=New-Object Text.UTF8Encoding($false)
function Hash([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function CheckHash([string]$path,[string]$digest) {
    if((Hash $path) -cne $digest) {throw "Input identity changed: $path"}
}
function Pe64([string]$path) {
    $b=[IO.File]::ReadAllBytes($path)
    if($b.Length -lt 64 -or $b[0] -ne 77 -or $b[1] -ne 90) {throw 'Not MZ/PE.'}
    $at=[BitConverter]::ToInt32($b,60)
    if($at -lt 64 -or $at+26 -gt $b.Length -or [BitConverter]::ToUInt32($b,$at) -ne 17744 -or
       [BitConverter]::ToUInt16($b,$at+4) -ne 34404 -or [BitConverter]::ToUInt16($b,$at+24) -ne 523) {
        throw "Not AMD64 PE32+: $path"
    }
}
function Quote([string]$value) {
    # The plan uses guarded path/flag arguments, never shell command strings.
    if($value -match '["\r\n]' -or $value.EndsWith('\')) {throw 'Unsupported host argument quoting.'}
    return '"'+$value+'"'
}
function Run([string]$name,[string]$executable,$arguments) {
    $info=New-Object Diagnostics.ProcessStartInfo
    $info.FileName=$executable
    $info.Arguments=(@($arguments | ForEach-Object {Quote ([string]$_)}) -join ' ')
    $info.UseShellExecute=$false;$info.CreateNoWindow=$true
    $info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
    $p=New-Object Diagnostics.Process;$p.StartInfo=$info
    if(!$p.Start()) {throw "Cannot launch $name"}
    try {
        $stdout=$p.StandardOutput.ReadToEndAsync();$stderr=$p.StandardError.ReadToEndAsync()
        if(!$p.WaitForExit([int]$plan.timeout_ms)) {throw "Timeout: $name"}
        $text=$stdout.GetAwaiter().GetResult();$errorText=$stderr.GetAwaiter().GetResult()
        [IO.File]::WriteAllText((Join-Path $out ($name+'.stdout.txt')),$text.Replace("`r`n","`n"),$utf8)
        [IO.File]::WriteAllText((Join-Path $out ($name+'.stderr.txt')),$errorText.Replace("`r`n","`n"),$utf8)
        if($p.ExitCode -ne 0) {throw "Exit$($p.ExitCode): $name`: $errorText"}
    } finally {
        if(!$p.HasExited) {$p.Kill();$p.WaitForExit()}
        $p.Dispose()
    }
}
foreach($planInput in $plan.inputs) {CheckHash $planInput.path $planInput.sha256}
$products=@{}
foreach($entry in $plan.products) {
    if($entry.name -notmatch '^th04-port64.*\.exe$') {throw 'Unexpected product name.'}
    $path=Join-Path $plan.executable_directory $entry.name
    CheckHash $path $entry.sha256;Pe64 $path;$products[$entry.name]=$entry.sha256
}
if($products.Count -ne $plan.product_count) {throw 'Incomplete product identity vector.'}
$contracts=@($plan.products | Where-Object {$_.name -like '*contracts.exe'})
if($contracts.Count -ne $plan.contract_count) {throw 'Incomplete contract vector.'}
foreach($entry in $contracts) {
    Run $entry.name (Join-Path $plan.executable_directory $entry.name) @()
    Write-Host "PASS Windows $($entry.name)"
}
$cases=@()
foreach($case in $plan.cases) {
    if(!(@($case.arguments) -contains '--mute')) {throw 'Frontend launch must be explicitly muted.'}
    if($case.phase_file) {[IO.File]::WriteAllText($case.phase_file,([string]$case.phase+"`n"),$utf8)}
    Run $case.name (Join-Path $plan.executable_directory 'th04-port64.exe') $case.arguments
    $files=@(Get-ChildItem -LiteralPath $case.output -Recurse -File)
    if($files.Count -ne @($case.expected.PSObject.Properties).Count) {throw "Unexpected frontend file count: $($case.name)"}
    $digests=@{}
    foreach($file in $files) {
        $relative=$file.FullName.Substring($case.output.Length+1).Replace('\','/')
        $expected=$case.expected.PSObject.Properties[$relative]
        $digest=Hash $file.FullName
        if(!$expected -or $digest -cne $expected.Value) {throw "Frontend differs: $($case.name)/$relative"}
        $digests[$relative]=$digest
    }
    $cases+=@{name=$case.name;files=$digests;reference_receipt_sha256=$case.reference_receipt_sha256}
    Write-Host "PASS Windows frontend $($case.name): $($files.Count) files"
}
$traces=@()
foreach($trace in $plan.traces) {
    if($trace.kind -cnotin @('pmd-fm','pmd-musical-fm','pmd-fm-player','pmd-musical-ssg','pmd-combined','pmd-commands','pmd-rhythm','pmd-timer-player','pmd-clock','pmd-pcm','pmd-resident') -or $trace.name -notmatch '^[A-Za-z0-9_-]+$' -or
       $trace.board -notin @(0,1,2)) {throw 'Unsupported component trace.'}
    $binary=if($trace.kind -ceq 'pmd-fm') {'th04-port64-pmd-fm-contracts.exe'} elseif($trace.kind -ceq 'pmd-musical-fm') {'th04-port64-pmd-musical-fm-contracts.exe'} elseif($trace.kind -ceq 'pmd-musical-ssg') {'th04-port64-pmd-musical-ssg-contracts.exe'} elseif($trace.kind -ceq 'pmd-combined') {'th04-port64-pmd-combined-contracts.exe'} elseif($trace.kind -ceq 'pmd-commands') {'th04-port64-pmd-commands-contracts.exe'} elseif($trace.kind -ceq 'pmd-rhythm') {'th04-port64-pmd-rhythm-contracts.exe'} elseif($trace.kind -ceq 'pmd-timer-player') {'th04-port64-pmd-timer-player-contracts.exe'} elseif($trace.kind -ceq 'pmd-clock') {'th04-port64-pmd-clock-contracts.exe'} elseif($trace.kind -ceq 'pmd-pcm') {'th04-port64-pmd-pcm-contracts.exe'} elseif($trace.kind -ceq 'pmd-resident') {'th04-port64-pmd-resident-contracts.exe'} else {'th04-port64-pmd-fm-player-contracts.exe'}
    if(!$products.ContainsKey($binary)) {throw 'Unattested FM trace product.'}
    $paths=if($trace.kind -ceq 'pmd-resident') {@($trace.resource,$trace.operations,$trace.rom)} else {@($trace.resource,$trace.mirror,$trace.operations)}
    if($trace.kind -cin @('pmd-fm-player','pmd-combined','pmd-commands','pmd-rhythm','pmd-timer-player','pmd-clock','pmd-pcm')) {$paths+=@($trace.effects)}
    if($trace.kind -ceq 'pmd-pcm') {$paths+=@($trace.rom,$trace.installation)}
    foreach($path in $paths) {
        if(!(@($plan.inputs | Where-Object {$_.path -ceq $path}).Count -eq 1)) {
            throw 'Component trace input lacks a unique identity.'
        }
    }
    $target=Join-Path $out ($trace.name+'.trace.txt')
    # This CPU-only component has no audio device or backend. It receives the
    # supplied EFC and explicit IRQ/time operations, without a device backend.
    $arguments=@($trace.resource,([string]$trace.board),$trace.mirror,$trace.operations,$target)
    if($trace.kind -cin @('pmd-fm-player','pmd-combined','pmd-commands','pmd-rhythm','pmd-timer-player','pmd-clock','pmd-pcm')) {
        $arguments=@($trace.resource,$trace.effects,([string]$trace.board),$trace.mirror,$trace.operations,$target)
    }
    if($trace.kind -ceq 'pmd-pcm') {$arguments=@($trace.resource,$trace.effects,([string]$trace.board),$trace.mirror,$trace.operations,$trace.rom,$trace.installation,$target)}
    if($trace.kind -ceq 'pmd-resident') {
        $pcm=Join-Path $out ($trace.name+'.pcm')
        $arguments=@($trace.resource,([string]$trace.board),$trace.rom,$trace.operations,$target,$pcm)
    }
    Run $trace.name (Join-Path $plan.executable_directory $binary) $arguments
    if($trace.kind -ceq 'pmd-resident') {CheckHash $pcm $trace.pcm_sha256}
    CheckHash $target $trace.expected_sha256
    $traceReceipt=@{name=$trace.name;sha256=(Hash $target);rows=$trace.rows;
        reference_receipt_sha256=$trace.reference_receipt_sha256}
    if($trace.kind -ceq 'pmd-resident') {$traceReceipt.pcm_sha256=(Hash $pcm)}
    $traces+= $traceReceipt
    Write-Host "PASS Windows component $($trace.name): $($trace.rows) rows"
}
foreach($planInput in $plan.inputs) {CheckHash $planInput.path $planInput.sha256}
foreach($entry in $plan.products) {CheckHash (Join-Path $plan.executable_directory $entry.name) $entry.sha256}
$receipt=@{
    passed=$true;utc=[DateTime]::UtcNow.ToString('o');host='actual-Windows-AMD64';muted=$true;
    source_manifest=$plan.source_manifest;product_producer_manifest=$plan.product_producer_manifest;
    plan_sha256=(Hash $PlanFile);products=$products;contract_count=$contracts.Count;cases=$cases;traces=$traces;
    os=[Environment]::OSVersion.VersionString;process_64bit=[Environment]::Is64BitProcess;
    powershell=$PSVersionTable.PSVersion.ToString();inputs=$plan.inputs;
    scope='Current Windows components and bounded frontend/storage/restart controls. Actor controls retain their documented limits; no full natural route, complete FM audio, physical timing or historical exactness acceptance.'
}
[IO.File]::WriteAllText((Join-Path $out 'receipt.json'),($receipt | ConvertTo-Json -Depth 15),$utf8)
Write-Host "PASS Windows $($contracts.Count) contracts, $($cases.Count) muted frontend launches and $($traces.Count) component traces"
