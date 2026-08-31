import React, { useState } from 'react'
import Link from 'next/link'
import { BarChart3, CreditCard, TrendingDown, Sparkles, ArrowRight, ShieldCheck, PieChart, Activity } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function AnalyticsHubPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')

  const hubs = [
    {
      title: 'Payment Method Intelligence',
      desc: 'Analyze failure vs recovery rates across UPI, Cards, Net Banking, and Wallets. View conversion uplifts by payment method.',
      href: '/analytics/payment-methods',
      icon: CreditCard,
      badge: '4 Payment Channels',
      stat: 'UPI: 72% Recovery'
    },
    {
      title: 'Failure Analysis & Spikes',
      desc: 'Root-cause breakdown of bank declines, insufficient funds, and network errors with real-time issuer spike alerts.',
      href: '/analytics/failures',
      icon: TrendingDown,
      badge: 'Live Bank Telemetry',
      stat: '38% Bank Declines'
    },
    {
      title: '7-Day Revenue Recovery Forecast',
      desc: 'Predictive machine learning models forecasting revenue at risk, expected recoverable volume, and scenario confidence intervals.',
      href: '/analytics/forecast',
      icon: Sparkles,
      badge: 'ML Forecast',
      stat: '₹1.9 Cr Expected'
    }
  ]

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="pb-6 border-b border-slate-200">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Analytics & Intelligence Hub</h1>
        <p className="text-xs text-slate-500 mt-1">
          Deep diagnostic telemetry, payment method benchmarks, failure root causes, and predictive revenue forecasts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        {hubs.map((hub, idx) => {
          const Icon = hub.icon
          return (
            <Link
              key={idx}
              href={hub.href}
              className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs hover:border-blue-300 hover:shadow-md transition flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                    {hub.badge}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 mt-4 group-hover:text-blue-600 transition">
                  {hub.title}
                </h3>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                  {hub.desc}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-800">{hub.stat}</span>
                <span className="text-xs font-semibold text-blue-600 inline-flex items-center gap-1 group-hover:translate-x-0.5 transition">
                  Explore <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </Link>
          )
        })}
      </div>
    </AppShell>
  )
}

