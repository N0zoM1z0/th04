@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build-TH04.ps1" %*
exit /b %ERRORLEVEL%
