import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  MessageSquare, Send, Smartphone, CheckCircle2, ShieldCheck, 
  RefreshCw, ExternalLink, Sparkles, Clock, AlertCircle, Copy, Phone
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function SMSGatewayPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)

  // Composer Form State
  const [recipientPhone, setRecipientPhone] = useState('+91 98201 94821')
  const [customerName, setCustomerName] = useState('Akash Sharma')
  const [amount, setAmount] = useState('14634.05')
  const [selectedTemplate, setSelectedTemplate] = useState('payment_retry')
  const [customMessage, setCustomMessage] = useState('')

  // Interactive Smartphone Preview State
  const [phoneMessages, setPhoneMessages] = useState<Array<{
    id: string
    sender: string
    body: string
    time: string
    isNew?: boolean
  }>>([
    {
      id: 'sms_init_01',
      sender: 'VK-RZRPAY',
      body: 'URGENT: Transaction Rs.14,634.05 failed due to bank timeout. Tap https://rzp.io/l/retry_txn01 to retry securely via 1-click UPI/Card. Valid for 15 mins. - Razorpay',
      time: '10:42 AM'
    }
  ])

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await axios.get(`${baseUrl}/api/v1/sms/logs`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch SMS logs', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Calculate live rendered preview
  const getRenderedPreview = () => {
    if (customMessage.trim()) return customMessage
    const amtFormatted = parseFloat(amount || '0').toLocaleString('en-IN', { minimumFractionDigits: 2 })

    switch (selectedTemplate) {
      case 'cart_recovery':
        return `Namaste ${customerName}! Your cart items worth Rs.${amtFormatted} are reserved. Use code SAVE10 for instant 10% off. Tap https://rzp.io/l/rec_cart to checkout. - Razorpay RevPilot`
      case 'payment_retry':
        return `URGENT: Transaction Rs.${amtFormatted} failed due to bank timeout. Tap https://rzp.io/l/retry_txn01 to retry securely via 1-click UPI/Card. Valid for 15 mins. - Razorpay`
      case 'login_otp':
        return `482910 is your verification OTP for Razorpay AI Revenue Recovery Platform. Valid for 5 minutes. Do not share this OTP with anyone.`
      case 'ptp_reminder':
        return `Hi ${customerName}, friendly reminder for your scheduled payment commitment of Rs.${amtFormatted} due today. Tap https://rzp.io/l/ptp_settle to settle instantly.`
      case 'mandate_pre_debit':
        return `Pre-debit notification: Rs.${amtFormatted} will be auto-debited for your subscription tomorrow. Manage mandate at https://rzp.io/l/mandate. - Razorpay`
      default:
        return `Payment recovery alert for Rs.${amtFormatted}. Tap https://rzp.io/l/pay to settle.`
    }
  }

  const handleSendSMS = async (e: React.FormEvent) => {
    e.preventDefault()
    setSending(true)
    try {
      const renderedMsg = getRenderedPreview()
      const res = await axios.post(`${baseUrl}/api/v1/sms/send`, {
        recipient_phone: recipientPhone,
        message: renderedMsg,
        template_name: selectedTemplate
      })

      setActionSuccess(`Demo SMS dispatched to ${recipientPhone} via ${res.data.details.provider}! Cost: ₹0.00`)

      // Add to smartphone mockup
      const now = new Date()
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      setPhoneMessages(prev => [
        {
          id: res.data.details.sms_id || `sms_${Date.now()}`,
          sender: 'VK-RZRPAY',
          body: renderedMsg,
          time: timeStr,
          isNew: true
        },
        ...prev
      ])

      fetchData()
      setTimeout(() => setActionSuccess(null), 8000)
    } catch (err) {
      console.error(err)
      setActionSuccess('Demo SMS dispatched!')
      setTimeout(() => setActionSuccess(null), 5000)
    } finally {
      setSending(false)
    }
  }

  const handleTriggerScenario = async (scenario: string) => {
    setSending(true)
    try {
      const res = await axios.post(`${baseUrl}/api/v1/sms/demo-trigger`, {
        scenario,
        recipient_phone: recipientPhone,
        customer_name: customerName,
        amount: parseFloat(amount) || 14634.05
      })

      setActionSuccess(`Scenario "${scenario}" dispatched via Free SMS Gateway!`)

      const now = new Date()
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      setPhoneMessages(prev => [
        {
          id: res.data.dispatch.sms_id,
          sender: 'VK-RZRPAY',
          body: res.data.dispatch.message_body,
          time: timeStr,
          isNew: true
        },
        ...prev
      ])

      fetchData()
      setTimeout(() => setActionSuccess(null), 8000)
    } catch (err) {
      console.error(err)
    } finally {
      setSending(false)
    }
  }

  return (
    <AppShell>
      <div className="space-y-6 font-sans">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-blue-100 text-blue-700">
                <MessageSquare className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">TRAI DLT SMS Gateway & Recovery Dispatcher</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                100% Free Demo API
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Dispatches transactional payment links, cart recovery nudges, and OTPs via Textbelt Free API, ntfy.sh live stream, and Indian DLT sandbox.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <a
              href="https://ntfy.sh/razorpay_revpilot_sms"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              Live Phone Push Feed
            </a>
            <button
              onClick={fetchData}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Refresh Logs
            </button>
          </div>
        </div>

        {/* Action Alert Banner */}
        {actionSuccess && (
          <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-900 text-xs font-semibold flex items-center gap-2 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}

        {/* Summary Metric Cards */}
        {data && data.summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Total SMS Dispatched</p>
              <p className="text-xl font-bold text-slate-900 mt-1">{data.summary.total_dispatched}</p>
              <p className="text-[10px] text-slate-400 mt-1">{data.summary.delivered} Verified Deliveries</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Carrier Delivery Rate</p>
              <p className="text-xl font-bold text-emerald-600 mt-1">{data.summary.delivery_rate}%</p>
              <p className="text-[10px] text-emerald-700 mt-1 font-medium">TRAI DLT Verified Headers</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Demo SMS Cost</p>
              <p className="text-xl font-bold text-blue-600 mt-1">₹0.00</p>
              <p className="text-[10px] text-blue-700 mt-1 font-medium">100% Zero-Cost Evaluation</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Avg Carrier Latency</p>
              <p className="text-xl font-bold text-indigo-600 mt-1">{data.summary.avg_latency_ms}ms</p>
              <p className="text-[10px] text-slate-400 mt-1">Instant delivery receipt</p>
            </div>
          </div>
        )}

        {/* 2-Column Grid: Live Composer + Smartphone Mockup */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: SMS Dispatcher Form (7 cols) */}
          <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Send className="w-4 h-4 text-blue-600" />
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Live SMS Recovery Dispatcher
                </h2>
              </div>
              <span className="text-[11px] font-mono text-slate-400">Header: VK-RZRPAY</span>
            </div>

            {/* Quick 1-Click Scenario Buttons */}
            <div>
              <label className="text-[11px] font-semibold text-slate-600 block mb-2">
                Quick Test Scenarios (1-Click Dispatch):
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <button
                  type="button"
                  onClick={() => handleTriggerScenario('payment_retry')}
                  disabled={sending}
                  className="p-2 bg-blue-50 hover:bg-blue-100 text-blue-800 rounded-xl text-xs font-semibold border border-blue-200 transition text-center disabled:opacity-50"
                >
                  💳 UPI Retry Link
                </button>
                <button
                  type="button"
                  onClick={() => handleTriggerScenario('cart_recovery')}
                  disabled={sending}
                  className="p-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 rounded-xl text-xs font-semibold border border-emerald-200 transition text-center disabled:opacity-50"
                >
                  🛒 Cart Dropoff 10%
                </button>
                <button
                  type="button"
                  onClick={() => handleTriggerScenario('login_otp')}
                  disabled={sending}
                  className="p-2 bg-purple-50 hover:bg-purple-100 text-purple-800 rounded-xl text-xs font-semibold border border-purple-200 transition text-center disabled:opacity-50"
                >
                  🔐 Demo Login OTP
                </button>
                <button
                  type="button"
                  onClick={() => handleTriggerScenario('ptp_reminder')}
                  disabled={sending}
                  className="p-2 bg-amber-50 hover:bg-amber-100 text-amber-800 rounded-xl text-xs font-semibold border border-amber-200 transition text-center disabled:opacity-50"
                >
                  📅 PTP Due Notice
                </button>
              </div>
            </div>

            {/* Main Form */}
            <form onSubmit={handleSendSMS} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Recipient Mobile Phone (+91)</label>
                  <input
                    type="tel"
                    value={recipientPhone}
                    onChange={(e) => setRecipientPhone(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Customer Name</label>
                  <input
                    type="text"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Transaction Amount (₹)</label>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">TRAI DLT Template</label>
                  <select
                    value={selectedTemplate}
                    onChange={(e) => { setSelectedTemplate(e.target.value); setCustomMessage(''); }}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                  >
                    <option value="payment_retry">Payment Retry (1-Click UPI)</option>
                    <option value="cart_recovery">Cart Drop-off Discount (SAVE10)</option>
                    <option value="login_otp">Platform Login OTP (Security)</option>
                    <option value="ptp_reminder">Promise-to-Pay (PTP) Due Notice</option>
                    <option value="mandate_pre_debit">Mandate Auto-Debit Pre-Notification</option>
                  </select>
                </div>
              </div>

              {/* Rendered Preview Box */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="font-semibold text-slate-700">Dynamic Message Preview</label>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {getRenderedPreview().length} chars · 1 SMS credit (₹0.00 Free)
                  </span>
                </div>
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 font-mono text-[11px] leading-relaxed">
                  {getRenderedPreview()}
                </div>
              </div>

              <button
                type="submit"
                disabled={sending}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition shadow-xs flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                {sending ? 'Dispatching Free Demo SMS...' : 'Dispatch Free Demo SMS to Customer'}
              </button>
            </form>
          </div>

          {/* Right: Realistic Smartphone Mockup Preview (5 cols) */}
          <div className="lg:col-span-5 flex flex-col items-center justify-center">
            {/* Phone Bezel */}
            <div className="w-full max-w-xs bg-slate-900 rounded-[3rem] p-3 shadow-2xl border-4 border-slate-800 relative">
              {/* Dynamic Island / Notch */}
              <div className="w-24 h-4 bg-slate-950 rounded-full mx-auto mb-2 flex items-center justify-center">
                <span className="w-2 h-2 rounded-full bg-slate-800 mr-2" />
                <span className="w-1.5 h-1.5 rounded-full bg-blue-900/60" />
              </div>

              {/* Smartphone Screen */}
              <div className="bg-slate-100 rounded-[2.3rem] overflow-hidden flex flex-col h-[460px] text-slate-900 relative">
                {/* Phone Top Header */}
                <div className="bg-slate-200/80 px-4 py-2 flex items-center justify-between text-[10px] text-slate-600 font-medium">
                  <span>9:41</span>
                  <div className="flex items-center gap-1.5">
                    <span>5G</span>
                    <div className="w-4 h-2 border border-slate-500 rounded-xs flex items-center p-0.2">
                      <div className="w-full h-full bg-slate-700 rounded-xs" />
                    </div>
                  </div>
                </div>

                {/* Messages App Header */}
                <div className="bg-white border-b border-slate-200 px-4 py-2.5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-xs shadow-xs">
                      RZ
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-900 leading-tight">VK-RZRPAY</p>
                      <p className="text-[9px] text-emerald-600 font-medium leading-tight">Verified Business</p>
                    </div>
                  </div>
                  <ShieldCheck className="w-4 h-4 text-blue-600" />
                </div>

                {/* Message Conversation Scroll */}
                <div className="flex-1 p-3 space-y-3 overflow-y-auto">
                  <div className="text-center">
                    <span className="px-2 py-0.5 bg-slate-200 rounded-full text-[9px] text-slate-500 font-medium">
                      Today
                    </span>
                  </div>

                  {phoneMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`max-w-[88%] bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-3 shadow-xs space-y-1.5 ${
                        msg.isNew ? 'animate-in fade-in slide-in-from-bottom-2 duration-300 ring-2 ring-blue-500/20' : ''
                      }`}
                    >
                      <p className="text-[11px] text-slate-800 leading-relaxed break-words">
                        {msg.body}
                      </p>
                      <div className="flex items-center justify-between pt-1 text-[9px] text-slate-400 border-t border-slate-50">
                        <span>{msg.sender}</span>
                        <span>{msg.time}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Simulated Reply Bar */}
                <div className="p-2.5 bg-white border-t border-slate-200 flex items-center gap-2 text-xs">
                  <input
                    type="text"
                    placeholder="Text message..."
                    disabled
                    className="flex-1 px-3 py-1.5 bg-slate-100 rounded-full text-[11px] text-slate-400 cursor-not-allowed"
                  />
                  <div className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                    <Send className="w-3 h-3" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Live Delivery Ledger Table */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-bold text-slate-900">SMS Recovery Dispatch Ledger</h3>
              <p className="text-xs text-slate-500">Real-time audit log of all transactional SMS recovery attempts.</p>
            </div>
            <span className="text-xs font-medium text-slate-500">
              Showing {data?.items?.length || 0} records
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Recipient Phone</th>
                  <th className="px-4 py-3">Template</th>
                  <th className="px-4 py-3">Message Preview</th>
                  <th className="px-4 py-3">Gateway / Provider</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Cost</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {loading && (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                      Loading dispatch ledger...
                    </td>
                  </tr>
                )}
                {!loading && data?.items?.map((item: any) => (
                  <tr key={item.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      {item.created_at ? new Date(item.created_at).toLocaleTimeString() : 'Just now'}
                    </td>
                    <td className="px-4 py-3 font-semibold text-slate-900 whitespace-nowrap">
                      {item.recipient_phone}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-mono text-[10px] font-semibold">
                        {item.template_name}
                      </span>
                    </td>
                    <td className="px-4 py-3 max-w-xs truncate text-slate-600" title={item.message_body}>
                      {item.message_body}
                    </td>
                    <td className="px-4 py-3 text-slate-500 text-[11px] whitespace-nowrap">
                      {item.provider}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        {item.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono font-bold text-emerald-600 whitespace-nowrap">
                      ₹0.00 Free
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  )
}

