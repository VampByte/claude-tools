# Herdr app: Git Bash con prompt Starship (Windows)

Guía para dejar **Git Bash dentro de la Herdr app** (y también fuera de ella) con un prompt de Starship
(directorio, rama de git con icono, estado y flecha), y poder replicarlo en otra laptop Windows.
Probado en Windows 11, Herdr app + herdr-core, Git for Windows (UCRT64) y Starship 1.27.0.

> **Atajo:** `python instalar.py` (en la raíz del repo), opción **4 "Starship y terminales"**, hace los pasos 1, 2,
> 3, 5 (menú "+"), 7a, 7b, 7c y 7d por ti. Si falta Git, Herdr o VS Code, avisa y salta esas partes. Antes de cambiar un archivo
> guarda una copia en `~/.claude-tools-backup/<fecha>/`. Esta guía explica qué hace cada paso y sirve para hacerlo a mano.
>
> Los archivos de configuración tienen **una sola copia**, en [`installer/plantillas/`](../installer/plantillas/):
> el instalador los usa tal cual y esta guía enlaza a ellos.

Resultado esperado:

```
claude-tools on  main [?]
➜ _
```

(directorio en cian, `on` en gris, rama en magenta con icono, `[?]` en rojo si hay archivos sin seguir, flecha verde).

