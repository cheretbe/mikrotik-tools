@ECHO OFF

CALL "%~dp0lib\get_credentials.bat"
IF ERRORLEVEL 1 EXIT /B %ERRORLEVEL%

SETLOCAL

IF "%ProgramFiles(x86)%"=="" (SET CPUArch=x86) ELSE (SET CPUArch=x64)
"%~dp0lib\python\%CPUArch%\python.exe" "%~dp0lib\download_config.py" %*

ENDLOCAL