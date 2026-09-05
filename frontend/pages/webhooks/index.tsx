import React, { useState, useEffect } from 'react'
import Head from 'next/head'
import { AppShell } from '../../components/layout/AppShell'
import {
  Webhook,
  Play,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Copy,
  Terminal,
  ShieldCheck,
  Zap,
  ArrowRight,
  Database
} from 'lucide-react'

interface WebhookEventItem {
  id: string
  provider: string
  event_type: string
  status: string
  idempotency_key: string
  transaction_id: string
  received_at: string
  payload_preview: any
}

export default function WebhookConsolePage() {
  const [events, setEvents] = useState<WebhookEventItem[]>([])
  const [loading, setLoading] = useState(false)
  const [simulating, setSimulating] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState('razorpay')
  const [simAmount, setSimAmount] = useState('18500')
  const [simReason, setSimReason] = useState('BAD_REQUEST_PAYMENT_TIMED_OUT')
  const [simulationResult, setSimulationResult] = useState<any>(null)

  const fetchEvents = async () => {
    try {
      setLoading(true)
      const res = await fetch('http://localhost:8000/api/v1/webhooks/events')
      if (res.ok) {
        const data = await res.json()
        setEvents(data.events || [])
      }
    } catch (e) {
      console.error('Failed to fetch events', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEvents()
  }, [])

  const handleSimulate = async () => {
    try {
      setSimulating(true)
      setSimulationResult(null)
      const res = await fetch('http://localhost:8000/api/v1/webhooks/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: selectedProvider,
          amount: parseFloat(simAmount) || 18500.0,
          customer_email: 'ananya.patel@example.com',
          customer_phone: '+91 98201 94821',
          failure_code: simReason,
          failure_reason: 'Bank connection timed out during 3DS OTP verification',
          merchant_id: 'merchant_urbankart'
        })
      })
      const data = await res.json()
      setSimulationResult(data)
      fetchEvents()
    } catch (e: any) {
      setSimulationResult({ error: e.message || 'Simulation request failed' })
    } finally {
      setSimulating(false)
    }
  }

  return (
    <AppShell>
      <Head>
        <title>Webhook Engine & Simulator | RevPilot</title>
      </Head>

      <div className="space-y-6 max-w-7xl mx-auto pb-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl border border-blue-100">
                <Webhook className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900 tracking-tight">Real-Time Webhook Engine</h1>
                <p className="text-xs text-slate-500 mt-0.5">
                  HMAC-SHA256 signature verification, deduplication guard, and autonomous recovery pipeline ingestion.
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchEvents}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh Log</span>
            </button>
          </div>
        </div>

        {/* Top Grid: Simulator & Specs */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Simulator Panel (7 cols) */}
          <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-500" />
                <h2 className="text-sm font-bold text-slate-900">Interactive Webhook Simulator</h2>
              </div>
              <span className="text-[11px] font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                Sandbox Mode Active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Gateway Provider</label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium focus:ring-1 focus:ring-blue-500"
                >
                  <option value="razorpay">Razorpay (India UPI/Card)</option>
                  <option value="stripe">Stripe (Global)</option>
                  <option value="generic">Generic Fintech ISO 20022</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Failed Amount (₹)</label>
                <input
                  type="number"
                  value={simAmount}
                  onChange={(e) => setSimAmount(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium focus:ring-1 focus:ring-blue-500"
                  placeholder="18500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">Decline Taxonomy Code</label>
                <select
                  value={simReason}
                  onChange={(e) => setSimReason(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium focus:ring-1 focus:ring-blue-500"
                >
                  <option value="BAD_REQUEST_PAYMENT_TIMED_OUT">3DS Timeout (Authentication)</option>
                  <option value="BAD_REQUEST_PAYMENT_ACCOUNT_INSUFFICIENT_BALANCE">Insufficient Funds (Customer)</option>
                  <option value="BAD_REQUEST_PAYMENT_DECLINED_BY_BANK">Issuer Decline (Bank)</option>
                  <option value="BAD_REQUEST_PAYMENT_CARD_INVALID">Invalid Card (Permanent)</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleSimulate}
              disabled={simulating}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-xs transition disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{simulating ? 'Ingesting & Triggering AI Recovery Pipeline...' : 'Fire Test Webhook Payload'}</span>
            </button>

            {/* Simulation Response Output */}
            {simulationResult && (
              <div className="mt-4 p-4 bg-slate-900 text-slate-100 rounded-xl text-xs font-mono space-y-2">
                <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-2">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Engine Ingestion Result</span>
                  </div>
                  <span className="text-[11px] text-emerald-400 font-semibold uppercase">
                    Status: {simulationResult.status || 'OK'}
                  </span>
                </div>
                <pre className="overflow-x-auto text-[11px] leading-relaxed text-emerald-300">
                  {JSON.stringify(simulationResult, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {/* Webhook Endpoint URLs (5 cols) */}
          <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              <h2 className="text-sm font-bold text-slate-900">Live Gateway Listeners</h2>
            </div>

            <div className="space-y-3">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">Razorpay Production URL</span>
                  <span className="text-[10px] text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full font-semibold">HMAC SHA256</span>
                </div>
                <code className="text-[11px] font-mono text-slate-600 block break-all">
                  POST /api/v1/webhooks/razorpay
                </code>
                <p className="text-[10px] text-slate-400">Verifies header X-Razorpay-Signature</p>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">Stripe Ingestion URL</span>
                  <span className="text-[10px] text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full font-semibold">Stripe-Signature</span>
                </div>
                <code className="text-[11px] font-mono text-slate-600 block break-all">
                  POST /api/v1/webhooks/stripe
                </code>
                <p className="text-[10px] text-slate-400">Normalizes payment_intent.payment_failed</p>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">Generic Gateway URL</span>
                  <span className="text-[10px] text-slate-600 bg-slate-200 px-2 py-0.5 rounded-full font-semibold">ISO 20022</span>
                </div>
                <code className="text-[11px] font-mono text-slate-600 block break-all">
                  POST /api/v1/webhooks/generic
                </code>
                <p className="text-[10px] text-slate-400">Accepts standardized fintech payloads</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Panel: Recent Ingestion Log */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-indigo-600" />
              <h2 className="text-sm font-bold text-slate-900">Raw Webhook Ingestion Log</h2>
            </div>
            <span className="text-xs text-slate-500 font-medium">
              Showing {events.length} received events
            </span>
          </div>

          {events.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs">
              No webhook events received yet. Click <strong>"Fire Test Webhook Payload"</strong> above to ingest a simulated live payment failure event.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-100 text-slate-400 font-semibold">
                    <th className="pb-2">Provider</th>
                    <th className="pb-2">Event Type</th>
                    <th className="pb-2">Status</th>
                    <th className="pb-2">Idempotency Key</th>
                    <th className="pb-2">Transaction ID</th>
                    <th className="pb-2">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                  {events.map((ev) => (
                    <tr key={ev.id} className="hover:bg-slate-50/80">
                      <td className="py-2.5 font-sans font-semibold capitalize text-slate-900">{ev.provider}</td>
                      <td className="py-2.5 text-blue-600">{ev.event_type}</td>
                      <td className="py-2.5">
                        <span className={`px-2 py-0.5 rounded-full font-sans font-semibold text-[10px] ${
                          ev.status === 'processed' ? 'bg-emerald-50 text-emerald-700' :
                          ev.status === 'duplicate' ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-600'
                        }`}>
                          {ev.status}
                        </span>
                      </td>
                      <td className="py-2.5 text-slate-500 truncate max-w-xs">{ev.idempotency_key}</td>
                      <td className="py-2.5 font-bold text-slate-800">{ev.transaction_id || 'N/A'}</td>
                      <td className="py-2.5 text-slate-400">{new Date(ev.received_at).toLocaleTimeString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  )
}

