' VBScript: Play sound from a URL
' Save this as PlaySound.vbs and double-click to run

Option Explicit

Dim url, player

' Set your audio file URL here (must be accessible online)
url = "https://archive.org/download/title_202308/title.mp3"

' Create Windows Media Player COM object
On Error Resume Next
Set player = CreateObject("WMPlayer.OCX")
If Err.Number <> 0 Then
    WScript.Echo "Error: Windows Media Player COM object not available."
    WScript.Quit 1
End If
On Error GoTo 0

' Assign the URL to the player
player.URL = url

' Start playing
player.Controls.play

' Keep script alive until playback finishes
Do While player.playState <> 1 ' 1 = Stopped
    WScript.Sleep 100
Loop

' Clean up
Set player = Nothing
