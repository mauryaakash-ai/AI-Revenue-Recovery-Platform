import React, { useRef, useEffect, useState } from 'react'

interface Message {
  id: string
  role: 'user' | 'agent'
  content: string
  timestamp: Date
}

interface InvestigationStep {
  step: number
  status: 'in_progress' | 'complete' | 'error'
  phase: string
  message: string
  details?: any
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [steps, setSteps] = useState<InvestigationStep[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [merchantId] = useState('demo-merchant')
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages, steps])
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim() || loading) return
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setSteps([])
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(
        `${baseUrl}/api/v1/merchants/${merchantId}/agent/query?query=${encodeURIComponent(input)}`,
        { method: 'POST' }
      )
      
      if (!response.ok) {
        throw new Error('Agent query failed')
      }
      
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      
      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          
          buffer = lines[lines.length - 1]
          
          for (let i = 0; i < lines.length - 1; i++) {
            const line = lines[i].trim()
            if (line.startsWith('data: ')) {
              try {
                const step = JSON.parse(line.slice(6))
                setSteps(prev => {
                  const existing = prev.findIndex(s => s.step === step.step)
                  if (existing >= 0) {
                    const updated = [...prev]
                    updated[existing] = step
                    return updated
                  }
                  return [...prev, step]
                })
              } catch (e) {
                // JSON parse error
              }
            }
          }
        }
      }
      
      // Add agent summary message
      const lastStep = steps[steps.length - 1]
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: lastStep?.message || 'Investigation complete',
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, agentMessage])
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">RevPilot Assistant</h1>
          <p className="text-sm text-gray-600">Ask me about revenue, anomalies, or recovery opportunities</p>
        </div>
      </div>
      
      {/* Chat Area */}
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 overflow-y-auto">
        {messages.length === 0 && steps.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <p className="text-lg font-medium mb-2">👋 Welcome to RevPilot</p>
            <p className="text-sm">Ask me questions like:</p>
            <ul className="text-xs mt-4 space-y-1 text-gray-600">
              <li>"Why is revenue down today?"</li>
              <li>"Which customers can I recover?"</li>
              <li>"What caused the payment failures?"</li>
            </ul>
          </div>
        ) : (
          <>
            {/* Messages */}
            {messages.map((msg) => (
              <div key={msg.id} className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-none' 
                    : 'bg-gray-200 text-gray-900 rounded-bl-none'
                }`}>
                  <p className="text-sm">{msg.content}</p>
                  <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-600'}`}>
                    {msg.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            
            {/* Investigation Steps */}
            {steps.length > 0 && (
              <div className="mb-6 bg-white rounded-lg p-6 border border-gray-200">
                <p className="text-sm font-bold text-gray-900 mb-4">📊 Investigation Timeline</p>
                <div className="space-y-3">
                  {steps.map((step) => (
                    <div key={step.step} className="flex items-start">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-3 flex-shrink-0 ${
                        step.status === 'complete' ? 'bg-green-100 text-green-700' :
                        step.status === 'error' ? 'bg-red-100 text-red-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {step.status === 'complete' ? '✓' : step.status === 'error' ? '✗' : '⏳'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">{step.phase}</p>
                        <p className="text-xs text-gray-600">{step.message}</p>
                        {step.details && (
                          <details className="mt-1 text-xs">
                            <summary className="cursor-pointer text-gray-500 hover:text-gray-700">Details</summary>
                            <pre className="mt-1 bg-gray-50 p-2 rounded text-xs overflow-auto">
                              {JSON.stringify(step.details, null, 2).slice(0, 200)}...
                            </pre>
                          </details>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      
      {/* Input Area */}
      <div className="bg-white border-t border-gray-200">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto px-4 py-4 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder={loading ? "Investigating..." : "Ask RevPilot..."}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-6 rounded-lg transition"
          >
            {loading ? 'Investigating...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  )
}
