import clsx from 'clsx'
import React from 'react'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  interactive?: boolean
  highlight?: boolean
}

export function Card({
  children,
  interactive = false,
  highlight = false,
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={clsx(
        'bg-white dark:bg-slate-900 rounded-lg border transition-all duration-200',
        'shadow-sm dark:shadow-sm',
        'border-gray-200 dark:border-slate-700',
        interactive && 'cursor-pointer hover:shadow-md dark:hover:shadow-md hover:border-primary-400',
        highlight && 'ring-2 ring-primary-500',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
}

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
  return (
    <div className="flex items-start justify-between px-6 py-4 border-b border-gray-200 dark:border-slate-700">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        {subtitle && <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}

interface CardBodyProps {
  children: React.ReactNode
  className?: string
}

export function CardBody({ children, className }: CardBodyProps) {
  return <div className={clsx('p-6', className)}>{children}</div>
}

interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div
      className={clsx(
        'px-6 py-4 border-t border-gray-200 dark:border-slate-700',
        'flex items-center justify-between',
        className
      )}
    >
      {children}
    </div>
  )
}
