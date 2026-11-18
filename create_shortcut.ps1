# Script pembuat shortcut desktop untuk ClipperAI Studio
$WshShell = New-Object -ComObject WScript.Shell
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Cari folder Desktop (termasuk jika diarahkan ke drive E)
$desktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
if (-not (Test-Path $desktopPath)) {
    $desktopPath = "E:\USER_DATA_C\Desktop"
}

$iconPath = Join-Path $scriptDir "static\clipper_icon.ico"
$batPath = Join-Path $scriptDir "Start_ClipperAI.bat"

# 1. Shortcut Utama: ClipperAI Studio.lnk
$shortcutPath1 = Join-Path $desktopPath "ClipperAI Studio.lnk"
$shortcut1 = $WshShell.CreateShortcut($shortcutPath1)
$shortcut1.TargetPath = $batPath
$shortcut1.WorkingDirectory = $scriptDir
$shortcut1.Description = "ClipperAI Studio - Universal AI Video Shorts Generator"
if (Test-Path $iconPath) {
    $shortcut1.IconLocation = "$iconPath,0"
}
$shortcut1.Save()
Write-Host "[OK] Shortcut ClipperAI Studio berhasil dibuat: $shortcutPath1"

# 2. Update shortcut lama: AutoClip Studio.lnk agar langsung mengarah ke sistem terbaru
$shortcutPath2 = Join-Path $desktopPath "AutoClip Studio.lnk"
$shortcut2 = $WshShell.CreateShortcut($shortcutPath2)
$shortcut2.TargetPath = $batPath
$shortcut2.WorkingDirectory = $scriptDir
$shortcut2.Description = "AutoClip Studio (ClipperAI) - Universal AI Video Shorts Generator"
if (Test-Path $iconPath) {
    $shortcut2.IconLocation = "$iconPath,0"
}
$shortcut2.Save()
Write-Host "[OK] Shortcut AutoClip Studio diperbarui: $shortcutPath2"

# 3. Shortcut Web Langsung (1-Klik langsung buka browser ke 127.0.0.1:8000)
$urlPath = Join-Path $desktopPath "ClipperAI Studio Web.url"
$urlContent = @"
[InternetShortcut]
URL=http://127.0.0.1:8000
IconFile=$iconPath
IconIndex=0
"@
Set-Content -Path $urlPath -Value $urlContent -Encoding ASCII
Write-Host "[OK] Shortcut Web ClipperAI Studio berhasil dibuat: $urlPath"
