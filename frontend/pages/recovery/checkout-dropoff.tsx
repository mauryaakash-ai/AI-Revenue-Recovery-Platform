import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  ShoppingCart, Send, ArrowUpRight, CheckCircle2, AlertCircle, 
  Sparkles, RefreshCw, Filter, MessageSquare, Mail, Smartphone, 
  DollarSign, Shield, Clock, ExternalLink, TrendingUp, Layers
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function CheckoutDropoffPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [selectedCause, setSelectedCause] = useState<string>('all')
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'all' | 'price_hesitation' | 'form_friction' | 'otp_delay' | 'session_expiry'>('all')

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const causeParam = activeTab !== 'all' ? `?cause=${activeTab}` : ''
      const res = await axios.get(`${baseUrl}/api/v1/checkout-dropoff/list${causeParam}`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch dropoffs', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const handleNudge = async (id: string, channel: string, discount?: string) => {
    try {
      const res = await axios.post(`${baseUrl}/api/v1/checkout-dropoff/${id}/nudge`, {
        channel,
        discount_code: discount || (channel === 'whatsapp' ? 'RECOVERY10' : undefined)
      })
      setActionSuccess(`Resume nudge sent via ${channel.toUpperCase()}! Link: ${res.data.resume_url}`)
      fetchData()
      setTimeout(() => setActionSuccess(null), 5000)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSimulateConversion = async (id: string) => {
    try {
      const res = await axios.post(`${baseUrl}/api/v1/checkout-dropoff/${id}/simulate-conversion`)
      setActionSuccess(`Cart resumed & converted! Recovered ₹${res.data.recovered_amount.toLocaleString('en-IN')}`)
      fetchData()
      setTimeout(() => setActionSuccess(null), 5000)
    } catch (err) {
      console.error(err)
    }
  }

  const formatINR = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`
    return `₹${val.toLocaleString('en-IN')}`
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-blue-100 text-blue-700">
                <ShoppingCart className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Checkout Drop-off Recovery</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                Real-Time Abandonment Interceptor
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Catches checkout friction before payment submission and dispatches 1-click cart-restoring resume links.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs self-start"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Stream
          </button>
        </div>

        {/* Action Alert Banner */}
        {actionSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-medium flex items-center gap-2 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}

        {/* Summary Metric Cards */}
        {data && data.summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Cart Value at Risk</p>
              <p className="text-xl font-bold text-slate-900 mt-1">{formatINR(data.summary.total_cart_value_at_risk)}</p>
              <p className="text-[10px] text-slate-400 mt-1">{data.summary.total_abandoned_sessions} Abandoned Sessions</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Recovered Revenue</p>
              <p className="text-xl font-bold text-emerald-600 mt-1">{formatINR(data.summary.recovered_revenue)}</p>
              <p className="text-[10px] text-emerald-700 mt-1 font-medium">↑ {data.summary.converted_sessions} Sessions Restored</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Resume Conversion Rate</p>
              <p className="text-xl font-bold text-blue-600 mt-1">{data.summary.conversion_rate}%</p>
              <p className="text-[10px] text-blue-700 mt-1 font-medium">+18.4% vs Generic Retargeting</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Top Drop-off Cause</p>
              <p className="text-xl font-bold text-amber-600 mt-1">Price Hesitation</p>
              <p className="text-[10px] text-slate-400 mt-1">42% routed to 10% instant voucher</p>
            </div>
          </div>
        )}

        {/* Cause Segmentation Filter Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto no-scrollbar">
          {[
            { id: 'all', label: 'All Abandonments' },
            { id: 'price_hesitation', label: 'Price Hesitation (Voucher Nudge)' },
            { id: 'form_friction', label: 'Form Friction (Fast Checkout Link)' },
            { id: 'otp_delay', label: 'OTP Delay (Instant UPI Intent)' },
            { id: 'session_expiry', label: 'Session Timeout (Cart Restore)' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white font-semibold shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Live Abandonment Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Abandoned Cart Stream & 1-Click Nudge Hub</h2>
            <span className="text-xs text-slate-400">Showing recent active drop-off events</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="px-4 py-3">Customer / Session</th>
                  <th className="px-4 py-3">Cart Value</th>
                  <th className="px-4 py-3">Items Summary</th>
                  <th className="px-4 py-3">Drop-off Stage</th>
                  <th className="px-4 py-3">AI Cause Attribution</th>
                  <th className="px-4 py-3">Nudge Status</th>
                  <th className="px-4 py-3 text-right">Recovery Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                      Loading real-time checkout drop-off telemetry...
                    </td>
                  </tr>
                ) : data?.items?.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                      No active drop-offs found for this filter.
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item: any) => (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-4 py-3">
                        <p className="font-bold text-slate-900">{item.customer_name}</p>
                        <p className="text-[10px] text-slate-400">{item.customer_phone || item.customer_email}</p>
                        <span className="font-mono text-[9px] text-slate-400">{item.session_id}</span>
                      </td>
                      <td className="px-4 py-3 font-bold text-slate-900">
                        ₹{item.cart_value.toLocaleString('en-IN')}
                      </td>
                      <td className="px-4 py-3 max-w-xs truncate text-slate-600" title={item.items_summary}>
                        {item.items_summary}
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700 uppercase">
                          {item.dropoff_stage.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            item.cause === 'price_hesitation' ? 'bg-amber-100 text-amber-800' :
                            item.cause === 'form_friction' ? 'bg-purple-100 text-purple-800' :
                            item.cause === 'otp_delay' ? 'bg-blue-100 text-blue-800' :
                            'bg-slate-100 text-slate-700'
                          }`}>
                            {item.cause.replace('_', ' ')}
                          </span>
                          <span className="text-[10px] text-slate-400 font-semibold">{item.cause_confidence}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.nudge_status === 'converted' ? 'bg-emerald-100 text-emerald-800' :
                          item.nudge_status === 'sent' ? 'bg-blue-100 text-blue-800' :
                          'bg-slate-100 text-slate-600'
                        }`}>
                          {item.nudge_status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {item.nudge_status === 'converted' ? (
                          <span className="text-emerald-600 font-semibold text-[11px] flex items-center justify-end gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Recovered
                          </span>
                        ) : (
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleNudge(item.id, 'whatsapp', item.cause === 'price_hesitation' ? 'SAVE10' : undefined)}
                              className="px-2.5 py-1 text-[11px] font-semibold bg-emerald-600 hover:bg-emerald-700 text-white rounded transition shadow-2xs flex items-center gap-1"
                              title="Send 1-Click WhatsApp Resume Link"
                            >
                              <MessageSquare className="w-3 h-3" />
                              WhatsApp
                            </button>
                            <button
                              onClick={() => handleSimulateConversion(item.id)}
                              className="px-2 py-1 text-[11px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition"
                              title="Simulate customer completing checkout"
                            >
                              Simulate Checkout
                            </button>
                          </div>
                        )}
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

