# Skills

Skills en formato `SKILL.md` (estándar "Agent Skills"). El mismo archivo funciona sin cambios en **Claude Code** y en **opencode**: solo hay que copiar la carpeta al lugar correcto.

## Skills disponibles

| Skill | Qué hace |
| --- | --- |
| [`entrevistador-procesos`](entrevistador-procesos) | Te entrevista para definir con claridad un proceso, workflow, automatización o proyecto antes de construirlo. |
| [`humanizador`](humanizador) | Reescribe textos generados por IA para que suenen naturales, directos y creíbles. |
| [`optimizador-prompts`](optimizador-prompts) | Convierte ideas desordenadas o prompts flojos en prompts claros y estructurados para cualquier herramienta de IA. |
| [`presentaciones-visuales`](presentaciones-visuales) | Crea presentaciones HTML modernas, listas para el navegador, a partir de una idea o documento. |
| [`jsk-opencode`](jsk-opencode) | Delega tareas sencillas a MiniMax-M3 vía `opencode run` para ahorrar tokens; Claude revisa siempre el resultado. Solo Claude Code (requiere `opencode` instalado); se invoca con `/jsk-opencode`. |
| [`verificador-datos`](verificador-datos) | Revisa textos y comprueba si sus afirmaciones son correctas, exageradas o no verificables. |
| [`presentacion-proyecto`](presentacion-proyecto) | Genera una infografía ejecutiva de una página o un video corto con voz de un proyecto, para presentarlo a Gerencia. Se distribuye como zip y sirve en Claude.ai (recomendado) y Claude Code; el instalador lo copia como carpeta. Instrucciones en [`INSTALACION.md`](presentacion-proyecto/INSTALACION.md). |

> **`superpowers` no está aquí.** Es un plugin del marketplace de Claude Code; instálalo desde ahí en vez de copiar una skill:
>
> ```
> /plugin install superpowers@anthropic-plugin-directory
> ```
>
> No hay equivalente en este repo para opencode.

> **Atajo:** desde la raíz del repo, `python instalar.py` y las opciones **1** (Claude Code) y **2** (opencode)
> copian las skills por ti, muestran cuáles ya están y actualizan las que cambiaron (guardando antes una copia
> en `~/.claude-tools-backup/`). Lo de abajo es para hacerlo a mano.

## Skills de terceros (instaladas, no incluidas en el repo)

Skills que uso pero que no se copian aquí: tienen varios archivos propios y las mantiene su autor. Se instalan desde su origen.

