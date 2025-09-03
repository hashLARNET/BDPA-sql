' ========================================
' BDPA Los Encinos - Crear Acceso Directo
' ========================================

Option Explicit

Dim objShell, objFSO, objDesktop
Dim strDesktopPath, strScriptPath, strVbsPath
Dim objShortcut, strIconPath

' Crear objetos
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Obtener rutas
strDesktopPath = objShell.SpecialFolders("Desktop")
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
strVbsPath = strScriptPath & "\iniciar_bdpa_simple.vbs"

' Verificar si existe el archivo VBS
If Not objFSO.FileExists(strVbsPath) Then
    MsgBox "Error: No se encontró el archivo iniciar_bdpa_simple.vbs" & vbCrLf & _
           "Ruta esperada: " & strVbsPath, vbCritical, "Error"
    WScript.Quit 1
End If

' Crear el acceso directo
On Error Resume Next
Set objShortcut = objShell.CreateShortcut(strDesktopPath & "\BDPA Los Encinos.lnk")
If Err.Number <> 0 Then
    MsgBox "Error al crear el acceso directo: " & Err.Description, vbCritical, "Error"
    WScript.Quit 1
End If
On Error Goto 0

' Configurar el acceso directo
With objShortcut
    .TargetPath = "wscript.exe"
    .Arguments = """" & strVbsPath & """"
    .WorkingDirectory = strScriptPath
    .Description = "BDPA Los Encinos - Sistema de Gestión de Mediciones"
    .WindowStyle = 1 ' Normal window
    
    ' Intentar usar un icono personalizado (si existe)
    strIconPath = strScriptPath & "\assets\icon.ico"
    If objFSO.FileExists(strIconPath) Then
        .IconLocation = strIconPath & ",0"
    Else
        ' Usar icono predeterminado de Windows para aplicaciones
        .IconLocation = "%SystemRoot%\System32\shell32.dll,21"
    End If
    
    ' Guardar el acceso directo
    On Error Resume Next
    .Save
    If Err.Number <> 0 Then
        MsgBox "Error al guardar el acceso directo: " & Err.Description, vbCritical, "Error"
        WScript.Quit 1
    End If
    On Error Goto 0
End With

' Mostrar mensaje de confirmación
MsgBox "✓ Acceso directo creado exitosamente" & vbCrLf & vbCrLf & _
       "Ubicación: " & strDesktopPath & "\BDPA Los Encinos.lnk" & vbCrLf & vbCrLf & _
       "Puedes usar este acceso directo para iniciar la aplicación BDPA Los Encinos.", _
       vbInformation, "BDPA - Acceso Directo Creado"

' Preguntar si desea ejecutar la aplicación ahora
Dim intResponse
intResponse = MsgBox("¿Deseas ejecutar la aplicación ahora?", vbYesNo + vbQuestion, "BDPA Los Encinos")

If intResponse = vbYes Then
    ' Ejecutar el archivo VBS silencioso
    objShell.Run """" & strVbsPath & """", 0, False
End If

' Limpiar objetos
Set objShortcut = Nothing
Set objShell = Nothing
Set objFSO = Nothing

WScript.Quit 0