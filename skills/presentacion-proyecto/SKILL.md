---
name: presentacion-proyecto
description: "Genera una infografía ejecutiva de una página o un video corto con voz a partir de una ficha de levantamiento de un proyecto (18 preguntas). Usar al presentar proyectos destacados a Gerencia."
---

# Presentación ejecutiva de proyecto (infografía o video)

Convierte la información de un proyecto en una pieza ejecutiva, clara y breve, orientada a Gerencia: valor e impacto, no detalle técnico. Todos los proyectos deben salir con la misma estructura visual. Solo para proyectos; las presentaciones personales o de perfil profesional no entran aquí.

## Flujo general

1. Definir el formato (infografía o video).
2. Reunir información: fuentes existentes primero, ficha después.
3. Validar y resumir con el usuario.
4. Generar la pieza.
5. Ofrecer revisión visual y entregar.

## Paso 1 — Formato y recursos

**Elegir el formato antes de hacer cualquier otra cosa**, incluso si el usuario ya pasó un enlace o datos del proyecto:
- Si el pedido dice explícitamente video (video narrado, animado, con voz), seguir el Paso 4B.
- Si dice explícitamente infografía (o una pieza de una sola página), seguir el Paso 4A.
- Si pide ambos, generar primero la infografía y reutilizar el contenido para el guion del video.
- Si no menciona ninguno de los dos, **preguntar siempre**: ¿infografía (una sola cara, horizontal) o video narrado (breve, con animación y voz)? Usar la herramienta de preguntas con esas dos opciones, no asumir ninguna y no seguir hasta recibir la respuesta. Si no hay nadie que pueda responder, hacer la infografía y avisarlo al entregar.

Preguntar una sola vez por los recursos visuales: logo, colores corporativos, captura o mockup del proyecto. Si no hay colores, usar la paleta USIL: Primary #002663, Secondary #1E50DC, Accent #438BE0, Surface #DFE8F7, Neutral #FFFFFF. Nunca inventar logos ni usar logos de terceros que el usuario no haya aportado. Si el logo trae texto blanco, el encabezado va sobre el color Primary.

Si el usuario da la URL de un mockup o sitio y no hay captura, capturarlo con el navegador del usuario y **recortar cualquier barra de administración (por ejemplo la de WordPress, que muestra el usuario) antes de usar la imagen**.

## Paso 2 — Levantamiento de información

### 2.1 Fuentes primero

Antes de preguntar, buscar si la información ya existe, en este orden: enlaces que dé el usuario (GitHub, Jira, Confluence, Notion, documentos), README y documentos de avance del repositorio (por ejemplo docs/avance/estado.md), y después lo que el usuario haya dicho en la conversación. Si el repositorio no es accesible desde la sesión, leerlo con el navegador del usuario. Pre-completar lo que se pueda y preguntar solo lo faltante.

Regla de oro: lo que no sale de una fuente ni de lo que dijo el usuario se marca como faltante; no se deduce. En particular la **necesidad** (pregunta 9) solo se redacta con un dato o con confirmación del usuario.

### 2.2 Ficha (si no hay fuentes, pedirla en 3 bloques, no las preguntas de golpe)

**Bloque A — Información general**
1. Nombre del proyecto
2. Responsable del proyecto
3. Área usuaria
4. Sponsor o solicitante (si es proyecto propio del área: "No aplica · proyecto propio de <área>")
5. Categoría (elegir una): Ecommerce, Plataforma Web, Landing Page, SEO, UX/UI, Automatización, Inteligencia Artificial, Integración, CRM / HubSpot, Analytics, Otro
6. Estado actual (elegir uno): Planificación, Desarrollo, Pruebas, Implementado, En producción, Cerrado
7. Presupuesto (sensible: si el usuario no quiere mostrarlo, omitirlo de la pieza y no dejar el campo vacío)
8. URL del proyecto (si aplica)

