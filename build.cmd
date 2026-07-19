@echo off
REM Build the native beep_player.exe from source.
REM Requires .NET Framework (csc.exe in PATH or at standard location).

set CSC=%SystemRoot%\Microsoft.NET\Framework64\v4.0.30319\csc.exe
if not exist "%CSC%" set CSC=%SystemRoot%\Microsoft.NET\Framework\v4.0.30319\csc.exe
if not exist "%CSC%" (
    echo csc.exe not found — install .NET Framework or add csc to PATH
    exit /b 1
)

"%CSC%" -nologo -out:beep_player.exe beep_player.cs
if %errorlevel% equ 0 (
    echo beep_player.exe built successfully.
) else (
    echo Build failed.
    exit /b 1
)
