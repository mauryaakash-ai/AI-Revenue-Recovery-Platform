import React from 'react'
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'

interface KpiCardProps {
  label: string
  value: string | number
  delta?: string
  trend?: 'up' | 'down' | 'neutral'
  subtext?: string
  highlight?: boolean
}

export const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  delta,
  trend,
  subtext,
  highlight = false
}) => {
  return (
    <div className={`bg-white rounded-lg border p-5 transition-shadow hover:shadow-sm ${
      highlight ? 'border-blue-300 ring-1 ring-blue-100' : 'border-slate-200'
    }`}>
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p>
        {delta && (
          <span className={`inline-flex items-center text-xs font-medium px-2 py-0.5 rounded ${
            trend === 'up'
              ? 'text-emerald-700 bg-emerald-50'
              : trend === 'down'
              ? 'text-red-700 bg-red-50'
              : 'text-slate-600 bg-slate-100'
          }`}>
            {trend === 'up' && <ArrowUpRight className="w-3 h-3 mr-0.5" />}
            {trend === 'down' && <ArrowDownRight className="w-3 h-3 mr-0.5" />}
            {trend === 'neutral' && <Minus className="w-3 h-3 mr-0.5" />}
            {delta}
          </span>
        )}
      </div>

      <div className="mt-2.5">
        <p className="text-2xl font-bold tracking-tight text-slate-900">{value}</p>
        {subtext && (
          <p className="mt-1 text-xs text-slate-500">{subtext}</p>
        )}
      </div>
    </div>
  )
}

