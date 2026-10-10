param([Parameter(Mandatory=$true)][string]$PlanFile)
$ErrorActionPreference='Stop'
$plan=Get-Content -Raw -LiteralPath $PlanFile | ConvertFrom-Json
function Hash([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
$planHash=Hash $PlanFile
foreach($entry in $plan.inputs) {if((Hash $entry.path) -cne $entry.sha256){throw ('Input changed: '+$entry.path)}}
# Assert the consumer is an AMD64 PE, independently of its filename.
$pe=[IO.File]::ReadAllBytes($plan.binary)
$offset=[BitConverter]::ToInt32($pe,60)
if($pe[0] -ne 77 -or $pe[1] -ne 90 -or [BitConverter]::ToUInt32($pe,$offset) -ne 17744 -or [BitConverter]::ToUInt16($pe,$offset+4) -ne 34404 -or [BitConverter]::ToUInt16($pe,$offset+24) -ne 523){throw 'Expected AMD64 PE32+'}
if(Test-Path -LiteralPath $plan.output){throw 'Use fresh output'}
$out=(New-Item -ItemType Directory -Path $plan.output).FullName
$info=New-Object Diagnostics.ProcessStartInfo
$info.FileName=$plan.binary;$info.Arguments='--frames "'+$plan.fixture+'" "'+$plan.assets+'"'
$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
$p=New-Object Diagnostics.Process;$p.StartInfo=$info
$compressed=Join-Path $out 'frames.bin.gz'
$file=[IO.File]::Create($compressed)
$zip=New-Object IO.Compression.GZipStream($file,[IO.Compression.CompressionLevel]::Fastest,$true)
try {
 if(!$p.Start()){throw 'Cannot start pixel component'}
 $stderr=$p.StandardError.ReadToEndAsync()
 # Use the binary BaseStream; text APIs would corrupt pixels and CRT newlines.
 $copy=$p.StandardOutput.BaseStream.CopyToAsync($zip)
 if(!$p.WaitForExit(600000)){throw 'Pixel component timeout'}
 $copy.GetAwaiter().GetResult();$err=$stderr.GetAwaiter().GetResult()
 $utf8=New-Object Text.UTF8Encoding($false)
 [IO.File]::WriteAllText((Join-Path $out 'stderr.txt'),$err,$utf8)
 if($p.ExitCode -ne 0){throw $err}
} finally {
 if($p.Id -and !$p.HasExited){$p.Kill();$p.WaitForExit()}
 $zip.Dispose();$file.Dispose();$p.Dispose()
}
$raw=[IO.File]::OpenRead($compressed)
$inflate=New-Object IO.Compression.GZipStream($raw,[IO.Compression.CompressionMode]::Decompress)
$hash=[Security.Cryptography.SHA256]::Create()
$buffer=New-Object byte[] 1048576
[long]$length=0
try {
 while(($n=$inflate.Read($buffer,0,$buffer.Length)) -gt 0){$null=$hash.TransformBlock($buffer,0,$n,$buffer,0);$length+=$n}
 $null=$hash.TransformFinalBlock((New-Object byte[] 0),0,0)
 $digest=([BitConverter]::ToString($hash.Hash)).Replace('-','').ToLowerInvariant()
} finally {$hash.Dispose();$inflate.Dispose();$raw.Dispose()}
if($digest -cne $plan.expected_sha256 -or $length -ne ([long]$plan.frames * [long]$plan.frame_bytes)){throw ('Original complete pixel stream differs: '+$digest+' / '+$length)}
foreach($entry in $plan.inputs){if((Hash $entry.path) -cne $entry.sha256){throw ('Input changed: '+$entry.path)}}
if((Hash $PlanFile) -cne $planHash){throw 'Plan changed'}
$receipt=@{passed=$true;host='actual-Windows-AMD64';source_manifest=$plan.source_manifest;product_producer_manifest=$plan.product_producer_manifest;reference_producer_manifest=$plan.reference_producer_manifest;cases=$plan.cases;frames=$plan.frames;frame_bytes=$plan.frame_bytes;uncompressed_bytes=$length;frames_sha256=$digest;compressed_sha256=(Hash $compressed);exe_sha256=(Hash $plan.binary);plan_sha256=$planHash;reference_receipt_sha256=$plan.reference_receipt_sha256;muted=$true;scope='Every indexed page, raw RGB palette, DAC and shown RGB refresh in the recorded original CPU corpus. Explicit PI/page/BFNT/clock/input/sound adapters; no physical video/chip/full-route or historical exactness claim.'}
[IO.File]::WriteAllText((Join-Path $out 'receipt.json'),($receipt | ConvertTo-Json -Depth 6),$utf8)
Write-Host "PASS actual Windows startup pixels: $($plan.cases)cases/$($plan.frames)frames"
