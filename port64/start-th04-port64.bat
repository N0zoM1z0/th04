@echo off
setlocal
cd /d "%~dp0"
echo TH04 native x64 - Stage 1 preview
echo Controls: arrows to move, Z to shoot, Shift to slow down.
echo Dialogue: release the key, then press Enter or Z to continue.
echo Preview ends after the post-boss dialogue. Later stages are not ready.
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
