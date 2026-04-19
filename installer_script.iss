; installer_script.iss - Скрипт для Inno Setup

[Setup]
AppName=Planner_Blender_3D
AppVersion=1.0.1
AppPublisher=UncleGriff81
AppPublisherURL=https://github.com/UncleGriff81/Planner_Blender_3D
AppSupportURL=https://github.com/UncleGriff81/Planner_Blender_3D/issues
DefaultDirName={userappdata}\Planner_Blender_3D
DefaultGroupName=Planner_Blender_3D
AllowNoIcons=yes
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
; ЭТУ СТРОКУ ОСТАВЛЯЕМ!
Filename: "{app}\Planner_Blender_3D.exe"; Description: "Запустить Planner_Blender_3D"; Flags: postinstall nowait skipifsilent

; ========== НОВЫЙ КОД (ДОБАВЛЯЕМ В КОНЕЦ ФАЙЛА) ==========
[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  mres: Integer;
  DataFolderPath: string;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataFolderPath := ExpandConstant('{userappdata}\PlannerBlenderData');
    
    if DirExists(DataFolderPath) then
    begin
      mres := MsgBox('Вы хотите удалить все ваши проекты, отчеты и настройки программы?', mbConfirmation, MB_YESNO or MB_DEFBUTTON2);
      
      if mres = IDYES then
      begin
        if DelTree(DataFolderPath, True, True, True) then
          MsgBox('Ваши данные были успешно удалены.', mbInformation, MB_OK)
        else
          MsgBox('Не удалось удалить папку с данными. Возможно, некоторые файлы используются.', mbError, MB_OK);
      end
      else
      begin
        MsgBox('Ваши проекты и настройки сохранены в папке: ' + DataFolderPath, mbInformation, MB_OK);
      end;
    end;
  end;
end;