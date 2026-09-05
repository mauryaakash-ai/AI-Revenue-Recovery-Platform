import React, { createContext, useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import axios from 'axios'

export interface UserProfile {
  id: string
  name: string
  email: string
  phone?: string
  role: string
  merchant_id: string
  merchant_name: string
  avatar: string
}

interface AuthContextType {
  user: UserProfile | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password?: string, personaId?: string) => Promise<boolean>
  loginWithOtp: (phone: string, otp: string) => Promise<boolean>
  sendOtp: (phone: string) => Promise<{ success: boolean; hint?: string; message: string }>
  logout: () => void
  switchPersona: (personaId: string) => Promise<void>
}

const DEFAULT_USER: UserProfile = {
  id: 'usr_akash_01',
  name: 'Akash Sharma',
  email: 'akash@urbankart.com',
  phone: '+91 98201 94821',
  role: 'Admin',
  merchant_id: 'merchant_urbankart',
  merchant_name: 'UrbanKart',
  avatar: 'AK'
}

const AuthContext = createContext<AuthContextType>({
  user: DEFAULT_USER,
  token: 'tok_demo_default',
  isAuthenticated: true,
  loading: false,
  login: async () => false,
  loginWithOtp: async () => false,
  sendOtp: async () => ({ success: false, message: '' }),
  logout: () => {},
  switchPersona: async () => {}
})

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const router = useRouter()
  const [user, setUser] = useState<UserProfile | null>(DEFAULT_USER)
  const [token, setToken] = useState<string | null>('tok_demo_default')
  const [loading, setLoading] = useState(true)

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('revpilot_user')
      const storedToken = localStorage.getItem('revpilot_token')
      if (storedUser && storedToken) {
        setUser(JSON.parse(storedUser))
        setToken(storedToken)
      } else {
        // Initialize with default demo session
        localStorage.setItem('revpilot_user', JSON.stringify(DEFAULT_USER))
        localStorage.setItem('revpilot_token', 'tok_demo_default')
      }
    } catch (e) {
      console.warn('LocalStorage error in AuthContext', e)
    } finally {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password?: string, personaId?: string): Promise<boolean> => {
    try {
      setLoading(true)
      const res = await axios.post(`${baseUrl}/api/v1/auth/login`, {
        email,
        password: password || 'demo123',
        persona_id: personaId
      })
      if (res.data.success) {
        const authedUser = res.data.user
        const authToken = res.data.token
        setUser(authedUser)
        setToken(authToken)
        localStorage.setItem('revpilot_user', JSON.stringify(authedUser))
        localStorage.setItem('revpilot_token', authToken)
        return true
      }
      return false
    } catch (err) {
      console.error('Login error', err)
      // Fallback for offline demo mode
      const name = email.split('@')[0] || 'Demo User'
      const fallbackUser: UserProfile = {
        id: 'usr_demo_fallback',
        name: name.charAt(0).toUpperCase() + name.slice(1),
        email,
        role: 'Revenue Operations',
        merchant_id: 'merchant_urbankart',
        merchant_name: 'UrbanKart',
        avatar: name.slice(0, 2).toUpperCase()
      }
      setUser(fallbackUser)
      setToken('tok_fallback')
      localStorage.setItem('revpilot_user', JSON.stringify(fallbackUser))
      localStorage.setItem('revpilot_token', 'tok_fallback')
      return true
    } finally {
      setLoading(false)
    }
  }

  const sendOtp = async (phone: string): Promise<{ success: boolean; hint?: string; message: string }> => {
    try {
      const res = await axios.post(`${baseUrl}/api/v1/auth/send-otp`, { phone })
      return {
        success: true,
        hint: res.data.demo_otp_hint,
        message: res.data.message
      }
    } catch (err) {
      console.error('Send OTP error', err)
      return {
        success: true,
        hint: '482910',
        message: 'Demo security OTP dispatched (482910)'
      }
    }
  }

  const loginWithOtp = async (phone: string, otp: string): Promise<boolean> => {
    try {
      setLoading(true)
      const res = await axios.post(`${baseUrl}/api/v1/auth/verify-otp`, { phone, otp })
      if (res.data.success) {
        const authedUser = res.data.user
        const authToken = res.data.token
        setUser(authedUser)
        setToken(authToken)
        localStorage.setItem('revpilot_user', JSON.stringify(authedUser))
        localStorage.setItem('revpilot_token', authToken)
        return true
      }
      return false
    } catch (err) {
      console.error('Verify OTP error', err)
      if (otp === '123456' || otp === '482910') {
        setUser(DEFAULT_USER)
        setToken('tok_demo_otp')
        localStorage.setItem('revpilot_user', JSON.stringify(DEFAULT_USER))
        localStorage.setItem('revpilot_token', 'tok_demo_otp')
        return true
      }
      return false
    } finally {
      setLoading(false)
    }
  }

  const switchPersona = async (personaId: string) => {
    await login('', undefined, personaId)
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('revpilot_user')
    localStorage.removeItem('revpilot_token')
    router.push('/login')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        loading,
        login,
        loginWithOtp,
        sendOtp,
        logout,
        switchPersona
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)

