@echo off
setlocal
cd /d "%~dp0"
echo TH04 native x64 reconstruction - Stages 1 through 6 preview
echo Controls: arrows to move, Z to shoot, Shift to slow down.
echo Dialogue: release the key, then press Enter or Z to continue.
echo Preview includes Stage 4 waves, two midboss encounters and NPC dialogue.
echo Both characters continue through their Stage 4 boss, dialogue and clear.
echo Stage 5 includes Yuuka attacks, thick lasers, defeat and post-dialogue.
echo Normal and Lunatic include Stage 6 waves, Yuuka's final battle and all-clear.
echo Normal and Lunatic continue through Good Ending; Easy runs Bad Ending.
echo Staff Roll includes both backgrounds and the original dissolve transitions.
echo The assessment screen includes the original grades and commentary.
echo Assessment: release the key, then press Enter or Z to confirm.
echo Congratulations: release the key, then press Enter or Z to continue.
echo Registration: arrows select, Z or Enter enters, X erases, Esc saves.
echo Scores save separately under LOCALAPPDATA\TH04 and return to the title.
echo Player death and Bombs are in development. This launcher stays muted.
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
th04-port64.exe --hdi "play-normal.hdi" --font-bmp "FREECG98.bmp" --title --mute
if errorlevel 1 (
  pause
  exit /b 1
)
