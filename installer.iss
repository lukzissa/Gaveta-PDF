; Instalador do Gaveta PDF — abra no Inno Setup 6 (gratuito) e clique em Compile.
; Rode build.bat antes para gerar dist\GavetaPDF.
#define AppName "Gaveta PDF"
; A versão vem do próprio GavetaPDF.exe (definida em gavetapdf\__init__.py)
#define AppVersion GetStringFileInfo(AddBackslash(SourcePath) + "dist\GavetaPDF\GavetaPDF.exe", "ProductVersion")

[Setup]
AppId={{6306A140-AEF0-4933-ADDD-C55BD0CA7C04}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Gaveta PDF
; Instala na pasta do usuario (sem admin): o programa grava GavetaPDF.ini e a pasta "dados"
; ao lado do .exe, entao a pasta precisa aceitar gravacao (Arquivos de Programas nao aceita).
DefaultDirName={userpf}\Gaveta PDF
PrivilegesRequired=lowest
DefaultGroupName=Gaveta PDF
UninstallDisplayIcon={app}\GavetaPDF.exe
OutputDir=dist
OutputBaseFilename=GavetaPDF-{#AppVersion}-setup
SetupIconFile=assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"
Name: "sendto"; Description: "Adicionar ao menu ""Enviar para"" do Explorer"; GroupDescription: "Atalhos:"

[Files]
Source: "dist\GavetaPDF\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Gaveta PDF"; Filename: "{app}\GavetaPDF.exe"
Name: "{group}\Desinstalar Gaveta PDF"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Gaveta PDF"; Filename: "{app}\GavetaPDF.exe"; Tasks: desktopicon
Name: "{usersendto}\Gaveta PDF"; Filename: "{app}\GavetaPDF.exe"; Tasks: sendto

[UninstallDelete]
Type: files; Name: "{app}\GavetaPDF.ini"
Type: filesandordirs; Name: "{app}\dados"

[Run]
Filename: "{app}\GavetaPDF.exe"; Description: "Abrir o Gaveta PDF"; Flags: nowait postinstall skipifsilent
