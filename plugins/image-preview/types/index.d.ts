export type Shot = { png: string; w: number; h: number; n: number }

declare module 'claude-code' {
  interface PluginState {
    'image-preview': { shot: Shot | null }
  }
}
