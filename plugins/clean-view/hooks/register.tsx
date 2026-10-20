import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Run, Step, StepStatus } from '../types'

const IDLE: Run = {
  phase: 'idle',
  startedAt: 0,
  endedAt: 0,
  waitingFor: '',
  stopReason: '',
  tasks: [],
  steps: [],
}

const enabledRef = { plugin: 'clean-view', key: 'enabled' } as const
const runRef = { plugin: 'clean-view', key: 'run' } as const
const tickRef = { plugin: 'clean-view', key: 'tick' } as const

const enabled = atom(enabledRef, true)
const run = atom(runRef, IDLE)
const tick = atom(tickRef, 0)

const STORE_KEY = 'enabled'
const ASKING = new Set(['AskUserQuestion', 'ExitPlanMode'])
const TASK_TOOLS = new Set(['TodoWrite', 'TaskCreate', 'TaskUpdate', 'TaskGet', 'TaskList'])
const MAX_STEPS = 8

const base = (path: unknown): string =>
  typeof path === 'string' ? (path.split(/[\\/]/).pop() ?? path) : ''

const short = (text: unknown, max: number): string => {
  const one = typeof text === 'string' ? text.replace(/\s+/g, ' ').trim() : ''

  return one.length > max ? `${one.slice(0, max - 1)}…` : one
}

// Etiqueta en español de lo que hace una herramienta, a partir de su entrada real.
const describe = (tool: string, a: Record<string, unknown>): string => {
  switch (tool) {
    case 'Read':
      return `Leyendo ${base(a.file_path)}`
    case 'Edit':
    case 'MultiEdit':
      return `Editando ${base(a.file_path)}`
    case 'Write':
      return `Escribiendo ${base(a.file_path)}`
    case 'NotebookEdit':
      return `Editando ${base(a.notebook_path)}`
    case 'Bash':
      return `Ejecutando: ${short(a.command, 48)}`
    case 'Grep':
    case 'Glob':
      return 'Buscando en el proyecto'
    case 'WebSearch':
      return `Buscando en la web: ${short(a.query, 40)}`
    case 'WebFetch':
      return 'Consultando una página web'
    case 'Agent':
    case 'Task':
      return `Delegando: ${short(a.description, 40)}`
    case 'AskUserQuestion':
      return 'Esperando tu respuesta a una pregunta'
    case 'ExitPlanMode':
      return 'Esperando tu aprobación del plan'
    default:
      return tool.startsWith('mcp__')
        ? `Usando ${tool.split('__').slice(2).join(' ') || tool}`
        : `Usando ${tool}`
  }
}

const taskStatus = (status: unknown): StepStatus =>
  status === 'in_progress' ? 'active' : status === 'completed' ? 'done' : 'pending'

const duration = (ms: number): string => {
  const total = Math.max(0, Math.round(ms / 1000))
  const m = Math.floor(total / 60)
  const s = total % 60

  return m > 0 ? `${m} min ${String(s).padStart(2, '0')} s` : `${s} s`
}

const mark = (status: StepStatus): string =>
  status === 'done' ? '✔' : status === 'active' ? '▶' : status === 'error' ? '✖' : '○'

const patch = (list: Step[], id: string, change: Partial<Step>): Step[] =>
  list.map(step => (step.id === id ? { ...step, ...change } : step))

async function setEnabled($: EngineInterface, value: boolean): Promise<void> {
  await update($, enabled, () => value)
  await $.store.set(STORE_KEY, value)
}

