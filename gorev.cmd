@echo off
goto :basla
rem --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
exit /b
:basla
rem Gorev Zamanlayici baslaticisi: betigi venv Python ile calistirir, ciktiyi data\log\LOG.log dosyasina ekler.
rem Kullanim: gorev.cmd LOG betik.py arg1 arg2 ...   (arguman sayisi sinirsiz). Yalniz ASCII yaz.
rem UYARI: bir gorev CALISIRKEN bu dosyayi degistirme; cmd dosyayi kaldigi bayttan okur.
rem Bastaki goto + 431. bayttaki exit /b: 20 Kas 2026 degisikliginde eski surumu okuyan gorevler icin.
cd /d C:\shorts
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1
set LOG=%1
set ARGS=%*
call set ARGS=%%ARGS:*%LOG% =%%
echo ==== %date% %time% %ARGS% >> data\log\%LOG%.log
.venv\Scripts\python %ARGS% >> data\log\%LOG%.log 2>&1
exit /b
