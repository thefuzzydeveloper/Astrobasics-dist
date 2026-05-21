; --- Configuration Variables ---
#define MyAppName "AstroBasics"
#define MyAppVersion "1.2.7"
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
; Refresh icons and associations after installation
ChangesAssociations=yes

; --- License Agreement ---
; This will force the user to accept the non-commercial terms before installing
LicenseFile=license.txt

; --- Installation Directory Settings (Per-User) ---
; Installs to C:\Users\Username\AppData\Local\Astro Basics
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Tells Windows NOT to ask for Admin rights (No UAC prompt)
PrivilegesRequired=lowest

; --- Modern Installer Tweaks ---
; Skips the "Choose Start Menu Folder" page for a faster, streamlined install
DisableProgramGroupPage=yes
; Sets the app icon in the Windows "Add/Remove Programs" list
UninstallDisplayIcon={app}\icon.ico

; --- Output Settings ---
; Where the installer .exe will be saved
OutputDir=.\
OutputBaseFilename=astrobasics_installer
; The icon for the installer .exe itself
SetupIconFile=icon.ico

; --- Compression Settings ---
Compression=lzma2/ultra64
SolidCompression=yes

[Languages]
; Explicitly define the standard English string file
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Makes the desktop shortcut an optional checkbox during installation
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Core Application Files (Grabs everything from the PyInstaller dist folder)
Source: "dist\AstroBasics\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Explicitly copies the icon file into the app folder so shortcuts can use it
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"

; Start Menu Updater Shortcut (Launches the standalone downloader)
Name: "{group}\Update {#MyAppName}"; Filename: "{app}\refresh_astrobasics.exe"; IconFilename: "{app}\icon.ico"

; Start Menu Uninstaller Shortcut
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"

; Desktop Shortcut (Now tied to the Task checkbox)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Registry]
; Register .milan extension for Current User (due to PrivilegesRequired=lowest)
Root: HKCU; Subkey: "Software\Classes\.milan"; ValueType: string; ValueName: ""; ValueData: "AstroBasics.Milan"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Milan"; ValueType: string; ValueName: ""; ValueData: "Kundali Milan Session"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Milan\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\icon.ico"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AstroBasics.Milan\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey

[Run]
; Checkbox option to launch the application when the installer finishes
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove all files in the update cache
Type: filesandordirs; Name: "{app}\update_cache"

; Remove Python cache files generated during runtime
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\dynamic_settings_modules\__pycache__"

; Remove the updater's tracking files
Type: files; Name: "{app}\manifest.json"
Type: files; Name: "{app}\.hash_cache.json"