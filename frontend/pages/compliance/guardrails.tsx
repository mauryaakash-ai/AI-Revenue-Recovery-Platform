import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle2, RefreshCw, 
  Clock, Moon, FileText, Slash, BellOff, Lock, UserX 
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function ComplianceGuardrailsPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState<string>('all')

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const actionParam = activeFilter !== 'all' ? `?action_taken=${activeFilter}` : ''
      const res = await axios.get(`${baseUrl}/api/v1/guardrails/audit-log${actionParam}`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch compliance logs', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [activeFilter])

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-emerald-100 text-emerald-700">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Stopping Rules & Compliance Guardrails</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                RBI & NPCI Regulatory Gatekeeper
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Guarantees strict adherence to quiet hours, TRAI DND registries, retry frequency caps, and automatic recovery halts.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs self-start"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Audit Logs
          </button>
        </div>

        {/* Live Guardrails Policy Cards */}
        {data && data.summary && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <div className="flex items-center gap-2 text-indigo-700 font-bold text-xs pb-1 border-b border-slate-100">
                <Moon className="w-4 h-4" />
                <span>NPCI Quiet Hours Gatekeeper</span>
              </div>
              <p className="text-xs text-slate-600 mt-2">
                Automated recovery messages and calls held between <strong>21:00 and 08:00 IST</strong> to respect regulatory quiet windows.
              </p>
              <div className="mt-3 flex items-center justify-between text-[10px] text-slate-400">
                <span className="text-emerald-700 font-semibold">100% Enforced</span>
                <span>NPCI Circular 2026/04</span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <div className="flex items-center gap-2 text-blue-700 font-bold text-xs pb-1 border-b border-slate-100">
                <BellOff className="w-4 h-4" />
                <span>TRAI National DND Filter</span>
              </div>
              <p className="text-xs text-slate-600 mt-2">
                Real-time validation against TRAI DND registry. Suppresses voice calls and SMS to prevent regulatory non-compliance.
              </p>
              <div className="mt-3 flex items-center justify-between text-[10px] text-slate-400">
                <span className="text-emerald-700 font-semibold">Zero Spam Violations</span>
                <span>TRAI TCCCPR Regulations</span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <div className="flex items-center gap-2 text-purple-700 font-bold text-xs pb-1 border-b border-slate-100">
                <Lock className="w-4 h-4" />
                <span>RBI Retry Frequency Cap</span>
              </div>
              <p className="text-xs text-slate-600 mt-2">
                Hard ceiling of <strong>maximum 3 retry attempts per 24 hours</strong> across Card and Mandate rails to prevent bank throttling.
              </p>
              <div className="mt-3 flex items-center justify-between text-[10px] text-slate-400">
                <span className="text-emerald-700 font-semibold">Acquirer Protected</span>
                <span>RBI CoF Tokenization Mandate</span>
              </div>
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto no-scrollbar">
          {[
            { id: 'all', label: 'All Evaluations' },
            { id: 'blocked_quiet_hours', label: 'Blocked: Quiet Hours' },
            { id: 'blocked_dnd', label: 'Blocked: DND Registry' },
            { id: 'throttled_max_attempts', label: 'Throttled: Max Attempts' },
            { id: 'halted_recovered', label: 'Halted: Already Paid' },
            { id: 'dispatched', label: 'Dispatched (Passed)' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                activeFilter === tab.id
                  ? 'bg-slate-900 text-white font-semibold shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Immutable Audit Ledger */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Immutable Compliance & Stopping Decision Ledger</h2>
            <span className="text-xs text-slate-400">Full audit trail for compliance verification</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Target & Channel</th>
                  <th className="px-4 py-3">Rule Applied</th>
                  <th className="px-4 py-3">Decision</th>
                  <th className="px-4 py-3">Compliance Rationale</th>
                  <th className="px-4 py-3">Regulatory Citation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                      Loading compliance audit logs...
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item: any) => (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-4 py-3 font-mono text-[10px] text-slate-500 whitespace-nowrap">
                        {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A'}
                      </td>
                      <td className="px-4 py-3">
                        <p className="font-bold text-slate-900 font-mono text-[11px]">{item.target_id}</p>
                        <span className="text-[10px] text-slate-500 uppercase">{item.target_type} · {item.channel}</span>
                      </td>
                      <td className="px-4 py-3 font-semibold text-slate-700">
                        {item.rule_applied.replace(/_/g, ' ').toUpperCase()}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.action_taken === 'dispatched' ? 'bg-emerald-100 text-emerald-800' :
                          item.action_taken === 'blocked_quiet_hours' ? 'bg-indigo-100 text-indigo-800' :
                          item.action_taken === 'blocked_dnd' ? 'bg-purple-100 text-purple-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          {item.action_taken.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 max-w-sm text-slate-600">
                        {item.rationale}
                      </td>
                      <td className="px-4 py-3 font-medium text-slate-500 text-[10px]">
                        {item.regulatory_citation}
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

