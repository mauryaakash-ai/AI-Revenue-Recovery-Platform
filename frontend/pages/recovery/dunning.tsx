import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Repeat, Calendar, CreditCard, AlertTriangle, CheckCircle2, 
  RefreshCw, MessageSquare, Mail, ShieldAlert, ArrowRight, 
  TrendingDown, UserX, UserCheck, Smartphone, ExternalLink 
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function SubscriptionDunningPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeStage, setActiveStage] = useState<string>('all')
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const stageParam = activeStage !== 'all' ? `?stage=${activeStage}` : ''
      const res = await axios.get(`${baseUrl}/api/v1/dunning/subscriptions${stageParam}`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch dunning queue', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [activeStage])

  const handleAction = async (id: string, action: string) => {
    try {
      const res = await axios.post(`${baseUrl}/api/v1/dunning/${id}/action`, { action })
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
              <div className="p-2 rounded-lg bg-indigo-100 text-indigo-700">
                <Repeat className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Subscription Dunning & Involuntary Churn</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-indigo-100 text-indigo-800 border border-indigo-200">
                Graduated Dunning Sequence
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Recovers failed recurring payments with salary-cycle retry alignment and in-flow payment update flows.
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

        {/* Summary Metrics */}
        {data && data.summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Recurring MRR at Risk</p>
              <p className="text-xl font-bold text-slate-900 mt-1">{formatINR(data.summary.mrr_at_risk)}</p>
              <p className="text-[10px] text-slate-400 mt-1">{data.summary.active_recovering_count} Subscriptions in Dunning</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Recovered MRR</p>
              <p className="text-xl font-bold text-emerald-600 mt-1">{formatINR(data.summary.recovered_mrr)}</p>
              <p className="text-[10px] text-emerald-700 mt-1 font-medium">{data.summary.recovered_count} Subscriptions Saved</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Dunning Recovery Rate</p>
              <p className="text-xl font-bold text-indigo-600 mt-1">{data.summary.recovery_rate}%</p>
              <p className="text-[10px] text-indigo-700 mt-1 font-medium">82% Involuntary vs 18% Voluntary</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Salary-Day Alignment</p>
              <p className="text-xl font-bold text-purple-600 mt-1">1st & 5th Peak</p>
              <p className="text-[10px] text-slate-400 mt-1">Retry success +34% on salary day</p>
            </div>
          </div>
        )}

        {/* Graduated Dunning Stage Pipeline */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Graduated Dunning Pipeline</h3>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div className={`p-3 rounded-lg border text-xs ${activeStage === 'day_0_in_app' ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200 bg-slate-50'}`}>
              <div className="flex items-center justify-between font-bold text-slate-900">
                <span>Stage 1: Day 0</span>
                <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 text-[10px]">In-App Modal</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Soft prompt on login with 1-click update payment method.</p>
            </div>
            <div className={`p-3 rounded-lg border text-xs ${activeStage === 'day_3_email' ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200 bg-slate-50'}`}>
              <div className="flex items-center justify-between font-bold text-slate-900">
                <span>Stage 2: Day 3</span>
                <span className="px-1.5 py-0.5 rounded bg-purple-100 text-purple-800 text-[10px]">Smart Email</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Friendly reminder + salary cycle smart retry schedule.</p>
            </div>
            <div className={`p-3 rounded-lg border text-xs ${activeStage === 'day_7_whatsapp' ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200 bg-slate-50'}`}>
              <div className="flex items-center justify-between font-bold text-slate-900">
                <span>Stage 3: Day 7</span>
                <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px]">WhatsApp Nudge</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">High-converting interactive WhatsApp button with direct UPI setup.</p>
            </div>
            <div className={`p-3 rounded-lg border text-xs ${activeStage === 'day_14_final' ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200 bg-slate-50'}`}>
              <div className="flex items-center justify-between font-bold text-slate-900">
                <span>Stage 4: Day 14</span>
                <span className="px-1.5 py-0.5 rounded bg-red-100 text-red-800 text-[10px]">Final Notice</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Urgency escalation before automated account suspension.</p>
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto no-scrollbar">
          {[
            { id: 'all', label: 'All Subscriptions' },
            { id: 'day_0_in_app', label: 'Day 0 In-App' },
            { id: 'day_3_email', label: 'Day 3 Email' },
            { id: 'day_7_whatsapp', label: 'Day 7 WhatsApp' },
            { id: 'day_14_final', label: 'Day 14 Final Notice' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveStage(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                activeStage === tab.id
                  ? 'bg-indigo-600 text-white font-semibold shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Subscription Queue Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Active Dunning & Involuntary Churn Roster</h2>
            <span className="text-xs text-slate-400">Targeting high-LTV recurring accounts</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="px-4 py-3">Customer & Plan</th>
                  <th className="px-4 py-3">Recurring Amount</th>
                  <th className="px-4 py-3">Failure Reason</th>
                  <th className="px-4 py-3">Dunning Stage</th>
                  <th className="px-4 py-3">Salary Cycle Day</th>
                  <th className="px-4 py-3">Retries</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Operational Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-slate-400">
                      Loading subscription dunning roster...
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item: any) => (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-4 py-3">
                        <p className="font-bold text-slate-900">{item.customer_name}</p>
                        <p className="text-[10px] text-slate-500">{item.plan_name}</p>
                        <span className="text-[9px] text-slate-400">{item.customer_email}</span>
                      </td>
                      <td className="px-4 py-3 font-bold text-slate-900">
                        ₹{item.recurring_amount.toLocaleString('en-IN')}/mo
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                          item.failure_reason === 'expired_card' ? 'bg-amber-100 text-amber-800' :
                          item.failure_reason === 'insufficient_balance' ? 'bg-blue-100 text-blue-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {item.failure_reason.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase">
                          {item.dunning_stage.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-semibold text-slate-700">{item.salary_cycle_day}th of month</span>
                      </td>
                      <td className="px-4 py-3 font-semibold text-slate-600">
                        {item.retry_count} attempts
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.status === 'recovered' ? 'bg-emerald-100 text-emerald-800' :
                          item.status === 'churned_involuntary' ? 'bg-red-100 text-red-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          {item.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {item.status === 'recovered' ? (
                          <span className="text-emerald-600 font-semibold text-[11px] flex items-center justify-end gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> MRR Saved
                          </span>
                        ) : (
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleAction(item.id, 'retry_now')}
                              className="px-2.5 py-1 text-[11px] font-semibold bg-indigo-600 hover:bg-indigo-700 text-white rounded transition shadow-2xs"
                              title="Smart Retry Aligned with Balance"
                            >
                              Smart Retry
                            </button>
                            <button
                              onClick={() => handleAction(item.id, 'send_payment_update_link')}
                              className="px-2 py-1 text-[11px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition"
                              title="Send Update Card / Bank Form"
                            >
                              Update Link
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

