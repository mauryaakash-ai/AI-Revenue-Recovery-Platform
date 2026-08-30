import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'

interface HealthStatus {
  status: string
  service: string
  environment?: string
}

export default function Home() {
  const [backendHealth, setBackendHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        setLoading(true)
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/health`)
        setBackendHealth(response.data)
        setError(null)
      } catch (err) {
        setError(`Failed to connect to backend: ${err}`)
        setBackendHealth(null)
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">RevPilot</h1>
          <p className="text-xl text-gray-600 mb-8">AI Revenue Intelligence & Action Agent</p>

          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Status</h2>
              
              <div className="bg-gray-100 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">Backend Health:</p>
                {loading ? (
                  <p className="text-gray-500">Checking...</p>
                ) : error ? (
                  <div className="text-red-600">
                    <p>❌ {error}</p>
                  </div>
                ) : backendHealth ? (
                  <div className="text-green-600">
                    <p>✓ Backend: {backendHealth.status}</p>
                    <p className="text-sm text-gray-600 mt-1">Service: {backendHealth.service}</p>
                    {backendHealth.environment && (
                      <p className="text-sm text-gray-600">Environment: {backendHealth.environment}</p>
                    )}
                  </div>
                ) : null}
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Navigation</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Link href="/dashboard" className="block p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition">
                  <h3 className="font-semibold text-blue-900">📊 Dashboard</h3>
                  <p className="text-sm text-blue-700 mt-1">KPIs, revenue leaks, recommended actions</p>
                </Link>
                
                <Link href="/chat" className="block p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition">
                  <h3 className="font-semibold text-green-900">💬 Chat</h3>
                  <p className="text-sm text-green-700 mt-1">Ask RevPilot questions in natural language</p>
                </Link>
                
                <Link href="/audit-log" className="block p-4 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition">
                  <h3 className="font-semibold text-purple-900">📋 Audit Log</h3>
                  <p className="text-sm text-purple-700 mt-1">Track all agent actions and approvals</p>
                </Link>
                
                <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="block p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition">
                  <h3 className="font-semibold text-gray-900">🔌 API Docs</h3>
                  <p className="text-sm text-gray-700 mt-1">FastAPI Swagger documentation</p>
                </a>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Features</h2>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Real-time anomaly detection</li>
                <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Root cause analysis</li>
                <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Revenue recovery ranking</li>
                <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Human-in-the-loop approval</li>
                <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Full audit trail</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
