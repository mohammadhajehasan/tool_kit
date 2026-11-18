# 🔐 التوقيع الرقمي عبر SignPath

هذا الدليل يشرح كيفية تفعيل **التوقيع الرقمي التلقائي** لملف `PDF_Toolbox.exe` عند كل إصدار، بحيث يتعرف الويندوز على الناشر بدل "ناشر غير معروف".

**SignPath** مجاني بالكامل للمشاريع مفتوحة المصدر ([برنامج المصادر المفتوحة](https://signpath.io/open-source))، ويعمل سحابياً من داخل GitHub Actions — لا حاجة لامتلاك شهادة أو بطاقة ذكية.

---

## ماذا يغيّر التوقيع؟

| قبل التوقيع | بعد التوقيع |
|---|---|
| UAC يعرض "ناشر غير معروف" (Unknown Publisher) | يظهر اسم الناشر الموثّق |
| خصائص الملف: لا تبويب "تواقيع رقمية" | تبويب تواقيع رقمية سليمة |
| SmartScreen: تحذير أزرق دائم | يختفي تدريجياً مع تراكم السمعة* |

> **\*ملاحظة صادقة:** الشهادة تُظهر اسم الناشر **فوراً** في UAC وخصائص الملف، لكن إزالة تحذير **SmartScreen** الأزرق تحتاج سمعة تتراكم مع عدد التنزيلات مع الوقت — حتى مع الشهادة. هذا سلوك ويندوز وليس نقصاً في الإعداد.

---

## كيف يعمل في هذا المشروع؟

خطوة `Sign EXE via SignPath` في [`.github/workflows/build.yml`](../.github/workflows/build.yml):

1. عند بناء أي وسم `v*` (أو تشغيل يدوي): يبنى الـexe كالمعتاد.
2. **إن لم توجد أسرار SignPath بعد** → تُتخطى خطوة التوقيع (مع notice) ويرُفع الملف غير الموقّع — لا فشل ولا انقطاع.
3. **إن وُجدت الأسرار** → يُضغط الـexe في حاوية zip → يُرسل طلب توقيع إلى SignPath → يُنتظر اكتماله (حتى 20 دقيقة) → يُنزَّل الملف الموقّع ويستبدل الأصل → يُرفق للإصدار.

كل ما عليك هو إتمام خطوات الإعداد التالية **مرة واحدة**.

---

## الخطوات

### 1) طلب حساب مجاني للمصادر المفتوحة

- قدّم الطلب من: <https://signpath.io/open-source>
- المطلوب غالباً: رابط المستودع العام، الترخيص (عندنا **MIT** ✓)، وبريد.
- **الموافقة يدوية وقد تستغرق أياماً** — أرسل الطلب مبكراً.
- ستستلم دعوة/مؤسسة (Organization) على `app.signpath.io`.

### 2) تجهيز المؤسسة والمشروع والسياسة

بعد الدخول إلى <https://app.signpath.io>:

**أ. المؤسسة (Organization)**
- إن لم تُنشأ تلقائياً مع القبول: أنشئها وسجّل **معرّفها (Organization ID)** — GUID يظهر في رابط الصفحة مثل:
  `https://app.signpath.io/api/v1/<ORG_ID>/...`

**ب. المشروع (Project)**
- أنشئ مشروعاً واجعل الـslug: `pdf-toolbox`
  (أو أي اسم آخر — انظر المتغيرات الاختيارية بالأسفل)

**ج. سياسة التوقيع (Signing Policy)**
- أنشئ سياسة باسم/slug: `release-signing` واربطها بالمشروع.
- إعداداتها المهمة:
  - **Origin verification**: `GitHub` — تتيح لـSignPath التحقق أن الأرتيفاكت جاء فعلاً من بناء GitHub Actions لهذا المستودع (الـworkflow يرسل `GithubRepository/Branch/RunId/RunAttempt`).
  - **Approval (الموافقة)**: اجعلها **تلقائية عند نجاح التحقق من المصدر (Trusted Build System)** — كي لا يتوقف كل إصدار بانتظار موافقة يدوية في لوحة SignPath.
- الشهادة: SignPath يخصّص للمشاريع المفتوحة شهادة الموقّعة — تُستخدم تلقائياً عبر السياسة.

**د. تكوين الأرتيفاكت (Artifact Configuration)**
- أنشئ تكويناً بـslug: `default` واربطه بالمشروع.
- مهمته أن يحدد أي ملف داخل الحاوية (zip) سيوقّع — عندنا `PDF_Toolbox.exe`.
- إن أتاحت الواجهة قالباً/نموذجاً جاهزاً عند الإنشاء فاختر ما يطابق ملفات exe.
- الصيغة الدقيقة لتكوين الأرتيفاكت موثقة في [وثائق SignPath — Artifact Configuration](https://about.signpath.io/documentation/artifact-configuration).
- 💡 إن فشل التوقيع بخطأ "no matching artifacts" فأنشئ تكويناً مخصصاً يحدد `PDF_Toolbox.exe` صراحة.

### 3) تثبيت تطبيق GitHub

ثبّت [SignPath GitHub App](https://github.com/apps/signpath) على هذا المستودع — يتيح التحقق من أن البناء حقيقي (شرط التوقيع التلقائي).

### 4) إضافة الأسرار (Secrets)

من GitHub: **Settings → Secrets and variables → Actions → New repository secret**

| الاسم | القيمة |
|---|---|
| `SIGNPATH_API_TOKEN` | توكن API من SignPath: صفحتك الشخصية → API tokens → أنشئ توكناً من نوع **User token** بصلاحية تقديم طلبات توقيع (Submit signing requests) |
| `SIGNPATH_ORGANIZATION_ID` | معرّف المؤسسة (GUID) من الخطوة 2-أ |

### 5) المتغيرات الاختيارية (Variables)

لا حاجة لها إن التزمت بأسماء الـslug الافتراضية أعلاه. للتخصيص: **Settings → Secrets and variables → Actions → Variables**

| المتغير | الافتراضي في الـworkflow |
|---|---|
| `SIGNPATH_PROJECT_SLUG` | `pdf-toolbox` |
| `SIGNPATH_SIGNING_POLICY_SLUG` | `release-signing` |
| `SIGNPATH_ARTIFACT_CONFIGURATION_SLUG` | `default` |

---

## التحقق من أن التوقيع نجح

بعد أول إصدار موقّع (وسم `v*` جديد):

```powershell
# في PowerShell
Get-AuthenticodeSignature .\PDF_Toolbox.exe | Format-List
```

أو من الواجهة: **زر يمين على الملف → Properties → Digital Signatures** — يجب أن ترى توقيعاً سليماً باسم الناشر.

---

## استكشاف الأخطاء

| الحالة | السبب المحتمل |
|---|---|
| `401 Unauthorized` | التوكن خاطئ أو منتهي أو غير مملوك للمؤسسة الصحيحة |
| `403 Forbidden` | التوكن بلا صلاحية تقديم طلبات، أو تجاوزت حصة الخطة |
| `422 Unprocessable` | خطأ في أسماء الـslug (project/policy/config)، أو تكوين الأرتيفاكت لا يطابق الملف داخل الحاوية |
| يعليق طويل على `WaitingForApproval` | السياسة ليست تلقائية الموافقة عند نجاح التحقق من المصدر — عدّلها (خطوة 2-ج)، أو وافق يدوياً من لوحة SignPath كحل مؤقت |
| فشل التحقق من المصدر (Origin verification) | تطبيق GitHub غير مثبّت على المستودع، أو البناء ليس من مستودع مطابق |

> **ملاحظة:** أول تشغيل CI بعد إضافة الأسرار هو الاختبار الفعلي لتفاصيل الاستدعاء — إن ظهرت استجابة بصيغة مختلفة عن المتوقع نُحدّث الـworkflow وفق [وثائق SignPath الرسمية](https://about.signpath.io/documentation/).