**Bloque B — Objetivo, cronograma y solución**
9. ¿Qué necesidad o desafío motivó el proyecto? Pedir el dato concreto (ej. "cada landing toma 4 días").
10. ¿Cuál era el objetivo principal?
10b. **Línea base → resultado**: la medida de antes y la de después o meta (ej. 4 días → 2 días). Opcional pero muy recomendable.
11. Principales fases (3 obligatorias, 4 opcional): nombre y período con fechas reales. Si una fase no tiene fecha confirmada, pedirla o mostrar solo su estado ("Completada", "En curso"); no usar fechas aproximadas.
12. ¿Qué se desarrolló o implementó? Máximo 4 puntos.

**Bloque C — Valor, próximos pasos y cierre**
13. Valor entregado (elegir las que apliquen): Captación, Conversión, Ingresos, Experiencia de Usuario, Automatización, Productividad, Continuidad Operativa, Posicionamiento, Innovación, Integración, Analítica, IA
14. Beneficios obtenidos, uno por valor elegido, con una cifra real si existe. **Cada cifra se pregunta como "logrado" o "meta"** (ej. "102 landings publicadas" es logrado; "-50% de tiempo" es meta).
15. Actividades de seguimiento pendientes
16. Mejoras futuras identificadas
17. Siguiente hito importante, con mes y año
18. El proyecto resumido en una sola frase. Si el usuario no la tiene, proponer una; no puede presentar una meta como si fuera un resultado ya logrado.

## Paso 3 — Validación (antes de generar)

Presentar un resumen compacto de lo recibido y señalar:
- Campos obligatorios vacíos: 1, 2, 3, 4, 5, 6, 9, 10, 11 (mínimo 3 fases), 12, 13, 18.
- Cifras sin confirmar: preguntar explícitamente si son correctas y publicables, y si son logradas o meta. Nunca inventar métricas, cifras ni fechas.
- Respuestas técnicas u operativas: reformularlas en lenguaje de negocio (ver filtro de lenguaje).
- Más de 4 puntos en la pregunta 12: proponer cuáles agrupar o recortar.
- Cada cifra en su categoría correcta (el volumen de entregas es Productividad, no Continuidad Operativa).

No generar hasta que el usuario confirme el resumen.

### Filtro de lenguaje de negocio

Traducir a beneficio o quitar: Elementor, Tailwind, Astro, headless, EMCP, plugin, traits, deploy, repositorio, commits, nombres de archivos o IDs. Nunca usar primera persona ("mi rol", "lideré"), nunca mezclar varios proyectos en una pieza y nunca incluir requerimientos funcionales ni tareas operativas.

## Paso 4A — Infografía

Formato: una página, horizontal, lienzo de 1920×1080, estilo dashboard gerencial, iconografía de trazo propia (SVG), indicadores visuales, poco texto.

Secciones, siempre en este orden y con la misma estructura:

- **Header** (alto ≈ 230 px, fondo Primary): logo, categoría como etiqueta (y el área si aplica), nombre del proyecto en una sola línea, subtítulo de una frase, mockup y, si hay URL, QR con la URL real (verificar que apunte a ella) y la frase "Escanea y prueba el mockup".
- **Cuerpo en rejilla de 3×2**, seis tarjetas del mismo alto (nada de columnas desiguales):
  1. **Objetivo del proyecto**: necesidad con el dato concreto; si hay línea base → resultado, una pieza visual grande ("4 → 2 días", el valor anterior tachado y el nuevo grande) junto al objetivo; impacto estratégico en una línea.
  2. **Ficha del proyecto**: responsable, área usuaria, sponsor, categoría, estado con barra segmentada de 6 etapas (nombrar solo la etapa actual y "etapa N de 6"), URL, presupuesto solo si el usuario lo autorizó.
  3. **Cronograma**: línea de tiempo vertical. Fases completadas con check, fecha real o su estado si no hay fecha, y un último punto futuro vacío con el hito siguiente y su mes y año.
  4. **Solución implementada**: máximo 4 mosaicos, cada uno con cifra grande, etiqueta, título corto y descripción de una a dos líneas.
  5. **Valor generado**: 3 a 5 mosaicos con la categoría y su cifra. Las metas llevan la palabra "meta" junto a la cifra; lo logrado lleva "logrado" o el contexto ("landings publicadas").
  6. **Próximos pasos**: seguimiento pendiente, mejoras identificadas y el próximo hito en una caja oscura destacada, con mes y año.
