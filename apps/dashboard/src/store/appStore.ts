import { create } from 'zustand'
import { AppState } from '../types'

interface AppStore extends AppState {
  setTheme: (theme: AppState['theme']) => void
  setLanguage: (language: string) => void
  toggleSidebar: () => void
}

const useAppStore = create<AppStore>((set) => {
  const savedTheme = (localStorage.getItem('theme') as AppState['theme']) || 'auto'
  const savedLanguage = localStorage.getItem('language') || 'pt-BR'
  const savedSidebarOpen = localStorage.getItem('sidebarOpen') !== 'false'

  return {
    theme: savedTheme,
    language: savedLanguage,
    sidebarOpen: savedSidebarOpen,

    setTheme: (theme) => {
      localStorage.setItem('theme', theme)
      set({ theme })
    },

    setLanguage: (language) => {
      localStorage.setItem('language', language)
      set({ language })
    },

    toggleSidebar: () => {
      set((state) => {
        const newState = !state.sidebarOpen
        localStorage.setItem('sidebarOpen', String(newState))
        return { sidebarOpen: newState }
      })
    },
  }
})

export default useAppStore
