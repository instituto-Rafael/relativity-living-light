import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { ChartConfig } from '../../types'

interface AnalysisChartProps {
  data: unknown[]
  config: ChartConfig
  colors?: string[]
}

const defaultColors = ['#0ea5e9', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b']

export function AnalysisChart({ data, config, colors = defaultColors }: AnalysisChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500 dark:text-gray-400">
        <p>Nenhum dado disponível</p>
      </div>
    )
  }

  const sharedProps = {
    data,
    margin: { top: 10, right: 30, left: 0, bottom: 0 },
  }

  switch (config.type) {
    case 'line':
      return (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart {...sharedProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
            <XAxis dataKey="name" stroke="currentColor" opacity={0.5} />
            <YAxis stroke="currentColor" opacity={0.5} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey={config.dataKey}
              stroke={colors[0]}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )

    case 'bar':
      return (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart {...sharedProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
            <XAxis dataKey="name" stroke="currentColor" opacity={0.5} />
            <YAxis stroke="currentColor" opacity={0.5} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
            <Legend />
            <Bar dataKey={config.dataKey} fill={colors[0]} radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )

    case 'area':
      return (
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart {...sharedProps}>
            <defs>
              <linearGradient id="colorArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors[0]} stopOpacity={0.8} />
                <stop offset="95%" stopColor={colors[0]} stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
            <XAxis dataKey="name" stroke="currentColor" opacity={0.5} />
            <YAxis stroke="currentColor" opacity={0.5} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
            <Area
              type="monotone"
              dataKey={config.dataKey}
              stroke={colors[0]}
              fillOpacity={1}
              fill="url(#colorArea)"
            />
          </AreaChart>
        </ResponsiveContainer>
      )

    case 'pie':
      return (
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}`}
              outerRadius={120}
              fill="#8884d8"
              dataKey={config.dataKey}
            >
              {(data as unknown[]).map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      )

    default:
      return <div>Tipo de gráfico não suportado</div>
  }
}
