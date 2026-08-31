import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Building2, DollarSign, Clock, AlertOctagon, CheckCircle2, 
  RefreshCw, Send, Mail, MessageSquare, PhoneCall, ArrowUpRight, 
  FileText, Shield, UserCheck, ChevronRight 
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function B2BChaserPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeTier, setActiveTier] = useState<string>('all')
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const tierParam = activeTier !== 'all' ? `?risk_tier=${activeTier}` : ''
      const res = await axios.get(`${baseUrl}/api/v1/b2b-chaser/invoices${tierParam}`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch B2B invoices', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [activeTier])

  const handleSendReminder = async (id: string, stage: string, channel: string = 'email') => {
    try {
      const res = await axios.post(`${baseUrl}/api/v1/b2b-chaser/${id}/send-reminder`, {
        stage,
        channel
      })
      setActionSuccess(res.data.message)
      fetchData()
      setTimeout(() => setActionSuccess(null), 5000)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSettle = async (id: string) => {
    try {
      const res = await axios.post(`${baseUrl}/api/v1/b2b-chaser/${id}/settle`)
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
              <div className="p-2 rounded-lg bg-teal-100 text-teal-700">
                <Building2 className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">B2B Receivables Chaser</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-teal-100 text-teal-800 border border-teal-200">
                Smart Invoice Aging & Escalation
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Prioritizes corporate receivables by expected recovery value and automates escalating reminder workflows.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs self-start"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Ledgers
          </button>
        </div>

        {/* Action Alert */}
        {actionSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-medium flex items-center gap-2 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}

        {/* Aging Buckets Grid */}
        {data && data.summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">0 - 30 Days Past Due (DPD)</p>
              <p className="text-xl font-bold text-slate-900 mt-1">{formatINR(data.summary.aging_buckets['0_30_dpd'])}</p>
              <p className="text-[10px] text-teal-700 mt-1 font-medium">Stage 1: Friendly Nudge</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">31 - 60 DPD</p>
              <p className="text-xl font-bold text-blue-600 mt-1">{formatINR(data.summary.aging_buckets['31_60_dpd'])}</p>
              <p className="text-[10px] text-blue-700 mt-1 font-medium">Stage 2: Formal Notice + SOA</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">61 - 90 DPD</p>
              <p className="text-xl font-bold text-amber-600 mt-1">{formatINR(data.summary.aging_buckets['61_90_dpd'])}</p>
              <p className="text-[10px] text-amber-700 mt-1 font-medium">Stage 3: Account Owner Escalation</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">90+ DPD (Critical Risk)</p>
              <p className="text-xl font-bold text-red-600 mt-1">{formatINR(data.summary.aging_buckets['90_plus_dpd'])}</p>
              <p className="text-[10px] text-red-700 mt-1 font-medium">Stage 4: Human Collections Handoff</p>
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto no-scrollbar">
          {[
            { id: 'all', label: 'All Invoices' },
            { id: 'critical', label: 'Critical Risk (90+ DPD)' },
            { id: 'high', label: 'High Risk (60-90 DPD)' },
            { id: 'medium', label: 'Medium Risk (30-60 DPD)' },
            { id: 'low', label: 'Low Risk (0-30 DPD)' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTier(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                activeTier === tab.id
                  ? 'bg-teal-600 text-white font-semibold shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Invoice Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Prioritized B2B Chase Ledger</h2>
            <span className="text-xs text-slate-400">Ranked by Expected Recovery Value ($Amount \times Probability$)</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="px-4 py-3">Buyer & Invoice #</th>
                  <th className="px-4 py-3">Outstanding Amount</th>
                  <th className="px-4 py-3">Days Past Due</th>
                  <th className="px-4 py-3">Recovery Probability</th>
                  <th className="px-4 py-3">Expected Recovery Value</th>
                  <th className="px-4 py-3">Escalation Stage</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-slate-400">
                      Loading B2B receivables chase queue...
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item: any) => (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-4 py-3">
                        <p className="font-bold text-slate-900">{item.buyer_name}</p>
                        <p className="text-[10px] text-teal-700 font-mono font-semibold">{item.invoice_number}</p>
                        <span className="text-[9px] text-slate-400">GST: {item.buyer_gstin}</span>
                      </td>
                      <td className="px-4 py-3 font-bold text-slate-900">
                        ₹{item.amount.toLocaleString('en-IN')}
                      </td>
                      <td className="px-4 py-3 font-semibold">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          item.days_past_due > 60 ? 'bg-red-100 text-red-800 font-bold' :
                          item.days_past_due > 30 ? 'bg-amber-100 text-amber-800' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {item.days_past_due} DPD
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-bold text-slate-900">{item.expected_recovery_prob}%</span>
                      </td>
                      <td className="px-4 py-3 font-bold text-emerald-600">
                        ₹{item.expected_recovery_value.toLocaleString('en-IN')}
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-800 uppercase">
                          {item.current_stage.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.status === 'settled' ? 'bg-emerald-100 text-emerald-800' :
                          item.status === 'in_collections' ? 'bg-red-100 text-red-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          {item.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {item.status === 'settled' ? (
                          <span className="text-emerald-600 font-semibold text-[11px] flex items-center justify-end gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Settled
                          </span>
                        ) : (
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleSendReminder(item.id, 'formal_notice', 'email')}
                              className="px-2.5 py-1 text-[11px] font-semibold bg-teal-600 hover:bg-teal-700 text-white rounded transition shadow-2xs flex items-center gap-1"
                              title="Send Reminder + 1-Click SOA"
                            >
                              <Mail className="w-3 h-3" />
                              Send SOA
                            </button>
                            <button
                              onClick={() => handleSettle(item.id)}
                              className="px-2 py-1 text-[11px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition"
                              title="Mark Invoice as Settled"
                            >
                              Mark Paid
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

