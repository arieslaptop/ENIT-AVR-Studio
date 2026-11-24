@echo off
title Push ENIT AVR Studio to GitHub
cd /d "%~dp0"
echo =====================================================================
echo Pushing ENIT AVR Studio to https://github.com/arieslaptop/ENIT-AVR-Studio
echo =====================================================================
git push -u --force origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Source code updated successfully on GitHub!
) else (
    echo [NOTE] If prompted by Git Credential Manager, complete browser sign-in.
)
pause
