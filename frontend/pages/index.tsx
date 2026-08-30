import React, { useEffect, useState } from 'react'
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
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Phase 1: Foundation</h2>
              <div className="space-y-2 text-gray-700">
                <p className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Next.js frontend initialized
                </p>
                <p className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  FastAPI backend structure ready
                </p>
                <p className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  PostgreSQL schema defined
                </p>
                <p className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Synthetic data generator created
                </p>
                <p className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  Docker Compose stack configured
                </p>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Next Steps</h2>
              <ol className="list-decimal list-inside space-y-2 text-gray-700">
                <li>Start Docker Compose: `docker compose up`</li>
                <li>Run synthetic data generator: `python data/generator.py`</li>
                <li>Build Phase 2: Analytics layer</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