// Un permiso respondido o una herramienta terminada: el turno vuelve a trabajar.
async function resume($: EngineInterface): Promise<void> {
  await update($, run, (r): Run => (r.phase === 'waiting' ? { ...r, phase: 'working', waitingFor: '' } : r))
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'simple',
      description: 'Activa o desactiva la vista simple (Clean View)',
      argumentHint: '[on|off]',
    })

    const saved = await $.store.get(STORE_KEY)
    await update($, enabled, () => saved !== false)

    // El tiempo transcurrido solo se redibuja mientras el turno está en marcha.
    $.clock.every(1000, async () => {
      const { value } = await $.state.get(runRef)

      if (value?.phase === 'working' || value?.phase === 'waiting') {
        await update($, tick, n => (n ?? 0) + 1)
      }
    })

    return next(e)
  })

  on('session.end', async ($, e, next) => {
    await update($, run, () => IDLE)

    return next(e)
  })

  on('command.run', { command: 'simple' }, async ($, e) => {
    const arg = e.args.trim().toLowerCase()
    const current = (await $.state.get(enabledRef)).value !== false

    if (arg !== '' && arg !== 'on' && arg !== 'off') {
      return { text: 'Uso: /simple on, /simple off o /simple (alterna).' }
    }

    const next = arg === '' ? !current : arg === 'on'
    await setEnabled($, next)

    return {
      text: next
        ? 'Vista simple activada: se ocultan las filas técnicas de herramientas, resultados y diffs. Ctrl+O las muestra.'
        : 'Vista simple desactivada: se muestran de nuevo todas las filas.',
    }
  })

  // ---- Estado real del turno ----

  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) {
      const now = await $.clock.now()
      await update($, run, (r): Run => ({
        ...r,
        phase: 'working',
        startedAt: now,
        endedAt: 0,
        waitingFor: '',
        stopReason: '',
        // Las tareas se conservan mientras queden pendientes; si todas acabaron, se limpian.
        tasks: r.tasks.every(t => t.status === 'done') ? [] : r.tasks,
        steps: [],
      }))
    }

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId === undefined) {
      const now = await $.clock.now()
      const phase = e.reason === 'answer' ? 'done' : 'stopped'
      const stopReason =
        e.reason === 'aborted'
          ? 'Interrumpido por ti'
          : e.reason === 'refusal'
            ? 'El modelo rechazó la petición'
            : e.reason === 'error'
              ? 'Terminó por un error de la API'
              : ''

      await update($, run, (r): Run => ({
        ...r,
        phase,
        endedAt: now,
        waitingFor: '',
        stopReason,
        // Lo que quedó a medias no se da por terminado.
        steps: r.steps.map(s => (s.status === 'active' ? { ...s, status: 'pending' as const } : s)),
      }))
    }

    return next(e)
  })

  // Un diálogo de permiso abierto: el turno espera a la persona.
  on('classic.PermissionRequest', async ($, e, next) => {
    const a = (e.tool_input ?? {}) as Record<string, unknown>
    await update($, run, (r): Run =>
      r.phase === 'working' || r.phase === 'waiting'
        ? { ...r, phase: 'waiting', waitingFor: `permiso para ${describe(e.tool_name, a).toLowerCase()}` }
        : r,
    )

    return next(e)
  })

  on('classic.PostToolUse', async ($, e, next) => {
    await resume($)

    return next(e)
  })

  on('classic.PostToolUseFailure', async ($, e, next) => {
    await resume($)

    return next(e)
  })

  on('classic.PermissionDenied', async ($, e, next) => {
    await resume($)

    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    if (e.agentId !== undefined) {
      return next(e)
    }

    const a = e as unknown as Record<string, unknown>
    const id = e.tool_use_id

    if (e.tool === 'TodoWrite') {
      const todos = (Array.isArray(a.todos) ? a.todos : []) as Array<Record<string, unknown>>
      await update($, run, (r): Run => ({
        ...r,
        tasks: todos.map((t, i) => ({
          id: String(i),
          label: String(t.status === 'in_progress' ? (t.activeForm ?? t.content) : t.content),
          status: taskStatus(t.status),
        })),
      }))

      return next(e)
    }

    if (e.tool === 'TaskCreate') {
      const ran = await next(e)
      const created = (ran.result as { task?: { id?: string; subject?: string } } | undefined)?.task

      if (created?.id !== undefined) {
        const step: Step = { id: String(created.id), label: String(created.subject ?? a.subject ?? ''), status: 'pending' }
        await update($, run, (r): Run => ({ ...r, tasks: [...r.tasks.filter(t => t.id !== step.id), step] }))
      }

      return ran
    }

    if (e.tool === 'TaskUpdate') {
      const ran = await next(e)
      const taskId = String(a.taskId)

      await update($, run, (r): Run => {
        if (a.status === 'deleted') {
          return { ...r, tasks: r.tasks.filter(t => t.id !== taskId) }
        }

        return {
          ...r,
          tasks: r.tasks.map(t =>
            t.id !== taskId
              ? t
              : {
                  ...t,
                  label: String(
                    (a.status === 'in_progress' ? a.activeForm : undefined) ?? a.subject ?? t.label,
                  ),
                  status: a.status === undefined ? t.status : taskStatus(a.status),
                },
          ),
        }
      })

      return ran
    }

    if (TASK_TOOLS.has(e.tool)) {
      return next(e)
    }

    const isAsking = ASKING.has(e.tool)
    const label = describe(e.tool, a)
    // Si el turno esperaba un permiso, este paso ya lo recibió.
    await update($, run, (r): Run => {
      const steps = [...r.steps, { id, label, status: 'active' as const }].slice(-MAX_STEPS)

      return r.phase === 'done' || r.phase === 'stopped' || r.phase === 'idle'
        ? { ...r, steps }
        : { ...r, steps, phase: isAsking ? 'waiting' : 'working', waitingFor: isAsking ? label.replace('Esperando ', '') : '' }
    })

    const ran = await next(e)
    const status: StepStatus = ran.deny !== undefined || ran.isError === true ? 'error' : 'done'

    await update($, run, (r): Run => ({
      ...r,
      steps: patch(r.steps, id, { status }),
      phase: isAsking && r.phase === 'waiting' ? 'working' : r.phase,
      waitingFor: isAsking ? '' : r.waitingFor,
    }))

    return ran
  })

  // ---- Panel sobre el cuadro de texto ----

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) {
      return next(e)
    }

    const isOn = await read($, enabled)
    const r = await read($, run)
    await read($, tick)
    const now = await $.clock.now()
    const { Box, Text, Button } = $.ui.resolve(e)

    const toggle = (
      <Button
        key="toggle"
        label={isOn ? 'Vista simple: activada' : 'Vista simple: desactivada'}
        onPress={() => setEnabled($, !isOn)}
      />
    )

    if (!isOn) {
      return (
        <Box>
          <Text dimColor>Clean View </Text>
          {toggle}
        </Box>
      )
    }

    if (r.phase === 'idle') {
      return (
        <Box>
          <Text dimColor>Clean View: listo. </Text>
          {toggle}
        </Box>
      )
    }

    const isLive = r.phase === 'working' || r.phase === 'waiting'
    const elapsed = duration((isLive ? now : r.endedAt) - r.startedAt)
    const list = r.tasks.length > 0 ? r.tasks : r.steps
    const done = r.tasks.filter(t => t.status === 'done').length
    // Porcentaje solo si existe una lista de tareas real; si no, "En curso".
    const progress =
      r.tasks.length > 0 ? `${done}/${r.tasks.length} pasos (${Math.round((done * 100) / r.tasks.length)} %)` : 'En curso'

    const headline =
      r.phase === 'working'
        ? { color: 'cyan', text: `▶ Trabajando · ${elapsed} · ${progress}` }
        : r.phase === 'waiting'
          ? { color: 'yellow', text: `? Pendiente de tu respuesta: ${r.waitingFor || 'se requiere tu decisión'} · ${elapsed}` }
          : r.phase === 'done'
            ? { color: 'green', text: `✔ Terminado en ${elapsed}${r.tasks.length > 0 ? ` · ${done}/${r.tasks.length} pasos` : ''}` }
            : { color: 'red', text: `■ Detenido a los ${elapsed}${r.stopReason ? ` · ${r.stopReason}` : ''}` }

    const room = Math.max(2, Math.min(6, e.props.maxRows - 3))
    const firstOpen = list.findIndex(s => s.status !== 'done')
    const start = r.tasks.length > 0 ? Math.max(0, Math.min(firstOpen === -1 ? list.length : firstOpen - 1, list.length - room)) : Math.max(0, list.length - room)
    const shown = list.slice(start, start + room)
    const hidden = list.length - shown.length

    return (
      <Box flexDirection="column">
        <Box>
          <Text bold color={headline.color}>
            {headline.text}{' '}
          </Text>
          {toggle}
        </Box>
        {shown.map(step => (
          <Text key={step.id} dimColor={step.status === 'done' || step.status === 'pending'} bold={step.status === 'active'} color={step.status === 'error' ? 'red' : undefined} wrap="truncate-end">
            {'  '}
            {mark(step.status)} {step.label}
          </Text>
        ))}
        {hidden > 0 && <Text dimColor>{`  … y ${hidden} más`}</Text>}
      </Box>
    )
  })

  // ---- Filas técnicas ocultas (se conservan errores, interrupciones y preguntas) ----

  on('ui.render', { component: 'ToolUse' }, async ($, e, next) => {
    const isOn = await read($, enabled)
    const p = e.props
    const keep = !isOn || p.isExpanded === true || p.isErrored || p.isInterrupted || ASKING.has(p.tool)

    if (keep) {
      return next(e)
    }

    const { Box } = $.ui.resolve(e)

    return <Box display="none" />
  })

  on('ui.render', { component: 'ToolResult' }, async ($, e, next) => {
    const isOn = await read($, enabled)
    const p = e.props
    const keep = !isOn || p.isExpanded === true || p.isErrored || ASKING.has(p.tool)

    if (keep) {
      return next(e)
    }

    const { Box } = $.ui.resolve(e)

    return <Box display="none" />
  })

  on('ui.render', { component: 'ToolGroup' }, async ($, e, next) => {
    const isOn = await read($, enabled)
    const p = e.props
    const hasProblem = p.calls.some(c => c.isErrored || c.isInterrupted)

    if (!isOn || p.isExpanded || hasProblem) {
      return next(e)
    }

    const { Box } = $.ui.resolve(e)

    return <Box display="none" />
  })

  on('ui.render', { component: 'ToolProgress' }, async ($, e, next) => {
    const isOn = await read($, enabled)

    return isOn ? next({ ...e, props: { ...e.props, hint: '' } }) : next(e)
  })
}
