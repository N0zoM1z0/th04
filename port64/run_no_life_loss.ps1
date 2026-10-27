param(
    [string]$Directory = $PSScriptRoot,
    [string]$SmokeOutput = ''
)
$ErrorActionPreference = 'Stop'
$exe = Join-Path $Directory 'th04-port64.exe'
$rom = Join-Path $Directory 'ym2608_adpcm_rom.bin'
if ((Get-FileHash -LiteralPath $rom -Algorithm SHA256).Hash.ToLowerInvariant() -cne '53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8') { throw 'OPNA rhythm ROM identity differs.' }
$builds = @{
    'eaa05bdde3c21f702df7b6d9885aa78813216a18449d34e56b296f85fe437e3a' = 916432
    '55dbe34d1edcf8b28b5d369c2b5ee686a346019c3ae698398aa5f718fe7d5d51' = 916432
    'c11f516a7f7421274b9622388829665c40ce4fe958e260b68a44c961fa2efc13' = 913744
    'b7aabad98c193ed1a425e5126bfa01a721b7f8f3dfa7949641b6270bd3493015' = 910384
    'ad4b09d4671da41f3008c7d895f0fe43d1b541a3bbc790d122b6a53168fb8ca2' = 910960
}
$noDeathBuilds = @{ '8257fbf8e952690ab8963844ba92f810399f9f67ca74db463ca006aaf3fbe750' = 2797664; '8a178d24c284e1703c4ffa71e0b68c4a4f0845481604b7e2655dae16c9752940' = 2797664; 'c0d1ca7deaa6a22697fa3926dd1218c08a6b3a88efded89255b04945365b8adc' = 2801760; '2dfd38e8eafefde4f0f428633c6dc3c31c1dd1ca6ff1211bfedc8d6d37f2e4a2' = 2801760 }
$expected = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
if (!$builds.ContainsKey($expected) -and !$noDeathBuilds.ContainsKey($expected)) { throw 'Unsupported executable; only attested reconstruction processes may be patched.' }
$noDeathMode = $noDeathBuilds.ContainsKey($expected)
$lifeRva = if ($noDeathMode) { [uint32]$noDeathBuilds[$expected] } else { [uint32]$builds[$expected] }
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Text;
using System.Runtime.InteropServices;
public static class Th04NoLifeLossLauncher {
 [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] struct Start {
  public int size; public string reserved,desktop,title;
  public int x,y,width,height,columns,rows,fill,flags;
  public short show,reservedSize; public IntPtr reservedPointer,input,output,error;
 }
 [StructLayout(LayoutKind.Sequential)] struct Child { public IntPtr process,thread; public uint pid,tid; }
 [StructLayout(LayoutKind.Sequential)] struct Basic { public IntPtr reserved,peb,r1,r2,pid,parent; }
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool CreateProcess(string exe,StringBuilder args,IntPtr pa,IntPtr ta,bool inherit,uint flags,IntPtr env,string cwd,ref Start startup,out Child child);
 [DllImport("ntdll.dll")] static extern int NtQueryInformationProcess(IntPtr process,int kind,out Basic info,uint size,out uint returned);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool ReadProcessMemory(IntPtr p,IntPtr at,byte[] bytes,UIntPtr size,out UIntPtr read);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool WriteProcessMemory(IntPtr p,IntPtr at,byte[] bytes,UIntPtr size,out UIntPtr written);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool VirtualProtectEx(IntPtr p,IntPtr at,UIntPtr size,uint protect,out uint old);
 [DllImport("kernel32.dll")] static extern bool FlushInstructionCache(IntPtr p,IntPtr at,UIntPtr size);
 [DllImport("kernel32.dll")] static extern uint ResumeThread(IntPtr thread);
 [DllImport("kernel32.dll")] static extern bool TerminateProcess(IntPtr p,uint code);
 [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr handle);
 [DllImport("kernel32.dll")] static extern uint WaitForSingleObject(IntPtr handle,uint milliseconds);
 [DllImport("kernel32.dll")] static extern bool GetExitCodeProcess(IntPtr p,out uint code);
 static void Require(bool ok,string why) { if(!ok)throw new Exception(why+" Win32="+Marshal.GetLastWin32Error()); }
 static byte[] Read(IntPtr p,IntPtr at,int count) {
  var bytes=new byte[count];UIntPtr read;
  Require(ReadProcessMemory(p,at,bytes,new UIntPtr((uint)count),out read) && read.ToUInt64()==(ulong)count,"Owned process read");return bytes;
 }
 static string Quote(string path) { Require(!path.Contains("\"") && !path.Contains("\n"),"Unsupported path");return "\""+path+"\""; }
 public static void Launch(string exe,string directory,string smoke,uint lifeRva,bool noDeath) {
  Require(Environment.Is64BitProcess,"64-bit launcher required");
  var save=Path.Combine(directory,"save-no-life-loss");Directory.CreateDirectory(save);
  string args=Quote(exe)+" --hdi "+Quote(Path.Combine(directory,"th04.hdi"))+" --font-bmp "+Quote(Path.Combine(directory,"FREECG98.BMP"))+" --save-dir "+Quote(save)+(String.IsNullOrEmpty(smoke)?" --audio":" --mute");
  args+=" --pmd-driver pmd86 --opna-rom "+Quote(Path.Combine(directory,"ym2608_adpcm_rom.bin"));
  args+=String.IsNullOrEmpty(smoke)?" --title":" --title-screenshot "+Quote(smoke);
  var startup=new Start();startup.size=Marshal.SizeOf(typeof(Start));Child child;
  Require(CreateProcess(exe,new StringBuilder(args),IntPtr.Zero,IntPtr.Zero,false,0x08004004,IntPtr.Zero,directory,ref startup,out child),"Create owned suspended game");
  bool resumed=false;
  try {
   Basic basic;uint returned;
   Require(NtQueryInformationProcess(child.process,0,out basic,48,out returned)==0,"Owned PEB");
   long image=BitConverter.ToInt64(Read(child.process,new IntPtr(basic.peb.ToInt64()+16),8),0);
   if(noDeath) {
    var gate=new IntPtr(image+lifeRva);Require(Read(child.process,gate,1)[0]==0xa4,"No-death gate starts disabled");
    UIntPtr written;Require(WriteProcessMemory(child.process,gate,new byte[]{0xa5},new UIntPtr(1),out written) && written.ToUInt64()==1,"Enable owned no-death gate");
    Require(Read(child.process,gate,1)[0]==0xa5,"No-death gate readback");
    File.WriteAllText(Path.Combine(save,"runtime-patch.txt"),"pid "+child.pid+"\nno_death_gate "+lifeRva.ToString("X")+"\nbefore A4\nafter A5\nMemory only; no hit acceptance, death animation, power loss or respawn.\n");
   } else {
   var at=new IntPtr(image+lifeRva);var before=Read(child.process,at,6);
   Require(BitConverter.ToString(before)=="83-E8-01-88-42-19","Unexpected life-decrement instruction");
   uint previous;var immediate=new IntPtr(at.ToInt64()+2);
   Require(VirtualProtectEx(child.process,immediate,new UIntPtr(1),0x40,out previous),"Owned code protection");
   try {
    UIntPtr written;Require(WriteProcessMemory(child.process,immediate,new byte[]{0},new UIntPtr(1),out written) && written.ToUInt64()==1,"Runtime patch");
    Require(FlushInstructionCache(child.process,at,new UIntPtr(6)),"Instruction cache");
   } finally { uint ignored;Require(VirtualProtectEx(child.process,immediate,new UIntPtr(1),previous,out ignored),"Restore code protection"); }
   Require(BitConverter.ToString(Read(child.process,at,6))=="83-E8-00-88-42-19","Runtime patch readback");
   File.WriteAllText(Path.Combine(save,"runtime-patch.txt"),"pid "+child.pid+"\nrva "+(lifeRva+2).ToString("X")+"\n83-E8-01-88-42-19 -> 83-E8-00-88-42-19\nMemory only; normal hits/respawns remain.\n");
   }
   Require(ResumeThread(child.thread)!=0xffffffff,"Resume patched game");resumed=true;
   if(!String.IsNullOrEmpty(smoke)) {
    Require(WaitForSingleObject(child.process,30000)==0,"Smoke timeout");uint code;GetExitCodeProcess(child.process,out code);Require(code==0 && File.Exists(smoke),"Smoke did not finish");
   }
  } finally {
   if(!resumed || (!String.IsNullOrEmpty(smoke) && WaitForSingleObject(child.process,0)!=0))TerminateProcess(child.process,1);
   CloseHandle(child.thread);CloseHandle(child.process);
  }
 }
}
'@
[Th04NoLifeLossLauncher]::Launch([IO.Path]::GetFullPath($exe), [IO.Path]::GetFullPath($Directory), $SmokeOutput, $lifeRva, $noDeathMode)
if ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant() -cne $expected) {
    throw 'Executable file changed.'
}
