@echo off
setlocal
cd /d "%~dp0"
echo TH04 native x64 reconstruction - Stages 1 through 4 preview
echo Controls: arrows to move, Z to shoot, Shift to slow down.
echo Dialogue: release the key, then press Enter or Z to continue.
echo Preview includes Stage 4 waves, two midboss encounters and NPC dialogue.
echo Both characters continue through their Stage 4 boss, dialogue and clear.
echo Stage 5 waves, scrolling stars and Yuuka dialogue are now playable.
echo Stage 5 boss onward, player death, Bombs and audio are in development.
if not exist "th04-port64.exe" (
  echo ERROR: th04-port64.exe is missing.
  pause
  exit /b 1
)
if not exist "play-normal.hdi" (
  echo ERROR: play-normal.hdi is missing.
  pause
  exit /b 1
)
if not exist "FREECG98.bmp" (
  echo ERROR: FREECG98.bmp is missing.
  pause
  exit /b 1
)
th04-port64.exe --hdi "play-normal.hdi" --font-bmp "FREECG98.bmp" --title
if errorlevel 1 (
  pause
  exit /b 1
)
