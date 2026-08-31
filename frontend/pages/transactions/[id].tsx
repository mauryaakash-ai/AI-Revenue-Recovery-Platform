import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import axios from 'axios'
import {
  ArrowLeft, CheckCircle2, AlertTriangle, Sparkles, Clock, Shield, ChevronRight, User, HelpCircle, Loader2
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'
import { StatusBadge } from '../../components/ui/StatusBadge'
import { ProbabilityBadge } from '../../components/ui/ProbabilityBadge'
import { ExplainabilityModal } from '../../components/ui/ExplainabilityModal'

export default function TransactionDetailPage() {
  const router = useRouter()
  const { id } = router.query
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)
  const [explainOpen, setExplainOpen] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  const loadTransaction = async () => {
    if (!id) return
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/transactions/${id}`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTransaction()
  }, [id, merchantId])

  const handleApprove = async () => {
    try {
      setActionLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/recovery/opportunities/${data.id}/execute`)
      alert(`Recovery initiated successfully! Channel: ${data.ai_recommendation?.recommended_channel || 'UPI Intent'}`)
      loadTransaction()
    } catch (err: any) {
      alert('Failed to execute: ' + err.message)
    } finally {
      setActionLoading(false)
    }
  }

  const handleDismiss = () => {
    alert('Recovery opportunity dismissed.')
    router.push('/recovery/opportunities')
  }

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      {/* Back button & ID */}
      <div className="pb-4 border-b border-slate-200">
        <button
          onClick={() => router.back()}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 mb-3 transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Ledger
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 font-mono font-bold">
              TX
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-slate-900 font-mono">{data?.id || id}</h1>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                  {data?.failure_reason || 'Bank Declined'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">Order ID: {data?.order_id || 'order_983102'}</p>
            </div>
          </div>

          <div className="text-right">
            <p className="text-2xl font-bold tracking-tight text-slate-900">{data?.amount_formatted || '₹45,000'}</p>
            <p className="text-xs text-slate-500">Authorized in INR</p>
          </div>
        </div>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Loading full transaction telemetry...</p>
        </div>
      ) : (
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Details & Timeline */}
          <div className="lg:col-span-2 space-y-6">
            {/* Section 21: AI Recommendation Box */}
            <div className="bg-gradient-to-br from-blue-50/90 via-indigo-50/40 to-white rounded-xl border border-blue-200 p-6 shadow-xs">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">AI Recovery Recommendation</h3>
                    <p className="text-xs text-slate-500">Automated Smart Recovery Strategy</p>
                  </div>
                </div>

                <ProbabilityBadge probability={data?.recovery_probability || 0.91} />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-5">
                <div className="bg-white/80 border border-blue-100 rounded-lg p-3">
                  <p className="text-[11px] font-semibold text-slate-500 uppercase">Recommended Strategy</p>
                  <p className="text-sm font-bold text-slate-900 mt-0.5">{data?.ai_recommendation?.recommended_strategy || 'Retry via UPI'}</p>
                </div>
                <div className="bg-white/80 border border-blue-100 rounded-lg p-3">
                  <p className="text-[11px] font-semibold text-slate-500 uppercase">Optimal Timing Window</p>
                  <p className="text-sm font-bold text-slate-900 mt-0.5">{data?.ai_recommendation?.recommended_time || '8:30 PM (Evening)'}</p>
                </div>
                <div className="bg-white/80 border border-blue-100 rounded-lg p-3">
                  <p className="text-[11px] font-semibold text-slate-500 uppercase">Expected Success Rate</p>
                  <p className="text-sm font-bold text-emerald-700 mt-0.5">{data?.ai_recommendation?.expected_success_rate || '91%'}</p>
                </div>
                <div className="bg-white/80 border border-blue-100 rounded-lg p-3">
                  <p className="text-[11px] font-semibold text-slate-500 uppercase">Recommended Channel</p>
                  <p className="text-sm font-bold text-slate-900 mt-0.5">{data?.ai_recommendation?.recommended_channel || 'UPI Intent / WhatsApp'}</p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-6 pt-4 border-t border-blue-100/80 flex flex-wrap items-center justify-between gap-3">
                <button
                  onClick={() => setExplainOpen(true)}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-700 hover:text-blue-900"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  Why this recommendation?
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleDismiss}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 transition"
                  >
                    Dismiss Opportunity
                  </button>
                  <button
                    disabled={actionLoading}
                    onClick={handleApprove}
                    className="px-4 py-1.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-xs transition flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Approve and Execute Recovery
                  </button>
                </div>
              </div>
            </div>

            {/* Section 20: Transaction Event Timeline */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
              <h3 className="text-sm font-bold text-slate-900 mb-4">Transaction Event Timeline</h3>

              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {data?.timeline?.map((evt: any, idx: number) => {
                  const isSuccess = evt.status === 'completed'
                  const isFail = evt.status === 'failed'
                  const isAi = evt.status === 'ai_processed' || evt.status === 'recommended'
                  const isScheduled = evt.status === 'scheduled'

                  return (
                    <div key={idx} className="relative">
                      <div className={`absolute -left-6 top-1 w-4 h-4 rounded-full border-2 bg-white flex items-center justify-center ${
                        isFail
                          ? 'border-rose-500 bg-rose-50'
                          : isSuccess
                          ? 'border-emerald-500 bg-emerald-50'
                          : isAi
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-slate-400 bg-slate-100'
                      }`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${
                          isFail ? 'bg-rose-500' : isSuccess ? 'bg-emerald-500' : isAi ? 'bg-blue-500' : 'bg-slate-400'
                        }`} />
                      </div>

                      <div className="flex items-center justify-between">
                        <p className="text-xs font-bold text-slate-900">{evt.event}</p>
                        <span className="text-[11px] font-mono text-slate-400">{evt.timestamp}</span>
                      </div>
                      <p className="text-xs text-slate-600 mt-0.5">{evt.description}</p>
                      <span className="text-[10px] text-slate-400 font-medium">Actor: {evt.actor}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Right Col: Customer Card & Meta */}
          <div className="space-y-6">
            {/* Customer Profile Card */}
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Customer Profile</span>
                <Link
                  href={`/customers/${data?.customer?.id}`}
                  className="text-xs font-semibold text-blue-600 hover:underline inline-flex items-center gap-0.5"
                >
                  Full Profile <ChevronRight className="w-3 h-3" />
                </Link>
              </div>

              <div className="mt-4 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-slate-900 text-white font-bold flex items-center justify-center text-sm">
                  {data?.customer?.name?.split(' ').map((n: string) => n[0]).join('') || 'AS'}
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-900">{data?.customer?.name}</p>
                  <p className="text-xs text-slate-500">{data?.customer?.email}</p>
                </div>
              </div>

              <div className="mt-4 space-y-2 text-xs border-t border-slate-100 pt-3">
                <div className="flex justify-between py-1 border-b border-slate-50">
                  <span className="text-slate-500">Customer Tier</span>
                  <span className="font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded uppercase text-[10px]">
                    {data?.customer?.segment || 'VIP'}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-50">
                  <span className="text-slate-500">Lifetime Value</span>
                  <span className="font-bold text-slate-900">{data?.customer?.lifetime_value_formatted || '₹2.4L'}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Historical Recovery Rate</span>
                  <span className="font-bold text-emerald-700">{Math.round((data?.customer?.historical_recovery_rate || 0.83) * 100)}%</span>
                </div>
              </div>
            </div>

            {/* Technical Metadata */}
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs text-xs space-y-2.5">
              <h4 className="font-semibold text-slate-900 uppercase tracking-wider text-[11px]">Technical Metadata</h4>
              
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Acquiring Bank</span>
                <span className="font-medium text-slate-900">{data?.bank_name}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Payment Method</span>
                <span className="font-medium uppercase text-slate-900">{data?.payment_method}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Failure Code</span>
                <span className="font-mono text-slate-700 text-[11px]">{data?.failure_code}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-500">Device Type</span>
                <span className="font-medium text-slate-900 capitalize">{data?.device_type || 'Mobile'}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Location</span>
                <span className="font-medium text-slate-900">{data?.location || 'Mumbai'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Explainability modal */}
      <ExplainabilityModal
        isOpen={explainOpen}
        onClose={() => setExplainOpen(false)}
        title={`AI Rationale for ${data?.id}`}
        recommendation={data?.ai_recommendation?.recommended_strategy}
        expectedUplift={data?.expected_recovery_formatted}
        reasons={data?.ai_recommendation?.why_reasons || []}
        onApprove={handleApprove}
      />
    </AppShell>
  )
}

