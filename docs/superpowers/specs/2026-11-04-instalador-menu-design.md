# Instalador por menú + registro de pasos extra (claude-tools)

## Contexto

En las dos últimas sesiones se instaló a mano en esta laptop todo lo que trae el repo: 6 skills de Claude Code, 5 de opencode, el mod `clean-view`, y Starship con Git Bash en Herdr, mintty y VS Code. Durante la instalación aparecieron pasos que la documentación no recoge o recoge mal:
- La carpeta de skills de opencode es `skills/` (en plural).
- El mod se instala con `claude plugin marketplace add` y luego `claude plugin install`.
- Faltaban el acceso directo "Git Bash (C)" y el perfil de Git Bash por defecto en VS Code.
- Se probó y se descartó poner Git Bash como terminal por defecto en Herdr.

Objetivo:
1. Dejar esos pasos escritos en el repo.
2. Añadir `python instalar.py`, un menú por consola que muestre qué está instalado y permita elegir qué instalar en la próxima laptop.

Decisiones ya tomadas con el usuario:
- Python, solo biblioteca estándar.
- Menú de lista numerada.
- 4 opciones: skills de Claude Code, skills de opencode, `clean-view` y "Starship y terminales".
- "Starship y terminales" es una sola opción, con aviso si faltan Git, Herdr o VS Code.
- Las plantillas tienen una sola copia, en `installer/plantillas/`, y la guía enlaza a ellas.
- Solo Windows (el uso es personal y los equipos tienen Git, Herdr y VS Code).

## Estructura

```
instalar.py                       # punto de entrada: python instalar.py
installer/
  __init__.py
  menu.py                         # dibuja la lista con estado, lee "1 3" / "todo" / "q", confirma
  comun.py                        # Rutas, backup(), escribir_conservando_eol(), winget(), jsonc_set(), which()
  componentes/
    __init__.py                   # lista ordenada COMPONENTES
    skills.py                     # SkillsClaude (6 a ~/.claude/skills/) y SkillsOpencode (5, sin jsk-opencode)
    clean_view.py                 # marketplace add + plugin install; estado desde installed_plugins.json
    starship.py                   # pasos 1-7 de abajo, cada uno idempotente
  plantillas/
    bashrc  bash_profile  starship.toml  minttyrc  programs.json
tests/
  test_comun.py  test_componentes.py  test_menu.py
```

Cada componente expone lo mismo:
- `nombre`
- `requisitos() -> list[str]`: los requisitos que faltan.
- `estado(rutas) -> Estado`: puede ser `instalado`, `parcial (n de m)` o `no`.
- `instalar(rutas, ui) -> list[str]`: devuelve el registro de acciones.

`Rutas` es un dataclass que se construye a partir de `USERPROFILE`, `APPDATA` y `LOCALAPPDATA`. Los tests lo crean apuntando a una carpeta temporal, sin tocar el perfil real.

## Comportamiento común (`comun.py`)

- **`backup(ruta)`:** antes de sobrescribir o editar un archivo, guarda una copia en `~/.claude-tools-backup/<AAAAMMDD-HHMMSS>/` con su ruta relativa. No usa la carpeta Temp.
- **Repetible sin efectos:** si el contenido de destino ya es igual al que se va a escribir, no hace nada ni crea copia.
- **`escribir_conservando_eol`:** detecta si el archivo existente usa CRLF o LF y lo respeta. Es la lección del `sed` que pasó CRLF a LF en `keys.json`.
- **`jsonc_set(texto, clave, valor)`:** edita claves de primer nivel del `settings.json` de VS Code, que admite comentarios. Si la clave existe, reemplaza su valor. Si no, la inserta tras `{`. Después valida el resultado quitando comentarios y comas finales antes de parsearlo, con la misma lógica que el validador usado en esta sesión. Si no valida, no escribe.
- **JSON puro** (`settings.json` y `programs.json` de Herdr): se carga, se fusiona y se vuelca con `json` e indentación de 2 espacios.
- **Requisitos:** se buscan con `shutil.which` (`git`, `herdr-app`, `code`, `claude`, `opencode`, `winget`).
- **Ruta corta de `bash.exe`:** se obtiene con `ctypes.windll.kernel32.GetShortPathNameW`. Si no hay nombres 8.3, usa la ruta larga y avisa.

