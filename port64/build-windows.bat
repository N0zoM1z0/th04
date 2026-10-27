@echo off
setlocal
where cmake >nul 2>nul
if errorlevel 1 goto missing
where ninja >nul 2>nul
if errorlevel 1 goto missing
where g++ >nul 2>nul
if errorlevel 1 goto missing
set "TH04_BUILD_DIR=%~dp0..\build\portable-win64"
cmake -S "%~dp0." -B "%TH04_BUILD_DIR%" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=g++ "-DCMAKE_CXX_FLAGS=--param=ggc-min-expand=5 --param=ggc-min-heapsize=4096"
if errorlevel 1 exit /b 1
cmake --build "%TH04_BUILD_DIR%" --target th04-port64 --parallel 1
if errorlevel 1 exit /b 1
echo Built: %TH04_BUILD_DIR%\th04-port64.exe
exit /b 0
:missing
echo Install 64-bit MinGW-w64 GCC, CMake and Ninja, and add their binaries to PATH.
exit /b 1
