# إصلاح crash عند فحص التحديث — استخدام ThreadPoolExecutor بدلاَ من QThread المباشر
import subprocess

subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
print("changes:", r.stdout[:200])
if r.stdout.strip():
    with open("_commit_msg.txt", "w", encoding="utf-8") as f:
        f.write("fix: منع crash التطبيق باستخدام ThreadPoolExecutor بدل QThread في فاحص التحديث\n"
                "replaced Worker-based update checker with concurrent.futures to avoid stack buffer overrun in frozen exe")
    r = subprocess.run(["git", "commit", "-F", "_commit_msg.txt"], capture_output=True, text=True)
    print("commit:", r.stdout[-300:], r.stderr[-200:])
    r2 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
    print("push:", (r2.stdout or r2.stderr)[-400:])
else:
    print("nothing to commit")
