# Estilo del chat de Claude Code

Cómo replicar en otro portátil Windows el aspecto del chat: skin `opencode`, caja ámbar en tus mensajes, negritas naranjas y reglas de formato.

> ⚠️ Esta guía **no se ha probado en un segundo portátil**. Las versiones probadas en el equipo original son `skins` 0.5.14, Claude Code 2.1.331 / 2.1.332 y la terminal Herdr app.

## 1. Plugin `skins`

Repo: [hellosverre/claude-skins](https://github.com/hellosverre/claude-skins).

```
claude plugin marketplace add hellosverre/claude-skins
claude plugin install skins@hellosverre-mods
```

## 2. Caja ámbar en tus mensajes

1. Instala el mod `my-messages` siguiendo [`my-messages.md`](my-messages.md).
2. No te saltes el paso de `prependPlugins`: con `skins` instalado, sin él la caja no aparece.

## 3. Skin `opencode`

No es un archivo del repo ni se descarga: es un skin propio que Claude crea con la herramienta `design` de `skins`. Se guarda en los datos del plugin (`~/.claude/plugins/store/skins_hellosverre-mods-<código>.json`), así que **no viaja con el repo** y hay que crearlo en cada portátil. No edites ese archivo a mano.

1. Abre una sesión nueva de Claude Code (con `skins` ya instalado).
2. Pega este pedido:

   ````
   /skins:skin-designer Guarda y aplica este skin exactamente así, sin cambiar ni añadir colores:

   ```json
   {
     "action": "save",
     "name": "opencode",
     "base": "tokyo-night",
     "palette": { "user": "#9d7cd8", "search": "#7fd88f", "fg": "#e8e8e8" }
   }
   ```
   ````

3. Claude debe responder que lo guardó y lo aplicó (`saved opencode and applied it`). El cambio se ve al momento.
4. Comprueba con `/skin list`: `opencode` aparece en la lista. Más adelante lo activas con `/skin opencode`.

Los demás colores y las palabras del spinner salen de `tokyo-night`.

Qué pinta cada color (según el código de `skins` 0.5.14):

| Color | Dónde se ve |
| --- | --- |
| `user` `#9d7cd8` | Títulos de nivel 1 y 2, números y duraciones, marcador de prompt, spinner, riel y barras de uso |
| `search` `#7fd88f` | Código dentro del texto, y Glob y Grep |
| `fg` `#e8e8e8` | Texto normal (y títulos de nivel 3 en adelante) |

> No lo repintes desde el panel de `/skin`: repintar un skin incluido crea uno llamado `my-<skin>`, no `opencode`.

### Ajustes generales

No forman parte del skin. En el equipo original solo **tres difieren de los valores por defecto**:

```
/skin rail off
/skin shimmer off
/skin quiet on
```

Los demás están por defecto (por ejemplo `icons unicode`, `prompt left`, `tables on`, `band`, `markdown` y `charts` activados). `/skin list` muestra todos.

### Volver atrás

`/skin tokyo-night` cambia de skin. Para borrar el propio, pide a Claude: "borra el skin opencode". Para recuperar los ajustes por defecto: `/skin rail on`, `/skin shimmer on` y `/skin quiet off`.

## 4. Negritas naranjas

El script [`scripts/skins-bold.ps1`](../scripts/skins-bold.ps1) pinta las negritas en `#ffa94d`.

> ⚠️ Modifica un plugin de terceros (`skins`, licencia MIT) ya instalado. El cambio **se pierde al actualizar `skins`**.

1. Desde el prompt de Claude Code:

   ```
   ! powershell -NoProfile -ExecutionPolicy Bypass -File "<ruta-repo>/scripts/skins-bold.ps1"
   ```

2. Lee el mensaje:

   | Mensaje | Significado |
   | --- | --- |
   | `APLICADO` | Cambió una línea de `hooks/prose.tsx` y dejó la copia `prose.tsx.orig` |
   | `OK` | Ya estaba aplicado |
   | `AVISO` | No modificó nada (`skins` no está instalado, falta el archivo o cambió su código) |

3. Tras `APLICADO`, ejecuta `/reload-plugins`.
4. Repite el script después de cada actualización de `skins` y comprueba el resultado en pantalla. Solo se probó con `skins` 0.5.14, no con una actualización real.

Solo cubre las negritas de párrafos y listas, no las de tablas ni títulos.

## 5. Reglas de formato

Añade este bloque a tu `~/.claude/CLAUDE.md` global, **sin borrar lo que ya tenga**. Se carga en las sesiones nuevas.

```markdown
# Formato de respuestas en el chat
- Usa iconos con sentido: ✅ hecho o correcto, ⚠️ riesgo o aviso, ❌ no se puede o falló. Sin decorar cada línea.
- Separa las respuestas largas con títulos cortos (`##`).
- Usa una tabla al comparar opciones o datos.
- Pon en **negrita** la conclusión y los datos clave, no frases enteras.
- Las respuestas cortas van sin títulos ni tablas.
- Esto aplica solo al chat, no a código, commits ni archivos del proyecto.
```

## 6. Verificación y cómo deshacer

Abre una sesión nueva y comprueba:

| Parte | Cómo verificar | Cómo deshacer |
| --- | --- | --- |
| `skins` | `claude plugin list` lo muestra enabled | `claude plugin uninstall skins@hellosverre-mods` |
| Caja ámbar | Envías un mensaje y sale en la caja ámbar | Desinstala `my-messages` y quita su id de `prependPlugins` |
| Skin `opencode` | Los títulos salen en morado y el código en verde | `/skin tokyo-night` |
| Negritas naranjas | Pides una respuesta con una negrita en un párrafo y sale naranja | Copia `prose.tsx.orig` sobre `prose.tsx` (en la carpeta `hooks` de `skins`, la ruta que muestra el script) y ejecuta `/reload-plugins` |
| Reglas de formato | Una respuesta larga usa títulos, iconos y tablas | Borra el bloque de `~/.claude/CLAUDE.md` |
