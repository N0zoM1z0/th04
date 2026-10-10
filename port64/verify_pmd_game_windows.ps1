param([Parameter(Mandatory=$true)][string]$PlanFile)
$ErrorActionPreference='Stop'
$plan=Get-Content -Raw -LiteralPath $PlanFile | ConvertFrom-Json
function Hash([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
$planHash=Hash $PlanFile
foreach($e in $plan.inputs){if((Hash $e.path) -cne $e.sha256){throw ('Input changed: '+$e.path)}}
$pe=[IO.File]::ReadAllBytes($plan.binary);$offset=[BitConverter]::ToInt32($pe,60)
if($pe[0] -ne 77 -or $pe[1] -ne 90 -or [BitConverter]::ToUInt32($pe,$offset) -ne 17744 -or [BitConverter]::ToUInt16($pe,$offset+4) -ne 34404 -or [BitConverter]::ToUInt16($pe,$offset+24) -ne 523){throw 'Expected AMD64 PE32+'}
if(Test-Path -LiteralPath $plan.output){throw 'Use a fresh output'}
$out=(New-Item -ItemType Directory -Path $plan.output).FullName;$utf8=New-Object Text.UTF8Encoding($false);$records=@()
foreach($c in $plan.cases){
 $raw=Join-Path $out 'current.txt'
 $args='"'+$c.music+'" "'+$c.effects+'" '+$c.board+' "'+$c.mirror+'" "'+$c.operations+'" "'+$raw+'"'
 $info=New-Object Diagnostics.ProcessStartInfo;$info.FileName=$plan.binary;$info.Arguments=$args;$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
 $p=New-Object Diagnostics.Process;$p.StartInfo=$info;$started=$false
 try {
  $started=$p.Start();if(!$started){throw 'Cannot start full-song component'}
  $stdout=$p.StandardOutput.ReadToEndAsync();$stderr=$p.StandardError.ReadToEndAsync()
  if(!$p.WaitForExit(300000)){throw 'Full-song component timeout'}
  $text=$stdout.GetAwaiter().GetResult();$errorText=$stderr.GetAwaiter().GetResult()
  [IO.File]::WriteAllText((Join-Path $out ($c.label+'-stderr.txt')),$errorText,$utf8)
  if($p.ExitCode -ne 0){throw $errorText}
 } finally {if($started -and !$p.HasExited){$p.Kill();$p.WaitForExit()};$p.Dispose()}
 # The existing contract opens its output as binary, so LF bytes stay exact.
 if((Hash $raw) -cne $c.raw_sha256){throw ('Original full-song rows differ: '+$c.label)}
 $zipPath=Join-Path $out ($c.label+'.txt.gz');$input=[IO.File]::OpenRead($raw);$file=[IO.File]::Create($zipPath);$zip=New-Object IO.Compression.GZipStream($file,[IO.Compression.CompressionLevel]::Fastest,$true)
 try {$input.CopyTo($zip)} finally {$zip.Dispose();$file.Dispose();$input.Dispose()}
 $input=[IO.File]::OpenRead($zipPath);$inflate=New-Object IO.Compression.GZipStream($input,[IO.Compression.CompressionMode]::Decompress);$hash=[Security.Cryptography.SHA256]::Create()
 try {$digest=([BitConverter]::ToString($hash.ComputeHash($inflate))).Replace('-','').ToLowerInvariant()} finally {$hash.Dispose();$inflate.Dispose();$input.Dispose()}
 if($digest -cne $c.raw_sha256){throw 'Lossless compression readback differs'}
 $records+=@{driver=$c.driver;song=$c.song;rows=$c.rows;raw_sha256=$digest;compressed_sha256=(Hash $zipPath)}
 Remove-Item -LiteralPath $raw
 Write-Host "PASS actual Windows full song: $($c.label)/$($c.rows)rows"
}
foreach($e in $plan.inputs){if((Hash $e.path) -cne $e.sha256){throw ('Input changed: '+$e.path)}}
if((Hash $PlanFile) -cne $planHash){throw 'Plan changed'}
$receipt=@{passed=$true;host='actual-Windows-AMD64';cases=$records;source_manifest=$plan.source_manifest;product_producer_manifest=$plan.product_producer_manifest;reference_producer_manifest=$plan.reference_producer_manifest;reference_receipt_sha256=$plan.reference_receipt_sha256;plan_sha256=$planHash;exe_sha256=(Hash $plan.binary);rows=$plan.rows;muted=$true;scope='All configured FM/SSG/rhythm/FM3 fields and ordered writes for all23suppliedsongs perdriver, through score end or two loops. Binary LF output, compressed immediately with full readback. Declared IRQ/DOS/board/third-party-resident adapters; no physical chip/full natural game route/exactness.'}
[IO.File]::WriteAllText((Join-Path $out 'receipt.json'),($receipt | ConvertTo-Json -Depth 7),$utf8)
Write-Host 'PASS actual Windows full supplied music corpus'
