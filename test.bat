@ECHO OFF

SETLOCAL

IF "%ProgramFiles(x86)%"=="" (
  SET CPUArch=x86
) ELSE (
  SET CPUArch=x64
)

:: ECHO "%~dp0python%CPUArch%\python.exe" "%~dp0..\bin\glog" %*
"%~dp0python\%CPUArch%\python.exe" %*

ENDLOCAL