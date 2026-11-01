; Inno Setup 6 script - ARCWorks Kathana Log Analyzer 1.0.0
#define MyAppName "ARCWorks Kathana Log Analyzer"
#define MyAppVersion "1.0.0"
#define MyExe "KathanaLogAnalyzer.exe"
[Setup]
AppId={{6B1E7A52-4C1D-4F7E-9A55-ARC0000KLA10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=ARCWorksPH
DefaultDirName={localappdata}\Programs\ARCWorks\KathanaLogAnalyzer
DefaultGroupName=ARCWorks
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=ARCWorks-Kathana-Log-Analyzer-{#MyAppVersion}-Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: checkedonce
[Files]
Source: "dist\{#MyExe}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyExe}"
Name: "{userdesktop}\Kathana Log Analyzer"; Filename: "{app}\{#MyExe}"; Tasks: desktopicon
[Run]
Filename: "{app}\{#MyExe}"; Description: "Open the Log Analyzer now"; Flags: nowait postinstall skipifsilent
