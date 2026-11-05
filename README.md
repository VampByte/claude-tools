# claude-tools

Colección de utilidades (mods) para Claude Code: herramientas para Claude. Cada mod vive en su propia carpeta dentro de `plugins/` y se instala por separado desde este marketplace.

## Mods

| Mod | Qué hace |
| --- | --- |
| [`clean-view`](plugins/clean-view) | Vista simple: panel de pasos en español sobre el cuadro de texto, filas técnicas de herramientas ocultas y comando `/simple`. |

## Skills

Además de los mods, el repo incluye 6 skills (`SKILL.md`) para Claude Code (todas menos `jsk-opencode` también sirven en opencode): `entrevistador-procesos`, `humanizador`, `jsk-opencode`, `optimizador-prompts`, `presentaciones-visuales` y `verificador-datos`. Lista y manual de instalación en [`skills/README.md`](skills/README.md).

## Guías

- [`docs/herdr-git-bash-starship.md`](docs/herdr-git-bash-starship.md): Git Bash con prompt Starship en Windows, paso a paso: Herdr app, Git Bash independiente (mintty) y VS Code.

## Instalador

Para instalar todo (o solo una parte) en una laptop nueva, desde la raíz del repo:

```
python instalar.py
```

Muestra un menú con el estado de cada opción y te deja elegir con números (`1 3`, `todo` o `q`):

1. Skills de Claude Code (las 6, en `~/.claude/skills/`)
2. Skills de opencode (5, en `~/.config/opencode/skills/`)
3. Mod `clean-view`
4. Starship y terminales: Herdr, mintty, el acceso directo "Git Bash (C)" y VS Code. Es lo de la
   [guía](docs/herdr-git-bash-starship.md), que pide Git, Herdr y VS Code (si falta alguno, avisa)

Se puede repetir sin problemas: lo que ya está no se toca. Antes de cambiar un archivo existente, guarda una copia en
`~/.claude-tools-backup/<fecha-hora>/`. Requiere Python 3.10 o superior (`winget install Python.Python.3.13` si no
está); solo usa la biblioteca estándar y por ahora solo funciona en Windows.

Tests: `python -m unittest` (desde la raíz del repo).

## Instalación del mod a mano

En una sesión de terminal:

```
/plugin install clean-view --marketplace vampbyte/claude-tools
```

Desde un shell, en dos pasos (es lo que hace el instalador):

```
claude plugin marketplace add vampbyte/claude-tools
claude plugin install clean-view@claude-tools --scope user
```

En la app de escritorio, donde `/plugin` no funciona: pulsa **+** junto al cuadro de texto, luego **Plugins**, **Add marketplace** con `vampbyte/claude-tools` y por último **Add plugin**.

Al instalar, responde `y` a "Add marketplace?" y elige el alcance (usuario). Para ver los mods disponibles, abre `/plugin` y busca el marketplace `claude-tools`.

## Añadir un mod nuevo

1. Crea `plugins/<nombre>/` con `.claude-plugin/plugin.json`, `hooks/hooks.json` y su módulo de hooks.
2. Agrégalo a `.claude-plugin/marketplace.json` con `"source": "./plugins/<nombre>"`.
3. Valida con `claude plugin validate plugins/<nombre>` y prueba con `claude plugin test plugins/<nombre>`.
