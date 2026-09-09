import { useTranslation } from 'react-i18next'
import { Card, CardBody, CardHeader } from '../ui/Card'
import useAppStore from '../../store/appStore'

export function SettingsPage() {
  const { t, i18n } = useTranslation()
  const { theme, setTheme, language, setLanguage } = useAppStore()

  const languages = [
    { code: 'pt-BR', name: 'Português' },
    { code: 'en-US', name: 'English' },
    { code: 'es-ES', name: 'Español' },
    { code: 'fr-FR', name: 'Français' },
    { code: 'de-DE', name: 'Deutsch' },
  ]

  const themes = [
    { value: 'light', label: t('settings.light') },
    { value: 'dark', label: t('settings.dark') },
    { value: 'auto', label: t('settings.auto') },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          {t('settings.title')}
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Personalize sua experiência
        </p>
      </div>

      <Card className="animate-slide-up">
        <CardHeader title={t('settings.theme')} />
        <CardBody>
          <div className="space-y-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Escolha como o aplicativo deve aparecer
            </p>
            <div className="grid grid-cols-3 gap-4">
              {themes.map(({ value, label }) => (
                <button
                  key={value}
                  onClick={() => setTheme(value as 'light' | 'dark' | 'auto')}
                  className={`p-4 rounded-lg border-2 transition-all font-medium ${
                    theme === value
                      ? 'border-primary-600 bg-primary-50 dark:bg-slate-800 text-primary-600'
                      : 'border-gray-200 dark:border-slate-700 hover:border-gray-300'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </CardBody>
      </Card>

      <Card className="animate-slide-up">
        <CardHeader title={t('settings.language')} />
        <CardBody>
          <div className="space-y-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Selecione o idioma preferido
            </p>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {languages.map(({ code, name }) => (
                <button
                  key={code}
                  onClick={() => {
                    setLanguage(code)
                    i18n.changeLanguage(code)
                  }}
                  className={`p-4 rounded-lg border-2 transition-all font-medium text-center ${
                    language === code
                      ? 'border-primary-600 bg-primary-50 dark:bg-slate-800 text-primary-600'
                      : 'border-gray-200 dark:border-slate-700 hover:border-gray-300'
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        </CardBody>
      </Card>

      <Card className="animate-slide-up">
        <CardHeader title={t('settings.notifications')} />
        <CardBody>
          <div className="space-y-3">
            {[
              { id: 'email', label: 'Notificações por Email' },
              { id: 'push', label: 'Notificações Push' },
              { id: 'desktop', label: 'Notificações Desktop' },
              { id: 'updates', label: 'Atualizações de Sistema' },
            ].map((notification) => (
              <label key={notification.id} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-4 h-4 rounded border-gray-300 text-primary-600"
                />
                <span className="text-gray-700 dark:text-gray-300">
                  {notification.label}
                </span>
              </label>
            ))}
          </div>
        </CardBody>
      </Card>

      <Card className="animate-slide-up">
        <CardHeader title={t('settings.privacy')} />
        <CardBody>
          <div className="space-y-3">
            {[
              { label: 'Compartilhar dados de análise' },
              { label: 'Permitir cookies de rastreamento' },
              { label: 'Histórico de atividades' },
            ].map((item, index) => (
              <label key={index} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-gray-300 text-primary-600"
                />
                <span className="text-gray-700 dark:text-gray-300">
                  {item.label}
                </span>
              </label>
            ))}
          </div>
        </CardBody>
      </Card>

      <div className="flex gap-3">
        <button className="px-6 py-2 bg-gray-200 dark:bg-slate-800 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-slate-700 transition-colors font-medium">
          Cancelar
        </button>
        <button className="px-6 py-2 bg-gradient-to-r from-primary-600 to-blue-600 text-white rounded-lg hover:from-primary-700 hover:to-blue-700 transition-all hover:shadow-lg font-medium">
          Salvar Alterações
        </button>
      </div>
    </div>
  )
}
