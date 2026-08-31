import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, LineChart, Line
} from 'recharts'
import { Sparkles, TrendingUp, ShieldCheck, ArrowUpRight, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'
import { KpiCard } from '../../components/ui/KpiCard'

export default function ForecastPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/analytics/forecast`)
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

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="pb-6 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">7-Day Revenue Recovery Forecast</h1>
          <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
            ML Predictive Model
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Probabilistic revenue forecasting generated from seasonal payment volumes, bank uptime signals, and historical recovery conversion curves.
        </p>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Running predictive Monte Carlo simulations...</p>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {/* Section 26: Forecast KPI Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <KpiCard
              label="Projected Revenue at Risk"
              value={data?.summary?.projected_risk || '₹4.2 Cr'}
              subtext="Next 7 days failure forecast"
            />
            <KpiCard
              label="Expected Recoverable"
              value={data?.summary?.expected_recoverable || '₹2.7 Cr'}
              subtext="64.3% addressable opportunity"
              highlight
            />
            <KpiCard
              label="Expected Recovery"
              value={data?.summary?.expected_recovery || '₹1.9 Cr'}
              subtext="70.4% conversion of recoverable"
              trend="up"
              delta="+8.4%"
            />
          </div>

          {/* Scenario Confidence Intervals */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-4">Forecast Range & Confidence Intervals</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-emerald-50/50 border border-emerald-200">
                <span className="text-xs font-semibold text-emerald-800 uppercase">Best-Case Scenario</span>
                <p className="text-xl font-bold text-emerald-900 mt-1">{data?.summary?.scenarios?.best_case || '₹2.2 Cr'}</p>
                <p className="text-[11px] text-emerald-700 mt-0.5">High bank authorization + peak UPI response</p>
              </div>

              <div className="p-4 rounded-lg bg-blue-50/50 border border-blue-200">
                <span className="text-xs font-semibold text-blue-800 uppercase">Expected Target</span>
                <p className="text-xl font-bold text-blue-900 mt-1">{data?.summary?.scenarios?.expected || '₹1.9 Cr'}</p>
                <p className="text-[11px] text-blue-700 mt-0.5">Statistical median trajectory (95% CI)</p>
              </div>

              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-xs font-semibold text-slate-700 uppercase">Worst-Case Floor</span>
                <p className="text-xl font-bold text-slate-900 mt-1">{data?.summary?.scenarios?.worst_case || '₹1.5 Cr'}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">Elevated issuer downtime & customer abandonment</p>
              </div>
            </div>
          </div>

          {/* 7-Day Forecast Chart */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-bold text-slate-900">Projected Daily Recovery Trajectory</h3>
                <p className="text-xs text-slate-500">Day-by-day expected recovery with high and low confidence bounds</p>
              </div>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data?.daily_forecast || []} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `₹${(v/100000).toFixed(1)}L`} />
                  <Tooltip formatter={(val: any, name: string) => [`₹${(Number(val)/100000).toFixed(2)}L`, name]} />
                  <Legend />
                  <Area type="monotone" dataKey="expected_recovery" name="Expected Recovery" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#forecastGrad)" />
                  <Area type="monotone" dataKey="risk" name="Projected Risk" stroke="#f43f5e" strokeWidth={1.5} fillOpacity={0.1} fill="#f43f5e" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  )
}

