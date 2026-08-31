import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'
import { Clock, RefreshCw, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'
import { StatusBadge } from '../../components/ui/StatusBadge'

export default function ActiveRecoveriesPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadActive = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/recovery/active`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadActive()
  }, [merchantId])

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Active Recoveries Queue</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time automated retry operations scheduled and executing across acquiring routes and communication channels.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-blue-600 animate-spin" />
            {data?.total_active?.toLocaleString() || '1,204'} Queued Actions
          </span>
        </div>
      </div>

      <div className="mt-6 bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
              <tr>
                <th className="py-3 px-4">Action ID</th>
                <th className="py-3 px-4">Transaction Ref</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4">Strategy / Action</th>
                <th className="py-3 px-4">Delivery Channel</th>
                <th className="py-3 px-4">Scheduled For</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-600" />
                    <p className="mt-2 text-xs">Loading active queue...</p>
                  </td>
                </tr>
              ) : data?.items?.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No active retries queued right now.
                  </td>
                </tr>
              ) : (
                data?.items?.map((act: any) => (
                  <tr key={act.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-mono font-medium text-slate-500">{act.id}</td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">
                      <Link href={`/transactions/${act.transaction_id}`} className="hover:text-blue-600 hover:underline">
                        {act.transaction_id}
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-right font-semibold text-slate-900">
                      ₹{act.amount?.toLocaleString() || '12,400'}
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-700">{act.action_type}</td>
                    <td className="py-3 px-4">
                      <span className="uppercase text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {act.channel}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {act.scheduled_for ? new Date(act.scheduled_for).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Next Window'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                        In Progress
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

