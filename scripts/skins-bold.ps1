# Vuelve a pintar en naranja las negritas del plugin skins (util despues de un update).
# -SkinsPath solo hace falta para probar contra otra carpeta.
param([string]$SkinsPath)

$ErrorActionPreference = 'Stop'
$old = 'color={slot === undefined ? palette.fg : palette[slot]}'
$new = "color={slot !== undefined ? palette[slot] : run.style === 'bold' ? '#ffa94d' : palette.fg}"

if (-not $SkinsPath) {
    $record = Join-Path $env:USERPROFILE '.claude\plugins\installed_plugins.json'
    $installed = (Get-Content -Raw -LiteralPath $record | ConvertFrom-Json).plugins.'skins@hellosverre-mods'
    $SkinsPath = @($installed | Where-Object { $_.scope -eq 'user' })[0].installPath
    if (-not $SkinsPath) { Write-Host 'AVISO: skins@hellosverre-mods no esta instalado. No se cambio nada.'; exit 1 }
}

$file = Join-Path $SkinsPath 'hooks\prose.tsx'
if (-not (Test-Path -LiteralPath $file)) { Write-Host "AVISO: no existe $file. No se cambio nada."; exit 1 }

# ReadAllText/WriteAllText sin BOM: conserva los finales de linea
$text = [IO.File]::ReadAllText($file)
if ($text.Contains($new)) { Write-Host "OK: las negritas ya estan en naranja ($file)"; exit 0 }

$count = ([regex]::Matches($text, [regex]::Escape($old))).Count
if ($count -ne 1) {
    Write-Host "AVISO: la linea esperada aparece $count veces en $file. skins cambio su codigo; no se toco nada."
    exit 1
}

# aqui el archivo esta sin parchear, asi que la copia es el original de esta version
Copy-Item -LiteralPath $file -Destination "$file.orig" -Force
[IO.File]::WriteAllText($file, $text.Replace($old, $new), (New-Object Text.UTF8Encoding($false)))
Write-Host "APLICADO: negritas en #ffa94d ($file)"
Write-Host "Copia del original: $file.orig"
Write-Host 'Ahora ejecuta /reload-plugins en Claude Code.'
