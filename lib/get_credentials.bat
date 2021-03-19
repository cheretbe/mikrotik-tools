@ECHO OFF

SETLOCAL ENABLEDELAYEDEXPANSION

SET "output_cnt=0"
FOR /F "delims=" %%f IN ('powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0%~n0.ps1"') DO (
    SET /A output_cnt+=1
    SET "output[!output_cnt!]=%%f"
)

IF NOT "%output[1]%"=="__OK__" (
  FOR /L %%n IN (1 1 !output_cnt!) DO ECHO !output[%%n]!
  CALL :set_error_level
  GOTO:EOF
)

ENDLOCAL & SET AO_MIKROTIK_CREDENTIALS=%output[2]%
GOTO:EOF

:set_error_level
EXIT /B 1