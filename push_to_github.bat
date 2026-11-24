@echo off
title Push ENIT AVR Studio to GitHub
cd /d "%~dp0"
echo =====================================================================
echo Pushing ENIT AVR Studio to https://github.com/ENIT/ENIT-AVR-Studio
echo =====================================================================
git push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Source code pushed successfully to GitHub!
) else (
    echo [NOTE] If prompted by Git Credential Manager, complete browser sign-in.
    echo Also ensure the repository 'ENIT-AVR-Studio' has been created at https://github.com/ENIT
)
pause
