; Inno Setup script for PDF Toolbox
; يبني مثبّتاً واحداً يجمع PDF_Toolbox.exe من مجلد dist
; البناء: ISCC.exe installer\PDF_Toolbox.iss
; المتطلبات: Inno Setup 6+ (https://jrsoftware.org/isinfo.php)

#define MyAppName "PDF Toolbox"
#define MyAppNameAr "أداة PDF"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Ahmad Al-Farhat"
#define MyAppURL "https://github.com/mohammadhajehasan/tool_kit"
#define MyAppExeName "PDF_Toolbox.exe"

[Setup]
AppId={{8E5C8B4A-3F1D-4E2B-9C7A-PDFTOOLBOX20}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist\installer
OutputBaseFilename=PDF_Toolbox_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
; اللغة العربية للتثبيت مع دعم اليمين لليسار
ShowLanguageDialog=no

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\PDF_Toolbox.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
; تنظيف بقايا التشغيل (سجل، إعدادات)
Type: filesandordirs; Name: "{userappdata}\{#MyAppName}"
