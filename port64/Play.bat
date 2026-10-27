@echo off
setlocal
cd /d "%~dp0"
for %%F in (th04-port64.exe th04.hdi FREECG98.BMP ym2608_adpcm_rom.bin) do if not exist "%~dp0%%F" goto missing
start "" "%~dp0th04-port64.exe" --hdi "%~dp0th04.hdi" --font-bmp "%~dp0FREECG98.BMP" --save-dir "%~dp0save-normal" --title --audio --pmd-driver pmd86 --opna-rom "%~dp0ym2608_adpcm_rom.bin"
exit /b 0
:missing
echo Add th04.hdi, FREECG98.BMP and ym2608_adpcm_rom.bin beside th04-port64.exe.
echo See README.md or the portable setup guide for required input identities.
pause
exit /b 1
