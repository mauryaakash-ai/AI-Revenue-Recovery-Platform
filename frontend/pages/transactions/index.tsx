import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import axios from 'axios'
import { Search, Filter, ArrowRight, ChevronLeft, ChevronRight, CreditCard, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'
import { StatusBadge } from '../../components/ui/StatusBadge'
import { ProbabilityBadge } from '../../components/ui/ProbabilityBadge'

export default function TransactionsPage() {
  const router = useRouter()
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [paymentMethod, setPaymentMethod] = useState('')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)
  const [page, setPage] = useState(0)
  const limit = 25

  useEffect(() => {
    if (router.query.search) {
      setSearch(router.query.search as string)
    }
  }, [router.query.search])

  const loadTransactions = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const params: any = {
        limit,
        offset: page * limit
      }
      if (search) params.search = search
      if (status) params.status = status
      if (paymentMethod) params.payment_method = paymentMethod

      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/transactions`, { params })
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTransactions()
  }, [merchantId, page, status, paymentMethod, search])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(0)
    loadTransactions()
  }

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Transactions Ledger</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time stream of all payment authorizations, bank decline events, and recovery status tags.
          </p>
        </div>
      </div>

      {/* Search & Filter bar */}
      <div className="mt-6 bg-white rounded-lg border border-slate-200 p-4 shadow-xs">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search transaction ID, order ID, failure reason..."
              className="w-full pl-9 pr-4 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <select
              value={status}
              onChange={(e) => { setStatus(e.target.value); setPage(0) }}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none cursor-pointer"
            >
              <option value="">All Statuses</option>
              <option value="failed">Failed</option>
              <option value="success">Success</option>
              <option value="authorized">Authorized</option>
            </select>

            <select
              value={paymentMethod}
              onChange={(e) => { setPaymentMethod(e.target.value); setPage(0) }}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none cursor-pointer"
            >
              <option value="">All Methods</option>
              <option value="upi">UPI</option>
              <option value="card">Cards</option>
              <option value="netbanking">Net Banking</option>
              <option value="wallet">Wallets</option>
            </select>

            <button
              type="submit"
              className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Transactions Table */}
      <div className="mt-6 bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
              <tr>
                <th className="py-3 px-4">Transaction ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4">Method & Bank</th>
                <th className="py-3 px-4">Status / Decline Reason</th>
                <th className="py-3 px-4">Recovery Potential</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-600" />
                    <p className="mt-2 text-xs">Fetching transactions...</p>
                  </td>
                </tr>
              ) : (
                data?.transactions?.map((t: any) => (
                  <tr key={t.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">
                      <Link href={`/transactions/${t.id}`} className="hover:text-blue-600 hover:underline">
                        {t.id}
                      </Link>
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-900">{t.customer_name}</td>
                    <td className="py-3 px-4 text-right font-bold text-slate-900">
                      ₹{t.amount.toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <p className="font-semibold text-slate-800 uppercase">{t.payment_method}</p>
                      <p className="text-[10px] text-slate-400">{t.bank_name}</p>
                    </td>
                    <td className="py-3 px-4">
                      {t.status === 'failed' ? (
                        <div>
                          <span className="inline-flex items-center text-rose-700 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5" />
                            {t.failure_reason || 'Decline'}
                          </span>
                          <p className="text-[10px] font-mono text-slate-400">{t.failure_code}</p>
                        </div>
                      ) : (
                        <StatusBadge status={t.status} />
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {t.status === 'failed' ? (
                        <ProbabilityBadge probability={t.recovery_probability} />
                      ) : (
                        <span className="text-slate-400 text-xs">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-500">
                      {new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        href={`/transactions/${t.id}`}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800"
                      >
                        Investigate
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && (
          <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
            <span>
              Total records: <span className="font-semibold text-slate-900">{data.total.toLocaleString()}</span>
            </span>

            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded border border-slate-200 bg-white disabled:opacity-40 hover:bg-slate-50 transition"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="font-medium text-slate-700">Page {page + 1}</span>
              <button
                disabled={(page + 1) * limit >= data.total}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded border border-slate-200 bg-white disabled:opacity-40 hover:bg-slate-50 transition"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}

