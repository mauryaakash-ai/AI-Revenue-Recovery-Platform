import React from 'react'
import { ArrowRight, CheckCircle2, Bot, AlertTriangle, ShieldCheck } from 'lucide-react'

interface FunnelStage {
  amount: number
  formatted: string
  count: number
  conversion_pct?: number
}

interface RecoveryFunnelProps {
  funnel: {
    failed_payments: FunnelStage
    ai_identified: FunnelStage
    recovery_attempts: FunnelStage
    successfully_recovered: FunnelStage
  }
}

export const RecoveryFunnel: React.FC<RecoveryFunnelProps> = ({ funnel }) => {
  const stages = [
    {
      title: 'Failed Payments',
      amount: funnel?.failed_payments?.formatted || '₹1.82 Cr',
      count: funnel?.failed_payments?.count || 3842,
      subtitle: '100% of at-risk base',
      conversion: '62.6% identified',
      icon: AlertTriangle,
      color: 'border-rose-200 bg-rose-50/40 text-rose-700',
      badgeColor: 'bg-rose-100 text-rose-800'
    },
    {
      title: 'AI Identified Opportunities',
      amount: funnel?.ai_identified?.formatted || '₹1.14 Cr',
      count: funnel?.ai_identified?.count || 2810,
      subtitle: '62.6% of failed volume',
      conversion: '80.7% attempted',
      icon: Bot,
      color: 'border-blue-200 bg-blue-50/40 text-blue-700',
      badgeColor: 'bg-blue-100 text-blue-800'
    },
    {
      title: 'Recovery Attempts',
      amount: funnel?.recovery_attempts?.formatted || '₹92.0 L',
      count: funnel?.recovery_attempts?.count || 2180,
      subtitle: '80.7% of opportunities',
      conversion: '85.4% recovered',
      icon: ShieldCheck,
      color: 'border-amber-200 bg-amber-50/40 text-amber-700',
      badgeColor: 'bg-amber-100 text-amber-800'
    },
    {
      title: 'Successfully Recovered',
      amount: funnel?.successfully_recovered?.formatted || '₹78.6 L',
      count: funnel?.successfully_recovered?.count || 1502,
      subtitle: '68.9% overall conversion',
      conversion: 'Realized Revenue',
      icon: CheckCircle2,
      color: 'border-emerald-200 bg-emerald-50/50 text-emerald-700',
      badgeColor: 'bg-emerald-100 text-emerald-800'
    }
  ]

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Recovery Conversion Funnel</h3>
          <p className="text-xs text-slate-500 mt-0.5">End-to-end recovery pipeline from failure detection to realized revenue</p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-700">
          Overall Recovery: 68.9%
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
        {stages.map((stage, idx) => {
          const Icon = stage.icon
          return (
            <div key={idx} className={`relative rounded-lg border p-4 ${stage.color}`}>
              <div className="flex items-center justify-between">
                <Icon className="w-5 h-5 opacity-90" />
                <span className={`text-[11px] font-semibold px-2 py-0.5 rounded ${stage.badgeColor}`}>
                  {stage.count.toLocaleString()} txns
                </span>
              </div>

              <div className="mt-3">
                <p className="text-xs font-medium opacity-80">{stage.title}</p>
                <p className="text-xl font-bold tracking-tight mt-0.5 text-slate-900">{stage.amount}</p>
                <p className="text-[11px] mt-1 text-slate-500">{stage.subtitle}</p>
              </div>

              {idx < stages.length - 1 && (
                <div className="hidden md:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 w-6 h-6 rounded-full bg-white border border-slate-200 items-center justify-center shadow-xs">
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

