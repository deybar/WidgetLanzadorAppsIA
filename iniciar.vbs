Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

strAppDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strAppDir
strUser = WshShell.ExpandEnvironmentStrings("%USERNAME%")

' Ruta del entorno virtual optimizado en C:
strPython = "C:\Users\" & strUser & "\.audio_translator_venv\Scripts\pythonw.exe"
If Not FSO.FileExists(strPython) Then
    strPython = "C:\Users\" & strUser & "\.audio_translator_venv\Scripts\python.exe"
End If
If Not FSO.FileExists(strPython) Then
    strPython = strAppDir & "\.venv\Scripts\pythonw.exe"
End If
If Not FSO.FileExists(strPython) Then
    strPython = strAppDir & "\.venv\Scripts\python.exe"
End If

' 0 = vbHide (100% silencioso sin ventana negra de consola CMD)
strCommand = Chr(34) & strPython & Chr(34) & " " & Chr(34) & strAppDir & "\main.py" & Chr(34)
WshShell.Run strCommand, 0, False

Set WshShell = Nothing
Set FSO = Nothing