| Skill | Qué hace | Origen | Licencia |
| --- | --- | --- | --- |
| `hallmark` (v2.0.0) | Diseño de sitios y páginas nuevas para que se vean diseñados y no generados: dirección visual, tokens de color y tipografía, y un linter (`sloplint`) que revisa el resultado. | [Nutlope/hallmark](https://github.com/Nutlope/hallmark) | MIT |
| `impeccable` (v4.7.0) | Diseño y mejora de interfaces: diseñar, rediseñar, criticar, auditar, pulir, simplificar o animar sitios, dashboards, componentes y pantallas móviles; también documenta sistemas de diseño (`DESIGN.md`). | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Sin verificar (no trae `LICENSE` en la copia instalada) |

**impeccable**
- Se activa sola ante pedidos de diseño o mejora de interfaces (UX, jerarquía, tipografía, color, movimiento, accesibilidad, responsive), o con `/impeccable`.
- Está en `~/.claude/skills/impeccable`, que es un enlace a `~/.agents/skills/impeccable` y, de ahí, a la carpeta de Skillshare (`%APPDATA%\skillshare\skills\impeccable`). Contiene `SKILL.md`, `reference/`, `agents/` y `scripts/`. Registrada en `~/.agents/.skill-lock.json` con origen `pbakaus/impeccable`, instalada el 2026-10-20.
- Al iniciar ejecuta `scripts/impeccable context`, un binario propio que se descarga solo en el primer uso (sin Node) y lee `PRODUCT.md` y `DESIGN.md` del proyecto.
- Para actualizarla, hazlo desde su origen o con Skillshare; no edites los archivos a mano.

**hallmark**
- Se invoca con `/hallmark <prompt>`, `/hallmark redesign <ruta>` o `/hallmark audit <ruta>`. Sin nombrarla, solo actúa en páginas nuevas, nunca sobre un diseño existente.
- Quedó en `~/.claude/skills/hallmark/` (`SKILL.md`, `references/`, `scripts/`, `agents/`), registrada en `~/.agents/.skill-lock.json` con el commit `04977e1`. Eso indica que se instaló con el instalador de skills (`npx skills add Nutlope/hallmark`); el comando exacto no está verificado.
- Para actualizarla, vuelve a instalarla desde el origen; no edites los archivos a mano.
- Opcional: con `TOGETHER_API_KEY` definida, usa el paso de maquetas con Together AI. Con Node disponible, corre `scripts/sloplint.mjs` al terminar. Declara soporte para opencode (`opencode/slash`).

## Obtener las skills

```bash
git clone https://github.com/vampbyte/claude-tools.git
cd claude-tools/skills
```

(Si ya tienes el repo, basta con entrar en la carpeta `skills/`.)

## Claude Code

Claude Code busca skills en carpetas `skills/<nombre>/SKILL.md`:

- **Global** (todos los proyectos): `~/.claude/skills/` → en Windows `%USERPROFILE%\.claude\skills\`
- **Un solo proyecto**: `.claude/skills/` en la raíz del proyecto

### Instalar todas (global)

PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force .\entrevistador-procesos, .\humanizador, .\jsk-opencode, .\optimizador-prompts, .\presentaciones-visuales, .\verificador-datos "$env:USERPROFILE\.claude\skills\"
```

Bash / Git Bash / macOS / Linux:

```bash
mkdir -p ~/.claude/skills
cp -r entrevistador-procesos humanizador jsk-opencode optimizador-prompts presentaciones-visuales verificador-datos ~/.claude/skills/
```

### Instalar solo una (o en un proyecto)

```bash
# una skill, global
cp -r humanizador ~/.claude/skills/

# una skill, solo para el proyecto actual
mkdir -p .claude/skills && cp -r humanizador .claude/skills/
```

### Verificar

Abre una sesión **nueva** de Claude Code (las skills se leen al iniciar) y pide algo que la dispare, por ejemplo: *"humaniza este texto: ..."*. También deberían aparecer al escribir `/`. Claude las activa solo, por la `description` de cada una.

## opencode

La carpeta de destino depende de tu versión de opencode.

### Opción A — Soporte nativo (opencode ≥ 1.0.190, recomendado)

Usa la carpeta `skills/` (**plural**):

- **Global**: `~/.config/opencode/skills/` → en Windows `%USERPROFILE%\.config\opencode\skills\`
- **Un solo proyecto**: `skill/` en la raíz del proyecto (sin comprobar con la versión actual)

> Las versiones actuales de opencode usan `skills/`. En la laptop de casa ya existía `~/.config/opencode/skills/`
> (con las skills `gsd-*` e `impeccable`) y no había `skill/`. Algunas versiones antiguas usaban `skill/` (singular):
> si `skills/` no existe y sí existe `skill/`, cópialas ahí.

PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\opencode\skills" | Out-Null
Copy-Item -Recurse -Force .\entrevistador-procesos, .\humanizador, .\optimizador-prompts, .\presentaciones-visuales, .\verificador-datos "$env:USERPROFILE\.config\opencode\skills\"
```

Bash:

```bash
mkdir -p ~/.config/opencode/skills
cp -r entrevistador-procesos humanizador optimizador-prompts presentaciones-visuales verificador-datos ~/.config/opencode/skills/
```

Permisos (opcional) en `opencode.json`, para permitir solo algunas:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "skill": {
      "humanizador": "allow",
      "verificador-datos": "allow",
      "*": "deny"
    }
  }
}
```

### Opción B — Plugin `opencode-skills` (opencode anterior a 1.0.190)

1. Añade el plugin en `opencode.json` (`~/.config/opencode/opencode.json` o el del proyecto):

   ```json
   {
     "$schema": "https://opencode.ai/config.json",
     "plugin": ["opencode-skills"]
   }
   ```

2. Copia las carpetas a `.opencode/skills/` (plural, con punto):

   ```bash
   mkdir -p ~/.opencode/skills        # global
   cp -r entrevistador-procesos humanizador optimizador-prompts presentaciones-visuales verificador-datos ~/.opencode/skills/
   ```

   Para un proyecto: `.opencode/skills/` en su raíz.

3. Control de acceso (opcional):

   ```json
   { "tools": { "skills*": false, "skills_humanizador": true } }
   ```

### Verificar

Abre opencode en cualquier proyecto (sesión nueva) y pide, por ejemplo, *"humaniza este texto: ..."*. Si la skill está bien colocada, opencode la detecta por su `description`.

## Problemas frecuentes

- **No aparece la skill:** el archivo debe quedar en `<carpeta-skills>/<nombre>/SKILL.md` (un nivel, no `<nombre>/<nombre>/SKILL.md`). Reinicia la sesión.
- **Mala ruta en Windows:** `~` no se expande en PowerShell/cmd; usa `$env:USERPROFILE`.
- **Migrar de plugin a nativo en opencode:** mueve `.opencode/skills` → `skill` y cambia `tools` por `permission.skill`; los `SKILL.md` no se tocan.
