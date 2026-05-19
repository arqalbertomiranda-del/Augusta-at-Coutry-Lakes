@echo off
set FAL_KEY=c3e735a2-6335-4786-a189-493b64ff4eb8:7212281c7ac39dd46407c21be2613ce2
cd /d "C:\Users\alber\Boma Desarrollos\Automatizaciones Boma - Documentos\05. Augusta"
python scripts\02_animate_voiceover_combine.py > logs\seedance2_run.log 2>&1
echo Exit code: %ERRORLEVEL% >> logs\seedance2_run.log
