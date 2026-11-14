[Setup]
AppId={{D01C4300-64AF-4455-BBEB-C6A70C9F2D75}
AppName=HUMANEX BOT v5.0
AppVersion=5.0.0
AppPublisher=Humanex
DefaultDirName={autopf}\HumanexBot
DefaultGroupName=HUMANEX BOT v5.0
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=HumanexBot-Setup-v5.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\humanexbot_v5.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\HUMANEX BOT v5.0"; Filename: "{app}\humanexbot_v5.exe"
Name: "{autodesktop}\HUMANEX BOT v5.0"; Filename: "{app}\humanexbot_v5.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\humanexbot_v5.exe"; Description: "Launch HUMANEX BOT v5.0"; Flags: nowait postinstall skipifsilent
