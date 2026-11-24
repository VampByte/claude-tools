# claude-tools

Colección de utilidades (mods) para Claude Code: herramientas para Claude. Cada mod vive en su propia carpeta dentro de `plugins/` y se instala por separado desde este marketplace.

## Mods

| Mod | Qué hace |
| --- | --- |
| [`clean-view`](plugins/clean-view) | Vista simple: panel de pasos en español sobre el cuadro de texto, filas técnicas de herramientas ocultas y comando `/simple`. |
| [`image-preview`](plugins/image-preview) | Miniatura de la imagen que pegas en el prompt, antes de enviarla (Windows, terminal con gráficos kitty). Guía: [`docs/image-preview.md`](docs/image-preview.md). |

## Skills

Además de los mods, el repo incluye 7 skills (`SKILL.md`) para Claude Code (todas menos `jsk-opencode` también sirven en opencode): `entrevistador-procesos`, `humanizador`, `jsk-opencode`, `optimizador-prompts`, `presentacion-proyecto`, `presentaciones-visuales` y `verificador-datos`. Lista y manual de instalación en [`skills/README.md`](skills/README.md), que también documenta las skills de terceros instaladas (por ahora `hallmark` e `impeccable`).

## Guías

- [`docs/herdr-git-bash-starship.md`](docs/herdr-git-bash-starship.md): Git Bash con prompt Starship en Windows, paso a paso: Herdr app, Git Bash independiente (mintty) y VS Code.
- [`docs/image-preview.md`](docs/image-preview.md): instalar el mod `image-preview` (miniatura de imágenes pegadas) en otro portátil Windows.

## Instalador

Para instalar todo (o solo una parte) en una laptop nueva, desde la raíz del repo:

```
python instalar.py
```

Muestra un menú con el estado de cada opción y te deja elegir con números (`1 3`, `todo` o `q`):

1. Skills de Claude Code (7, en `~/.claude/skills/`): después de elegirla, te deja escoger cuáles
2. Skills de opencode (6, en `~/.config/opencode/skills/`): igual, con selección de cuáles
3. Mod `clean-view`
4. Starship y terminales: Herdr, mintty, el acceso directo "Git Bash (C)" y VS Code. Es lo de la
   [guía](docs/herdr-git-bash-starship.md), que pide Git, Herdr y VS Code (si falta alguno, avisa)
5. y 6. Skills de terceros `hallmark` e `impeccable` (ver [`skills/README.md`](skills/README.md)): abre Claude Code con un
   prompt que las instala siguiendo el README de su repositorio. Hay que salir con `/exit` para que el menú continúe

**Desinstalar:** escribe `d` en el menú, elige las opciones y confirma. Las skills y las partes de Starship te dejan
escoger cuáles quitar. Solo se borra lo que puso el instalador: un `.bashrc` o `.bash_profile` con cambios tuyos se
conserva, y las claves de VS Code, Herdr y mintty se quitan una a una sin tocar el resto. Starship y la fuente se
desinstalan con `winget` y borrando los `.ttf`. De lo borrado queda copia en `~/.claude-tools-backup/`.

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
