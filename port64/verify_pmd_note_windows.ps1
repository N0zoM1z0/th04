param([Parameter(Mandatory=$true)][string]$PlanFile)
$ErrorActionPreference='Stop'
$plan=Get-Content -Raw -LiteralPath $PlanFile | ConvertFrom-Json
function Hash([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
$planHash=Hash $PlanFile
foreach($e in $plan.inputs){if((Hash $e.path) -cne $e.sha256){throw ('Input changed: '+$e.path)}}
if(Test-Path -LiteralPath $plan.output){throw 'Use a fresh output'}
$out=(New-Item -ItemType Directory -Path $plan.output).FullName;$utf8=New-Object Text.UTF8Encoding($false)
function Run([string]$binary,[string[]]$arguments,[string]$label){
 $data=[IO.File]::ReadAllBytes($binary);$offset=[BitConverter]::ToInt32($data,60)
 if($data[0] -ne 77 -or $data[1] -ne 90 -or [BitConverter]::ToUInt32($data,$offset) -ne 17744 -or [BitConverter]::ToUInt16($data,$offset+4) -ne 34404 -or [BitConverter]::ToUInt16($data,$offset+24) -ne 523){throw 'Expected AMD64 PE32+'}
 $info=New-Object Diagnostics.ProcessStartInfo;$info.FileName=$binary;$info.Arguments=($arguments | ForEach-Object {'"'+$_+'"'}) -join ' ';$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
 $p=New-Object Diagnostics.Process;$p.StartInfo=$info;$started=$false
 try {
  $started=$p.Start();if(!$started){throw 'Cannot start component'}
  $stdout=$p.StandardOutput.ReadToEndAsync();$stderr=$p.StandardError.ReadToEndAsync()
  if(!$p.WaitForExit(300000)){throw 'Component timeout'}
  $text=$stdout.GetAwaiter().GetResult();$errorText=$stderr.GetAwaiter().GetResult()
  [IO.File]::WriteAllText((Join-Path $out ($label+'-stdout.txt')),$text,$utf8)
  [IO.File]::WriteAllText((Join-Path $out ($label+'-stderr.txt')),$errorText,$utf8)
  if($p.ExitCode -ne 0){throw ($label+': '+$errorText)}
 } finally {if($started -and !$p.HasExited){$p.Kill();$p.WaitForExit()};$p.Dispose()}
}
foreach($binary in $plan.contracts){Run -binary $binary -arguments @() -label ([IO.Path]::GetFileNameWithoutExtension($binary))}
$matrix=Join-Path $out 'notes.bin';Run -binary $plan.binary -arguments @('--transpose-bytes',$matrix) -label 'note-matrix'
if((Hash $matrix) -cne $plan.arithmetic_sha256){throw 'Original note arithmetic differs'}
$records=@()
foreach($c in $plan.cases){
 $raw=Join-Path $out 'current.txt';Run -binary $plan.musical_binary -arguments @($c.music,$c.effects,([string]$c.board),$c.mirror,$c.operations,$raw) -label $c.label
 if((Hash $raw) -cne $c.raw_sha256){throw ('Original note boundary rows differ: '+$c.label)}
 $zipPath=Join-Path $out ($c.label+'.txt.gz');$input=[IO.File]::OpenRead($raw);$file=[IO.File]::Create($zipPath);$zip=New-Object IO.Compression.GZipStream($file,[IO.Compression.CompressionLevel]::Fastest,$true)
 try {$input.CopyTo($zip)} finally {$zip.Dispose();$file.Dispose();$input.Dispose()}
 $input=[IO.File]::OpenRead($zipPath);$inflate=New-Object IO.Compression.GZipStream($input,[IO.Compression.CompressionMode]::Decompress);$hash=[Security.Cryptography.SHA256]::Create()
 try {$digest=([BitConverter]::ToString($hash.ComputeHash($inflate))).Replace('-','').ToLowerInvariant()} finally {$hash.Dispose();$inflate.Dispose();$input.Dispose()}
 if($digest -cne $c.raw_sha256){throw 'Lossless compression readback differs'}
 $records+=@{driver=$c.driver;song=$c.song;rows=$c.rows;raw_sha256=$digest;compressed_sha256=(Hash $zipPath)};Remove-Item -LiteralPath $raw
 Write-Host "PASS actual Windows note boundary: $($c.label)"
}
foreach($e in $plan.inputs){if((Hash $e.path) -cne $e.sha256){throw ('Input changed: '+$e.path)}}
if((Hash $PlanFile) -cne $planHash){throw 'Plan changed'}
$receipt=@{passed=$true;host='actual-Windows-AMD64';cases=$records;contracts=$plan.contracts.Count;arithmetic_sha256=(Hash $matrix);arithmetic_rows=$plan.arithmetic_rows;rows=$plan.rows;source_manifest=$plan.source_manifest;product_producer_manifest=$plan.product_producer_manifest;reference_producer_manifest=$plan.reference_producer_manifest;reference_receipt_sha256=$plan.reference_receipt_sha256;plan_sha256=$planHash;exe_sha256=(Hash $plan.binary);musical_exe_sha256=(Hash $plan.musical_binary);muted=$true;scope='Original note-byte matrix and configured FM/SSG/FM3 fields/ordered writes for constructed legal boundary phrases. Explicit IRQ/DOS/board adapters. No audio device, physical chip, natural route or DOS exactness.'}
[IO.File]::WriteAllText((Join-Path $out 'receipt.json'),($receipt | ConvertTo-Json -Depth 7),$utf8)
Write-Host 'PASS actual Windows note arithmetic/boundaries'
