' ========================================
' BDPA Los Encinos - Iniciador Simple
' ========================================

Option Explicit

Dim objShell, objFSO, strScriptPath, strBatchPath

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

' Cambiar al directorio del script
objShell.CurrentDirectory = strScriptPath

' Ejecutar el archivo batch de forma oculta
On Error Resume Next
objShell.Run """" & strBatchPath & """", 0, False
If Err.Number <> 0 Then
    MsgBox "Error al ejecutar la aplicación: " & Err.Description, vbCritical, "BDPA - Error"
    WScript.Quit 1
End If
On Error Goto 0

' Limpiar objetos
Set objShell = Nothing
Set objFSO = Nothing

' Script terminado - la aplicación seguirá ejecutándose
WScript.Quit 0