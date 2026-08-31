import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import {
  Download, Sparkles, HelpCircle, ArrowRight, CheckCircle2, ShieldCheck, RefreshCw, Filter, ChevronRight, Loader2
} from 'lucide-react'
import { AppShell } from '../components/layout/AppShell'
import { KpiCard } from '../components/ui/KpiCard'
import { StatusBadge } from '../components/ui/StatusBadge'
import { ProbabilityBadge } from '../components/ui/ProbabilityBadge'
import { RecoveryFunnel } from '../components/ui/RecoveryFunnel'
import { ExplainabilityModal } from '../components/ui/ExplainabilityModal'

export default function Dashboard() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [timeframe, setTimeframe] = useState('7D')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Explainability modal state
  const [explainOpen, setExplainOpen] = useState(false)
  const [selectedOpp, setSelectedOpp] = useState<any>(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/analytics/overview?timeframe=${timeframe}`)
      setData(res.data)
      setError(null)
    } catch (err: any) {
      console.error(err)
      setError('Unable to load overview data. Please verify backend is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [merchantId, timeframe])

  const handleExport = () => {
    if (!data?.top_opportunities) return
    const csvContent = "data:text/csv;charset=utf-8," + 
      ["Transaction ID,Merchant,Amount,Failure Reason,Recovery Probability,Recommended Action"].join(",") + "\n" +
      data.top_opportunities.map((o: any) => `${o.transaction_id},${o.merchant_name},${o.amount},${o.failure_reason},${Math.round(o.recovery_probability * 100)}%,${o.recommended_action}`).join("\n")
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", `razorpay_revenue_recovery_${timeframe}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleApproveRecovery = async (oppId: string) => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/recovery/opportunities/${oppId}/execute`)
      alert('Recovery initiated successfully via UPI fallback link.')
      loadData()
    } catch (err: any) {
      alert('Failed to execute recovery: ' + err.message)
    }
  }

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Revenue Recovery</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              Live Engine
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Recover more revenue from failed payments with AI-powered retry strategies and customer-affinity routing.
          </p>
        </div>

        {/* Timeframe selector & Export */}
        <div className="flex items-center gap-2.5">
          <div className="inline-flex rounded-lg border border-slate-200 bg-white p-0.5 shadow-xs">
            {['24H', '7D', '30D', '90D', '6M', '1Y'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                  timeframe === tf
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          <button
            onClick={handleExport}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs transition"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            Export
          </button>
        </div>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="text-xs text-slate-500 mt-3 font-medium">Computing deterministic recovery telemetry & models...</p>
        </div>
      ) : error ? (
        <div className="my-6 p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
          {error}
        </div>
      ) : (
        <div className="space-y-6 pt-6">
          {/* Section 12: 6 KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            <KpiCard
              label="Revenue at Risk"
              value={data?.kpis?.revenue_at_risk?.formatted || '₹1.82 Cr'}
              delta={data?.kpis?.revenue_at_risk?.delta || '-4.8%'}
              trend="down"
              subtext="vs previous period"
            />
            <KpiCard
              label="Recoverable Revenue"
              value={data?.kpis?.recoverable_revenue?.formatted || '₹1.14 Cr'}
              subtext="AI estimated (62.6%)"
              highlight
            />
            <KpiCard
              label="Revenue Recovered"
              value={data?.kpis?.recovered_revenue?.formatted || '₹78.6 L'}
              delta={data?.kpis?.recovered_revenue?.delta || '+12.4%'}
              trend="up"
              subtext="vs previous period"
            />
            <KpiCard
              label="Recovery Rate"
              value={data?.kpis?.recovery_rate?.formatted || '68.9%'}
              delta={data?.kpis?.recovery_rate?.delta || '+5.2%'}
              trend="up"
              subtext="Benchmark avg: 54%"
            />
            <KpiCard
              label="Active Recoveries"
              value={data?.kpis?.active_recoveries?.formatted || '3,842'}
              subtext="1,204 high priority"
            />
            <KpiCard
              label="Net Recovered"
              value={data?.kpis?.net_revenue_recovered?.formatted || '₹76.2 L'}
              subtext="After recovery costs · 3175% ROI"
            />
          </div>

          {/* Section 13: Main Revenue Chart */}
          <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
              <div>
                <h3 className="text-base font-semibold text-slate-900">Revenue Recovery Performance</h3>
                <p className="text-xs text-slate-500">Telemetry tracking failed payment volume against AI recoverable and recovered amounts</p>
              </div>

              <div className="flex items-center gap-4 text-xs">
                <span className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-400" />
                  Revenue at Risk
                </span>
                <span className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                  Recoverable
                </span>
                <span className="flex items-center gap-1.5 text-slate-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  Recovered
                </span>
              </div>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data?.chart_data || []} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.15}/>
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0}/>
                    </linearGradient>
                    <linearGradient id="recovPotGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                    </linearGradient>
                    <linearGradient id="recovGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.25}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    tickFormatter={(val) => `₹${(val / 100000).toFixed(1)}L`}
                  />
                  <Tooltip
                    formatter={(value: any, name: string) => [
                      `₹${(Number(value) / 100000).toFixed(2)}L`,
                      name === 'revenue_at_risk' ? 'Revenue at Risk' : name === 'recoverable' ? 'Recoverable' : 'Recovered'
                    ]}
                  />
                  <Area type="monotone" dataKey="revenue_at_risk" stroke="#f43f5e" strokeWidth={2} fillOpacity={1} fill="url(#riskGrad)" />
                  <Area type="monotone" dataKey="recoverable" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#recovPotGrad)" />
                  <Area type="monotone" dataKey="recovered" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#recovGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Section 14: Recovery Funnel */}
          <RecoveryFunnel funnel={data?.funnel} />

          {/* Section 16 & 17: AI Recommendation Panel */}
          {data?.ai_recommendation && (
            <div className="bg-gradient-to-r from-blue-50/80 via-indigo-50/50 to-white rounded-lg border border-blue-200/80 p-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-3.5">
                  <div className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-blue-700">AI Recommendation</span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800">High Impact</span>
                    </div>
                    <p className="text-sm font-semibold text-slate-900 mt-1 leading-snug">
                      {data.ai_recommendation.highlight}
                    </p>
                    <p className="text-xs text-slate-600 mt-1">
                      <span className="font-medium text-slate-800">Recommended action:</span> {data.ai_recommendation.recommended_action}
                      <span className="mx-2 text-slate-300">|</span>
                      <span className="text-emerald-700 font-semibold">Expected uplift: {data.ai_recommendation.expected_incremental_formatted}</span>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2.5 shrink-0 pl-13 md:pl-0">
                  <button
                    onClick={() => {
                      setSelectedOpp(data.ai_recommendation)
                      setExplainOpen(true)
                    }}
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-white border border-blue-200 rounded-lg hover:bg-blue-50 transition"
                  >
                    <HelpCircle className="w-3.5 h-3.5 text-blue-500" />
                    Why?
                  </button>
                  <button
                    onClick={() => {
                      alert(`Reviewing recommendation: ${data.ai_recommendation.recommended_action}`)
                    }}
                    className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition"
                  >
                    Review recommendation
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Section 15: AI Recovery Opportunities Table */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-slate-900">Top Recovery Opportunities</h3>
                <p className="text-xs text-slate-500">High-probability payment failures ranked by recovery impact</p>
              </div>

              <Link
                href="/recovery/opportunities"
                className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition"
              >
                View all opportunities
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
                  <tr>
                    <th className="py-3 px-4">Transaction</th>
                    <th className="py-3 px-4">Merchant / Customer</th>
                    <th className="py-3 px-4 text-right">Amount</th>
                    <th className="py-3 px-4">Failure</th>
                    <th className="py-3 px-4">Probability</th>
                    <th className="py-3 px-4">Recommended Action</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-800">
                  {data?.top_opportunities?.map((opp: any) => (
                    <tr key={opp.id} className="hover:bg-slate-50/80 transition">
                      <td className="py-3 px-4 font-mono font-medium text-slate-900">
                        <Link href={`/transactions/${opp.transaction_id}`} className="hover:text-blue-600 hover:underline">
                          {opp.transaction_id}
                        </Link>
                      </td>
                      <td className="py-3 px-4">
                        <p className="font-semibold text-slate-900">{opp.merchant_name}</p>
                        <p className="text-[11px] text-slate-500">{opp.customer_name}</p>
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-slate-900">
                        ₹{opp.amount.toLocaleString()}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                          <span className="font-medium text-slate-700">{opp.failure_reason}</span>
                        </div>
                        <span className="text-[10px] text-slate-400">{opp.bank_name}</span>
                      </td>
                      <td className="py-3 px-4">
                        <ProbabilityBadge probability={opp.recovery_probability} />
                      </td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center gap-1 font-medium text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded text-xs">
                          {opp.recommended_action}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => {
                              setSelectedOpp({
                                title: `Recommendation for ${opp.transaction_id}`,
                                highlight: `${opp.recommended_action} for ₹${opp.amount.toLocaleString()} (${opp.failure_reason})`,
                                recommended_action: opp.recommended_action,
                                expected_incremental_formatted: `₹${opp.expected_recovery.toLocaleString()}`,
                                why_reasons: opp.explainability_reasons,
                                oppId: opp.id
                              })
                              setExplainOpen(true)
                            }}
                            className="p-1 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-100"
                            title="Why this recommendation?"
                          >
                            <HelpCircle className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleApproveRecovery(opp.id)}
                            className="px-2.5 py-1 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded transition"
                          >
                            Approve
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Explainability Dialog */}
      <ExplainabilityModal
        isOpen={explainOpen}
        onClose={() => setExplainOpen(false)}
        title={selectedOpp?.title}
        recommendation={selectedOpp?.recommended_action}
        expectedUplift={selectedOpp?.expected_incremental_formatted}
        reasons={selectedOpp?.why_reasons || []}
        onApprove={selectedOpp?.oppId ? () => handleApproveRecovery(selectedOpp.oppId) : undefined}
      />
    </AppShell>
  )
}
