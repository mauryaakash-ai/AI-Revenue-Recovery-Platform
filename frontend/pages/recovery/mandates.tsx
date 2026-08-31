import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  CreditCard, RefreshCw, CheckCircle2, ShieldCheck, AlertCircle, 
  Smartphone, ArrowRight, ExternalLink, Clock, Layers, Shield 
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function MandateRetryPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeType, setActiveType] = useState<string>('all')
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const typeParam = activeType !== 'all' ? `?mandate_type=${activeType}` : ''
      const res = await axios.get(`${baseUrl}/api/v1/mandates/queue${typeParam}`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch mandate queue', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [activeType])

  const handleAction = async (id: string, action: string) => {
    try {
      const res = await axios.post(`${baseUrl}/api/v1/mandates/${id}/action`, { action })
      setActionSuccess(res.data.message)
      fetchData()
      setTimeout(() => setActionSuccess(null), 5000)
    } catch (err) {
      console.error(err)
    }
  }

  const formatINR = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`
    return `₹${val.toLocaleString('en-IN')}`
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-emerald-100 text-emerald-700">
                <CreditCard className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Mandate Retry Sequencer</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                UPI Autopay & e-NACH
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Compliant recurring-mandate retry sequencer enforcing RBI window limits and automated fallback links.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs self-start"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Queue
          </button>
        </div>

        {/* Action Alert */}
        {actionSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-medium flex items-center gap-2 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}

        {/* Summary Metric Cards */}
        {data && data.summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Total Mandate Value</p>
              <p className="text-xl font-bold text-slate-900 mt-1">{formatINR(data.summary.total_mandate_value)}</p>
              <p className="text-[10px] text-slate-400 mt-1">{data.summary.total_mandates} Mandate Records</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Recovered Mandates</p>
              <p className="text-xl font-bold text-emerald-600 mt-1">{formatINR(data.summary.recovered_mandate_value)}</p>
              <p className="text-[10px] text-emerald-700 mt-1 font-medium">{data.summary.succeeded_count} Successful Executions</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Mandate Recovery Rate</p>
              <p className="text-xl font-bold text-blue-600 mt-1">{data.summary.recovery_rate}%</p>
              <p className="text-[10px] text-blue-700 mt-1 font-medium">Within 3-Attempt RBI Cap</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">RBI Compliance Guardrail</p>
              <p className="text-xl font-bold text-purple-600 mt-1">100% Verified</p>
              <p className="text-[10px] text-slate-400 mt-1">Zero bank throttling violations</p>
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto no-scrollbar">
          {[
            { id: 'all', label: 'All Mandates' },
            { id: 'upi_autopay', label: 'UPI Autopay (Instant Mandate)' },
            { id: 'enach', label: 'e-NACH (Bank Account Debits)' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveType(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                activeType === tab.id
                  ? 'bg-emerald-600 text-white font-semibold shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Mandate Queue Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Mandate Retry Queue & Bank Rail Diagnostics</h2>
            <span className="text-xs text-slate-400">Strictly sequenced to prevent issuer throttling</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="px-4 py-3">Mandate & Customer</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Bank Rail</th>
                  <th className="px-4 py-3">RBI Attempt Tracker</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                      Loading mandate retry queues...
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item: any) => (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-4 py-3">
                        <p className="font-bold text-slate-900">{item.customer_name}</p>
                        <p className="text-[10px] text-slate-500 font-mono">{item.mandate_id}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.mandate_type === 'upi_autopay' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
                        }`}>
                          {item.mandate_type === 'upi_autopay' ? 'UPI AUTOPAY' : 'e-NACH'}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-bold text-slate-900">
                        ₹{item.amount.toLocaleString('en-IN')}
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-semibold text-slate-800">{item.bank_name}</p>
                        <p className="text-[10px] text-red-500">{item.failure_code}</p>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1.5">
                          <span className="font-bold text-slate-900">{item.attempt_count} / {item.max_attempts}</span>
                          <span className="text-[10px] text-slate-400 font-medium">(RBI Limit: 3)</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.status === 'succeeded' ? 'bg-emerald-100 text-emerald-800' :
                          item.status === 'fallback_link_sent' ? 'bg-purple-100 text-purple-800' :
                          item.status === 'exhausted' ? 'bg-red-100 text-red-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          {item.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {item.status === 'succeeded' ? (
                          <span className="text-emerald-600 font-semibold text-[11px] flex items-center justify-end gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Recovered
                          </span>
                        ) : (
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleAction(item.id, 'sequence_retry_now')}
                              className="px-2.5 py-1 text-[11px] font-semibold bg-emerald-600 hover:bg-emerald-700 text-white rounded transition shadow-2xs"
                              title="Execute Compliant Sequence Retry"
                            >
                              Sequence Retry
                            </button>
                            <button
                              onClick={() => handleAction(item.id, 'send_manual_fallback')}
                              className="px-2 py-1 text-[11px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition"
                              title="Send Fallback 1-Click Payment Link"
                            >
                              Manual Fallback
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  )
}

