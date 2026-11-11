# ═══════════════════════════════════════════════════════════════
#  Jarvis aktualisieren (Windows) – ein Befehl für alles:
#    powershell -ExecutionPolicy Bypass -File $HOME\claude\jarvis\update.ps1
# ═══════════════════════════════════════════════════════════════
$ErrorActionPreference = "Continue"
$Repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Repo
$env:Path = "$HOME\.local\bin;$env:LOCALAPPDATA\OpenJarvis\src\.venv\Scripts;$env:Path"

Write-Host "> Neueste Version holen ..." -ForegroundColor Red
git pull --ff-only

Write-Host "> jarvis-plus aktualisieren ..." -ForegroundColor Red
uv tool install --force --with garminconnect (Join-Path $Repo "jarvis\jarvis_plus")

Write-Host "> Gehirn auf Claude stellen ..." -ForegroundColor Red
jarvis-plus reparieren

Write-Host "> Persoenlichkeit (SOUL.md) und Einstellungen aktualisieren ..." -ForegroundColor Red
$oj = Join-Path $HOME ".openjarvis"
Copy-Item (Join-Path $Repo "jarvis\config\SOUL.md") (Join-Path $oj "SOUL.md") -Force
$envf = Join-Path $oj "jarvis-plus.env"
foreach ($k in @("ELEVENLABS_API_KEY=", "ELEVENLABS_VOICE_ID=")) {
    if (-not (Select-String -Path $envf -Pattern ("^" + $k) -Quiet)) { Add-Content $envf $k }
}

Write-Host "> Jarvis neu starten ..." -ForegroundColor Red
Get-Process jarvis-plus, jarvis -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
jarvis-plus autostart
Start-Sleep -Seconds 8
jarvis-plus open

Write-Host "`nFertig. Sag einfach: 'Jarvis, ...'" -ForegroundColor Green
