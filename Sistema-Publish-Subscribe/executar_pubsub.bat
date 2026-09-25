@echo off
title Inicializando Publish-Subscribe

echo.
echo ==========================================
echo       SISTEMA PUBLISH-SUBSCRIBE
echo ==========================================
echo.

echo Iniciando Pyro Name Server...
start "Pyro Name Server" cmd /k "python -m Pyro5.nameserver"
timeout /t 3 /nobreak >nul

powershell -command "$wshell = New-Object -ComObject WScript.Shell; $wshell.AppActivate('Pyro Name Server'); $wshell.SendKeys('% n')"


echo.
echo Iniciando Intermediario...
start "Intermediario" cmd /k "python intermediario.py"
timeout /t 3 /nobreak >nul

powershell -command "$wshell = New-Object -ComObject WScript.Shell; $wshell.AppActivate('Intermediario'); $wshell.SendKeys('% n')"


echo.
echo ==========================================
echo          SUBSCRIBER 1
echo ==========================================
echo.

start "Subscriber 1" cmd /k "python subscriber.py"

echo Configure o Subscriber 1 na janela aberta.
echo Quando terminar, volte aqui e pressione ENTER.
pause >nul


echo.
echo ==========================================
echo          SUBSCRIBER 2
echo ==========================================
echo.

start "Subscriber 2" cmd /k "python subscriber.py"

echo Configure o Subscriber 2 na janela aberta.
echo Quando terminar, volte aqui e pressione ENTER.
pause >nul


echo.
echo ==========================================
echo          SUBSCRIBER 3
echo ==========================================
echo.

start "Subscriber 3" cmd /k "python subscriber.py"

echo Configure o Subscriber 3 na janela aberta.
echo Quando terminar, volte aqui e pressione ENTER.
pause >nul


echo.
echo ==========================================
echo        CENTRAL DE NOTICIAS
echo ==========================================
echo.

start "Central de Noticias" cmd /k "python publisher.py"

exit