import React, { useState } from 'react'
import axios from 'axios'
import { Bot, Send, X, Sparkles, TrendingDown, ArrowUpRight, CheckCircle2, ChevronRight, Loader2, ShieldCheck, FileText, HelpCircle } from 'lucide-react'

interface CopilotDrawerProps {
  isOpen: boolean
  onClose: () => void
  merchantId?: string
}

export const CopilotDrawer: React.FC<CopilotDrawerProps> = ({
  isOpen,
  onClose,
  merchantId = 'merchant_urbankart'
}) => {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<Array<{ sender: 'user' | 'assistant'; content: any }>>([
    {
      sender: 'assistant',
      content: {
        headline: 'Welcome to Revenue AI Copilot',
        drivers: [
          'Ask any questions about payment failure root causes, bank degradation, recovery evidence, or regulatory policies.'
        ],
        suggested_followups: [
          "Why did recovery rate fall yesterday?",
          "Which issuer bank caused the greatest loss in the last 6 hours?",
          "Show evidence for recommending WhatsApp UPI links",
          "How much revenue can we recover this week?"
        ]
      }
    }
  ])

  const suggestedQuestions = [
    "Why did recovery rate fall yesterday?",
    "Which issuer bank caused the greatest loss in the last 6 hours?",
    "Show evidence for recommending WhatsApp UPI links",
    "How much revenue can we recover this week?",
    "Which recovery policy performed best for high-LTV customers?"
  ]

  const handleAsk = async (text: string) => {
    if (!text.trim() || loading) return

    const userMessage = text.trim()
    setQuery('')
    setHistory(prev => [...prev, { sender: 'user', content: userMessage }])
    setLoading(true)

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/copilot/ask`, {
        query: userMessage,
        user_role: "Revenue Operations"
      })
      setHistory(prev => [...prev, { sender: 'assistant', content: res.data }])
    } catch (err: any) {
      setHistory(prev => [
        ...prev,
        {
          sender: 'assistant',
          content: {
            headline: 'Unable to process query at this time.',
            drivers: ['Please ensure backend service is running on http://localhost:8000']
          }
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/30 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-lg bg-white h-full shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Revenue AI Copilot</h2>
              <p className="text-xs text-slate-500">RAG Grounded · Multi-Source Evidence Intelligence</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {history.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.sender === 'user' ? (
                <div className="bg-blue-600 text-white rounded-lg px-4 py-2.5 max-w-[85%] font-medium">
                  {msg.content}
                </div>
              ) : (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3 max-w-[98%] text-slate-800 shadow-xs">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-bold text-slate-900 text-sm leading-snug">{msg.content.headline}</p>
                    {msg.content.uncertainty_assessment?.confidence_score && (
                      <span className="shrink-0 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        {Math.round(msg.content.uncertainty_assessment.confidence_score * 100)}% Confidence
                      </span>
                    )}
                  </div>

                  {/* Metrics Row */}
                  {msg.content.metrics && msg.content.metrics.length > 0 && (
                    <div className="grid grid-cols-3 gap-2 pt-1 pb-1">
                      {msg.content.metrics.map((m: any, mIdx: number) => (
                        <div key={mIdx} className="bg-white border border-slate-200 rounded p-2 text-center">
                          <p className="text-[10px] text-slate-500 truncate">{m.label}</p>
                          <p className="text-xs font-bold text-slate-900 mt-0.5">{m.value}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Structured Diagnostics Card (If returned) */}
                  {msg.content.structured_diagnostic && (
                    <div className="bg-white border border-blue-100 rounded-lg p-3 space-y-2 text-[11px]">
                      <div>
                        <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">Root Cause: </span>
                        <span className="text-slate-800">{msg.content.structured_diagnostic.likely_root_cause}</span>
                      </div>
                      <div>
                        <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">Recommended Action: </span>
                        <span className="text-blue-700 font-semibold">{msg.content.structured_diagnostic.recommended_action}</span>
                      </div>
                      <div className="pt-1 border-t border-slate-100 flex items-center justify-between text-slate-500 text-[10px]">
                        <span>Risk: {msg.content.structured_diagnostic.risks}</span>
                        <span className="font-semibold text-emerald-700">Uplift: {msg.content.structured_diagnostic.expected_uplift}</span>
                      </div>
                    </div>
                  )}

                  {/* Drivers & Evidence */}
                  {msg.content.drivers && (
                    <div className="space-y-1 pt-1">
                      {msg.content.drivers.map((d: string, dIdx: number) => (
                        <p key={dIdx} className="text-slate-700 leading-relaxed">{d}</p>
                      ))}
                    </div>
                  )}

                  {/* Evidence Citations */}
                  {msg.content.citations && msg.content.citations.length > 0 && (
                    <div className="pt-2 border-t border-slate-200/80 space-y-1">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                        <FileText className="w-3 h-3" /> Grounded Evidence Citations:
                      </p>
                      <div className="flex flex-wrap gap-1.5 pt-0.5">
                        {msg.content.citations.map((c: any, cIdx: number) => (
                          <span key={cIdx} className="px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-800 text-[10px] font-medium">
                            {c.title}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Button */}
                  {msg.content.recommended_action && (
                    <div className="pt-2">
                      <button 
                        onClick={() => {
                          alert(`Strategy Approved: ${msg.content.recommended_action.action_button}`)
                        }}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-3 rounded-lg text-xs transition flex items-center justify-center gap-1.5 shadow-xs"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        {msg.content.recommended_action.action_button}
                      </button>
                    </div>
                  )}

                  {/* Followups */}
                  {msg.content.suggested_followups && (
                    <div className="pt-2 border-t border-slate-200 space-y-1">
                      <p className="text-[10px] uppercase font-semibold text-slate-400">Suggested queries:</p>
                      {msg.content.suggested_followups.map((s: string, sIdx: number) => (
                        <button
                          key={sIdx}
                          onClick={() => handleAsk(s)}
                          className="block text-left w-full text-blue-600 hover:text-blue-800 text-[11px] py-1 hover:underline truncate"
                        >
                          • {s}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-slate-500 text-xs p-3">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              <span>Retrieving telemetry & validating grounding citations...</span>
            </div>
          )}
        </div>

        {/* Suggested Prompts Pill Carousel */}
        <div className="px-4 py-2 border-t border-slate-100 bg-slate-50/70 overflow-x-auto flex gap-1.5 no-scrollbar">
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(q)}
              className="text-[11px] whitespace-nowrap px-2.5 py-1 rounded-full bg-white border border-slate-200 text-slate-700 hover:border-blue-400 hover:text-blue-600 transition shrink-0"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3 border-t border-slate-200 bg-white">
          <form 
            onSubmit={(e) => {
              e.preventDefault()
              handleAsk(query)
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about revenue drops, bank outages, evidence..."
              className="flex-1 px-3.5 py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white p-2 rounded-lg transition"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
