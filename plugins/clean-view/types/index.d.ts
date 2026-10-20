export type Phase = 'idle' | 'working' | 'waiting' | 'done' | 'stopped'

export type StepStatus = 'pending' | 'active' | 'done' | 'error'

export type Step = { id: string; label: string; status: StepStatus }

export type Run = {
  phase: Phase
  startedAt: number
  endedAt: number
  /** Qué espera el turno de la persona (permiso o pregunta); '' si nada. */
  waitingFor: string
  /** Por qué se detuvo, cuando phase es 'stopped'. */
  stopReason: string
  /** Tareas reales del modelo (TodoWrite, TaskCreate/TaskUpdate). */
  tasks: Step[]
  /** Actividad real: una entrada por llamada a herramienta del turno. */
  steps: Step[]
}

declare module 'claude-code' {
  interface PluginState {
    'clean-view': { run: Run; enabled: boolean; tick: number }
  }
}
