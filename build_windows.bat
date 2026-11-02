@echo off
REM سكريبت بناء تطبيق exe لويندوز
REM يجب تشغيله من داخل بيئة ويندوز بعد تثبيت Python والمتطلبات

echo === تثبيت المتطلبات ===
pip install -r requirements.txt

echo === بناء ملف exe ===
pyinstaller --noconfirm --onedir --windowed ^
  --name "PDF_Toolbox" ^
  --icon=resources\icons\app.ico ^
  --add-data "resources;resources" ^
  main.py

echo === تم الانتهاء ===
echo يوجد الملف الناتج داخل مجلد dist\PDF_Toolbox\PDF_Toolbox.exe
pause
