import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'
import { Search, User, ArrowRight, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function CustomersIndexPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [search, setSearch] = useState('')
  const [segment, setSegment] = useState('')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)
  const [page, setPage] = useState(0)
  const limit = 20

  const loadCustomers = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const params: any = {
        limit,
        offset: page * limit
      }
      if (search) params.search = search
      if (segment) params.segment = segment

      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/customers`, { params })
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCustomers()
  }, [merchantId, page, segment])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(0)
    loadCustomers()
  }

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Customer Profiles & Affinity</h1>
          <p className="text-xs text-slate-500 mt-1">
            Customer lifetime value, typical payment hours, method affinities, and recovery success likelihoods.
          </p>
        </div>
      </div>

      <div className="mt-6 bg-white rounded-lg border border-slate-200 p-4 shadow-xs">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search customer name, email, or ID..."
              className="w-full pl-9 pr-4 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <select
              value={segment}
              onChange={(e) => { setSegment(e.target.value); setPage(0) }}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none cursor-pointer"
            >
              <option value="">All Segments</option>
              <option value="vip">VIP Customers</option>
              <option value="high_value">High Value</option>
              <option value="standard">Standard</option>
              <option value="at_risk">At Risk</option>
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

      <div className="mt-6 bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
              <tr>
                <th className="py-3 px-4">Customer Name</th>
                <th className="py-3 px-4">Segment</th>
                <th className="py-3 px-4 text-right">Lifetime Value (LTV)</th>
                <th className="py-3 px-4">Preferred Method</th>
                <th className="py-3 px-4">Active Hours</th>
                <th className="py-3 px-4">Recovery Rate</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-600" />
                    <p className="mt-2 text-xs">Loading customer directory...</p>
                  </td>
                </tr>
              ) : (
                data?.items?.map((c: any) => (
                  <tr key={c.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-700 text-[11px]">
                          {c.name.split(' ').map((n: string) => n[0]).join('')}
                        </div>
                        <div>
                          <Link href={`/customers/${c.id}`} className="font-semibold text-slate-900 hover:text-blue-600 hover:underline">
                            {c.name}
                          </Link>
                          <p className="text-[11px] text-slate-400">{c.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="uppercase text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                        {c.segment}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-slate-900">
                      ₹{c.lifetime_value?.toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <span className="uppercase font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded text-[11px]">
                        {c.preferred_payment_method}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-600">{c.typical_payment_hours}</td>
                    <td className="py-3 px-4 font-bold text-emerald-700">
                      {Math.round(c.historical_recovery_rate * 100)}%
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        href={`/customers/${c.id}`}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800"
                      >
                        Profile
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {data && (
          <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
            <span>
              Total customers: <span className="font-semibold text-slate-900">{data.total.toLocaleString()}</span>
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

