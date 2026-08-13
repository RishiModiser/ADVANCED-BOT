[Setup]
AppId={{D01C4300-64AF-4455-BBEB-C6A70C9F2D75}
AppName=HumanexBot
AppVersion=5.0
AppPublisher=Humanex
DefaultDirName={autopf}\HumanexBot
DefaultGroupName=HumanexBot
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
Name: "{autoprograms}\HumanexBot"; Filename: "{app}\humanexbot_v5.exe"
Name: "{autodesktop}\HumanexBot"; Filename: "{app}\humanexbot_v5.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\humanexbot_v5.exe"; Description: "{cm:LaunchProgram,HumanexBot}"; Flags: nowait postinstall skipifsilent
