import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { CreditCard, Sparkles, TrendingUp, CheckCircle2, ArrowRight, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function PaymentMethodsAnalyticsPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/analytics/payment-methods`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [merchantId])

  const chartData = [
    { method: 'UPI', failure_rate: 4.2, recovery_rate: 72.0 },
    { method: 'Cards', failure_rate: 6.8, recovery_rate: 61.0 },
    { method: 'Net Banking', failure_rate: 5.1, recovery_rate: 58.0 },
    { method: 'Wallets', failure_rate: 3.9, recovery_rate: 69.0 }
  ]

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="pb-6 border-b border-slate-200">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Payment Method Intelligence</h1>
        <p className="text-xs text-slate-500 mt-1">
          Comparative analysis of failure rates, recovery success rates, and customer method migration patterns.
        </p>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Aggregating multi-channel telemetry...</p>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {/* Method Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {data?.methods?.map((m: any, idx: number) => (
              <div key={idx} className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{m.method}</span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                    {m.volume_share} share
                  </span>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Failure Rate</span>
                    <span className="font-bold text-rose-600">{m.failure_rate}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Recovery Rate</span>
                    <span className="font-bold text-emerald-600">{m.recovery_rate}</span>
                  </div>
                  <div className="flex justify-between text-xs pt-1 border-t border-slate-100">
                    <span className="text-slate-500">Recovered Volume</span>
                    <span className="font-bold text-slate-900">{m.recovered_volume}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Comparative Chart */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-bold text-slate-900">Failure vs Recovery Rate Comparison</h3>
                <p className="text-xs text-slate-500">Benchmarked across all merchant payment channels</p>
              </div>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="method" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(val) => `${val}%`} />
                  <Tooltip formatter={(value: any) => [`${value}%`]} />
                  <Legend />
                  <Bar dataKey="failure_rate" name="Failure Rate (%)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="recovery_rate" name="Recovery Rate (%)" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* AI Strategic Takeaway */}
          <div className="bg-blue-50/70 rounded-xl border border-blue-200 p-6 flex items-start gap-3.5">
            <Sparkles className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h4 className="text-xs font-bold uppercase tracking-wider text-blue-900">Channel Strategy Insight</h4>
              <p className="text-xs text-blue-800 leading-relaxed">
                UPI demonstrates the highest recovery conversion (72.0%) due to frictionless biometric authorization and seamless deep linking. 
                Routing card failure recovery attempts to UPI Intent links generates an estimated <span className="font-semibold">+₹9.4L/month</span> in incremental recovered revenue.
              </p>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  )
}

