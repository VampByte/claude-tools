# clean-view

Mod de Claude Code que ofrece una **vista simple** de lo que hace Claude.

## Qué hace

- Muestra un **panel de pasos en español** sobre el cuadro de texto: estado del turno (trabajando, pendiente de tu respuesta, terminado o detenido), tiempo transcurrido y la lista de pasos o tareas.
- **Oculta las filas técnicas** de herramientas, resultados y diffs. Los errores, las interrupciones y las preguntas siempre se muestran, y Ctrl+O vuelve a mostrar todo.
- Se controla con el comando `/simple on`, `/simple off` o `/simple` (alterna), y con el botón del panel.
- La **preferencia se guarda** y se recupera al iniciar la siguiente sesión.

## Cómo comprobar que cargó

Escribe `/simple`: debe responder que la vista simple está activada o desactivada. Además, sobre el cuadro de texto aparece el panel "Clean View: listo." con el botón de la vista simple.

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

Al instalar, responde `y` a "Add marketplace?" y elige el alcance (usuario).
