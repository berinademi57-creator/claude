# ═══════════════════════════════════════════════════════════════
#  Jarvis-Installer für Windows (PowerShell)
#  Aufruf (im Ordner dieses Repos):
#    powershell -ExecutionPolicy Bypass -File jarvis\install.ps1
# ═══════════════════════════════════════════════════════════════
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($env:OPENJARVIS_HOME) { $OJ = $env:OPENJARVIS_HOME }
elseif ($env:XDG_DATA_HOME) { $OJ = Join-Path $env:XDG_DATA_HOME "openjarvis" }
else { $OJ = Join-Path $HOME ".openjarvis" }

function Say($t) { Write-Host "`n> $t" -ForegroundColor Cyan }

# 1) OpenJarvis
if (Get-Command jarvis -ErrorAction SilentlyContinue) {
    Say "OpenJarvis ist schon installiert"
} else {
    Say "Installiere OpenJarvis (ca. 3 Minuten) ..."
    Invoke-RestMethod https://open-jarvis.github.io/OpenJarvis/install.ps1 | Invoke-Expression
}
$env:Path = "$HOME\.local\bin;$env:Path"

# 2) jarvis-plus
Say "Installiere jarvis-plus ..."
$pkg = Join-Path $Here "jarvis_plus"
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv tool install --force --with garminconnect "$pkg"
} else {
    python -m pip install --user --upgrade "$pkg[garmin]"
}
$jp = (Get-Command jarvis-plus -ErrorAction SilentlyContinue).Source
if (-not $jp) { throw "jarvis-plus nicht gefunden. Ist $HOME\.local\bin im PATH?" }

# 3) Konfiguration
Say "Richte Konfiguration in $OJ ein ..."
New-Item -ItemType Directory -Force -Path $OJ | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($f in @("config.toml", "SOUL.md")) {
    $dst = Join-Path $OJ $f
    if (($args -notcontains "--update") -and (Test-Path $dst) -and
        (Select-String -Path $dst -Pattern "Dein persönlicher Jarvis", "Du bist \*\*Jarvis\*\*" -Quiet)) {
        Write-Host "  $f behalten (schon eingerichtet)"
        continue
    }
    if (Test-Path $dst) { Copy-Item $dst "$dst.backup-$stamp" }
    Copy-Item (Join-Path $Here "config\$f") $dst -Force
}
$userMd = Join-Path $OJ "USER.md"
if (-not ((Test-Path $userMd) -and (Select-String -Path $userMd -Pattern "Über mich" -Quiet))) {
    Copy-Item (Join-Path $Here "config\USER.md") $userMd -Force
}
$creds = Join-Path $OJ "credentials.toml"
if (-not (Test-Path $creds)) { Copy-Item (Join-Path $Here "config\credentials.toml.example") $creds }
$envf = Join-Path $OJ "jarvis-plus.env"
if (-not (Test-Path $envf)) { Copy-Item (Join-Path $Here "config\jarvis-plus.env.example") $envf }

$servers = @(@{ name = "jarvis-plus"; command = $jp; args = @("serve") })
ConvertTo-Json -InputObject $servers -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $OJ "mcp-servers.json")

Write-Host @"

Installation fertig!

Zugaenge eintragen (einmalig):
  1. $creds     -> ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN
  2. $envf      -> Whoop-Secret, Garmin, Twilio, Instagram, Telegram-Chat-ID
  3. $userMd    -> alles ueber dich
  4. In $OJ\config.toml bei [channel.telegram] deine Chat-ID eintragen

Verbinden:   jarvis-plus whoop-login ; jarvis-plus garmin-login ; jarvis connect gdrive
Testen:      jarvis-plus test-telegram ; jarvis-plus test-call
Starten:     jarvis start ; jarvis gui ; jarvis-plus watch
"@ -ForegroundColor Green
