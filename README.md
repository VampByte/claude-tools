# claude-tools

Colección de utilidades (mods) para Claude Code: herramientas para Claude. Cada mod vive en su propia carpeta dentro de `plugins/` y se instala por separado desde este marketplace.

## Mods

| Mod | Qué hace |
| --- | --- |
| [`clean-view`](plugins/clean-view) | Vista simple: panel de pasos en español sobre el cuadro de texto, filas técnicas de herramientas ocultas y comando `/simple`. |

## Skills

Además de los mods, el repo incluye 5 skills (`SKILL.md`) reutilizables en Claude Code y opencode: `entrevistador-procesos`, `humanizador`, `optimizador-prompts`, `presentaciones-visuales` y `verificador-datos`. Lista y manual de instalación en [`skills/README.md`](skills/README.md).

## Instalación

En una sesión de terminal:

```
/plugin install clean-view --marketplace vampbyte/claude-tools
```

Desde un shell:

```
claude plugin install clean-view --marketplace vampbyte/claude-tools
```

En la app de escritorio, donde `/plugin` no funciona: pulsa **+** junto al cuadro de texto, luego **Plugins**, **Add marketplace** con `vampbyte/claude-tools` y por último **Add plugin**.

Al instalar, responde `y` a "Add marketplace?" y elige el alcance (usuario). Para ver los mods disponibles, abre `/plugin` y busca el marketplace `claude-tools`.

## Añadir un mod nuevo

1. Crea `plugins/<nombre>/` con `.claude-plugin/plugin.json`, `hooks/hooks.json` y su módulo de hooks.
2. Agrégalo a `.claude-plugin/marketplace.json` con `"source": "./plugins/<nombre>"`.
3. Valida con `claude plugin validate plugins/<nombre>` y prueba con `claude plugin test plugins/<nombre>`.
