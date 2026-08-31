import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'
import { History, CheckCircle2, DollarSign, TrendingUp, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'
import { KpiCard } from '../../components/ui/KpiCard'

export default function RecoveryHistoryPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadHistory = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/recovery/history`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [merchantId])

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Recovery History & Net ROI</h1>
          <p className="text-xs text-slate-500 mt-1">
            Complete audit trail of executed recoveries, communication overheads, and net realized revenue.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
        <KpiCard
          label="Total Recovered Volume"
          value="₹78.6 L"
          subtext="1,502 successful recovery events"
          trend="up"
          delta="+12.4%"
        />
        <KpiCard
          label="Total Recovery Overheads"
          value="₹2.4 L"
          subtext="Avg ₹1.85 / communication attempt"
        />
        <KpiCard
          label="Net Revenue Recovered"
          value="₹76.2 L"
          subtext="Net ROI: 3,175% across all cohorts"
          highlight
        />
      </div>

      {/* History Ledger Table */}
      <div className="mt-6 bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
        <div className="px-6 py-4 border-b border-slate-200">
          <h3 className="text-base font-semibold text-slate-900">Executed Recoveries Audit Log</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
              <tr>
                <th className="py-3 px-4">Transaction ID</th>
                <th className="py-3 px-4">Action Type</th>
                <th className="py-3 px-4">Channel</th>
                <th className="py-3 px-4 text-right">Recovered Amount</th>
                <th className="py-3 px-4 text-right">Channel Cost</th>
                <th className="py-3 px-4 text-right">Net Recovered</th>
                <th className="py-3 px-4">Executed Timestamp</th>
                <th className="py-3 px-4">Outcome</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-600" />
                    <p className="mt-2 text-xs">Loading recovery history...</p>
                  </td>
                </tr>
              ) : (
                data?.items?.map((item: any) => (
                  <tr key={item.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-mono font-semibold text-slate-900">
                      <Link href={`/transactions/${item.transaction_id}`} className="hover:text-blue-600 hover:underline">
                        {item.transaction_id}
                      </Link>
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-700">{item.action_type}</td>
                    <td className="py-3 px-4">
                      <span className="uppercase text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {item.channel}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-slate-900">
                      ₹{item.recovered_amount?.toLocaleString() || '12,400'}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-500">
                      ₹{item.cost?.toFixed(2) || '1.85'}
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-emerald-700">
                      ₹{item.net_recovered ? item.net_recovered.toLocaleString() : (item.recovered_amount - 1.85).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {new Date(item.executed_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Recovered
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  )
}

