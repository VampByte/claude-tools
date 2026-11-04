# Herdr app: Git Bash con prompt Starship (Windows)

Guía para dejar **Git Bash dentro de la Herdr app** con un prompt de Starship (directorio, rama de git con icono,
estado y flecha), y poder replicarlo en otra laptop Windows. Probado en Windows 11, Herdr app + herdr-core,
Git for Windows (UCRT64) y Starship 1.27.0.

Resultado esperado:

```
claude-tools on  main [?]
➜ _
```

(directorio en cian, `on` en gris, rama en magenta con icono, `[?]` en rojo si hay archivos sin seguir, flecha verde).

Sustituye `<usuario>` por el nombre de usuario de Windows.
Todos los archivos de Herdr están en `C:\Users\<usuario>\.config\herdr-app\`.

## Requisitos

- Herdr app instalada (`herdr-app` y `hc` en el PATH).
- Git for Windows (`C:\Program Files\Git`), que trae `bash.exe` y `env.exe`.
- `winget` (viene con Windows 11).

## Paso 0: comprobar cuál es `HOME` para Git Bash (importante)

Git Bash calcula `~` a partir de `HOMEDRIVE` + `HOMEPATH`. En la laptop original esas variables eran
`U:` y `\`, así que `~` era `U:\` y Bash **nunca encontraba `~/.bashrc`** (el prompt salía con el estilo
por defecto de Git aunque todo lo demás estuviera bien).

```powershell
"$env:HOMEDRIVE$env:HOMEPATH"      # normal: \Users\<usuario> con C:   -> si sale U:\ u otra cosa rara, usa el Paso 5b
"$env:USERPROFILE"                 # C:\Users\<usuario>
```

Y dentro de Git Bash: `echo $HOME` debe dar `/c/Users/<usuario>`. Si da otra ruta, aplica el **Paso 5b**
(lanzar Bash con `env.exe HOME=...`). Si ya da `/c/Users/<usuario>`, puedes lanzar Bash sin `env.exe`.

## Paso 1: instalar Starship

```powershell
winget install --id Starship.Starship --exact --scope user --accept-package-agreements --accept-source-agreements
```

Instala sin administrador y añade su carpeta al PATH de usuario
(`%LOCALAPPDATA%\Microsoft\WinGet\Packages\Starship.Starship_Microsoft.Winget.Source_8wekyb3d8bbwe`).
Los programas ya abiertos (incluida Herdr) **no ven ese PATH hasta reiniciarse**; el `.bashrc` del Paso 3
incluye un respaldo para eso.

## Paso 2: Nerd Font en Herdr

El icono de la rama (`U+E0A0`) y otros símbolos no existen en las fuentes normales: sin una Nerd Font
sale un cuadrado o un hueco. Se usa la variante **Mono** (iconos de una sola celda, no se solapan con el texto).

1. Descarga `FiraCode.zip` de la última release de https://github.com/ryanoasis/nerd-fonts/releases
   (probado con v3.5.1) y extráelo en una carpeta nueva y vacía.
2. Copia `FiraCodeNerdFontMono-Regular.ttf` y `FiraCodeNerdFontMono-Bold.ttf` a
   `C:\Users\<usuario>\.config\herdr-app\fonts\` (créala si no existe). Herdr carga ahí las fuentes
   `.ttf`/`.otf` **al arrancar**; no hace falta instalarlas en Windows.
3. En `C:\Users\<usuario>\.config\herdr-app\settings.json` pon:

```json
"font": "FiraCode Nerd Font Mono",
"font_size": 16
```

   El nombre debe ser exactamente la familia de la fuente. Se puede comprobar con:

```powershell
Add-Type -AssemblyName System.Drawing
$p = New-Object System.Drawing.Text.PrivateFontCollection
$p.AddFontFile("$env:USERPROFILE\.config\herdr-app\fonts\FiraCodeNerdFontMono-Regular.ttf")
$p.Families[0].Name        # FiraCode Nerd Font Mono
```

Ojo: `font` en `settings.json` vale para **todas** las terminales de Herdr (también PowerShell). Con otra
Nerd Font el procedimiento es el mismo; cambia el nombre de familia.

## Paso 3: `.bashrc` y `.bash_profile`

`C:\Users\<usuario>\.bashrc` (la guarda del principio evita ensuciar shells no interactivos, por ejemplo la
herramienta Bash de Claude Code):

```bash
# Solo shells interactivos: no ensuciar la salida de herramientas (p. ej. la herramienta Bash de Claude Code)
case $- in *i*) ;; *) return ;; esac

