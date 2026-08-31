import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import axios from 'axios'
import { ArrowLeft, User, Sparkles, CheckCircle2, CreditCard, Clock, Phone, Mail, ArrowRight, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'
import { KpiCard } from '../../components/ui/KpiCard'
import { StatusBadge } from '../../components/ui/StatusBadge'

export default function CustomerProfilePage() {
  const router = useRouter()
  const { id } = router.query
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadCustomer = async () => {
    if (!id) return
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/customers/${id}`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCustomer()
  }, [id, merchantId])

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      {/* Header */}
      <div className="pb-4 border-b border-slate-200">
        <button
          onClick={() => router.back()}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 mb-3 transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Customers
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-slate-900 text-white font-bold text-base flex items-center justify-center shadow-xs">
              {data?.name?.split(' ').map((n: string) => n[0]).join('') || 'C'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-slate-900">{data?.name || 'Customer Profile'}</h1>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 uppercase">
                  {data?.segment || 'VIP Customer'}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-1">
                <span className="flex items-center gap-1"><Mail className="w-3 h-3 text-slate-400" /> {data?.email}</span>
                <span className="flex items-center gap-1"><Phone className="w-3 h-3 text-slate-400" /> {data?.phone}</span>
                <span>Customer since {data?.created_at ? new Date(data.created_at).toLocaleDateString([], { month: 'short', year: 'numeric' }) : '2024'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Compiling customer behavioral intelligence...</p>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {/* 4 Customer Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard
              label="Total Payments Volume"
              value={data?.total_payments_formatted || '₹8.6L'}
              subtext="Lifetime processed GMV"
            />
            <KpiCard
              label="Payment Success Rate"
              value={`${data?.success_rate || 96.2}%`}
              subtext="Primary mode: UPI"
              trend="up"
            />
            <KpiCard
              label="Lifetime Value (LTV)"
              value={data?.lifetime_value_formatted || '₹2.4L'}
              highlight
            />
            <KpiCard
              label="Recovery History"
              value={data?.recovery_history_summary || '4 of 5 recovered'}
              subtext="80% conversion rate"
            />
          </div>

          {/* Section 23: AI Customer Insight Panel */}
          {data?.ai_insight && (
            <div className="bg-gradient-to-r from-blue-50/90 via-indigo-50/50 to-white rounded-xl border border-blue-200 p-6 shadow-xs">
              <div className="flex items-start gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div className="space-y-3 flex-1">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700">AI Customer Insight</span>
                    <p className="text-base font-bold text-slate-900 mt-0.5">{data.ai_insight.headline}</p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-white/80 border border-blue-100 rounded-lg p-3 text-xs">
                    <div>
                      <p className="text-slate-500">Preferred Mode</p>
                      <p className="font-bold text-slate-900 mt-0.5">{data.ai_insight.preferred_payment_method}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Typical Payment Time</p>
                      <p className="font-bold text-slate-900 mt-0.5">{data.ai_insight.typical_payment_time}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Recommended Recovery</p>
                      <p className="font-bold text-blue-700 mt-0.5">{data.ai_insight.recommended_approach}</p>
                    </div>
                  </div>

                  <div className="space-y-1.5 pt-1">
                    <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider text-[10px]">Attribution Rationale:</p>
                    {data.ai_insight.rationale?.map((r: string, idx: number) => (
                      <div key={idx} className="flex items-center gap-2 text-xs text-slate-600">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recent Customer Transactions */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
            <div className="px-6 py-4 border-b border-slate-200">
              <h3 className="text-sm font-bold text-slate-900">Recent Transaction History</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
                  <tr>
                    <th className="py-3 px-4">Transaction ID</th>
                    <th className="py-3 px-4 text-right">Amount</th>
                    <th className="py-3 px-4">Method</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-800">
                  {data?.transactions?.map((t: any) => (
                    <tr key={t.id} className="hover:bg-slate-50/80 transition">
                      <td className="py-3 px-4 font-mono font-semibold text-slate-900">{t.id}</td>
                      <td className="py-3 px-4 text-right font-bold text-slate-900">₹{t.amount.toLocaleString()}</td>
                      <td className="py-3 px-4 uppercase font-semibold text-slate-700">{t.payment_method}</td>
                      <td className="py-3 px-4">
                        <StatusBadge status={t.status} />
                      </td>
                      <td className="py-3 px-4 text-slate-500">
                        {new Date(t.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link href={`/transactions/${t.id}`} className="text-xs font-semibold text-blue-600 hover:underline">
                          Investigate
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  )
}

