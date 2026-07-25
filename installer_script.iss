; --- Configuration Variables ---
#define MyAppName "AstroBasics"
#define MyAppVersion "1.3.93"
#define MyAppPublisher "The Developer"
#define MyAppExeName "AstroBasics.exe"

[Setup]
; --- Application Information ---
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; --- Modern UI & Safeguards ---
WizardStyle=modern
SetupMutex={#MyAppName}SetupMutex
CloseApplications=yes
ChangesAssociations=yes

; --- License Agreement ---
LicenseFile=license.txt

; --- Installation Directory Settings (Per-User) ---
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest

; --- Modern Installer Tweaks ---
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\icon.ico

; --- Output Settings ---
OutputDir=.\
OutputBaseFilename=astrobasics_installer
SetupIconFile=icon.ico

; --- Compression Settings ---
Compression=lzma2/ultra64
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\AstroBasics\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\Update {#MyAppName}"; Filename: "{app}\refresh_astrobasics.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Registry]
; Register .milan extension
Root: HKCU; Subkey: "Software\Classes\.milan"; ValueType: string; ValueName: ""; ValueData: "AstroBasics.Milan"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Milan"; ValueType: string; ValueName: ""; ValueData: "Kundali Milan Session"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Milan\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icon.ico"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Milan\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey

; Register .astrobasic extension
Root: HKCU; Subkey: "Software\Classes\.astrobasic"; ValueType: string; ValueName: ""; ValueData: "AstroBasics.Chart"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Chart"; ValueType: string; ValueName: ""; ValueData: "AstroBasics Chart File"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Chart\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icon.ico"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Chart\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey

; Register .astroanalysis extension
Root: HKCU; Subkey: "Software\Classes\.astroanalysis"; ValueType: string; ValueName: ""; ValueData: "AstroBasics.Analysis"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Analysis"; ValueType: string; ValueName: ""; ValueData: "AstroBasics Analysis Report"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Analysis\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icon.ico"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Analysis\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey

; Register .astroresearch extension
Root: HKCU; Subkey: "Software\Classes\.astroresearch"; ValueType: string; ValueName: ""; ValueData: "AstroBasics.Research"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Research"; ValueType: string; ValueName: ""; ValueData: "AstroBasics Research Session"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Research\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icon.ico"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Research\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; --- STRICTLY ONLY CLEAN EXECUTABLE / RUNTIME CACHE FILES ---
; The {app}\saves, {app}\analysis_export, and Documents\AstroBasics folders are EXPLICITLY PRESERVED.

Type: files; Name: "{app}\astro_settings.json"
Type: files; Name: "{app}\chart_cache_index.json"
Type: files; Name: "{app}\manifest.json"
Type: files; Name: "{app}\.hash_cache.json"

Type: filesandordirs; Name: "{app}\update_cache"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\dynamic_settings_modules\__pycache__"
Type: filesandordirs; Name: "{app}\my_plugins\__pycache__"