import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Header } from './components/Layout/Header'
import { Sidebar } from './components/Layout/Sidebar'
import { DashboardPage } from './components/Dashboard/DashboardPage'
import { SettingsPage } from './components/Settings/SettingsPage'
import { ExportPanel } from './components/Export/ExportPanel'
import { AnalysisPanel } from './components/Analysis/AnalysisPanel'
import useAppStore from './store/appStore'

const mockAnalysisData = [
  { name: 'Q1', value: 400, category: 'vendas' },
  { name: 'Q2', value: 300, category: 'vendas' },
  { name: 'Q3', value: 200, category: 'vendas' },
  { name: 'Q4', value: 278, category: 'vendas' },
]

export function App() {
  const { t } = useTranslation()
  const { theme } = useAppStore()
  const [activePage, setActivePage] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else if (theme === 'light') {
      document.documentElement.classList.remove('dark')
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }, [theme])

  const handleExport = (format: string) => {
    console.log('Exporting data as:', format)
    // Implementar lógica de exportação
  }

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeItem={activePage}
        onItemClick={setActivePage}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <main className="flex-1 overflow-auto">
          <div className="p-4 sm:p-6 lg:p-8">
            {activePage === 'dashboard' && <DashboardPage />}

            {activePage === 'analysis' && (
              <AnalysisPanel
                title={t('analysis.title')}
                data={mockAnalysisData}
                config={{
                  title: 'Análise de Dados',
                  type: 'line',
                  dataKey: 'value',
                  responsive: true,
                }}
              />
            )}

            {activePage === 'export' && (
              <ExportPanel
                data={mockAnalysisData}
                onExport={(options) => {
                  console.log('Export options:', options)
                  handleExport(options.format)
                }}
              />
            )}

            {activePage === 'settings' && <SettingsPage />}

            {activePage === 'data' && (
              <div className="space-y-6">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {t('nav.data')}
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Gerenciamento de dados em construção...
                </p>
              </div>
            )}

            {activePage === 'trends' && (
              <div className="space-y-6">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {t('dashboard.trends')}
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Análise de tendências em construção...
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
