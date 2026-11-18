# كوميت نهائي لتطبيق التصليحات
import subprocess

subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
if r.stdout.strip():
    with open("_commit_msg.txt", "w", encoding="utf-8") as f:
        f.write("chore: تحديث .gitignore وتطهير ملفات النسخ التجريبية + إعادة بناء v2.0.1 مع exe المصلح")
    r = subprocess.run(["git", "commit", "-F", "_commit_msg.txt"], capture_output=True, text=True)
    print(r.stdout[-200:], r.stderr[-200:])
    # دفع
    r2 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
    print((r2.stdout or r2.stderr)[-300:])
else:
    print("nothing to commit")
