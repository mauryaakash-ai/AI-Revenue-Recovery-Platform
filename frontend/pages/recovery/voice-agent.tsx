import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  PhoneCall, Mic, Volume2, Play, Pause, CheckCircle2, 
  Sparkles, RefreshCw, MessageSquare, Clock, UserCheck, 
  ArrowRight, Shield, AlertCircle, Headphones, VolumeX 
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function VoiceAgentPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [simulating, setSimulating] = useState(false)
  const [activeCallSim, setActiveCallSim] = useState<any>(null)
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)
  const [isSpeaking, setIsSpeaking] = useState(false)

  // Simulation Form State
  const [simName, setSimName] = useState('Akash Sharma')
  const [simPhone, setSimPhone] = useState('+91 9820194821')
  const [simAmount, setSimAmount] = useState('14500')
  const [simObjection, setSimObjection] = useState('salary_pending')

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await axios.get(`${baseUrl}/api/v1/voice/calls`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch voice calls', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Web Speech API (Free in-browser Voice Synthesizer)
  const speakDialogue = (text: string) => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      
      const cleanText = text
        .replace(/AI:/g, 'Assistant says:')
        .replace(/Customer:/g, 'Customer says:')
      
      const utterance = new SpeechSynthesisUtterance(cleanText)
      utterance.rate = 0.95
      utterance.pitch = 1.05

      // Select Hindi or Indian English voice if available in browser
      const voices = window.speechSynthesis.getVoices()
      const indianVoice = voices.find(v => v.lang.includes('hi') || v.lang.includes('IN') || v.name.includes('India'))
      if (indianVoice) {
        utterance.voice = indianVoice
      }

      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => setIsSpeaking(false)

      window.speechSynthesis.speak(utterance)
    }
  }

  const stopSpeaking = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    }
  }

  const handleLaunchCallSim = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSimulating(true)
      const res = await axios.post(`${baseUrl}/api/v1/voice/simulate-call`, {
        customer_name: simName,
        customer_phone: simPhone,
        amount: parseFloat(simAmount) || 14500,
        customer_objection: simObjection
      })
      setActiveCallSim(res.data)
      setActionSuccess(`Hinglish AI Voice Call completed! PTP date extracted: ${new Date(res.data.captured_ptp_date).toLocaleDateString()}`)
      
      // Automatically speak the Hinglish dialogue out loud via browser audio!
      speakDialogue(res.data.transcript_hinglish)

      fetchData()
      setTimeout(() => setActionSuccess(null), 8000)
    } catch (err) {
      console.error(err)
    } finally {
      setSimulating(false)
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
              <div className="p-2 rounded-lg bg-pink-100 text-pink-700">
                <PhoneCall className="w-5 h-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Hinglish AI Voice Recovery Agent</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                Free Live Audio Engine Active
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Natural Hindi-English code-switched voice calls with real in-browser speech audio playback and PTP extraction.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-xs self-start"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Call Records
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
              <p className="text-[11px] font-medium text-slate-500">Total Outbound Voice Calls</p>
              <p className="text-xl font-bold text-slate-900 mt-1">{data.summary.total_calls_initiated}</p>
              <p className="text-[10px] text-slate-400 mt-1">{data.summary.completed_calls} Completed Engagements</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">PTP Commitments Captured</p>
              <p className="text-xl font-bold text-pink-600 mt-1">{formatINR(data.summary.ptp_captured_value)}</p>
              <p className="text-[10px] text-pink-700 mt-1 font-medium">{data.summary.ptp_captured_count} Customer PTPs Synced</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Call Completion Rate</p>
              <p className="text-xl font-bold text-blue-600 mt-1">{data.summary.call_completion_rate}%</p>
              <p className="text-[10px] text-blue-700 mt-1 font-medium">+38% vs English-only IVRs</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <p className="text-[11px] font-medium text-slate-500">Top Customer Objection</p>
              <p className="text-xl font-bold text-amber-600 mt-1">Salary Pending</p>
              <p className="text-[10px] text-slate-400 mt-1">Auto-scheduled on salary date</p>
            </div>
          </div>
        )}

        {/* Interactive Call Simulator Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Simulator Form */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
              <Headphones className="w-4 h-4 text-pink-600" />
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Live Hinglish Call Simulator</h2>
            </div>

            <form onSubmit={handleLaunchCallSim} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Customer Name</label>
                <input
                  type="text"
                  value={simName}
                  onChange={(e) => setSimName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-pink-500"
                  required
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Customer Phone (+91)</label>
                <input
                  type="text"
                  value={simPhone}
                  onChange={(e) => setSimPhone(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-pink-500"
                  required
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Transaction Amount (₹)</label>
                <input
                  type="number"
                  value={simAmount}
                  onChange={(e) => setSimAmount(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-pink-500"
                  required
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Simulated Customer Objection</label>
                <select
                  value={simObjection}
                  onChange={(e) => setSimObjection(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-pink-500"
                >
                  <option value="salary_pending">"Salary pending hai, Friday pay karunga"</option>
                  <option value="retry_link_needed">"Card OTP fail hua, WhatsApp UPI link bhejo"</option>
                  <option value="will_pay_online">"Online laptop se shaam tak clear karunga"</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={simulating}
                className="w-full bg-pink-600 hover:bg-pink-700 text-white font-semibold py-2.5 rounded-lg transition flex items-center justify-center gap-2 shadow-xs disabled:opacity-50"
              >
                <PhoneCall className="w-4 h-4" />
                {simulating ? 'Dialing Hinglish AI Voice Agent...' : 'Launch Outbound Voice Call (Hear Audio)'}
              </button>
            </form>
          </div>

          {/* Active Call Live Transcript / Audio Visualizer */}
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${isSpeaking ? 'bg-pink-500 animate-ping' : 'bg-emerald-500'}`} />
                  <span className="text-xs font-bold text-slate-900">
                    {isSpeaking ? 'Speaking Hinglish Voice Audio...' : 'Live Call Intelligence & Speech Parser'}
                  </span>
                </div>

                {activeCallSim && (
                  <div className="flex items-center gap-2">
                    {isSpeaking ? (
                      <button
                        onClick={stopSpeaking}
                        className="px-2.5 py-1 text-[11px] font-semibold bg-red-100 text-red-700 hover:bg-red-200 rounded-md transition flex items-center gap-1"
                      >
                        <VolumeX className="w-3.5 h-3.5" /> Stop Audio
                      </button>
                    ) : (
                      <button
                        onClick={() => speakDialogue(activeCallSim.transcript_hinglish)}
                        className="px-2.5 py-1 text-[11px] font-semibold bg-pink-50 text-pink-700 hover:bg-pink-100 rounded-md transition flex items-center gap-1"
                      >
                        <Volume2 className="w-3.5 h-3.5" /> Replay Audio Voice
                      </button>
                    )}
                  </div>
                )}
              </div>

              {activeCallSim ? (
                <div className="mt-4 space-y-4 text-xs">
                  {/* Audio Waveform Animation Indicator */}
                  {isSpeaking && (
                    <div className="p-3 bg-pink-50/80 border border-pink-200 rounded-xl flex items-center justify-between">
                      <div className="flex items-center gap-2 text-pink-800 font-semibold text-xs">
                        <Volume2 className="w-4 h-4 animate-bounce" />
                        <span>AI Voice is speaking in real-time through your speakers...</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="w-1 h-4 bg-pink-600 animate-pulse rounded-full" />
                        <span className="w-1 h-6 bg-pink-600 animate-bounce rounded-full" />
                        <span className="w-1 h-3 bg-pink-600 animate-pulse rounded-full" />
                        <span className="w-1 h-7 bg-pink-600 animate-bounce rounded-full" />
                        <span className="w-1 h-4 bg-pink-600 animate-pulse rounded-full" />
                      </div>
                    </div>
                  )}

                  {/* Dialogue View */}
                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3 font-sans">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Bilingual Code-Switched Transcript (Hinglish):</p>
                    <div className="space-y-2 whitespace-pre-line text-slate-800 leading-relaxed font-medium">
                      {activeCallSim.transcript_hinglish}
                    </div>
                  </div>

                  {/* Extracted Structured Intelligence */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-emerald-50 border border-emerald-100 rounded-lg text-emerald-900">
                      <p className="text-[10px] font-bold uppercase text-emerald-700">Detected Verbal Intent</p>
                      <p className="font-semibold mt-0.5">{activeCallSim.detected_intent}</p>
                    </div>
                    <div className="p-3 bg-purple-50 border border-purple-100 rounded-lg text-purple-900">
                      <p className="text-[10px] font-bold uppercase text-purple-700">Captured PTP Commitment Date</p>
                      <p className="font-semibold mt-0.5">{new Date(activeCallSim.captured_ptp_date).toLocaleDateString()}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="my-12 text-center text-slate-400 text-xs space-y-2">
                  <Headphones className="w-8 h-8 mx-auto text-slate-300" />
                  <p>Click "Launch Outbound Voice Call" on the left to hear the AI speak live Hinglish audio.</p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Free Browser Web Speech Audio Synthesizer</span>
              <span className="text-emerald-700 font-semibold">Auto-Synced with Promise-to-Pay (PTP) Ledger</span>
            </div>
          </div>
        </div>

        {/* Historical Call Logs Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Outbound Voice Recovery Audit History</h2>
            <span className="text-xs text-slate-400">Click any row to hear audio dialogue</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="px-4 py-3">Customer & Phone</th>
                  <th className="px-4 py-3">Call SID</th>
                  <th className="px-4 py-3">Duration</th>
                  <th className="px-4 py-3">Objection Category</th>
                  <th className="px-4 py-3">Extracted PTP Commitment</th>
                  <th className="px-4 py-3 text-right">Voice Audio Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                      Loading voice call archives...
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item: any) => (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-4 py-3">
                        <p className="font-bold text-slate-900">{item.customer_name}</p>
                        <p className="text-[10px] text-slate-400">{item.customer_phone}</p>
                      </td>
                      <td className="px-4 py-3 font-mono text-[10px] text-slate-500">
                        {item.call_sid}
                      </td>
                      <td className="px-4 py-3 font-semibold text-slate-700">
                        {item.duration_seconds}s
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
                          {item.detected_objection.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {item.captured_ptp_date ? (
                          <div>
                            <p className="font-bold text-emerald-700">₹{item.captured_ptp_amount?.toLocaleString('en-IN')}</p>
                            <p className="text-[10px] text-slate-500">Promised for {new Date(item.captured_ptp_date).toLocaleDateString()}</p>
                          </div>
                        ) : (
                          <span className="text-slate-400 text-[10px]">No PTP committed</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => speakDialogue(item.transcript_hinglish)}
                          className="px-2.5 py-1 text-[11px] font-semibold bg-pink-50 hover:bg-pink-100 text-pink-700 rounded-md transition inline-flex items-center gap-1 shadow-2xs"
                        >
                          <Volume2 className="w-3 h-3" />
                          Listen Call
                        </button>
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
