$WshShell = New-Object -ComObject WScript.Shell
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)

# If Windows redirected Desktop to another drive
if (-not (Test-Path $desktopPath)) {
    $desktopPath = "E:\USER_DATA_C\Desktop"
}

$shortcutPath = Join-Path $desktopPath "ClipperAI Studio.lnk"
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $scriptDir "Start_ClipperAI.bat"
$shortcut.WorkingDirectory = $scriptDir
$shortcut.Description = "ClipperAI Studio - Universal AI Video Shorts Generator"
$shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $shortcutPath"
