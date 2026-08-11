import { useTranslation } from 'react-i18next'
import { Download, FileJson, FileText } from 'lucide-react'
import { Card, CardHeader, CardBody } from '../ui/Card'
import { ExportOptions } from '../../types'

interface ExportPanelProps {
  data: unknown[]
  onExport: (options: ExportOptions) => void
}

export function ExportPanel({ data, onExport }: ExportPanelProps) {
  const { t } = useTranslation()

  const exportFormats: Array<{
    format: ExportOptions['format']
    label: string
    icon: React.ReactNode
    description: string
  }> = [
    {
      format: 'json',
      label: t('export.json'),
      icon: <FileJson className="w-8 h-8" />,
      description: 'Formato JSON para integração',
    },
    {
      format: 'csv',
      label: t('export.csv'),
      icon: <FileText className="w-8 h-8" />,
      description: 'Formato CSV para Excel',
    },
    {
      format: 'pdf',
      label: t('export.pdf'),
      icon: <FileText className="w-8 h-8" />,
      description: 'Relatório em PDF',
    },
    {
      format: 'xlsx',
      label: t('export.excel'),
      icon: <FileText className="w-8 h-8" />,
      description: 'Planilha Excel completa',
    },
  ]

  return (
    <Card className="animate-fade-in">
      <CardHeader title={t('export.title')} />
      <CardBody>
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            {t('export.selectFormat')}
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {exportFormats.map(({ format, label, icon, description }) => (
              <button
                key={format}
                aria-label={`${label} (${data.length} registros)`}
                onClick={() => onExport({ format, includeMetadata: true })}
                className="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 dark:border-slate-700 hover:border-primary-500 dark:hover:border-primary-400 hover:shadow-md transition-all bg-white dark:bg-slate-900"
              >
                <div className="text-primary-600 dark:text-primary-400">
                  {icon}
                </div>
                <span className="font-medium text-sm text-gray-900 dark:text-white">
                  {label}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  {description}
                </span>
              </button>
            ))}
          </div>

          <div className="mt-8 p-4 bg-blue-50 dark:bg-slate-800 rounded-lg">
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">
              Opções Adicionais
            </h4>
            <div className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Incluir metadados
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Incluir data/hora
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Compactar arquivo
                </span>
              </label>
            </div>
          </div>

          <button className="w-full mt-6 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-primary-600 to-blue-600 text-white font-medium rounded-lg hover:from-primary-700 hover:to-blue-700 transition-all hover:shadow-lg">
            <Download className="w-5 h-5" />
            Exportar Selecionados
          </button>
        </div>
      </CardBody>
    </Card>
  )
}