## Componentes

1. **Skills de Claude Code.** Copia `skills/{entrevistador-procesos,humanizador,jsk-opencode,optimizador-prompts,presentaciones-visuales,verificador-datos}` a `~/.claude/skills/`. El estado cuenta las que ya están. Si falta `opencode`, avisa de que `jsk-opencode` lo necesita, pero la instala igual.
2. **Skills de opencode.** Las mismas 5 skills, sin `jsk-opencode`, a `~/.config/opencode/skills/`.
3. **clean-view.**
   - Requiere `claude`.
   - Ejecuta `claude plugin marketplace add vampbyte/claude-tools`, o lo omite si el marketplace ya existe.
   - Después ejecuta `claude plugin install clean-view@claude-tools --scope user`.
   - El estado sale de `~/.claude/plugins/installed_plugins.json`, buscando la clave `clean-view@claude-tools`.
4. **Starship y terminales.**
   - Requisitos: Git, Herdr y VS Code. Si falta alguno, lo dice y pregunta si seguir sin esa parte.
   - Pasos:
     1. `winget install --id Starship.Starship --exact --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity`, si `starship` no está.
     2. **Fuente:** descarga `FiraCode.zip` v3.5.1 en una carpeta nueva con `tempfile.mkdtemp()` y extrae solo `FiraCodeNerdFontMono-{Regular,Bold}.ttf` con `zipfile`. Los copia a `~/.config/herdr-app/fonts/` y a `%LOCALAPPDATA%\Microsoft\Windows\Fonts`, y los registra en `HKCU\...\Fonts` con `winreg`. Si los archivos ya están, se salta la descarga.
     3. **Archivos de shell:** `~/.bashrc`, `~/.bash_profile` y `~/.config/starship.toml`, desde las plantillas.
     4. **Herdr:** en `settings.json` pone `"font": "FiraCode Nerd Font Mono"`. En `programs.json` fusiona la entrada `git-bash` y conserva los demás programas. **No toca** `keys.json` ni los mods.
     5. **mintty:** crea `~/.minttyrc`. Si ya existe, solo cambia o añade las claves de la plantilla.
     6. **Acceso directo:** crea `Git Bash (C).lnk` en el menú Inicio del usuario, con `powershell -NoProfile -Command` y WScript.Shell. Destino `git-bash.exe`, inicio en `C:\`.
     7. **VS Code:** en `%APPDATA%\Code\User\settings.json` aplica `jsonc_set` a:
        - `terminal.integrated.defaultProfile.windows = "Git Bash"`
        - `terminal.integrated.profiles.windows["Git Bash"] = {path: "C:/Program Files/Git/bin/bash.exe", args: ["--login","-i"], icon: "terminal-bash"}`, fusionado con los perfiles que ya existan.
        - `terminal.integrated.fontFamily = "FiraCode Nerd Font Mono"`
   - El estado es "instalado" solo si los 7 pasos lo están. Si no, "parcial (n de 7)".

## Menú (`menu.py`)

```
claude-tools: instalador

  1. [x] Skills de Claude Code     (instaladas)
  2. [ ] Skills de opencode        (2 de 5)
  3. [ ] Mod clean-view            (requiere: claude)
  4. [ ] Starship y terminales     (requiere Git, Herdr, VS Code)

