import { useTranslation } from 'react-i18next'
import { Card, CardBody, CardHeader } from '../ui/Card'
import { AnalysisChart } from '../Charts/AnalysisChart'
import { TrendingUp, Users, BarChart3, Activity } from 'lucide-react'

interface Metric {
  label: string
  value: string | number
  change?: string
  icon: React.ReactNode
}

const mockChartData = [
  { name: 'Jan', value: 400, uv: 240, pv: 2400 },
  { name: 'Feb', value: 300, uv: 221, pv: 2210 },
  { name: 'Mar', value: 200, uv: 229, pv: 2290 },
  { name: 'Apr', value: 278, uv: 200, pv: 2000 },
  { name: 'May', value: 189, uv: 229, pv: 2181 },
  { name: 'Jun', value: 239, uv: 200, pv: 2500 },
]

export function DashboardPage() {
  const { t } = useTranslation()

  const metrics: Metric[] = [
    {
      label: 'Total de Usuários',
      value: '12,543',
      change: '+2.5%',
      icon: <Users className="w-8 h-8" />,
    },
    {
      label: 'Taxa de Atividade',
      value: '87%',
      change: '+5.2%',
      icon: <Activity className="w-8 h-8" />,
    },
    {
      label: 'Análises Processadas',
      value: '1,234',
      change: '+12.3%',
      icon: <BarChart3 className="w-8 h-8" />,
    },
    {
      label: 'Tendências Positivas',
      value: '94',
      change: '+8.1%',
      icon: <TrendingUp className="w-8 h-8" />,
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          {t('dashboard.title')}
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          {t('dashboard.subtitle')}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <Card key={index} interactive className="animate-slide-up">
            <CardBody>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {metric.label}
                  </p>
                  <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                    {metric.value}
                  </p>
                  {metric.change && (
                    <p className="mt-1 text-sm font-medium text-green-600 dark:text-green-400">
                      {metric.change}
                    </p>
                  )}
                </div>
                <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg text-blue-600 dark:text-blue-400">
                  {metric.icon}
                </div>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="animate-slide-up">
          <CardHeader
            title={t('dashboard.trends')}
            subtitle="Últimos 6 meses"
          />
          <CardBody>
            <AnalysisChart
              data={mockChartData}
              config={{
                title: 'Análise de Tendências',
                type: 'line',
                dataKey: 'value',
                responsive: true,
              }}
            />
          </CardBody>
        </Card>

        <Card className="animate-slide-up">
          <CardHeader
            title={t('dashboard.performance')}
            subtitle="Distribuição por categoria"
          />
          <CardBody>
            <AnalysisChart
              data={[
                { name: 'Categoria A', value: 35 },
                { name: 'Categoria B', value: 25 },
                { name: 'Categoria C', value: 20 },
                { name: 'Categoria D', value: 20 },
              ]}
              config={{
                title: 'Desempenho',
                type: 'pie',
                dataKey: 'value',
                responsive: true,
              }}
            />
          </CardBody>
        </Card>
      </div>

      <Card className="animate-slide-up">
        <CardHeader
          title={t('dashboard.metrics')}
          subtitle="Análise detalhada"
        />
        <CardBody>
          <AnalysisChart
            data={mockChartData}
            config={{
              title: 'Métricas Detalhadas',
              type: 'bar',
              dataKey: 'value',
              responsive: true,
            }}
          />
        </CardBody>
      </Card>
    </div>
  )
}
