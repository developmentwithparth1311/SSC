@echo off
setlocal
cd /d "%~dp0frontend"
echo == Building React bundle for production API ==
call yarn cap:sync
if errorlevel 1 exit /b 1
cd android
echo == Building debug APK (Firebase App Distribution) ==
call gradlew.bat assembleDebug
if errorlevel 1 exit /b 1
copy /Y app\build\outputs\apk\debug\app-debug.apk C:\Users\smash\Desktop\SSC\APK\SSC-app-debug.apk
echo.
echo DONE: frontend\android\app\build\outputs\apk\debug\app-debug.apk
echo Firebase upload: C:\Users\smash\Desktop\SSC\APK\SSC-app-debug.apk
endlocal