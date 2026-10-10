param([Parameter(Mandatory=$true)][string]$Plan)
$ErrorActionPreference='Stop'
$planData=Get-Content -Raw -LiteralPath $Plan | ConvertFrom-Json
if($planData.version -ne 1 -or !$planData.muted) {throw 'Requires a pinned muted plan.'}
function Hash([string]$path) {(Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()}
foreach($inputFile in $planData.inputs) {if((Hash $inputFile.path) -cne $inputFile.sha256) {throw 'Input identity differs.'}}
if(Test-Path -LiteralPath $planData.output) {throw 'Output must be fresh.'}
New-Item -ItemType Directory -Path $planData.output | Out-Null
$save=Join-Path $planData.output 'saves';New-Item -ItemType Directory -Path $save | Out-Null
$cfg=[byte[]]@(3,6,2,2,1,1,0,0,0,15)
[IO.File]::WriteAllBytes((Join-Path $save 'MIKO.CFG'),$cfg)
[IO.File]::WriteAllBytes((Join-Path $planData.output 'initial-MIKO.CFG'),$cfg)
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;
public static class Th04WindowProbe {
 [StructLayout(LayoutKind.Sequential)] public struct KEYBDINPUT {public ushort vk,scan;public uint flags,time;public UIntPtr extra;}
 [StructLayout(LayoutKind.Explicit,Size=40)] public struct INPUT {[FieldOffset(0)] public uint type;[FieldOffset(8)] public KEYBDINPUT key;}
 [DllImport("user32.dll")] public static extern uint SendInput(uint count,INPUT[] inputs,int size);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd,out uint pid);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd,int cmd);
 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hwnd,IntPtr after,int x,int y,int cx,int cy,uint flags);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern IntPtr CreateWindowEx(uint ex,string cls,string text,uint style,int x,int y,int w,int h,IntPtr parent,IntPtr menu,IntPtr instance,IntPtr data);
 [DllImport("user32.dll")] public static extern bool DestroyWindow(IntPtr hwnd);
 public static void Key(ushort vk,bool up,bool extended) {var i=new INPUT();i.type=1;i.key.vk=vk;i.key.flags=(up?2u:0u)|(extended?1u:0u);if(SendInput(1,new INPUT[]{i},Marshal.SizeOf(typeof(INPUT)))!=1)throw new Exception("SendInput rejected");}
 public static string Tail(string path) {using(var s=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite)){s.Seek(Math.Max(0,s.Length-16384),SeekOrigin.Begin);using(var r=new StreamReader(s)){return r.ReadToEnd();}}}
}
'@
$traceDir=Join-Path $planData.output 'trace';$trace=Join-Path $traceDir 'window.tsv'
$arguments=@('--hdi',('"'+$planData.hdi+'"'),'--font-bmp',('"'+$planData.font+'"'),'--save-dir',('"'+$save+'"'),'--title','--mute','--window-trace',('"'+$traceDir+'"'))
$beforeForeground=[Th04WindowProbe]::GetForegroundWindow()
$process=Start-Process -FilePath $planData.exe -ArgumentList $arguments -PassThru -RedirectStandardOutput (Join-Path $planData.output 'stdout.txt') -RedirectStandardError (Join-Path $planData.output 'stderr.txt')
$actions=New-Object 'System.Collections.Generic.List[object]'
$held=New-Object 'System.Collections.Generic.List[object]'
$sink=[IntPtr]::Zero;$window=[IntPtr]::Zero
function Latest {
 if(!(Test-Path -LiteralPath $trace)) {return $null}
 $lines=[Th04WindowProbe]::Tail($trace) -split "`n"
 for($i=$lines.Length-2;$i -ge 0;$i--) {if($lines[$i].StartsWith('R ')) {$parts=$lines[$i].Trim() -split ' ';if($parts.Length -eq 29){return ,$parts}}}
 return $null
}
function WaitState([scriptblock]$predicate,[int]$seconds=45) {
 $deadline=[DateTime]::UtcNow.AddSeconds($seconds)
 while([DateTime]::UtcNow -lt $deadline) {
  $process.Refresh();if($process.HasExited){throw 'Window exited during observation.'}
  $state=Latest;if($null -ne $state -and (& $predicate $state)){return ,$state}
  Start-Sleep -Milliseconds 25
 }
 throw 'Window observation timed out.'
}
function OwnForeground {
 $fg=[Th04WindowProbe]::GetForegroundWindow()
 if($fg -ne $window -and $fg -ne $sink){throw 'Focus left the owned probe windows; input stopped.'}
}
function Focus([IntPtr]$handle) {
 [Th04WindowProbe]::ShowWindow($handle,5)|Out-Null
 [Th04WindowProbe]::SetForegroundWindow($handle)|Out-Null
 Start-Sleep -Milliseconds 100
 if([Th04WindowProbe]::GetForegroundWindow() -ne $handle){throw 'Could not establish owned foreground.'}
}
function Action([string]$name,[object[]]$keys,[int]$milliseconds) {
 OwnForeground;$state=WaitState {param($r) $true};$begin=[long]$state[1]
 foreach($key in $keys){[Th04WindowProbe]::Key([ushort]$key.vk,$false,[bool]$key.extended);$held.Add($key)}
 Start-Sleep -Milliseconds $milliseconds
 OwnForeground;$state=WaitState {param($r) $true};$end=[long]$state[1]
 for($i=$keys.Length-1;$i -ge 0;$i--){[Th04WindowProbe]::Key([ushort]$keys[$i].vk,$true,[bool]$keys[$i].extended);$held.Remove($keys[$i])|Out-Null}
 $actions.Add(@{name=$name;keys=$keys;begin=$begin;end=$end});Start-Sleep -Milliseconds 60
}
try {
 WaitState {param($r) $true}|Out-Null
 $process.Refresh();$window=$process.MainWindowHandle
 if($window -eq [IntPtr]::Zero){throw 'Missing owned main window.'}
 [uint32]$owner=0;[Th04WindowProbe]::GetWindowThreadProcessId($window,[ref]$owner)|Out-Null
 if($owner -ne $process.Id){throw 'Window owner differs.'}
 # Visible OS window on the active desktop; offscreen to avoid covering work.
 [Th04WindowProbe]::SetWindowPos($window,[IntPtr]::Zero,-32000,-32000,0,0,0x0015)|Out-Null
 Focus $window
 WaitState {param($r) $r[10] -ceq 'menu'}|Out-Null
 $enter=@{vk=13;extended=$false};$right=@{vk=39;extended=$true};$left=@{vk=37;extended=$true};$shift=@{vk=16;extended=$false}
 Action 'start' @($enter) 150;WaitState {param($r) $r[10] -ceq 'character'}|Out-Null
 Action 'marisa' @($right) 150;Action 'character' @($enter) 150
 WaitState {param($r) $r[10] -ceq 'shot'}|Out-Null
 Action 'shot-b' @(@{vk=40;extended=$true}) 150;Action 'selection' @($enter) 150
 WaitState {param($r) $r[10] -ceq 'main' -and [int]$r[13] -ge 96}|Out-Null
 Action 'enter' @($enter) 150;Action 'keypad-enter' @(@{vk=13;extended=$true}) 150
 Action 'right' @($right) 150;Action 'shift-left' @($shift,$left) 150
 Action 'shot' @(@{vk=90;extended=$false}) 300;Action 'release' @() 800
 $sink=[Th04WindowProbe]::CreateWindowEx(0,'STATIC','TH04 owned input focus control',0x10CF0000,-32000,-32000,120,80,[IntPtr]::Zero,[IntPtr]::Zero,[IntPtr]::Zero,[IntPtr]::Zero)
 if($sink -eq [IntPtr]::Zero){throw 'Cannot create owned focus sink.'}
 Focus $sink;WaitState {param($r) $r[7] -eq '0'}|Out-Null
 Action 'background' @($shift,$right) 150
 Focus $window;WaitState {param($r) $r[7] -eq '1'}|Out-Null
 OwnForeground;[Th04WindowProbe]::Key(27,$false,$false)
 Start-Sleep -Milliseconds 80;[Th04WindowProbe]::Key(27,$true,$false)
 if(!$process.WaitForExit(15000) -or $process.ExitCode -ne 0){throw 'Window exit failed.'}
 if((Hash (Join-Path $save 'MIKO.CFG')) -cne (Hash (Join-Path $planData.output 'initial-MIKO.CFG'))){throw 'Configuration changed.'}
 foreach($inputFile in $planData.inputs){if((Hash $inputFile.path) -cne $inputFile.sha256){throw 'Final immutable identity differs.'}}
 @{passed=$true;source_manifest=$planData.source_manifest;command=$arguments;actions=$actions.ToArray();trace_sha256=(Hash $trace);scope='Actual Windows active-desktop SendInput/GetAsyncKeyState; offscreen visible owned window. Muted; no audio device. Independent Python assessment still required.'}|ConvertTo-Json -Depth 12|Set-Content -Encoding UTF8 (Join-Path $planData.output 'controller.json')
} catch {
 ($_ | Format-List * -Force | Out-String) | Set-Content -Encoding UTF8 (Join-Path $planData.output 'error.txt')
 throw
} finally {
 foreach($key in $held){[Th04WindowProbe]::Key([ushort]$key.vk,$true,[bool]$key.extended)}
 $process.Refresh();if(!$process.HasExited){$process.Kill();$process.WaitForExit()}
 if($sink -ne [IntPtr]::Zero){[Th04WindowProbe]::DestroyWindow($sink)|Out-Null}
 if($beforeForeground -ne [IntPtr]::Zero){[Th04WindowProbe]::SetForegroundWindow($beforeForeground)|Out-Null}
 $actions.ToArray()|ConvertTo-Json -Depth 12|Set-Content -Encoding UTF8 (Join-Path $planData.output 'actions.json')
}
