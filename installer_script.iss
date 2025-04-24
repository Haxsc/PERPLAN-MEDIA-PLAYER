[Setup]
AppName=PPL Player
AppVersion=1.2
DefaultDirName={localappdata}\PPL Player
DefaultGroupName=PPL Player
OutputDir=.\Installer\
OutputBaseFilename=Media Installer
Compression=lzma
SolidCompression=yes
SetupIconFile=.\Installer\Installer.ico
PrivilegesRequired=lowest

[Files]
Source: "dist\PPL Player\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Atalho no menu iniciar
Name: "{group}\PPL Player"; Filename: "{app}\PPL Player.exe"; WorkingDir: "{app}"
; Atalho na área de trabalho
Name: "{userdesktop}\PPL Player"; Filename: "{app}\PPL Player.exe"; WorkingDir: "{app}";
; Atalho para desinstalar
Name: "{group}\Desinstalar PPL Player"; Filename: "{uninstallexe}"

[Run]
; Executar após instalação (opcional)
; Filename: "{app}\main.exe"; Description: "Executar PPL Player"; Flags: nowait postinstall skipifsilent
