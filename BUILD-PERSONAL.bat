@echo off
setlocal
cd /d "%~dp0"
title ARCWorks Kathana Log Analyzer 1.0.0 build
REM Double-click me. Needs Python 3.13 64-bit ("Add python.exe to PATH") + Inno Setup 6 + internet.
echo.
echo  Building ARCWorks Kathana Log Analyzer 1.0.0 ...
echo.
set PY=py -3.13
%PY% --version >nul 2>&1 || set PY=python
for /f "tokens=2" %%v in ('%PY% --version 2^>^&1') do set PYV=%%v
echo  Using Python %PYV%
echo %PYV% | findstr /b "3.13." >nul || (echo  WARNING: Python 3.13 is recommended. 3.14/3.15 will FAIL on pythonnet.)
if not exist icon.ico %PY% -c "import base64;open('icon.ico','wb').write(base64.b64decode(open('icon.ico.b64').read()))" || goto :failed
%PY% -m pip install --upgrade pip || goto :failed
%PY% -m pip install -r requirements.txt || goto :failed
%PY% tests\run_tests.py || goto :failed
%PY% -m PyInstaller --noconfirm --clean KathanaLogAnalyzer.spec || goto :failed
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (echo  Inno Setup 6 not found - the plain exe is in dist\KathanaLogAnalyzer.exe & goto :done)
%ISCC% KathanaLogAnalyzer.iss || goto :failed
echo.
echo  DONE. Setup: installer\ARCWorks-Kathana-Log-Analyzer-1.0.0-Setup.exe
explorer /select,"%~dp0installer\ARCWorks-Kathana-Log-Analyzer-1.0.0-Setup.exe"
goto :done
:failed
echo.
echo  BUILD FAILED - read the messages above, fix that, and double-click again.
pause
exit /b 1
:done
echo.
pause
