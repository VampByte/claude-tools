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

No es un archivo del repo: se crea pidiéndoselo a Claude.

1. Ejecuta `/skins:skin-designer` y pide un skin con estos datos, y que lo aplique:
   - Nombre: `opencode`
   - Base: `tokyo-night`
   - Colores: `user` `#9d7cd8`, `search` `#7fd88f`, `fg` `#e8e8e8`

Qué pinta cada color:

| Color | Dónde se ve |
| --- | --- |
| `user` | Títulos, números, marcador de prompt y spinner |
| `search` | Código y filas de Glob y Grep |

Volver atrás: `/skin tokyo-night`.

En el equipo original, estos ajustes de `skins` estaban así. Son generales, no forman parte del skin, y se cambian con `/skin`:

| Ajuste | Valor |
| --- | --- |
| `icons` | `unicode` |
| `prompt` | `left` |
| `rail` | `false` |
| `tables` | `on` |
| `shimmer` | `false` |
| `band` | `true` |
| `markdown` | `true` |
| `quiet` | `true` |
| `charts` | `true` |

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
