@echo off
REM ============================================
REM  تثبيت أداة PDF على سطح المكتب
REM  ينشئ اختصاراً على سطح المكتب
REM ============================================
chcp 65001 >nul
title تثبيت أداة PDF

echo.
echo ═══════════════════════════════════════════
echo    📄  أداة PDF — التثبيت على سطح المكتب
echo ═══════════════════════════════════════════
echo.

REM التحقق من وجود ملف exe
if not exist "dist\PDF_Toolbox\PDF_Toolbox.exe" (
    echo ❌ خطأ: ملف PDF_Toolbox.exe غير موجود!
    echo    قم بتشغيل build_windows.bat أولاً.
    pause
    exit /b 1
)

REM إنشاء اختصار على سطح المكتب
set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGET=%CD%\dist\PDF_Toolbox\PDF_Toolbox.exe"
set "ICON=%CD%\resources\icons\app.ico"
set "SHORTCUT=%DESKTOP%\أداة PDF.lnk"

echo 📁  إنشاء اختصار على سطح المكتب...
powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut('%SHORTCUT%'); " ^
  "$s.TargetPath = '%TARGET%'; " ^
  "$s.WorkingDirectory = '%CD%\dist\PDF_Toolbox'; " ^
  "$s.IconLocation = '%ICON%'; " ^
  "$s.Description = 'أداة PDF — ضغط، تقطيع، دمج، وتحويل ملفات PDF'; " ^
  "$s.Save()"

if exist "%SHORTCUT%" (
    echo ✅ تم إنشاء الاختصار بنجاح!
    echo    الموقع: %SHORTCUT%
) else (
    echo ❌ فشل إنشاء الاختصار.
)

echo.
echo ═══════════════════════════════════════════
echo    ✅ تم التثبيت بنجاح!
echo    يمكنك الآن فتح "أداة PDF" من سطح المكتب
echo ═══════════════════════════════════════════
echo.
pause