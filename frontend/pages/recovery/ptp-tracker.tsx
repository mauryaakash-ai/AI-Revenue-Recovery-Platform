import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  CalendarCheck, Clock, CheckCircle2, XCircle, AlertTriangle, 
  RefreshCw, MessageSquare, PhoneCall, Mail, Shield, UserCheck, 
  ArrowUpRight, Award 
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function PTPTrackerPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeStatus, setActiveStatus] = useState<string>('all')
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const statusParam = activeStatus !== 'all' ? `?fulfillment_status=${activeStatus}` : ''
      const res = await axios.get(`${baseUrl}/api/v1/ptp/records${statusParam}`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch PTP records', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [activeStatus])

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      const res = await axios.post(`${baseUrl}/api/v1/ptp/${id}/update-status`, {
        fulfillment_status: status
      })
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
              <div className="p-2 rounded-lg bg-cyan-100 text-cyan-700">
                <CalendarCheck className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Promise-to-Pay (PTP) Tracker</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-cyan-100 text-cyan-800 border border-cyan-200">
                Customer Commitment & Reliability Scoring
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Monitors promised payment dates from voice calls and WhatsApp chat with automated pre-due nudges and reliability scoring.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs self-start"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Commitments
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
              <p className="text-[11px] font-medium text-slate-500">Total Committed Value</p>
              <p className="text-xl font-bold text-slate-900 mt-1">{formatINR(data.summary.total_committed_value)}</p>
              <p className="text-[10px] text-slate-400 mt-1">{data.summary.total_commitments} Total PTP Records</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Realized Kept Revenue</p>
              <p className="text-xl font-bold text-emerald-600 mt-1">{formatINR(data.summary.realized_kept_value)}</p>
              <p className="text-[10px] text-emerald-700 mt-1 font-medium">{data.summary.kept_count} Promises Kept</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">PTP Fulfillment Rate</p>
              <p className="text-xl font-bold text-cyan-600 mt-1">{data.summary.commitment_kept_rate}%</p>
              <p className="text-[10px] text-cyan-700 mt-1 font-medium">Auto Pre-Due Nudges Sent</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Avg Customer Reliability</p>
              <p className="text-xl font-bold text-purple-600 mt-1">{data.summary.average_reliability_score}%</p>
              <p className="text-[10px] text-slate-400 mt-1">Trust-based channel modulation</p>
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto no-scrollbar">
          {[
            { id: 'all', label: 'All Commitments' },
            { id: 'pending', label: 'Pending PTPs (Upcoming)' },
            { id: 'kept', label: 'Kept Promises (Fulfilled)' },
            { id: 'broken', label: 'Broken Promises (Escalated)' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveStatus(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                activeStatus === tab.id
                  ? 'bg-cyan-600 text-white font-semibold shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* PTP Records Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Promise-to-Pay Scheduled Ledger</h2>
            <span className="text-xs text-slate-400">Integrated with Voice Agent and WhatsApp reply trackers</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="px-4 py-3">Customer & Ref</th>
                  <th className="px-4 py-3">Promised Amount</th>
                  <th className="px-4 py-3">Promised Date</th>
                  <th className="px-4 py-3">Source Channel</th>
                  <th className="px-4 py-3">Reliability Score</th>
                  <th className="px-4 py-3">Fulfillment Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                      Loading Promise-to-Pay commitments...
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item: any) => (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-4 py-3">
                        <p className="font-bold text-slate-900">{item.customer_name}</p>
                        <p className="text-[10px] text-slate-500 font-mono">{item.reference_type.toUpperCase()} · {item.reference_id}</p>
                      </td>
                      <td className="px-4 py-3 font-bold text-slate-900">
                        ₹{item.promised_amount.toLocaleString('en-IN')}
                      </td>
                      <td className="px-4 py-3 font-semibold text-slate-800">
                        {item.promised_date ? new Date(item.promised_date).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 uppercase">
                          {item.channel_source.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1.5">
                          <span className={`font-bold ${item.reliability_score >= 80 ? 'text-emerald-600' : 'text-amber-600'}`}>
                            {item.reliability_score}%
                          </span>
                          <Award className="w-3 h-3 text-slate-400" />
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.fulfillment_status === 'kept' ? 'bg-emerald-100 text-emerald-800' :
                          item.fulfillment_status === 'broken' ? 'bg-red-100 text-red-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          {item.fulfillment_status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {item.fulfillment_status === 'kept' ? (
                          <span className="text-emerald-600 font-semibold text-[11px] flex items-center justify-end gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Kept
                          </span>
                        ) : (
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleUpdateStatus(item.id, 'kept')}
                              className="px-2.5 py-1 text-[11px] font-semibold bg-emerald-600 hover:bg-emerald-700 text-white rounded transition shadow-2xs"
                              title="Mark as Paid / Kept"
                            >
                              Mark Kept
                            </button>
                            <button
                              onClick={() => handleUpdateStatus(item.id, 'broken')}
                              className="px-2 py-1 text-[11px] font-medium bg-red-50 hover:bg-red-100 text-red-700 rounded transition"
                              title="Mark as Broken & Escalate"
                            >
                              Mark Broken
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

