# Skills

Skills en formato `SKILL.md` (estándar "Agent Skills"). El mismo archivo funciona sin cambios en **Claude Code** y en **opencode**: solo hay que copiar la carpeta al lugar correcto.

## Skills disponibles

| Skill | Qué hace |
| --- | --- |
| [`entrevistador-procesos`](entrevistador-procesos) | Te entrevista para definir con claridad un proceso, workflow, automatización o proyecto antes de construirlo. |
| [`humanizador`](humanizador) | Reescribe textos generados por IA para que suenen naturales, directos y creíbles. |
| [`optimizador-prompts`](optimizador-prompts) | Convierte ideas desordenadas o prompts flojos en prompts claros y estructurados para cualquier herramienta de IA. |
| [`presentaciones-visuales`](presentaciones-visuales) | Crea presentaciones HTML modernas, listas para el navegador, a partir de una idea o documento. |
| [`superpowers`](superpowers) | Modo de trabajo riguroso para proyectos complejos: entender, planificar, detectar riesgos y recién después construir. |
| [`verificador-datos`](verificador-datos) | Revisa textos y comprueba si sus afirmaciones son correctas, exageradas o no verificables. |

> **Ojo con `superpowers`:** si ya tienes instalado el plugin `superpowers` en Claude Code, el nombre colisiona. En ese caso no la instales. En opencode no hay problema.

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
Copy-Item -Recurse -Force .\entrevistador-procesos, .\humanizador, .\optimizador-prompts, .\presentaciones-visuales, .\verificador-datos, .\superpowers "$env:USERPROFILE\.claude\skills\"
```

Bash / Git Bash / macOS / Linux:

```bash
mkdir -p ~/.claude/skills
cp -r entrevistador-procesos humanizador optimizador-prompts presentaciones-visuales verificador-datos superpowers ~/.claude/skills/
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

Usa la carpeta `skill/` (singular):

- **Global**: `~/.config/opencode/skill/` → en Windows `%USERPROFILE%\.config\opencode\skill\`
- **Un solo proyecto**: `skill/` en la raíz del proyecto

PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\opencode\skill" | Out-Null
Copy-Item -Recurse -Force .\entrevistador-procesos, .\humanizador, .\optimizador-prompts, .\presentaciones-visuales, .\verificador-datos, .\superpowers "$env:USERPROFILE\.config\opencode\skill\"
```

Bash:

```bash
mkdir -p ~/.config/opencode/skill
cp -r entrevistador-procesos humanizador optimizador-prompts presentaciones-visuales verificador-datos superpowers ~/.config/opencode/skill/
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
   cp -r entrevistador-procesos humanizador optimizador-prompts presentaciones-visuales verificador-datos superpowers ~/.opencode/skills/
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
