; installer_script.iss - Упрощённая версия

[Setup]
AppName=Planner_Blender_3D
AppVersion=1.0.1
DefaultDirName={userappdata}\Planner_Blender_3D
DefaultGroupName=Planner_Blender_3D
OutputDir=Output
OutputBaseFilename=Planner_Blender_3D_Setup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Files]
Source: "dist\Planner_Blender_3D.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "themes.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Planner_Blender_3D"; Filename: "{app}\Planner_Blender_3D.exe"
Name: "{userdesktop}\Planner_Blender_3D"; Filename: "{app}\Planner_Blender_3D.exe"

[Run]
Filename: "{app}\Planner_Blender_3D.exe"; Description: "Запустить Planner_Blender_3D"; Flags: postinstall nowait skipifsilent