- **Conclusión ejecutiva** (alto ≈ 110 px, fondo Secondary): frase destacada al pie. Si el resultado es una meta, redactarla como objetivo ("apunta a"), no como hecho.

Reglas de diseño:
- Texto mínimo de 14 px (cuerpo 16–18 px) y contraste mínimo 4.5:1 (3:1 desde 24 px). No usar gris claro para texto ni para valores tachados.
- Todo el estilo va en línea (atributo style) para que el usuario pueda editarlo desde el panel de propiedades; en la cabecera de la página solo van las fuentes, `body{margin:0}` y el color de los enlaces. Fuente Montserrat.
- Poco texto: cada descripción de mosaico cabe en dos líneas; si algo no entra, se recorta texto, no se reduce la letra por debajo de 14 px.
- Misma grilla, mismos íconos por categoría y misma jerarquía en todos los proyectos.
- Sin detalles técnicos, requerimientos funcionales ni tareas operativas.

Entrega de la infografía: **Claude Design tiene siempre la prioridad**. Antes de escribir ningún archivo, llamar a `list_types` (cargar antes las herramientas de artefactos si están diferidas) y crear la pieza desde el tipo Design: sube las imágenes (logo, mockup, QR) como recursos, escribe el lienzo y el artboard. Solo si Design no está disponible en el entorno (no hay herramientas de artefactos o `list_types` no lo lista), generar HTML autocontenido y exportarlo a PDF o PNG, y decirlo en una línea al entregar. No elegir HTML por iniciativa propia, aunque sea más rápido. Ese tipo de artefacto indica no abrir ni renderizar el resultado salvo que el usuario lo pida: **no hacer la revisión visual por cuenta propia; ofrecerla en una línea** ("¿quieres que la revise visualmente?") y calcular con holgura las alturas de las tarjetas para evitar cortes.

## Paso 4B — Video

Antes de producir, usar el skill `video-making` de la sesión para las decisiones técnicas (animación, voz, render).

Especificaciones:
- Duración: 60-90 segundos, horizontal 16:9.
- Animación con motion graphics (textos e íconos que entran y salen, barras y **contadores animados** para las cifras, pieza "antes → después" que se transforma, línea de tiempo que se dibuja), sin diapositivas estáticas.
- Voz en off amigable, dinámica y natural, en español neutro (peruano si el usuario lo prefiere), tono cercano pero profesional. Las metas se locutan como metas ("buscamos reducir a la mitad"), nunca como hechos.
- Misma estructura que la infografía, una escena por sección: apertura con nombre del proyecto (5-8 s), objetivo y antes → después (8-12 s), ficha rápida (6-8 s), cronograma (8-10 s), solución en máximo 4 puntos (12-15 s), valor generado en 3-5 bloques (12-15 s), próximos pasos (8-10 s), cierre con frase ejecutiva y URL/QR (5-8 s).
- Mismas reglas de contenido: sin detalle técnico, enfocado en valor e impacto.

Proceso:
1. Redactar el guion por escena (texto de voz + qué se ve + duración) y pedir aprobación antes de producir.
2. Producir voz, animación y render.
3. Revisar el resultado final (sincronía voz-imagen, texto legible, duración) antes de entregar.
4. Si el entorno no permite generar voz o video, decirlo claramente y entregar el guion aprobado más una versión animada en HTML, sin presentarla como video terminado.

## Paso 5 — Entrega

Entregar la pieza con una línea de contexto. Ofrecer como siguiente paso la versión alterna (video si se hizo infografía, o al revés) reutilizando la misma ficha, y la revisión visual. Ofrecer guardar la ficha completada para regenerar la pieza cuando cambie el estado del proyecto.

## Prohibiciones

- No inventar datos, cifras, fechas, logos ni QR sin URL.
- No presentar una meta como resultado logrado.
- No incluir detalle técnico (stack, arquitectura), requerimientos funcionales ni tareas operativas.
- No exceder una página en infografía ni 90 segundos en video sin autorización explícita.
- No usar fotos de personas públicas descargadas de la web.
- No dejar visible en capturas datos del usuario (barras de administración, correos, nombres de sesión).