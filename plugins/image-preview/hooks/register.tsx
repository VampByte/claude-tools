import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Shot } from '../types'

const shot = atom({ plugin: 'image-preview', key: 'shot' } as const, null)

// Clipboard image -> PNG scaled to max 640 px, printed as "W H base64". Needs STA.
const PS = [
  'Add-Type -AssemblyName System.Windows.Forms,System.Drawing',
  '$i=[Windows.Forms.Clipboard]::GetImage()',
  'if($null -eq $i){exit 3}',
  '$s=[Math]::Min(1,640/[Math]::Max($i.Width,$i.Height))',
  '$w=[Math]::Max(1,[int]($i.Width*$s));$h=[Math]::Max(1,[int]($i.Height*$s))',
  '$b=New-Object Drawing.Bitmap $w,$h',
  '$g=[Drawing.Graphics]::FromImage($b);$g.InterpolationMode="HighQualityBicubic";$g.DrawImage($i,0,0,$w,$h)',
  '$m=New-Object IO.MemoryStream;$b.Save($m,[Drawing.Imaging.ImageFormat]::Png)',
  '"$w $h "+[Convert]::ToBase64String($m.ToArray())',
].join(';')

// Mark numbers pasted so far: "[Image #3]" -> [3]
const marks = (text: string) => [...text.matchAll(/\[Image #(\d+)\]/g)].map(m => Number(m[1]))

export const register: Register = on => {
  let seen = 0
  let isBusy = false

  on('prompt.change', async ($, e, next) => {
    const n = marks(e.text)

    if (n.length === 0) {
      seen = 0
      await update($, shot, () => null)
    } else if (n.length > seen && !isBusy) {
      seen = n.length
      isBusy = true
      try {
        const r = await $.process.run(
          ['powershell.exe', '-NoProfile', '-Sta', '-NonInteractive', '-Command', PS],
          { timeoutMs: 8000 },
        )
        const [w, h, png] = r.stdout.trim().split(' ')
        // clipboard held no image (e.g. a dragged file): show nothing, never block typing
        const found: Shot | null =
          r.exitCode === 0 && png ? { png, w: Number(w), h: Number(h), n: Math.max(...n) } : null
        await update($, shot, () => found)
      } catch {
        await update($, shot, () => null)
      } finally {
        isBusy = false
      }
    } else {
      seen = n.length
    }

    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const s = await read($, shot)
    if (e.props.hasSurvey || s === null) return next(e)

    const ui = $.ui.resolve(e)
    if (!('Image' in ui)) return next(e) // only the terminal surface draws pictures
    const { Box, Text, Image } = ui
    // terminal cells are about twice as tall as wide
    const columns = Math.max(4, Math.min(40, Math.round(s.w / 12)))
    const rows = Math.max(2, Math.min(14, Math.round((columns * s.h) / s.w / 2)))

    return (
      <Box flexDirection="column">
        <Text dimColor>Vista previa [Image #{s.n}] ({s.w}x{s.h})</Text>
        <Image source={{ png: s.png }} columns={columns} rows={rows} alt={`[Image #${s.n}]`} />
      </Box>
    )
  })
}