# Respaldo: si el PATH heredado aun no incluye Starship (instalado con winget), anade su carpeta
command -v starship >/dev/null 2>&1 || PATH="$PATH:/c/Users/<usuario>/AppData/Local/Microsoft/WinGet/Packages/Starship.Starship_Microsoft.Winget.Source_8wekyb3d8bbwe"

command -v starship >/dev/null 2>&1 && eval "$(starship init bash)"
```

`C:\Users\<usuario>\.bash_profile` (los shells de login, `bash --login`, leen este archivo, no `.bashrc`):

```bash
[ -f ~/.bashrc ] && . ~/.bashrc
```

## Paso 4: `starship.toml`

`C:\Users\<usuario>\.config\starship.toml` (UTF-8; contiene el carácter `➜`):

```toml
# Estilo: directorio en cian, "on" en gris, rama en magenta, [?] en rojo, flecha verde en segunda linea
add_newline = true
format = "$directory$git_branch$git_status$line_break$character"

[directory]
style = "bold cyan"
truncation_length = 4
truncate_to_repo = true
use_os_path_sep = false

[git_branch]
format = "[on](bright-black) [$symbol$branch]($style) "
style = "bold purple"

[git_status]
style = "bold red"

[character]
success_symbol = "[➜](bold green)"
error_symbol = "[➜](bold red)"
```

Los colores exactos de cian/magenta/rojo/gris salen del **tema de Herdr** (paleta `ansi` del tema activo),
no de Starship.

## Paso 5: lanzar Git Bash desde Herdr

### Obtener la ruta corta de Git

Herdr envuelve el `argv` en `powershell.exe -NoExit -Command & '...'`. Con la ruta larga
(`C:/Program Files/...`) la comprobación de "instalado" del menú "+" daba `installed=False` y no mostraba la
entrada. La ruta corta 8.3 (sin espacios) funcionó:

```powershell
(New-Object -ComObject Scripting.FileSystemObject).GetFile("C:\Program Files\Git\bin\bash.exe").ShortPath
# C:\PROGRA~1\Git\bin\bash.exe     (usa barras / en los JSON)
```

Si el equipo tiene los nombres 8.3 desactivados, esa orden devuelve la ruta larga; en ese caso hay que
comprobar si la entrada del menú sale como instalada.

### 5a. Si `HOME` ya es correcto

`argv` = `["C:/PROGRA~1/Git/bin/bash.exe", "--login", "-i"]`

### 5b. Si `HOME` es incorrecto (caso `U:\`)

Se lanza Bash a través de `env.exe`, que fija `HOME` **solo para ese proceso** (sin tocar variables de Windows):

`argv` = `["C:/PROGRA~1/Git/usr/bin/env.exe", "HOME=C:/Users/<usuario>", "C:/PROGRA~1/Git/bin/bash.exe", "--login", "-i"]`

Prueba rápida, simulando el entorno roto, desde Git Bash:

```bash
env -u HOME HOMEDRIVE=U: HOMEPATH='\' "/c/Program Files/Git/usr/bin/env.exe" HOME=C:/Users/<usuario> \
  "/c/Program Files/Git/bin/bash.exe" --login -i -c 'echo $HOME; type -t starship'
