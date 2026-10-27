// Test controller for one pinned, reconstructed Windows x64 executable.
// Creates only owned processes on an inactive desktop; input and life patches
// affect those processes only. No global keyboard, foreground, or audio APIs.
using System;
using System.IO;
using System.Text;
using System.Threading;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public static class Th04BackgroundController {
 [StructLayout(LayoutKind.Sequential,CharSet=CharSet.Unicode)] struct SI {public int cb;public string reserved,desktop,title;public int x,y,xsize,ysize,xcount,ycount,fill,flags;public short show,reserved2;public IntPtr reservedPtr,input,output,error;}
 [StructLayout(LayoutKind.Sequential)] struct PI {public IntPtr process,thread;public uint pid,tid;}
 [StructLayout(LayoutKind.Sequential)] struct Basic {public long processTime,jobTime;public uint flags;public UIntPtr min,max;public uint active;public UIntPtr affinity;public uint priority,scheduling;}
 [StructLayout(LayoutKind.Sequential)] struct IO {public ulong a,b,c,d,e,f;}
 [StructLayout(LayoutKind.Sequential)] struct Extended {public Basic basic;public IO io;public UIntPtr processMemory,jobMemory,peakProcess,peakJob;}
 [StructLayout(LayoutKind.Sequential)] struct Rate {public uint flags,rate;}
 [StructLayout(LayoutKind.Sequential)] struct Rect {public int left,top,right,bottom;}
 delegate bool EnumWindow(IntPtr h,IntPtr data);
 [DllImport("user32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr CreateDesktop(string n,IntPtr d,IntPtr dm,uint f,uint access,IntPtr sa);
 [DllImport("user32.dll",SetLastError=true)] static extern bool SetThreadDesktop(IntPtr h);
 [DllImport("user32.dll")] static extern IntPtr GetThreadDesktop(uint t);
 [DllImport("kernel32.dll")] static extern uint GetCurrentThreadId();
 [DllImport("user32.dll",SetLastError=true)] static extern IntPtr OpenInputDesktop(uint f,bool inherit,uint access);
 [DllImport("user32.dll")] static extern bool CloseDesktop(IntPtr h);
 [DllImport("user32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool GetUserObjectInformation(IntPtr h,int index,StringBuilder s,int size,out int need);
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool CreateProcess(string a,StringBuilder c,IntPtr pa,IntPtr ta,bool inherit,uint flags,IntPtr env,string cwd,ref SI si,out PI pi);
 [DllImport("kernel32.dll")] static extern uint ResumeThread(IntPtr h);
 [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
 [DllImport("kernel32.dll")] static extern uint WaitForSingleObject(IntPtr h,uint ms);
 [DllImport("kernel32.dll")] static extern bool GetExitCodeProcess(IntPtr h,out uint code);
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode)] static extern IntPtr CreateJobObject(IntPtr a,string name);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool SetInformationJobObject(IntPtr h,int c,ref Extended info,int len);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool SetInformationJobObject(IntPtr h,int c,ref Rate info,int len);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool AssignProcessToJobObject(IntPtr h,IntPtr p);
 [DllImport("user32.dll")] static extern bool EnumDesktopWindows(IntPtr d,EnumWindow cb,IntPtr arg);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h,out uint pid);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] static extern bool PostMessage(IntPtr h,uint m,UIntPtr w,IntPtr l);
 [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flags);
 [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr h,out Rect r);

 [DllImport("kernel32.dll",SetLastError=true)] static extern IntPtr VirtualAllocEx(IntPtr p,IntPtr at,UIntPtr size,uint kind,uint protect);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool VirtualProtectEx(IntPtr p,IntPtr at,UIntPtr size,uint protect,out uint old);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool ReadProcessMemory(IntPtr p,IntPtr at,byte[] b,UIntPtr size,out UIntPtr done);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool WriteProcessMemory(IntPtr p,IntPtr at,byte[] b,UIntPtr size,out UIntPtr done);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool FlushInstructionCache(IntPtr p,IntPtr at,UIntPtr size);
 [DllImport("kernel32.dll",SetLastError=true)] static extern uint SuspendThread(IntPtr t);

 [StructLayout(LayoutKind.Sequential)] struct SA {public int size;public IntPtr descriptor;public int inherit;}
 [StructLayout(LayoutKind.Sequential)] struct PBI {public IntPtr reserved,peb,r1,r2,pid,parent;}
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr CreateFile(string p,uint access,uint share,ref SA a,uint disposition,uint flags,IntPtr template);
 [DllImport("ntdll.dll")] static extern int NtQueryInformationProcess(IntPtr p,int c,out PBI basic,uint size,out uint done);
 static uint lifeRva=0xde430;public static void SetLifePatchRva(uint value){lifeRva=value;}
 static string soundDriver="",soundRom="";
 public static void SetSoundProfile(string driver,string rom) {
  if(driver!="" && driver!="pmd" && driver!="pmd86" && driver!="pmdb2" && driver!="none")throw new ArgumentException("Unsupported sound profile");
  if((driver=="pmd86" || driver=="pmdb2") && !File.Exists(rom))throw new ArgumentException("OPNA ROM required");
  soundDriver=driver;soundRom=rom;
 }
 static string SoundArgs(string fallback) {return " --pmd-driver "+(soundDriver.Length==0 ? fallback : soundDriver)+((soundDriver=="pmd86" || soundDriver=="pmdb2") ? " --opna-rom "+Quote(soundRom) : "");}
 static uint noDeathRva;public static void SetNoDeathRva(uint value){noDeathRva=value;}
 static bool immortal;static string routeWords,seedScore;static IntPtr stdoutFile,stdinFile;
 static IntPtr ImageBase(){PBI basic;uint done;Check(NtQueryInformationProcess(child.process,0,out basic,48,out done)==0,"Owned PEB query");return new IntPtr(BitConverter.ToInt64(Read(new IntPtr(basic.peb.ToInt64()+16),8),0));}
 static void PatchNoLifeDecrement(){
  var image=ImageBase();Check(Read(image,2)[0]==77 && Read(image,2)[1]==90,"Owned mapped MZ");
  if(noDeathRva!=0){
   var gate=new IntPtr(image.ToInt64()+noDeathRva);Check(Read(gate,1)[0]==0xa4,"No-death gate starts disabled");
   Write(gate,new byte[]{0xa5});Check(Read(gate,1)[0]==0xa5,"No-death gate readback");
   File.WriteAllText(Path.Combine(root,"life-patch.txt"),"no_death_gate "+noDeathRva.ToString("X")+"\nbefore A4\nafter A5\nprocess_only_pid "+child.pid+"\nSuppresses hit acceptance; no miss/respawn animation or power loss.\n");return;
  }
  var at=new IntPtr(image.ToInt64()+lifeRva);var expected=new byte[]{0x83,0xe8,0x01,0x88,0x42,0x19};var before=Read(at,6);
  Check(BitConverter.ToString(before)==BitConverter.ToString(expected),"No-life-decrement instruction identity");
  var patch=new IntPtr(at.ToInt64()+2);uint previous;Check(VirtualProtectEx(child.process,patch,new UIntPtr(1),0x40,out previous),"Runtime life patch writable");
  try{Write(patch,new byte[]{0});Check(FlushInstructionCache(child.process,at,new UIntPtr(6)),"Flush life patch");}finally{uint ignored;Check(VirtualProtectEx(child.process,patch,new UIntPtr(1),previous,out ignored),"Restore life protection");}
  var after=Read(at,6);Check(after[2]==0 && after[0]==0x83 && after[1]==0xe8,"Read back no-loss patch");
  File.WriteAllText(Path.Combine(root,"life-patch.txt"),"rva "+lifeRva.ToString("X")+"\nbefore "+BitConverter.ToString(before)+"\nafter "+BitConverter.ToString(after)+"\nprocess_only_pid "+child.pid+"\nNo stock loss; ordinary hits, misses and respawns remain. Not an unmodified difficulty/balance result.\n");
 }

 static IntPtr hookData,hookCode,hookIat;static byte[] oldImport;static uint importRva;
 static void Write(IntPtr at,byte[] b){UIntPtr done;Check(WriteProcessMemory(child.process,at,b,new UIntPtr((uint)b.Length),out done) && done.ToUInt64()==(ulong)b.Length,"Owned memory write");}
 static byte[] Read(IntPtr at,int count){var b=new byte[count];UIntPtr done;Check(ReadProcessMemory(child.process,at,b,new UIntPtr((uint)count),out done) && done.ToUInt64()==(ulong)count,"Owned memory read");return b;}
 static void InstallInputHook(){
  Guard();Check(Environment.Is64BitProcess,"64-bit hook controller required");
  var image=Process.GetProcessById((int)child.pid).MainModule.BaseAddress;
  Check(Read(image,2)[0]==77 && Read(image,2)[1]==90,"Owned PE header");
  Check(SuspendThread(child.thread)!=0xffffffff,"Suspend owned thread for hook");
  try{
   hookIat=new IntPtr(image.ToInt64()+importRva);oldImport=Read(hookIat,8);Check(BitConverter.ToInt64(oldImport,0)!=0,"Missing resolved import");
   hookData=VirtualAllocEx(child.process,IntPtr.Zero,new UIntPtr(4096),0x3000,4);hookCode=VirtualAllocEx(child.process,IntPtr.Zero,new UIntPtr(4096),0x3000,4);
   Check(hookData!=IntPtr.Zero && hookCode!=IntPtr.Zero,"Owned hook allocation");
   // Test-owned x64 adapter: return the HWND stored in our separate data page.
   // It changes only this candidate's GetForegroundWindow import, not game state.
   var code=new byte[11];code[0]=0x48;code[1]=0xa1;Array.Copy(BitConverter.GetBytes(hookData.ToInt64()),0,code,2,8);code[10]=0xc3;Write(hookCode,code);Write(hookData,BitConverter.GetBytes(window.ToInt64()));
   uint previous;Check(VirtualProtectEx(child.process,hookCode,new UIntPtr(4096),0x20,out previous),"Hook code RX");Check(FlushInstructionCache(child.process,hookCode,new UIntPtr(11)),"Flush owned adapter");
   Check(VirtualProtectEx(child.process,hookIat,new UIntPtr(8),4,out previous),"IAT writable");Write(hookIat,BitConverter.GetBytes(hookCode.ToInt64()));uint ignored;Check(VirtualProtectEx(child.process,hookIat,new UIntPtr(8),previous,out ignored),"Restore IAT protection");
   Check(BitConverter.ToInt64(Read(hookIat,8),0)==hookCode.ToInt64(),"Read back hook");
   File.WriteAllText(Path.Combine(root,"hook.txt"),"import USER32.GetForegroundWindow\niat_rva "+importRva+"\nold_pointer "+BitConverter.ToInt64(oldImport,0)+"\nadapter_code "+BitConverter.ToString(code)+"\nonly_owned_PID "+child.pid+"\n");
  }finally{Check(ResumeThread(child.thread)!=0xffffffff,"Resume hooked child");}
 }
 static void VirtualFocus(bool focused){Guard();Check(hookData!=IntPtr.Zero,"Missing input adapter");Check(SuspendThread(child.thread)!=0xffffffff,"Suspend focus update");try{Write(hookData,BitConverter.GetBytes(focused?window.ToInt64():0));}finally{ResumeThread(child.thread);}Check(PostMessage(window,focused?7u:8u,UIntPtr.Zero,IntPtr.Zero),"Owned focus message");Wait(r=>r[7]==(focused?"1":"0"));}

 static string root,trace,desktopName,inputName;static IntPtr desktop,window;static PI child;
 static StreamWriter actions;static readonly List<Tuple<uint,bool,int>> held=new List<Tuple<uint,bool,int>>();
 static void Check(bool ok,string m){if(!ok)throw new Exception(m+" Win32="+Marshal.GetLastWin32Error());}
 static string Name(IntPtr h){Check(h!=IntPtr.Zero,"Missing desktop");var s=new StringBuilder(512);int n;Check(GetUserObjectInformation(h,2,s,1024,out n),"Desktop name");return s.ToString();}
 static string InputName(){var h=OpenInputDesktop(0,false,1);try{return Name(h);}finally{if(h!=IntPtr.Zero)CloseDesktop(h);}}
 static void Guard(){Check(Name(GetThreadDesktop(GetCurrentThreadId()))==desktopName,"Wrong controller desktop");Check(InputName()==inputName && inputName!=desktopName,"Input desktop changed; refuse input");}
 static string[] Latest(){if(!File.Exists(trace))return null;using(var f=new FileStream(trace,FileMode.Open,FileAccess.Read,FileShare.ReadWrite)){f.Seek(Math.Max(0,f.Length-32768),SeekOrigin.Begin);using(var r=new StreamReader(f)){var s=r.ReadToEnd();var lines=s.Split('\n');for(int i=lines.Length-2;i>=0;i--)if(lines[i].StartsWith("R ")){var p=lines[i].Trim().Split(' ');if(p.Length==40)return p;}}}return null;}
 static string[] Wait(Func<string[],bool> test,int ms=45000){var w=Stopwatch.StartNew();while(w.ElapsedMilliseconds<ms){uint c;GetExitCodeProcess(child.process,out c);Check(c==259,"Child exited "+c);Guard();var r=Latest();if(r!=null && test(r))return r;Thread.Sleep(15);}throw new Exception("Checkpoint timeout; latest="+String.Join(" ",Latest()??new string[0]));}
 static IntPtr Find(){IntPtr found=IntPtr.Zero;EnumDesktopWindows(desktop,delegate(IntPtr h,IntPtr p){uint id;GetWindowThreadProcessId(h,out id);var c=new StringBuilder(128);GetClassName(h,c,128);if(id==child.pid && c.ToString()=="TH04Port64Title")found=h;return true;},IntPtr.Zero);return found;}
 static void Key(uint vk,bool ext,int scan,bool up){Guard();uint owner;GetWindowThreadProcessId(window,out owner);Check(owner==child.pid,"Wrong owned HWND");long l=1L|((long)scan<<16)|(ext?1L<<24:0)|(up?3L<<30:0);Check(PostMessage(window,up?0x101u:0x100u,new UIntPtr(vk),new IntPtr(l)),"Owned key message");}
 static Tuple<uint,bool,int> K(uint vk,bool ext=false,int scan=0){return Tuple.Create(vk,ext,scan);}
 static void Action(string name,int ms,params Tuple<uint,bool,int>[] keys){var a=Wait(r=>true);foreach(var k in keys){Key(k.Item1,k.Item2,k.Item3,false);held.Add(k);}Thread.Sleep(ms);var b=Wait(r=>true);for(int i=keys.Length-1;i>=0;i--){var k=keys[i];Key(k.Item1,k.Item2,k.Item3,true);held.Remove(k);}actions.WriteLine(name+"\t"+a[1]+"\t"+b[1]);actions.Flush();Thread.Sleep(100);}
 static void Picture(string name){Guard();Rect r;Check(GetClientRect(window,out r),"Client dimensions");using(var b=new Bitmap(r.right,r.bottom,PixelFormat.Format32bppArgb))using(var g=Graphics.FromImage(b)){var dc=g.GetHdc();bool ok;try{ok=PrintWindow(window,dc,1);}finally{g.ReleaseHdc(dc);}Check(ok,"PrintWindow");b.Save(Path.Combine(root,name+".png"),ImageFormat.Png);}}
 static string Quote(string s){Check(!s.Contains("\""),"Unsupported quote in path");return "\""+s+"\"";}
 static void Inner(string exe,string hdi,string font,string output,string mode){desktop=window=hookData=hookCode=hookIat=IntPtr.Zero;child=new PI();stdoutFile=stdinFile=IntPtr.Zero;actions=null;oldImport=null;held.Clear();root=output;trace=Path.Combine(root,"trace","window.tsv");Directory.CreateDirectory(root);var save=Path.Combine(root,"saves");Directory.CreateDirectory(save);File.WriteAllBytes(Path.Combine(save,"MIKO.CFG"),new byte[]{(byte)(mode=="route"?1:3),6,2,2,1,1,0,0,0,(byte)(mode=="route"?13:15)});
 inputName=InputName();desktopName="TH04Smoke-"+Guid.NewGuid().ToString("N");var original=GetThreadDesktop(GetCurrentThreadId());IntPtr job=IntPtr.Zero;
 try{
 desktop=CreateDesktop(desktopName,IntPtr.Zero,IntPtr.Zero,0,0x10000000,IntPtr.Zero);Check(desktop!=IntPtr.Zero,"Create private desktop");Check(SetThreadDesktop(desktop),"Set private desktop");Guard();
 job=CreateJobObject(IntPtr.Zero,null);Check(job!=IntPtr.Zero,"Create owned job");var ext=new Extended();ext.basic.flags=0x2000|0x200;ext.jobMemory=new UIntPtr(768UL*1024*1024);Check(SetInformationJobObject(job,9,ref ext,Marshal.SizeOf(typeof(Extended))),"Bound job memory");var rate=new Rate{flags=5,rate=3500};Check(SetInformationJobObject(job,15,ref rate,8),"Bound job CPU");
 var args=Quote(exe)+" --hdi "+Quote(hdi)+" --font-bmp "+Quote(font)+" --save-dir "+Quote(save)+" --title --mute"+(soundDriver.Length==0 ? "" : SoundArgs("none"))+" --window-trace "+Quote(Path.GetDirectoryName(trace));
 if(mode=="route"){File.WriteAllText(Path.Combine(save,"route-plan.txt"),routeWords+"\n");args=Quote(exe)+" --hdi "+Quote(hdi)+" --font-bmp "+Quote(font)+" --save-dir "+Quote(save)+" --mute"+SoundArgs("pmd")+" --natural-route-checks "+Quote(Path.Combine(root,"route"));}
 if(mode.StartsWith("--")){
  Check(Array.IndexOf(new string[]{"--resident-sound-checks","--ui-performance-checks","--registration-checks","--render-components","--bomb-checks","--pause-checks","--gameover-checks","--score-route-checks","--configuration-checks","--ending-screenshots","--extra-maine-checks"},mode)>=0,"Unapproved headless flag");
  if(mode=="--ending-screenshots")Directory.CreateDirectory(Path.Combine(root,"checks"));
  args=Quote(exe)+" --hdi "+Quote(hdi)+" --font-bmp "+Quote(font)+" --save-dir "+Quote(save)+" --mute"+(soundDriver.Length==0 ? "" : SoundArgs("pmd"))+" "+mode+" "+Quote(Path.Combine(root,"checks"));
 }
 if(mode=="--render-components"){
  var checks=Path.Combine(root,"checks");Directory.CreateDirectory(checks);
  args=Quote(exe)+" --hdi "+Quote(hdi)+" --font-bmp "+Quote(font)+" --save-dir "+Quote(save)+" --mute"+SoundArgs("none");
  args+=" --title-screenshot "+Quote(Path.Combine(checks,"title.bmp"))+" --main-screenshot "+Quote(Path.Combine(checks,"main.bmp"));
  foreach(var name in new string[]{"shooting","combat","dialog","stage2","stage4","stage5"}){
   var folder=Path.Combine(checks,name);Directory.CreateDirectory(folder);args+=" --"+name+"-screenshots "+Quote(folder);
  }
 }
 if(mode=="route" && !String.IsNullOrEmpty(seedScore))File.Copy(seedScore,Path.Combine(save,"GENSOU.SCR"));
 if(mode=="--configuration-checks"){Check(!String.IsNullOrEmpty(seedScore),"Configuration fixture needs scores");File.WriteAllText(Path.Combine(save,"phase.txt"),"0\n");File.Copy(seedScore,Path.Combine(save,"scores.SCR"));for(int r=0;r<4;r++)for(int k=0;k<2;k++)File.Copy(Path.Combine(save,"MIKO.CFG"),Path.Combine(save,"r"+r+"-k"+k+".cfg"));}
 File.WriteAllText(Path.Combine(root,"command.txt"),args);var si=new SI();si.cb=Marshal.SizeOf(typeof(SI));si.desktop="WinSta0\\"+desktopName;
 var sa=new SA();sa.size=Marshal.SizeOf(typeof(SA));sa.inherit=1;
 stdoutFile=CreateFile(Path.Combine(root,"stdout.txt"),0x40000000,3,ref sa,2,0x80,IntPtr.Zero);stdinFile=CreateFile("NUL",0x80000000,3,ref sa,3,0x80,IntPtr.Zero);Check(stdoutFile.ToInt64()!=-1 && stdinFile.ToInt64()!=-1,"Owned stdout/NUL handles");si.flags|=0x100;si.output=si.error=stdoutFile;si.input=stdinFile;
 Check(CreateProcess(exe,new StringBuilder(args),IntPtr.Zero,IntPtr.Zero,true,0x08004004,IntPtr.Zero,Path.GetDirectoryName(exe),ref si,out child),"Create isolated child");Check(AssignProcessToJobObject(job,child.process),"Assign owned job");if(immortal)PatchNoLifeDecrement();Check(ResumeThread(child.thread)!=0xffffffff,"Resume owned child");
 actions=new StreamWriter(Path.Combine(root,"actions.tsv"));File.WriteAllText(Path.Combine(root,"isolation.txt"),"input_desktop "+inputName+"\nprivate_desktop "+desktopName+"\npid "+child.pid+"\nkey_method PostMessage_owned_HWND\nno_SwitchDesktop_no_SendInput\n");
 if(mode=="route" || mode.StartsWith("--")){Check(WaitForSingleObject(child.process,(mode=="--render-components" || mode=="route")?600000u:180000u)==0,"Headless route timeout");uint routeCode;GetExitCodeProcess(child.process,out routeCode);Check(routeCode==0,"Headless route exit "+routeCode);Guard();File.WriteAllText(Path.Combine(root,"controller-passed.txt"),"exit 0\n");return;}
 if(mode=="ui-registration" || mode=="ui-ending") {
  Wait(r=>true);window=Find();Check(window!=IntPtr.Zero,"Owned UI HWND missing");InstallInputHook();VirtualFocus(true);
  if(mode=="ui-ending") {
   Picture("ending-start");var clock=Stopwatch.StartNew();
   while(clock.ElapsedMilliseconds<150000 && Wait(r=>true)[10]!="registration") {
    Action("story-shot",140,K(90));Action("story-release",140);
   }
   Check(Wait(r=>true)[10]=="registration","Ending did not reach registration");Picture("ending-registration");
  }
  Wait(r=>r[10]=="registration" && int.Parse(r[13])>=2);
  Picture("registration-start");Action("cursor-right",110,K(39,true));Action("cursor-right-hold",900,K(39,true));
  Action("cursor-down",110,K(40,true));Action("cursor-left",110,K(37,true));
  Action("name-shot",110,K(90));Picture("registration-edited");
  Action("save",110,K(27));Wait(r=>r[10]=="startup" || r[10]=="menu");Picture("saved-return");
  Guard();Check(PostMessage(window,0x10,UIntPtr.Zero,IntPtr.Zero),"Owned UI close");
  Check(WaitForSingleObject(child.process,15000)==0,"UI close timeout");uint uiCode;GetExitCodeProcess(child.process,out uiCode);Check(uiCode==0,"UI exit code");
  File.WriteAllText(Path.Combine(root,"controller-passed.txt"),"exit 0\n");return;
 }
 Wait(r=>true);window=Find();Check(window!=IntPtr.Zero,"Owned HWND missing");if(mode=="hook" || mode=="music-room"){InstallInputHook();VirtualFocus(true);}Wait(r=>r[10]=="menu");Picture("menu");
 if(mode=="music-room") {
  // Fresh fixture has no Extra unlock, so menu navigation skips it.
  for(int i=0;i<2;i++)Action("menu-music-"+i,110,K(40,true));
  Action("music-room",110,K(13));var entry=Wait(r=>r[10]=="music");
  Wait(r=>r[10]=="music" && long.Parse(r[1])>=long.Parse(entry[1])+40);Picture("music-entry");
  for(int i=0;i<6;i++)Action("select-bad-apple-"+i,110,K(40,true));
  Action("play-bad-apple",110,K(90));var play=Wait(r=>r[10]=="music");
  Wait(r=>r[10]=="music" && long.Parse(r[1])>=long.Parse(play[1])+720);Picture("music-bad-apple");
  Action("select-stage3-boss",110,K(40,true));Action("play-stage3-boss",110,K(13));var boss=Wait(r=>r[10]=="music");
  Wait(r=>r[10]=="music" && long.Parse(r[1])>=long.Parse(boss[1])+120);Picture("music-stage3-boss");
  Action("leave-music",110,K(27));Wait(r=>r[10]=="menu");Picture("music-return");
  Guard();Check(PostMessage(window,0x10,UIntPtr.Zero,IntPtr.Zero),"Owned Music Room close");
  Check(WaitForSingleObject(child.process,15000)==0,"Music Room close timeout");uint musicCode;GetExitCodeProcess(child.process,out musicCode);Check(musicCode==0,"Music Room exit code");
  File.WriteAllText(Path.Combine(root,"controller-passed.txt"),"exit 0\n");return;
 }
 Action("start",180,K(13));Wait(r=>r[10]=="character");Action("marisa",180,K(39,true));Action("character",180,K(13));Wait(r=>r[10]=="shot");Action("shot-b",180,K(40,true));Action("selection",180,K(13));Wait(r=>r[10]=="main" && int.Parse(r[13])>=96);
 if(mode=="hook"){
 Action("enter",220,K(13));Action("keypad-enter",220,K(13,true));Action("right",220,K(39,true));Action("shift-left",220,K(16,false,0x2a),K(37,true));Action("shot",400,K(90));Action("release",1000);Picture("main");Action("bomb",220,K(88));Picture("bomb");
 Action("pause",220,K(27));var paused=Wait(r=>true);var frame=paused[13];Wait(r=>long.Parse(r[1])>=long.Parse(paused[1])+20);Check(Wait(r=>true)[13]==frame,"Pause did not freeze actors");Picture("pause");Action("resume",220,K(27));Wait(r=>int.Parse(r[13])>int.Parse(frame));
 VirtualFocus(false);Action("background",220,K(16,false,0x2a),K(39,true));VirtualFocus(true);Wait(r=>r[5]=="0" && r[6]=="0");
 }else{Picture("main");var start=Wait(r=>true);Wait(r=>int.Parse(r[13])>=int.Parse(start[13])+240);Picture("main-later");}

 Guard();Check(PostMessage(window,0x10,UIntPtr.Zero,IntPtr.Zero),"Owned WM_CLOSE");Check(WaitForSingleObject(child.process,15000)==0,"Owned close timeout");uint code;GetExitCodeProcess(child.process,out code);Check(code==0,"Child exit code "+code);Guard();File.WriteAllText(Path.Combine(root,"controller-passed.txt"),"exit 0\n");
 }finally{if(actions!=null)actions.Dispose();if(stdoutFile!=IntPtr.Zero)CloseHandle(stdoutFile);if(stdinFile!=IntPtr.Zero)CloseHandle(stdinFile);if(job!=IntPtr.Zero)CloseHandle(job);if(child.thread!=IntPtr.Zero)CloseHandle(child.thread);if(child.process!=IntPtr.Zero)CloseHandle(child.process);if(desktop!=IntPtr.Zero){SetThreadDesktop(original);CloseDesktop(desktop);}}}
 public static void Run(string exe,string hdi,string font,string output,string mode,uint iatRva,bool noLifeLoss,string planWords,string initialScore){routeWords=String.IsNullOrEmpty(planWords)?"1 0 200000 0 0 0":planWords;seedScore=initialScore;immortal=noLifeLoss;importRva=iatRva;Exception error=null;var t=new Thread(()=>{try{Inner(exe,hdi,font,output,mode);}catch(Exception e){error=e;}});t.Start();t.Join();if(error!=null){File.WriteAllText(Path.Combine(output,"error.txt"),error.ToString());throw error;}}
}