Elige números separados por espacio, "todo" o "q" para salir:
```

- Valida la entrada y muestra un resumen ("Se va a instalar: …").
- Pide confirmación con `s/n`.
- Ejecuta lo elegido en orden. Al final muestra el registro, la carpeta de copias de seguridad y los avisos para reiniciar: Herdr, VS Code y una sesión nueva de Claude Code.
- Si un componente falla, muestra el error y sigue con el siguiente.
- Al terminar vuelve a dibujar el estado.

## Documentación

- **`docs/herdr-git-bash-starship.md`:**
  - Al inicio, una línea: "Atajo: `python instalar.py`, opción 4".
  - Los bloques de `.bashrc`, `.bash_profile`, `starship.toml`, `.minttyrc` y `programs.json` se sustituyen por enlaces a `installer/plantillas/…`.
  - Paso 2: indicar que el `settings.json` de Herdr puede venir con otra fuente (aquí era `Cascadia Code`) y hay que reemplazarla.
  - Paso 7d ampliado: perfil explícito de Git Bash con `"path": "C:/Program Files/Git/bin/bash.exe"` y `["--login","-i"]`, `defaultProfile.windows = "Git Bash"`, rutas con `/` (con `\` sin escapar el JSON se rompe), y las terminales abiertas no cambian.
  - Nueva sección **"Probado y descartado: Git Bash como terminal por defecto en Herdr"**. Herdr no tiene opción de shell por defecto. Hace falta poner `argv` en `keys.json` (`tab.new`, `space.new`, `pane.split`) y editar `mods/new-menu/main.js` y `mods/menu/main.js`. Esos mods se sobrescriben al actualizar Herdr, y editarlos con `sed` cambia los saltos de línea. Se decidió dejar PowerShell por defecto y Git Bash solo en el menú "+".
  - "Cómo deshacerlo": mencionar la carpeta `~/.claude-tools-backup/`.
- **`skills/README.md`:** para opencode, la carpeta es `skills/` (en plural) en la versión instalada. Se deja `skill/` como alternativa, se corrige la Opción A y se añade el atajo `python instalar.py`.
- **`README.md`:**
  - Nueva sección "Instalador" con `python instalar.py` y el requisito de Python 3.10 o superior (`winget install Python.Python.3.13` si no está).
  - Instalación de `clean-view` desde un shell con los dos comandos que funcionaron: `claude plugin marketplace add vampbyte/claude-tools` y `claude plugin install clean-view@claude-tools`.
- **Spec:** se guarda este diseño en `docs/superpowers/specs/2026-11-04-instalador-menu-design.md`.

## Orden de implementación

1. Guardar el spec y hacer commit.
2. TDD de `comun.py`: `jsonc_set` (clave nueva, clave existente, comentarios, coma final), conservación de CRLF, copia de seguridad que no se repite si el contenido es igual, y `Rutas` con una carpeta de usuario temporal.
3. Plantillas copiadas tal cual de los archivos instalados hoy.
4. Componentes con sus tests de estado e instalación sobre una carpeta de usuario temporal. Las llamadas a `winget`, `claude`, la descarga, el registro y PowerShell van detrás de funciones inyectables y se simulan en los tests.
5. Menú y tests del parser de entrada (`"1 3"`, `"todo"`, números fuera de rango, `"q"`).
6. Documentación: guía, `skills/README.md` y `README.md`.
7. Un commit por bloque, con mensajes en español al estilo del repo (`feat(installer): …`, `docs: …`).

## Verificación

- `python -m unittest discover -s tests -v`: todo en verde.
- `python instalar.py` en esta laptop, donde todo está instalado:
  - Las 4 opciones deben salir como "instalado".
  - Elegir "todo" y confirmar no debe cambiar ningún archivo. Se comprueba que `~/.claude-tools-backup/` no crea carpeta nueva, o la crea vacía, y que no se modifican las fechas de `.bashrc` ni de `settings.json`.
- Prueba en una carpeta de usuario temporal (variables `USERPROFILE`, `APPDATA` y `LOCALAPPDATA` apuntando a una carpeta vacía) con las opciones 1 y 2: deben copiarse las skills y salir "instalado".
- Comprobar que el `settings.json` de VS Code sigue siendo válido con el validador de JSON con comentarios, y que `keys.json` y los mods de Herdr no cambian (comparar el hash antes y después).
