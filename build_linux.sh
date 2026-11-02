#!/bin/bash
# سكريبت بناء تجريبي لتوليد ملف تنفيذي على لينكس (للاختبار المحلي فقط)
# لبناء نسخة .exe لويندوز يجب تشغيل build_windows.bat على جهاز ويندوز

set -e
echo "=== تثبيت المتطلبات ==="
pip install -r requirements.txt --break-system-packages

echo "=== بناء الملف التنفيذي ==="
pyinstaller --noconfirm --onedir --windowed \
  --name "PDF_Toolbox" \
  --add-data "resources:resources" \
  main.py

echo "=== تم الانتهاء ==="
echo "الملف الناتج: dist/PDF_Toolbox/PDF_Toolbox"
