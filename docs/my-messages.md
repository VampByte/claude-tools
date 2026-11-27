# my-messages: resalta tus mensajes en el chat

Guía del mod [`my-messages`](../plugins/my-messages), que se instala desde el marketplace `claude-tools` de este repo.

## Qué hace

Redibuja **solo tus mensajes** (`ui.render` sobre `UserMessage`, con origen `composer` o `bridge`, es decir, terminal o Remote Control):

- Barra lateral ámbar `#e0a82e`.
- Fondo `#4a3b12` y texto blanco `#ffffff`.
- Una línea de padding arriba y abajo, y una línea de margen por fuera.

Las respuestas de Claude, las notificaciones y los mensajes de otras sesiones no cambian.

## Requisitos

- Claude Code con soporte de mods (probado en 2.1.331), en terminal.
- Probado en Windows dentro de Herdr app, con el plugin `skins` instalado (requiere el paso 4 de la instalación).

## Instalación en otro portátil

1. Clona el repo, o actualízalo con `git pull`:

   ```
   git clone https://github.com/VampByte/claude-tools
   ```

2. Añade la carpeta del repo como marketplace:

   ```
   claude plugin marketplace add "C:\ruta\a\claude-tools"
   ```

   Si ya lo tenías añadido, actualízalo:

   ```
   claude plugin marketplace update claude-tools
   ```

3. Instala el mod:

   ```
   claude plugin install my-messages@claude-tools
   ```

4. **Solo si tienes el plugin `skins`:** sin este paso la caja ámbar **no aparece**, porque `skins` también dibuja `UserMessage` sin llamar a `next` y queda por encima. Haz una copia de `~/.claude/settings.json` y añade en el nivel raíz del archivo:

   ```json
   "prependPlugins": ["my-messages@claude-tools"]
   ```

   Si `prependPlugins` ya existe, añade `my-messages@claude-tools` a esa lista. El id lleva el nombre del marketplace desde el que instalaste el mod. Según la documentación de mods, esta lista se ignora en planes Team/Enterprise o con ciertas políticas administradas.

5. Reinicia la sesión: sal y ejecuta `claude --resume` (o abre una nueva). Sin `skins`, basta con `/reload-plugins`. No se probó que `/reload-plugins` aplique el orden de `prependPlugins`.

## Verificación

1. `claude plugin list` muestra `my-messages` como enabled.
2. Envía un mensaje: debe verse dentro de la caja ámbar.

## Personalizar

1. Edita `plugins/my-messages/hooks/register.tsx`:
   - Colores: constantes `BAR`, `BG` y `FG`, al inicio del archivo.
   - Espaciado: `paddingY` (dentro de la caja) y `marginTop` / `marginBottom` (fuera).
2. Actualiza el plugin y ejecuta `/reload-plugins`, o abre una sesión nueva.

## Límites

- Tus mensajes pierden el marcador de prompt que dibuja `skins`.
- El texto se dibuja como texto plano, sin formato markdown.
- Los colores son fijos y están pensados para un tema oscuro.

## Desinstalar

```
claude plugin uninstall my-messages@claude-tools
```

Si añadiste `prependPlugins`, quita `my-messages@claude-tools` de la lista en `~/.claude/settings.json` (o la línea completa si era el único) y reinicia la sesión.