# /c/Users/<usuario>  y  file
```

### Entrada en el menú "+" de la barra de pestañas

`C:\Users\<usuario>\.config\herdr-app\programs.json` (se aplica en vivo; si el JSON es inválido, Herdr lo dice
en `programs.error`; usa el `argv` del caso 5a o 5b en `run`):

```json
{
  "programs": {
    "git-bash": {
      "name": "Git Bash",
      "icon": "icons/git.svg",
      "tint": true,
      "tile": "#f05032",
      "color": "#ffffff",
      "run": ["C:/PROGRA~1/Git/usr/bin/env.exe", "HOME=C:/Users/<usuario>", "C:/PROGRA~1/Git/bin/bash.exe", "--login", "-i"]
    }
  }
}
```

### (Opcional) Que `ctrl-shift-t` abra Git Bash

En `keys.json`, sección `global`, cambia `"ctrl-shift-t": "tab.new"` por:

```json
"ctrl-shift-t": {"command": "tab.new", "args": {"argv": ["C:/PROGRA~1/Git/usr/bin/env.exe", "HOME=C:/Users/<usuario>", "C:/PROGRA~1/Git/bin/bash.exe", "--login", "-i"]}},
```

Consecuencias: solo cambia el teclado (el botón "+" y su fila "Terminal" siguen abriendo PowerShell, porque
ese menú lo tiene fijo el mod `new-menu`); y al editar `keys.json`, Herdr deja de añadirle atajos nuevos en
futuras versiones.

## Paso 6: comprobar

1. **Reinicia Herdr** (carga la fuente y el PATH nuevo).
2. Abre una pestaña nueva: menú "+" → Git Bash, o `ctrl-shift-t` si lo configuraste. Las pestañas
   abiertas antes no cambian.
3. Debe salir el directorio y la flecha `➜`. Entra en un repo (`cd /c/ruta/de/un/repo`) y debe aparecer
   `on  main`. Si el icono sale como cuadrado o hueco, la fuente no se cargó (reinicia Herdr y revisa el
   nombre de familia del Paso 2).
4. Comprueba la guarda: `"/c/Program Files/Git/bin/bash.exe" --login -c 'type -t starship'` **no debe
   imprimir nada** (shell no interactivo).

Alternativa sin hacer clic: `herdr-app do tab.new '{"name":"Git Bash test","argv":[ ...el argv... ]}'`
y `herdr-app shot ruta.png` para capturar la ventana.

## Problemas conocidos

| Síntoma | Causa | Solución |
|---|---|---|
| Git Bash abre con el prompt por defecto (`usuario@PC UCRT64 C:\...` y `$`) | `HOME` apunta a otra unidad (`U:\`) y no encuentra `~/.bashrc` | Paso 5b |
| Cuadrado o hueco donde va el icono de la rama | Herdr usa una fuente sin Nerd Font | Paso 2 y reiniciar Herdr |
| La entrada Git Bash no aparece en el menú "+" (`installed=False`) | Ruta con espacios en `run` | Usar la ruta corta 8.3 |
| `starship: command not found` en Bash | PATH heredado de antes de instalar Starship | Reiniciar Herdr; el `.bashrc` ya trae respaldo |
| `herdr-app do ...` falla con `args are not JSON` en PowerShell 5.1 | PowerShell se come las comillas dobles del JSON | Ejecutarlo desde Bash (o `!` en Claude Code) |
| En pestañas Git Bash, Claude no se reanuda solo tras reiniciar Herdr | Esas pestañas no ejecutan el perfil de PowerShell | Abrir esas pestañas como PowerShell |
| `=>` no se dibuja como flecha (ligaduras) | El terminal de Herdr no dibuja ligaduras con ninguna fuente | Sin solución; no existe opción en Herdr |

## Cómo deshacerlo

- Borra `~/.bashrc` y `~/.bash_profile` (si no existían antes) y el `starship.toml`.
- En `settings.json` vuelve `font` a la anterior y borra los `.ttf` de la carpeta `fonts/`.
- Quita la entrada de `programs.json` y, si lo cambiaste, vuelve `"ctrl-shift-t": "tab.new"` en `keys.json`.
- `winget uninstall Starship.Starship`.
