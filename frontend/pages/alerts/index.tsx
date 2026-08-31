import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'
import {
  Bell, AlertTriangle, ShieldAlert, CheckCircle2, Clock, Check, ArrowRight, Loader2
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'
import { StatusBadge } from '../../components/ui/StatusBadge'

export default function AlertsCenterPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadAlerts = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/alerts`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAlerts()
  }, [merchantId])

  const handleAction = async (alertId: string, action: string) => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/alerts/${alertId}/action`, { action })
      loadAlerts()
    } catch (err: any) {
      alert('Failed to update alert: ' + err.message)
    }
  }

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Real-Time Alerts Center</h1>
            <span className="text-xs font-bold px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200">
              {data?.active_count || 3} Active
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Automated anomaly detection, bank gateway degradation alerts, and high-value revenue recovery triggers.
          </p>
        </div>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Scanning telemetry for anomalies...</p>
        </div>
      ) : (
        <div className="mt-6 space-y-4">
          {data?.alerts?.map((alt: any) => {
            const isCritical = alt.severity === 'critical'
            const isResolved = alt.status === 'resolved'

            return (
              <div
                key={alt.id}
                className={`bg-white rounded-xl border p-6 shadow-xs transition ${
                  isResolved
                    ? 'opacity-60 border-slate-200'
                    : isCritical
                    ? 'border-red-300 ring-1 ring-red-100'
                    : 'border-slate-200'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex items-start gap-3.5">
                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                      isCritical ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                    }`}>
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-bold text-slate-900">{alt.title}</h3>
                        <StatusBadge status={alt.severity} type="severity" />
                        {isResolved && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                            Resolved
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">{alt.description}</p>
                      
                      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 bg-slate-50 border border-slate-100 p-3 rounded-lg text-xs">
                        <div>
                          <span className="text-slate-400 font-semibold uppercase text-[10px]">Potential Impact</span>
                          <p className="font-bold text-red-600 mt-0.5">{alt.potential_impact}</p>
                        </div>
                        <div>
                          <span className="text-slate-400 font-semibold uppercase text-[10px]">AI Assessment</span>
                          <p className="font-medium text-slate-800 mt-0.5">{alt.ai_assessment}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap sm:flex-col items-end gap-2 shrink-0">
                    <span className="text-[11px] text-slate-400">
                      Detected {new Date(alt.detected_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>

                    {!isResolved && (
                      <div className="flex items-center gap-1.5 mt-2">
                        <button
                          onClick={() => handleAction(alt.id, 'acknowledge')}
                          className="px-2.5 py-1 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded text-xs font-semibold"
                        >
                          Acknowledge
                        </button>
                        <button
                          onClick={() => handleAction(alt.id, 'snooze')}
                          className="px-2.5 py-1 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded text-xs font-semibold"
                        >
                          Snooze 1h
                        </button>
                        <button
                          onClick={() => handleAction(alt.id, 'resolve')}
                          className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-semibold flex items-center gap-1"
                        >
                          <Check className="w-3 h-3" />
                          Resolve
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </AppShell>
  )
}

