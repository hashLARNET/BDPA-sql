' ========================================
' BDPA Los Encinos - Iniciador Silencioso
' ========================================

Option Explicit

Dim objShell, objFSO, strScriptPath, strBatchPath
Dim objWMIService, colProcesses, objProcess
Dim intBackendPID, intFrontendPID
Dim strMessage

' Crear objetos principales
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Obtener la ruta del script actual
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
strBatchPath = strScriptPath & "\iniciar_bdpa.bat"

' Verificar si existe el archivo batch
If Not objFSO.FileExists(strBatchPath) Then
    MsgBox "Error: No se encontró el archivo iniciar_bdpa.bat" & vbCrLf & _
           "Ruta esperada: " & strBatchPath, vbCritical, "BDPA - Error"
    WScript.Quit 1
End If

' Mostrar mensaje de inicio usando MsgBox simple
strMessage = "BDPA Los Encinos" & vbCrLf & vbCrLf & _
             "Iniciando aplicación..." & vbCrLf & _
             "• Backend (FastAPI)" & vbCrLf & _
             "• Frontend (Tkinter)" & vbCrLf & vbCrLf & _
             "La aplicación se ejecutará en segundo plano."

' Usar el método Popup del WScript.Shell
objShell.Popup strMessage, 5, "BDPA Los Encinos", 64
' El popup se cerrará automáticamente después de 5 segundos (64 = vbInformation)

' Cambiar al directorio del script
objShell.CurrentDirectory = strScriptPath

' Ejecutar el archivo batch de forma oculta
On Error Resume Next
objShell.Run """" & strBatchPath & """", 0, False
If Err.Number <> 0 Then
    objIE.Quit
    MsgBox "Error al ejecutar la aplicación: " & Err.Description, vbCritical, "BDPA - Error"
    WScript.Quit 1
End If
On Error Goto 0

' Limpiar objetos
Set objShell = Nothing
Set objFSO = Nothing

' Script terminado - la aplicación seguirá ejecutándose
WScript.Quit 0