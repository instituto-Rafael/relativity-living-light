import { useTranslation } from 'react-i18next'
import { BarChart3, LineChart, TrendingUp, Settings, FileDown, Database, X } from 'lucide-react'
import useAppStore from '../../store/appStore'
import clsx from 'clsx'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  activeItem: string
  onItemClick: (item: string) => void
}

const menuItems = [
  { id: 'dashboard', label: 'nav.dashboard', icon: BarChart3 },
  { id: 'analysis', label: 'nav.analysis', icon: LineChart },
  { id: 'trends', label: 'dashboard.trends', icon: TrendingUp },
  { id: 'data', label: 'nav.data', icon: Database },
  { id: 'export', label: 'nav.export', icon: FileDown },
  { id: 'settings', label: 'nav.settings', icon: Settings },
]

export function Sidebar({ isOpen, onClose, activeItem, onItemClick }: SidebarProps) {
  const { t } = useTranslation()
  const { toggleSidebar } = useAppStore()

  const handleItemClick = (id: string) => {
    onItemClick(id)
    if (window.innerWidth < 768) {
      toggleSidebar()
    }
  }

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-30"
          onClick={onClose}
        />
      )}

      <aside
        className={clsx(
          'fixed md:static inset-y-0 left-0 w-64 bg-white dark:bg-slate-900 shadow-lg md:shadow-none',
          'transform transition-transform duration-300 ease-in-out z-40',
          'border-r border-gray-200 dark:border-slate-700',
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        <div className="flex items-center justify-between p-6 md:hidden">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Menu</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="px-4 py-8 md:py-6">
          <ul className="space-y-2">
            {menuItems.map(({ id, label, icon: Icon }) => (
              <li key={id}>
                <button
                  onClick={() => handleItemClick(id)}
                  className={clsx(
                    'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                    activeItem === id
                      ? 'bg-primary-600 text-white shadow-md'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-800'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{t(label)}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
    </>
  )
}