Sustituye `<usuario>` por el nombre de usuario de Windows. Los archivos de Herdr están en
`C:\Users\<usuario>\.config\herdr-app\`. **La misma configuración sirve en cualquier laptop**: lo único que
cambia entre equipos es si hace falta el Paso 4 (solo cuando `HOME` no es el perfil local).

## Requisitos

- Herdr app instalada (`herdr-app` y `hc` en el PATH).
- Git for Windows (`C:\Program Files\Git`), que trae `bash.exe`.
- `winget` (viene con Windows 11).

## Paso 0: ¿dónde está `HOME` para Git Bash?

Git Bash calcula `~` (`HOME`) a partir de `HOMEDRIVE` + `HOMEPATH`:

```powershell
"$env:HOMEDRIVE$env:HOMEPATH"      # equipo "normal": C:\Users\<usuario>      equipo con carpeta de red: U:\
"$env:USERPROFILE"                 # C:\Users\<usuario>  (perfil local, donde vive la configuración)
```

- **Si `HOME` es el perfil local** (`C:\Users\<usuario>`): `~/.bashrc` y `~/.bash_profile` ya están en el
  sitio correcto. Salta el Paso 4.
- **Si `HOME` es otra unidad** (en la laptop del trabajo: `U:\` = `\\servidor\data\<usuario>`, carpeta personal
  en red que ya contiene `.gitconfig`, `.ssh` y el historial): haz el Paso 4.

> **No fuerces `HOME` con `env.exe` ni con una variable de Windows para "arreglarlo".** Se probó y rompe
> cosas: con `HOME=C:\Users\<usuario>` Git deja de leer `U:\.gitconfig` (`git config --global user.name`
> sale vacío, los commits pierden la identidad), `.ssh` y el historial de Bash pasan a otro sitio.
> Se deja `HOME` como está y se enlaza desde ahí (Paso 4).

## Paso 1: instalar Starship

```powershell
winget install --id Starship.Starship --exact --scope user --accept-package-agreements --accept-source-agreements
```

Instala sin administrador y añade su carpeta al PATH de usuario. Los programas ya abiertos (incluida Herdr)
**no ven ese PATH hasta reiniciarse**; el `.bashrc` del Paso 3 incluye un respaldo.

## Paso 2: Nerd Font en Herdr

El icono de la rama (`U+E0A0`) y otros símbolos no existen en las fuentes normales: sin una Nerd Font
sale un cuadrado o un hueco. Se usa la variante **Mono** (iconos de una sola celda).

1. Descarga `FiraCode.zip` de la última release de https://github.com/ryanoasis/nerd-fonts/releases
   (probado con v3.5.1) y extráelo en una carpeta nueva y vacía.
2. Copia `FiraCodeNerdFontMono-Regular.ttf` y `FiraCodeNerdFontMono-Bold.ttf` a
   `C:\Users\<usuario>\.config\herdr-app\fonts\` (créala si no existe). Herdr carga ahí las fuentes
   `.ttf`/`.otf` **al arrancar**; no hace falta instalarlas en Windows.
3. En `C:\Users\<usuario>\.config\herdr-app\settings.json`:

```json
"font": "FiraCode Nerd Font Mono",
"font_size": 16
```

   Herdr ya trae una clave `font` con otra fuente (en la laptop de casa era `"Cascadia Code"`): hay que **cambiar
   su valor**, no añadir otra clave `font`.

   El nombre debe ser exactamente la familia de la fuente. Se puede comprobar con:

```powershell
Add-Type -AssemblyName System.Drawing
$p = New-Object System.Drawing.Text.PrivateFontCollection
$p.AddFontFile("$env:USERPROFILE\.config\herdr-app\fonts\FiraCodeNerdFontMono-Regular.ttf")
$p.Families[0].Name        # FiraCode Nerd Font Mono
```

`font` en `settings.json` vale para **todas** las terminales de Herdr (también PowerShell). Fuera de Herdr
(Git Bash independiente, terminal de VS Code) esa carpeta `fonts/` no cuenta: ver el Paso 7.

## Paso 3: `.bashrc`, `.bash_profile` y `starship.toml` en el perfil local

Tres archivos, copiados tal cual de las plantillas (con saltos de línea **LF**: con CRLF Bash falla):

| Destino | Plantilla | Qué hace |
|---|---|---|
| `C:\Users\<usuario>\.bashrc` | [`bashrc`](../installer/plantillas/bashrc) | Solo en shells interactivos (no ensucia la salida de herramientas como la Bash de Claude Code); añade Starship al PATH si el PATH heredado aún no lo tiene; fija `STARSHIP_CONFIG` en el perfil local (por si `HOME` es otra unidad) y ejecuta `starship init bash`. No lleva el usuario escrito: sirve en cualquier laptop. |
| `C:\Users\<usuario>\.bash_profile` | [`bash_profile`](../installer/plantillas/bash_profile) | Los shells de login (`bash --login`) leen este archivo y no `.bashrc`: lo carga. |
| `C:\Users\<usuario>\.config\starship.toml` | [`starship.toml`](../installer/plantillas/starship.toml) | El estilo del prompt (UTF-8; contiene el carácter `➜`). |

Copiarlos a mano desde la raíz del repo (Git Bash):

```bash
cp installer/plantillas/bashrc ~/.bashrc
cp installer/plantillas/bash_profile ~/.bash_profile
mkdir -p ~/.config && cp installer/plantillas/starship.toml ~/.config/starship.toml
```

El repo tiene un `.gitattributes` que mantiene LF en `installer/plantillas/`, aunque Git para Windows convierta a CRLF el resto.

Los colores exactos de cian/magenta/rojo/gris salen del **tema de Herdr** (paleta `ansi` del tema activo),
no de Starship.

## Paso 4: solo si `HOME` NO es el perfil local (caso `U:\`)

Se crean dos archivos mínimos **en el `HOME` real** (p. ej. `U:\`) que cargan el `.bashrc` del perfil local.
Así el contenido sigue en un solo sitio (`C:`) y en la unidad de red solo quedan unas líneas.
Comprueba antes que no existan ya (`Test-Path U:\.bashrc`, `U:\.bash_profile`); si existen, añade las líneas
al final en vez de sobrescribir.

`U:\.bash_profile`:

```bash
[ -f ~/.bashrc ] && . ~/.bashrc
```

`U:\.bashrc`:

```bash
# HOME apunta a U:\ (carpeta de red). La configuracion real vive en el perfil local (C:\Users\<usuario>\.bashrc).
# Solo se enlaza si HOME no es ya el perfil local (evita bucle) y el archivo existe.
_win_home="$(cygpath -u "$USERPROFILE")"
[ "$HOME" != "$_win_home" ] && [ -f "$_win_home/.bashrc" ] && . "$_win_home/.bashrc"
unset _win_home
```

Efectos: cualquier Git Bash que arranque con ese `HOME` (el de Herdr, el del menú Inicio, el de VS Code)
carga Starship, y `.gitconfig`, `.ssh` e historial siguen siendo los de siempre. Los archivos viven en la
unidad de red: sin red, Bash ya tenía ese `HOME` roto de antes.

## Paso 5: lanzar Git Bash desde Herdr

Herdr envuelve el `argv` en `powershell.exe -NoExit -Command & '...'`. Con la ruta larga
(`C:/Program Files/...`) la comprobación de "instalado" del menú "+" daba `installed=False` y no mostraba la
entrada. La ruta corta 8.3 (sin espacios) funcionó:

```powershell
(New-Object -ComObject Scripting.FileSystemObject).GetFile("C:\Program Files\Git\bin\bash.exe").ShortPath
# C:\PROGRA~1\Git\bin\bash.exe     (usa barras / en los JSON)
```

Si el equipo tiene los nombres 8.3 desactivados, esa orden devuelve la ruta larga; en ese caso hay que
comprobar si la entrada del menú sale como instalada.

`argv` = `["C:/PROGRA~1/Git/bin/bash.exe", "--login", "-i"]` (el mismo en todas las laptops).

### Entrada en el menú "+" de la barra de pestañas

`C:\Users\<usuario>\.config\herdr-app\programs.json` (se aplica en vivo; si el JSON es inválido, Herdr lo dice
en `programs.error`): contenido de la plantilla [`programs.json`](../installer/plantillas/programs.json). Si ya tienes otros programas
en ese archivo, añade solo la entrada `git-bash` dentro de `programs` (el instalador lo hace así).

PowerShell sigue siendo la terminal por defecto (atajos y fila "Terminal"); Git Bash se abre desde su entrada del
menú "+". Hacer de Git Bash la terminal por defecto se probó y se descartó: ver
[Probado y descartado](#probado-y-descartado-git-bash-como-terminal-por-defecto-en-herdr).

## Paso 6: comprobar

1. **Reinicia Herdr** (carga la fuente y el PATH nuevo).
2. Abre una pestaña nueva: menú "+" → Git Bash. Las pestañas abiertas antes no cambian.
3. Debe salir el directorio y la flecha `➜`. Entra en un repo (`cd /c/ruta/de/un/repo`) y debe aparecer
   `on  main`. Si el icono sale como cuadrado o hueco, la fuente no se cargó (reinicia Herdr y revisa el
   nombre de familia del Paso 2).
4. Dentro de esa pestaña: `echo $HOME` (en el trabajo `/u/`, en casa `/c/Users/<usuario>`) y
   `git config --global user.name` (debe seguir saliendo tu nombre).
5. Guarda no interactiva: `"/c/Program Files/Git/bin/bash.exe" --login -c 'type -t starship'` **no debe
   imprimir nada**.

Alternativa sin hacer clic: `herdr-app do tab.new '{"name":"Git Bash test","argv":["C:/PROGRA~1/Git/bin/bash.exe","--login","-i"]}'`
y `herdr-app shot ruta.png` para capturar la ventana.

## Paso 7: Git Bash independiente (mintty) y VS Code

El **prompt** funciona igual fuera de Herdr (con el Paso 4 si hace falta), porque lo da `.bashrc`. Lo que **no se
hereda** es el aspecto: la fuente y los colores de Herdr solo valen dentro de Herdr.

**Qué es mintty:** el programa que dibuja la **ventana** del Git Bash independiente (el del menú Inicio, o el que
abre `git-bash.exe`). Bash ejecuta los comandos; mintty es la terminal donde se ven. Viene con Git for Windows
(`C:\Program Files\Git\usr\bin\mintty.exe`) y se configura con `~/.minttyrc`. Dentro de Herdr no se usa mintty:
ahí Herdr dibuja la terminal. Sin los pasos siguientes, el icono de la rama sale como cuadrado en mintty.

### 7a. Instalar la fuente en Windows (solo para el usuario, sin administrador)

mintty no lee la carpeta `fonts/` de Herdr: la fuente tiene que estar instalada en Windows. Se copian los mismos
`.ttf` del Paso 2 a la carpeta de fuentes del usuario y se registran en `HKCU`:

```powershell
$src = "$env:USERPROFILE\.config\herdr-app\fonts"            # donde ya estan los .ttf del Paso 2
$dst = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
New-Item -ItemType Directory -Force $dst | Out-Null
$reg = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
foreach ($f in @(@('FiraCodeNerdFontMono-Regular.ttf','FiraCode Nerd Font Mono Regular (TrueType)'),
                 @('FiraCodeNerdFontMono-Bold.ttf',   'FiraCode Nerd Font Mono Bold (TrueType)'))) {
    Copy-Item "$src\$($f[0])" "$dst\$($f[0])" -Force
    New-ItemProperty -Path $reg -Name $f[1] -Value "$dst\$($f[0])" -PropertyType String -Force | Out-Null
}
```

Comprobar en un proceso **nuevo** (los ya abiertos no ven la fuente):

```powershell
Add-Type -AssemblyName System.Drawing
(New-Object System.Drawing.Text.InstalledFontCollection).Families | Where-Object { $_.Name -like '*FiraCode Nerd*' }
# FiraCode Nerd Font Mono
```

### 7b. `~/.minttyrc` con la fuente y los colores del tema de Herdr

La ruta es `~/.minttyrc`, y `~` es **el `HOME` del Paso 0**: `C:\Users\<usuario>\.minttyrc` en un equipo normal,
`U:\.minttyrc` en el equipo con carpeta de red. Si ya existe, no lo sobrescribas: añade o cambia solo estas claves.
El contenido está en la plantilla [`minttyrc`](../installer/plantillas/minttyrc) (fuente `FiraCode Nerd Font Mono`, `FontHeight=12` y
los colores del tema `ocean-high-contrast` de Herdr, `~/.config/herdr-app/themes/ocean-high-contrast.json`, pasados
de `#rrggbb` a `r,g,b`). El instalador solo cambia o añade esas claves y conserva las demás que tengas.

