import { beforeEach, describe, expect, it } from 'vitest'
import useAppStore from './appStore'

describe('dashboard preference persistence', () => {
  beforeEach(() => {
    localStorage.clear()
    useAppStore.setState({ theme: 'auto', language: 'pt-BR', sidebarOpen: true })
  })

  it('saves selected theme to the store and browser storage', () => {
    useAppStore.getState().setTheme('dark')
    expect(useAppStore.getState().theme).toBe('dark')
    expect(localStorage.getItem('theme')).toBe('dark')
  })

  it('persists language preferences independently of the theme', () => {
    useAppStore.getState().setLanguage('en')
    expect(useAppStore.getState().language).toBe('en')
    expect(localStorage.getItem('language')).toBe('en')
    expect(useAppStore.getState().theme).toBe('auto')
  })

  it('toggles sidebar visibility and preserves the new state', () => {
    useAppStore.getState().toggleSidebar()
    expect(useAppStore.getState().sidebarOpen).toBe(false)
    expect(localStorage.getItem('sidebarOpen')).toBe('false')
    useAppStore.getState().toggleSidebar()
    expect(useAppStore.getState().sidebarOpen).toBe(true)
    expect(localStorage.getItem('sidebarOpen')).toBe('true')
  })
})
