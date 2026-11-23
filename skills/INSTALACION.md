# Instalar el skill /presentacion-proyecto

Genera una **infografía ejecutiva de una página** o un **video corto narrado** de un proyecto, para presentarlo a Gerencia. Usa siempre la misma estructura y la paleta USIL.

Archivo a instalar: `presentacion-proyecto.zip` (contiene la carpeta `presentacion-proyecto/` con un `SKILL.md`).

## Opción A — Claude.ai o app de escritorio (recomendada)

Aquí funciona Claude Design, que es lo que el skill usa por defecto para la infografía.

1. Descarga `presentacion-proyecto.zip` y **no lo descomprimas**.
2. Abre Claude (web o escritorio) y ve a **Configuración › Capacidades › Skills** (el nombre exacto del menú puede variar según tu plan o versión).
3. Elige **Subir skill** y selecciona el zip.
4. Activa el skill con su interruptor.
5. En un chat nuevo escribe `/presentacion-proyecto` seguido del enlace o nombre del proyecto.

Si tu cuenta es de equipo u organización y no ves la opción de subir skills, pide a un administrador que la habilite, o que lo suba para toda la organización.

## Opción B — Claude Code (terminal)

1. Descomprime el zip.
2. Copia la carpeta `presentacion-proyecto` en una de estas rutas:
   - Personal (todos tus proyectos): `~/.claude/skills/presentacion-proyecto/` (en Windows: `%USERPROFILE%\.claude\skills\presentacion-proyecto\`)
   - Un proyecto concreto, compartido por git: `<repositorio>/.claude/skills/presentacion-proyecto/`
3. Debe quedar el archivo `.../presentacion-proyecto/SKILL.md`.
4. Abre una sesión nueva de Claude Code y escribe `/presentacion-proyecto`.

Limitación: Claude Design no existe en Claude Code de terminal. Allí el skill avisa y entrega la infografía en HTML exportable a PDF o PNG, sin lienzo editable.

## Cómo usarlo

1. Escribe `/presentacion-proyecto` con el proyecto. Si no dices si quieres **infografía o video narrado**, te lo preguntará.
2. Si pasas un enlace (GitHub, Jira, Notion, documentos), lee ahí primero; pregunta solo lo que falte.
3. Te muestra un resumen de la ficha. Confirma las cifras (¿logradas o meta?) y las fechas antes de que genere nada.
4. Entrega la pieza. Puedes pedir la revisión visual y la versión alterna (video o infografía).

## Qué conviene tener a mano

- Nombre, responsable, área usuaria, sponsor, estado y URL del proyecto.
- Cifras reales con su medida de antes y después (por ejemplo, de 4 a 2 días) y si ya se lograron o son meta.
- Fechas reales de las fases y el próximo hito.
- Logo y una captura o mockup del proyecto, si existen.

## Notas

- El skill nunca inventa cifras ni fechas: lo que falte lo marca como pendiente.
- La paleta USIL (#002663, #1E50DC, #438BE0, #DFE8F7) es la predeterminada. Para otra paleta, indícala al pedir la pieza.
- Para actualizar el skill, vuelve a subir el zip nuevo (opción A) o reemplaza la carpeta (opción B).