Con otro tema de Herdr, convierte sus 16 colores `ansi` (índices 0 a 7 → `Black`…`White`, 8 a 15 → `BoldBlack`…`BoldWhite`).
`FontHeight=12` (puntos) equivale aproximadamente a los 16 px de Herdr; ajústalo si se ve pequeño o grande.
mintty lee el archivo **al arrancar**: cierra el Git Bash abierto y abre uno nuevo. mintty ignora en silencio las
claves que no conoce. Puede no verse idéntico a Herdr (suavizado y espaciado propios de mintty).

### 7c. (Opcional) Que el Git Bash del menú Inicio arranque en otra carpeta

El acceso directo "Git Bash" que instala Git arranca con `--cd-to-home` y "Iniciar en" `%HOMEDRIVE%%HOMEPATH%`:
siempre empieza en `~`. Si `~` es una unidad de red (`U:\`) y quieres empezar en `C:\`, ese acceso directo es de
todos los usuarios y no se puede cambiar sin administrador. Se crea uno propio (sin `--cd-to-home`, y con
"Iniciar en" la carpeta que quieras; sin ese argumento Git Bash arranca donde diga "Iniciar en"):

```powershell
$sh  = New-Object -ComObject WScript.Shell
$lnk = Join-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs" 'Git Bash (C).lnk'
$l = $sh.CreateShortcut($lnk)
$l.TargetPath       = 'C:\Program Files\Git\git-bash.exe'
$l.Arguments        = ''
$l.WorkingDirectory = 'C:\'                     # o la carpeta de proyectos que prefieras
$l.IconLocation     = 'C:\Program Files\Git\git-bash.exe,0'
$l.Save()
```

`HOME` no cambia (`.gitconfig`, `.ssh`, `.bashrc` y `.minttyrc` siguen siendo los de `~`); solo cambia la carpeta de
inicio. Los anclajes que ya tuvieras en el menú Inicio o la barra de tareas siguen usando el acceso directo viejo:
hay que anclar el nuevo.

### 7d. Terminal de VS Code

Para que la terminal integrada abra Git Bash con Starship, en el `settings.json` de usuario
(`%APPDATA%\Code\User\settings.json`) hacen falta tres claves de primer nivel (la fuente requiere el 7a):

```json
"terminal.integrated.defaultProfile.windows": "Git Bash",
"terminal.integrated.profiles.windows": {
    "Git Bash": {
        "path": "C:/Program Files/Git/bin/bash.exe",
        "args": ["--login", "-i"],
        "icon": "terminal-bash"
    }
},
"terminal.integrated.fontFamily": "FiraCode Nerd Font Mono",
```

- VS Code trae por defecto `Command Prompt` (o PowerShell): ahí Starship no aparece, aunque `.bashrc` esté bien.
- El perfil se define a mano con `--login -i` para no depender del que VS Code detecta solo.
- Escribe la ruta con barras `/`. Con `\` sin duplicar (`"C:\Program Files\..."`) el JSON deja de ser válido y
  VS Code ignora el archivo entero.
- Si `terminal.integrated.profiles.windows` ya existe, añade `"Git Bash"` dentro en vez de crear otra clave igual.
- Las terminales ya abiertas no cambian: abre una nueva (y reinicia VS Code si el icono de la rama sale como cuadrado).

## Probado y descartado: Git Bash como terminal por defecto en Herdr

Herdr **no tiene opción de "shell por defecto"**: cuando una acción no lleva `argv`, el core abre PowerShell. Para
que todo abriera Git Bash hubo que tocar dos sitios:

- `keys.json`, sección `global`: poner `argv` en `ctrl-shift-t` (`tab.new`), `ctrl-shift-n` (`space.new`) y
  `ctrl-shift-o` / `ctrl-shift-e` (`pane.split`), con la forma
  `{"command": "tab.new", "args": {"argv": ["C:/PROGRA~1/Git/bin/bash.exe", "--login", "-i"]}}`.
- Los mods `mods/new-menu/main.js` (fila "Terminal" del menú "+") y `mods/menu/main.js` ("New tab" del clic
  derecho), añadiendo el mismo `argv` a su `run("tab.new", ...)`.

Funcionó, pero se deshizo y **no se recomienda**:

- Esos mods son de Herdr y **se sobrescriben al actualizar** (la prueba coincidió con una actualización a 0.1.13).
- Al editar `keys.json`, Herdr deja de añadirle atajos nuevos en futuras versiones.
- Editarlos con `sed -i` desde Git Bash **cambia CRLF por LF** en todo el archivo. Para deshacer, hubo que
  restaurar las copias originales byte a byte.

Se dejó PowerShell por defecto y Git Bash solo en el menú "+" (Paso 5). El instalador no toca `keys.json` ni los mods.

## Problemas conocidos

| Síntoma | Causa | Solución |
|---|---|---|
| Git Bash abre con el prompt por defecto (`usuario@PC UCRT64 C:\...` y `$`) | `HOME` apunta a otra unidad (`U:\`) y no encuentra `~/.bashrc` | Paso 4. **No** forzar `HOME` (pierde `.gitconfig`) |
| `git config --global user.name` sale vacío en Git Bash | `HOME` forzado a otra carpeta | Quitar el `HOME` forzado; usar Paso 4 |
| Cuadrado o hueco donde va el icono de la rama | La fuente de esa terminal no es Nerd Font | Paso 2 y reiniciar Herdr (en mintty o VS Code, Paso 7) |
| La entrada Git Bash no aparece en el menú "+" (`installed=False`) | Ruta con espacios en `run` | Usar la ruta corta 8.3 |
| `starship: command not found` en Bash | PATH heredado de antes de instalar Starship | Reiniciar Herdr; el `.bashrc` ya trae respaldo |
| Starship sale con el estilo por defecto | No encuentra `starship.toml` (HOME en otra unidad) | `STARSHIP_CONFIG` del `.bashrc` del Paso 3 |
| `herdr-app do ...` falla con `args are not JSON` en PowerShell 5.1 | PowerShell se come las comillas dobles del JSON | Ejecutarlo desde Bash (o `!` en Claude Code) |
| En pestañas Git Bash, Claude no se reanuda solo tras reiniciar Herdr | Esas pestañas no ejecutan el perfil de PowerShell | Abrir esas pestañas como PowerShell |
| `=>` no se dibuja como flecha (ligaduras) | El terminal de Herdr no dibuja ligaduras con ninguna fuente | Sin solución; no existe opción en Herdr |
| La terminal de VS Code no muestra Starship | El perfil por defecto es `Command Prompt` o PowerShell | Paso 7d (`defaultProfile.windows` = `"Git Bash"`) y abrir una terminal nueva |
| VS Code ignora todo `settings.json` tras editarlo | Ruta con `\` sin duplicar dentro del JSON | Usar barras `/` en `path` |
| Bash da errores raros con `\r` al arrancar | `.bashrc` guardado con CRLF | Guardarlo con LF (las plantillas ya lo están; `.gitattributes` lo mantiene) |

## Cómo deshacerlo

Si usaste `python instalar.py`, cada archivo que existía antes y se cambió está copiado en
`~/.claude-tools-backup/<fecha-hora>/`, con su ruta relativa al perfil (por ejemplo
`AppData/Roaming/Code/User/settings.json`): basta con copiarlo de vuelta. Los archivos que no existían no tienen copia.

- Borra `~/.bashrc` y `~/.bash_profile` del perfil local (si no existían antes), el `starship.toml` y, si hiciste el
  Paso 4, `U:\.bashrc` y `U:\.bash_profile` (si no existían antes).
- En `settings.json` vuelve `font` a la anterior y borra los `.ttf` de la carpeta `fonts/`.
- Si hiciste el Paso 7: borra `~/.minttyrc` (si no existía antes), el acceso directo `Git Bash (C).lnk` del menú Inicio,
  y las dos fuentes de `%LOCALAPPDATA%\Microsoft\Windows\Fonts` junto con sus valores `FiraCode Nerd Font Mono *`
  en `HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts`.
- Quita la entrada `git-bash` de `programs.json`.
- VS Code: quita las tres claves del Paso 7d (o vuelve `defaultProfile.windows` a `"Command Prompt"`).
- `winget uninstall Starship.Starship`.
