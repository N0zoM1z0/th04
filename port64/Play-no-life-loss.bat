@echo off
setlocal
for %%F in (th04-port64.exe th04.hdi FREECG98.BMP ym2608_adpcm_rom.bin run_no_life_loss.ps1) do if not exist "%~dp0%%F" goto missing
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_no_life_loss.ps1" %*
if errorlevel 1 goto failed
exit /b 0
:missing
echo Add th04.hdi, FREECG98.BMP and ym2608_adpcm_rom.bin beside th04-port64.exe.
echo See README.md or the portable setup guide for required input identities.
:failed
pause
exit /b 1
