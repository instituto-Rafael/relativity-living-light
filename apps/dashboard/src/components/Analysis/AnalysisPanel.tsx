import { useTranslation } from 'react-i18next'
import { Card, CardHeader, CardBody } from '../ui/Card'
import { AnalysisChart } from '../Charts/AnalysisChart'
import { AnalysisFilter, ChartConfig } from '../../types'

interface AnalysisPanelProps {
  title: string
  data: unknown[]
  config: ChartConfig
  filters?: AnalysisFilter
  onFilterChange?: (filters: AnalysisFilter) => void
}

export function AnalysisPanel({
  title,
  data,
  config,
  filters = {},
  onFilterChange,
}: AnalysisPanelProps) {
  const { t } = useTranslation()

  return (
    <Card className="animate-fade-in">
      <CardHeader
        title={title}
        subtitle={t('dashboard.subtitle')}
      />
      <CardBody>
        <div className="space-y-6">
          {onFilterChange && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('common.filter')}
                </label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white"
                  onChange={(e) => {
                    if (onFilterChange) {
                      onFilterChange({
                        ...filters,
                        startDate: new Date(e.target.value),
                      })
                    }
                  }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('common.sort')}
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white">
                  <option>Ascendente</option>
                  <option>Descendente</option>
                </select>
              </div>
            </div>
          )}

          <div className="bg-gradient-to-br from-blue-50 dark:from-slate-800 to-transparent p-4 rounded-lg">
            <AnalysisChart
              data={data}
              config={config}
            />
          </div>
        </div>
      </CardBody>
    </Card>
  )
}
