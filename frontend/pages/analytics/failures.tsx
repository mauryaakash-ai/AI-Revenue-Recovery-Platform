import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts'
import { AlertTriangle, TrendingUp, ShieldAlert, Sparkles, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function FailureAnalyticsPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/analytics/failures-breakdown`)
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

  const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#64748b']

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="pb-6 border-b border-slate-200">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Payment Failure Diagnostics</h1>
        <p className="text-xs text-slate-500 mt-1">
          Detailed taxonomy of decline reasons, bank-level error spikes, and automated root-cause detection.
        </p>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Classifying bank error telemetry...</p>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {/* Spike Anomaly Alert Banner */}
          {data?.spike_detected && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-5 flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-lg bg-red-600 text-white flex items-center justify-center shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-red-900">Anomaly Spike Detected</span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-red-100 text-red-800">Critical</span>
                </div>
                <p className="text-sm font-semibold text-slate-900 mt-1">{data.spike_detected.title}</p>
                <p className="text-xs text-slate-600 mt-0.5">{data.spike_detected.description}</p>
                <div className="mt-3 flex items-center gap-2">
                  <span className="text-xs font-semibold text-red-700">Root cause: {data.spike_detected.root_cause}</span>
                  <span className="text-slate-300">|</span>
                  <span className="text-xs font-semibold text-slate-800">Action: {data.spike_detected.recommended_action}</span>
                </div>
              </div>
            </div>
          )}

          {/* 2 Grids: Breakdown by Reason & Bank */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Failure by Reason */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
              <h3 className="text-sm font-bold text-slate-900 mb-4">Failures by Reason</h3>
              
              <div className="h-60 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data?.failure_reasons || []}
                      dataKey="percentage"
                      nameKey="reason"
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={4}
                    >
                      {data?.failure_reasons?.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(val) => [`${val}%`, 'Share']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="mt-4 space-y-2 text-xs">
                {data?.failure_reasons?.map((r: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between py-1 border-b border-slate-50">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                      <span className="font-medium text-slate-800">{r.reason}</span>
                    </div>
                    <div className="flex items-center gap-3 font-medium">
                      <span className="text-slate-500">₹{r.amount}</span>
                      <span className="font-bold text-slate-900">{r.percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Failure by Bank */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
              <h3 className="text-sm font-bold text-slate-900 mb-4">Failures by Issuing Bank</h3>
              
              <div className="h-60 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data?.bank_distribution || []} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                    <XAxis type="number" stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `${v}%`} />
                    <YAxis type="category" dataKey="bank" stroke="#94a3b8" fontSize={11} width={80} />
                    <Tooltip formatter={(val) => [`${val}%`, 'Failure Share']} />
                    <Bar dataKey="percentage" fill="#ef4444" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="mt-4 space-y-2 text-xs">
                {data?.bank_distribution?.map((b: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between py-1 border-b border-slate-50">
                    <span className="font-medium text-slate-800">{b.bank}</span>
                    <div className="flex items-center gap-3 font-medium">
                      <span className="text-slate-500">₹{b.amount}</span>
                      <span className="font-bold text-slate-900">{b.percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  )
}

