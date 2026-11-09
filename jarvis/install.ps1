# ═══════════════════════════════════════════════════════════════
#  Jarvis-Installer für Windows (PowerShell)
#  Aufruf (im Ordner dieses Repos):
#    powershell -ExecutionPolicy Bypass -File jarvis\install.ps1
#  Erneut ausführen ist sicher. Mit "--update" werden config.toml und SOUL.md erneuert.
# ═══════════════════════════════════════════════════════════════
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($env:OPENJARVIS_HOME) { $OJ = $env:OPENJARVIS_HOME }
elseif ($env:XDG_DATA_HOME) { $OJ = Join-Path $env:XDG_DATA_HOME "openjarvis" }
else { $OJ = Join-Path $HOME ".openjarvis" }
$Update = $args -contains "--update"
$Priv = Join-Path $Here "private"

function Say($t) { Write-Host "`n> $t" -ForegroundColor Red }
function Warn($t) { Write-Host "  ! $t" -ForegroundColor Yellow }

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
if (-not (Get-Command jarvis-plus -ErrorAction SilentlyContinue)) {
    throw "jarvis-plus nicht gefunden. Ist $HOME\.local\bin im PATH?"
}

# 3) Konfiguration
Say "Richte Konfiguration in $OJ ein ..."
New-Item -ItemType Directory -Force -Path (Join-Path $OJ "skills") | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($f in @("config.toml", "SOUL.md")) {
    $dst = Join-Path $OJ $f
    if ((-not $Update) -and (Test-Path $dst) -and
        (Select-String -Path $dst -Pattern "Dein persönlicher Jarvis", "Du bist \*\*Jarvis\*\*" -Quiet)) {
        Write-Host "  $f behalten (schon eingerichtet)"
        continue
    }
    if (Test-Path $dst) { Copy-Item $dst "$dst.backup-$stamp" }
    Copy-Item (Join-Path $Here "config\$f") $dst -Force
}

function Is-Template($p) {
    if (-not (Test-Path $p)) { return $true }
    if (Select-String -Path $p -Pattern "füll das aus" -Quiet) { return $true }
    return -not (Select-String -Path $p -Pattern "Über mich" -Quiet)
}
$userMd = Join-Path $OJ "USER.md"
if ((Test-Path (Join-Path $Priv "USER.md")) -and (Is-Template $userMd)) {
    Copy-Item (Join-Path $Priv "USER.md") $userMd -Force; Write-Host "  USER.md aus privatem Paket"
} elseif (Is-Template $userMd) {
    Copy-Item (Join-Path $Here "config\USER.md") $userMd -Force
}
$privMem = Join-Path $Priv "MEMORY.md"
if (Test-Path $privMem) {
    $mem = Join-Path $OJ "MEMORY.md"
    if (Test-Path $mem) { Copy-Item $mem "$mem.backup-$stamp" }
    Copy-Item $privMem $mem -Force; Write-Host "  MEMORY.md (Business-Wissen) aus privatem Paket"
}
$creds = Join-Path $OJ "credentials.toml"
if (-not (Test-Path $creds)) { Copy-Item (Join-Path $Here "config\credentials.toml.example") $creds }
$envf = Join-Path $OJ "jarvis-plus.env"
if (-not (Test-Path $envf)) { Copy-Item (Join-Path $Here "config\jarvis-plus.env.example") $envf }

jarvis-plus register

# 4) Skills
Say "Installiere Skills ..."
foreach ($root in @((Join-Path $Here "skills"), (Join-Path $Priv "skills"))) {
    if (-not (Test-Path $root)) { continue }
    Get-ChildItem $root -Directory | Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } | ForEach-Object {
        $dst = Join-Path $OJ "skills\$($_.Name)"
        New-Item -ItemType Directory -Force -Path $dst | Out-Null
        Copy-Item (Join-Path $_.FullName "*") $dst -Recurse -Force
        Write-Host "  + $($_.Name)"
    }
}
$ghSkills = @(
    @("frontend-design", "https://github.com/anthropics/skills"),
    @("web-artifacts-builder", "https://github.com/anthropics/skills"),
    @("theme-factory", "https://github.com/anthropics/skills"),
    @("impeccable", "https://github.com/pbakaus/impeccable"),
    @("design-taste-frontend", "https://github.com/Leonxlnx/taste-skill"),
    @("web-design-guidelines", "https://github.com/vercel-labs/agent-skills")
)
foreach ($s in $ghSkills) {
    $null | jarvis skill install "github:$($s[0])" --url $s[1] --force *> $null
    if ($LASTEXITCODE -eq 0) { Write-Host "  + $($s[0])" } else { Warn "$($s[0]) nicht installiert (später: jarvis skill install github:$($s[0]) --url $($s[1]))" }
}

# 5) Node.js
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Warn "Node.js fehlt (für Connectoren + 'jarvis gui'): winget install OpenJS.NodeJS.LTS"
}

# 6) Immer im Hintergrund
$autoDone = $false
if (Select-String -Path $creds -Pattern '^ANTHROPIC_API_KEY *= *"[^"]+"' -Quiet) {
    Say "Starte Jarvis im Hintergrund (Autostart) ..."
    jarvis-plus autostart an
    $autoDone = $true
}

Write-Host @"

Installation fertig!

Noch zu tun (einmalig):
  1. $creds   -> ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN
  2. $envf    -> Whoop-Secret, Garmin, Twilio, Instagram, Netlify, Telegram-Chat-ID
  3. In $OJ\config.toml bei [channel.telegram] deine Chat-ID eintragen

Verbinden:  jarvis-plus whoop-login ; jarvis-plus garmin-login ; jarvis connect gdrive
            jarvis-plus connect higgsfield   (auch: canva, notion, figma, 21st)
Pruefen:    jarvis-plus status
"@ -ForegroundColor Green
if ($autoDone) { Write-Host "Jarvis laeuft im Hintergrund. HUD: http://localhost:8765" -ForegroundColor Green }
else { Write-Host "Danach einmal:  jarvis-plus autostart   ->  HUD: http://localhost:8765" -ForegroundColor Green }
