# image-preview: miniatura de las imágenes que pegas en Claude Code

Guía para instalar el mod `image-preview` en otro portátil Windows. El mod vive en [`plugins/image-preview`](../plugins/image-preview) y se instala desde el marketplace `claude-tools` de este repo.

## Qué hace

Al pegar una imagen en el prompt de Claude Code (terminal):

1. Un hook `prompt.change` detecta el marcador `[Image #N]` en el texto.
2. Un PowerShell (`-Sta`) lee la imagen del portapapeles, la escala a un máximo de 640 px y la devuelve como PNG en base64.
3. Una banda sobre el prompt (`ui.render` en `AbovePrompt`) la dibuja con el elemento `Image`.

Si borras el marcador, la miniatura desaparece.

## Requisitos

- Windows con PowerShell 5.1 (`powershell.exe`).
- Claude Code con soporte de mods/plugins con hooks (probado en 2.1.331).
- Una terminal con gráficos kitty (probado en Herdr app). En otras terminales solo se vería el texto alternativo `[Image #N]`.

## Instalación

1. Clona o copia este repo en el portátil:

   ```
   git clone https://github.com/VampByte/claude-tools
   ```

2. Añade la carpeta como marketplace e instala el mod. El nombre del marketplace es `claude-tools` (está en `.claude-plugin/marketplace.json`):

   ```
   claude plugin marketplace add C:\ruta\a\claude-tools
   claude plugin install image-preview@claude-tools --scope user
   ```

   Si ya añadiste el marketplace desde GitHub (`vampbyte/claude-tools`), salta el primer comando.

3. Abre una sesión nueva de Claude Code (o recarga los plugins).

## Verificación

- `claude plugin list` debe mostrar `image-preview` como enabled.
- Pega una captura en el prompt: debe aparecer la miniatura sobre el cuadro de texto.
- Borra el marcador `[Image #N]`: la miniatura desaparece.

## Límites

- La miniatura sale del **portapapeles**: si copias otra cosa antes de enviar, puede no coincidir con la imagen pegada.
- Con varias imágenes pegadas solo se ve la última.
- Arrastrar un archivo al prompt no muestra nada (el portapapeles no tiene imagen).
- El PowerShell tiene un timeout de 8 s; si se agota, no se muestra miniatura y el prompt sigue funcionando.

## Problemas conocidos

- **No aparece nada:** comprueba que la terminal soporta gráficos kitty y que el mod figura como enabled; abre una sesión nueva.
- **Sale la imagen equivocada:** vuelve a copiar la imagen y pégala otra vez.
- **PowerShell bloqueado por política corporativa:** el mod no muestra nada y no rompe el prompt.

## Desinstalar

```
claude plugin uninstall image-preview@claude-tools
```
