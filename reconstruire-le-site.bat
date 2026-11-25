@echo off
REM Reconstruit la version de test du site apres une modification (Python 3.12+ et Pillow requis)
cd /d "%~dp0"
python build.py ..\SFX1_V5_TEST
pause
