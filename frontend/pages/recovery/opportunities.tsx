import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'
import {
  Search, Filter, Download, HelpCircle, CheckCircle2, RefreshCw, ArrowUpDown, ChevronLeft, ChevronRight, Loader2, CheckSquare, Square,
  PhoneCall, MessageSquare
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'
import { StatusBadge } from '../../components/ui/StatusBadge'
import { ProbabilityBadge } from '../../components/ui/ProbabilityBadge'
import { ExplainabilityModal } from '../../components/ui/ExplainabilityModal'

export default function RecoveryOpportunitiesPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [search, setSearch] = useState('')
  const [priority, setPriority] = useState('')
  const [paymentMethod, setPaymentMethod] = useState('')
  const [failureType, setFailureType] = useState('')
  const [status, setStatus] = useState('identified')
  const [minProb, setMinProb] = useState<number | ''>('')
  
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)
  const [page, setPage] = useState(0)
  const limit = 20

  // Selection for batch actions
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  
  // Explainability modal
  const [explainOpen, setExplainOpen] = useState(false)
  const [activeExplain, setActiveExplain] = useState<any>(null)

  const loadOpportunities = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const params: any = {
        limit,
        offset: page * limit
      }
      if (search) params.search = search
      if (priority) params.priority = priority
      if (paymentMethod) params.payment_method = paymentMethod
      if (failureType) params.failure_type = failureType
      if (status) params.status = status
      if (minProb !== '') params.min_prob = Number(minProb) / 100

      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/recovery/opportunities`, { params })
      setData(res.data)
      setSelectedIds([])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOpportunities()
  }, [merchantId, page, priority, paymentMethod, failureType, status, minProb])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(0)
    loadOpportunities()
  }

  const handleToggleSelectAll = () => {
    if (!data?.items) return
    if (selectedIds.length === data.items.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(data.items.map((i: any) => i.id))
    }
  }

  const handleToggleSelect = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id))
    } else {
      setSelectedIds([...selectedIds, id])
    }
  }

  const handleBatchExecute = async () => {
    if (selectedIds.length === 0) return
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/recovery/opportunities/batch-execute`, {
        opportunity_ids: selectedIds
      })
      alert(`Successfully executed ${selectedIds.length} recoveries!`)
      loadOpportunities()
    } catch (err: any) {
      alert('Batch execution failed: ' + err.message)
    }
  }

  const handleExecuteSingle = async (oppId: string) => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/recovery/opportunities/${oppId}/execute`)
      alert('Recovery action initiated.')
      loadOpportunities()
    } catch (err: any) {
      alert('Failed: ' + err.message)
    }
  }

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Recovery Opportunities</h1>
          <p className="text-xs text-slate-500 mt-1">
            <span className="font-semibold text-slate-800">3,842 transactions</span> can potentially be recovered using AI-optimized strategies.
          </p>
        </div>

        {selectedIds.length > 0 && (
          <div className="flex items-center gap-3 bg-blue-50 border border-blue-200 px-4 py-2 rounded-lg animate-in fade-in">
            <span className="text-xs font-semibold text-blue-900">{selectedIds.length} selected</span>
            <button
              onClick={handleBatchExecute}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition"
            >
              Batch Approve Recoveries
            </button>
          </div>
        )}
      </div>

      {/* Filter Bar */}
      <div className="mt-6 bg-white rounded-lg border border-slate-200 p-4 shadow-xs space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Transaction ID, Customer Name, or Failure..."
              className="w-full pl-9 pr-4 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={priority}
              onChange={(e) => { setPriority(e.target.value); setPage(0) }}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none cursor-pointer"
            >
              <option value="">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High Priority</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
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

            <select
              value={failureType}
              onChange={(e) => { setFailureType(e.target.value); setPage(0) }}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none cursor-pointer"
            >
              <option value="">All Failure Types</option>
              <option value="temporary">Temporary / Timeout</option>
              <option value="issuer_declined">Issuer Declined</option>
              <option value="insufficient_funds">Insufficient Funds</option>
              <option value="technical">Technical / Network</option>
            </select>

            <select
              value={minProb}
              onChange={(e) => { setMinProb(e.target.value ? Number(e.target.value) : ''); setPage(0) }}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none cursor-pointer"
            >
              <option value="">Any Probability</option>
              <option value="80">&gt; 80% High Probability</option>
              <option value="70">&gt; 70% Moderate</option>
              <option value="50">&gt; 50% Standard</option>
            </select>

            <select
              value={status}
              onChange={(e) => { setStatus(e.target.value); setPage(0) }}
              className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none cursor-pointer"
            >
              <option value="identified">Identified (Active)</option>
              <option value="scheduled">Scheduled</option>
              <option value="recovered">Recovered</option>
              <option value="abandoned">Abandoned</option>
              <option value="">All Statuses</option>
            </select>

            <button
              type="submit"
              className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition"
            >
              Filter
            </button>
          </div>
        </form>
      </div>

      {/* Opportunities Data Table */}
      <div className="mt-6 bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
              <tr>
                <th className="py-3 px-4 w-10">
                  <button onClick={handleToggleSelectAll} className="p-0.5 text-slate-400 hover:text-slate-600">
                    {data?.items && selectedIds.length === data.items.length && data.items.length > 0 ? (
                      <CheckSquare className="w-4 h-4 text-blue-600" />
                    ) : (
                      <Square className="w-4 h-4" />
                    )}
                  </button>
                </th>
                <th className="py-3 px-4">Transaction</th>
                <th className="py-3 px-4">Merchant / Customer</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4">Failure Code / Bank</th>
                <th className="py-3 px-4">Recovery Probability</th>
                <th className="py-3 px-4">Recommended Strategy</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-600" />
                    <p className="mt-2 text-xs">Filtering recovery candidates...</p>
                  </td>
                </tr>
              ) : data?.items?.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    <p className="font-semibold text-slate-700">No recovery opportunities match selected filters.</p>
                    <p className="text-xs mt-1 text-slate-400">Try broadening your search or resetting probability threshold.</p>
                  </td>
                </tr>
              ) : (
                data?.items?.map((opp: any) => {
                  const isSelected = selectedIds.includes(opp.id)
                  return (
                    <tr key={opp.id} className={`hover:bg-slate-50/80 transition ${isSelected ? 'bg-blue-50/40' : ''}`}>
                      <td className="py-3 px-4">
                        <button onClick={() => handleToggleSelect(opp.id)} className="p-0.5 text-slate-400 hover:text-slate-600">
                          {isSelected ? <CheckSquare className="w-4 h-4 text-blue-600" /> : <Square className="w-4 h-4" />}
                        </button>
                      </td>
                      <td className="py-3 px-4 font-mono font-medium text-slate-900">
                        <Link href={`/transactions/${opp.transaction_id}`} className="hover:text-blue-600 hover:underline">
                          {opp.transaction_id}
                        </Link>
                      </td>
                      <td className="py-3 px-4">
                        <p className="font-semibold text-slate-900">{opp.merchant_name}</p>
                        <p className="text-[11px] text-slate-500">{opp.customer_name} · <span className="uppercase text-[10px] font-semibold text-slate-400">{opp.customer_segment}</span></p>
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge status={opp.priority} type="priority" />
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-slate-900">
                        ₹{opp.amount.toLocaleString()}
                      </td>
                      <td className="py-3 px-4">
                        <p className="font-medium text-slate-700">{opp.failure_reason}</p>
                        <p className="text-[10px] text-slate-400 font-mono">{opp.bank_name} · {opp.payment_method.toUpperCase()}</p>
                      </td>
                      <td className="py-3 px-4">
                        <ProbabilityBadge probability={opp.recovery_probability} showBar />
                      </td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center gap-1 font-medium text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded text-xs">
                          {opp.recommended_action}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <Link
                            href="/recovery/voice-agent"
                            className="p-1 text-pink-600 hover:text-pink-700 rounded hover:bg-pink-50"
                            title="Launch Free AI Voice Call"
                          >
                            <PhoneCall className="w-3.5 h-3.5" />
                          </Link>
                          <Link
                            href="/recovery/sms-gateway"
                            className="p-1 text-blue-600 hover:text-blue-700 rounded hover:bg-blue-50"
                            title="Send Demo Recovery SMS"
                          >
                            <MessageSquare className="w-3.5 h-3.5" />
                          </Link>
                          <button
                            onClick={() => {
                              setActiveExplain({
                                title: `AI Strategy for ${opp.transaction_id}`,
                                recommendation: opp.recommended_action,
                                expectedUplift: `₹${opp.expected_recovery.toLocaleString()}`,
                                reasons: opp.explainability_reasons,
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
                            onClick={() => handleExecuteSingle(opp.id)}
                            className="px-2.5 py-1 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded transition"
                          >
                            Approve
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {data && (
          <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
            <span>
              Showing <span className="font-semibold text-slate-900">{page * limit + 1}</span> to{' '}
              <span className="font-semibold text-slate-900">{Math.min((page + 1) * limit, data.total)}</span> of{' '}
              <span className="font-semibold text-slate-900">{data.total.toLocaleString()}</span> opportunities
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

      <ExplainabilityModal
        isOpen={explainOpen}
        onClose={() => setExplainOpen(false)}
        title={activeExplain?.title}
        recommendation={activeExplain?.recommendation}
        expectedUplift={activeExplain?.expectedUplift}
        reasons={activeExplain?.reasons || []}
        onApprove={activeExplain?.oppId ? () => handleExecuteSingle(activeExplain.oppId) : undefined}
      />
    </AppShell>
  )
}

