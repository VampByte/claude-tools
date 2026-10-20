import { expect, mock, test } from 'claude-code/testing'

const BAND = {
  plugin: 'clean-view',
  component: 'AbovePrompt',
  requestId: 'band',
  props: {
    hasSurvey: false,
    isWorking: true,
    maxRows: 10,
    bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 10 },
    view: {},
  },
} as const

const TOOL_USE = {
  plugin: 'clean-view',
  component: 'ToolUse',
  requestId: 'toolu_1',
  props: {
    tool_use_id: 'toolu_1',
    tool: 'Bash',
    input: { command: 'ls' },
    isRunning: false,
    isErrored: false,
    isInterrupted: false,
  },
} as const

function stand(on: Parameters<Parameters<typeof test>[1]>[1]) {
  mock.store(on)
  const clock = mock.clock(on, { now: 1000 })
  on('command.register', () => ({ value: { command: 'simple' } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('turn.start', (_, e) => ({ turnId: e.turnId }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('tool.call', () => ({ result: {} }))
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text>engine</Text>
  })

  return clock
}

test('/simple off muestra las filas técnicas y /simple on las oculta', async ($, on) => {
  stand(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  for (const surface of ['terminal', 'desktop'] as const) {
    const hidden = await $.ui.mount({ ...TOOL_USE, surface })
    expect(await hidden.find({ type: 'Text', text: /engine/ })).toBeUndefined()
    await hidden.unmount()
  }

  const off = await $.command.run({ command: 'simple', args: 'off' })
  expect(off.text).toMatch(/desactivada/)

  const shown = await $.ui.mount({ ...TOOL_USE, surface: 'terminal' })
  expect(await shown.find({ type: 'Text', text: /engine/ })).toBeDefined()
  await shown.unmount()

  const again = await $.command.run({ command: 'simple', args: 'on' })
  expect(again.text).toMatch(/activada/)
})

test('un error, una interrupción y una pregunta nunca se ocultan', async ($, on) => {
  stand(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const cases = [
    { ...TOOL_USE.props, isErrored: true },
    { ...TOOL_USE.props, isInterrupted: true },
    { ...TOOL_USE.props, tool: 'AskUserQuestion' },
  ]

  for (const props of cases) {
    const ui = await $.ui.mount({ ...TOOL_USE, props, surface: 'terminal' })
    expect(await ui.find({ type: 'Text', text: /engine/ })).toBeDefined()
    await ui.unmount()
  }
})

test('el panel distingue en curso, pendiente, terminado y detenido', async ($, on) => {
  stand(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const text = async () => {
    const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
    const found = await ui.find({ type: 'Text', text: /Trabajando|Pendiente|Terminado|Detenido|listo/ })
    await ui.unmount()

    return found?.text ?? ''
  }

  expect(await text()).toMatch(/listo/)

  await $.turn.start({ text: 'hola', turnId: 't1' })
  expect(await text()).toMatch(/Trabajando.*En curso/)

  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.turn.complete({ answer: 'ok', durationMs: 10, isAborted: false, turnId: 't1', reason: 'answer' })
  expect(await text()).toMatch(/Terminado/)

  await $.turn.start({ text: 'otra', turnId: 't2' })
  await $.turn.complete({ answer: '', durationMs: 10, isAborted: true, turnId: 't2', reason: 'aborted' })
  expect(await text()).toMatch(/Detenido.*Interrumpido/)
})

test('la preferencia se guarda y se lee al iniciar la sesión', async ($, on) => {
  stand(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'simple', args: 'off' })

  // Una sesión nueva lee la preferencia guardada: sigue desactivada.
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  const ui = await $.ui.mount({ ...TOOL_USE, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /engine/ })).toBeDefined()
  await ui.unmount()
  await $.command.run({ command: 'simple', args: 'on' })

  const bad = await $.command.run({ command: 'simple', args: 'tal vez' })
  expect(bad.text).toMatch(/Uso/)
})

test('un diálogo de permiso deja el turno pendiente de respuesta', async ($, on) => {
  stand(on)
  on('classic.PermissionRequest', () => ({}))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.turn.start({ text: 'borra algo', turnId: 't3' })
  await $.classic.PermissionRequest({
    tool_name: 'Bash',
    tool_input: { command: 'rm x' },
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /Pendiente de tu respuesta/ }))?.text).toMatch(/permiso/)
  await ui.unmount()
})
