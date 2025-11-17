import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { FileQuestion, History, User, LogOut } from 'lucide-react'
import { useEffect, useState } from 'react'
import api from '../lib/api'

export default function Dashboard() {
  const { user, logout } = useAuthStore()
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0 })

  useEffect(() => {
    // Fetch user stats
    api
      .get('/queries?limit=100')
      .then((res) => {
        const queries = res.data
        setStats({
          total: queries.length,
          completed: queries.filter((q: any) => q.status === 'completed').length,
          pending: queries.filter((q: any) => q.status === 'processing').length,
        })
      })
      .catch(console.error)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">LegalAI Dashboard</h1>
          <div className="flex items-center gap-4">
            <Link to="/profile" className="flex items-center gap-2 text-gray-700 hover:text-blue-600">
              <User className="w-5 h-5" />
              <span>{user?.full_name}</span>
            </Link>
            <button
              onClick={logout}
              className="flex items-center gap-2 text-gray-700 hover:text-red-600"
            >
              <LogOut className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name}!
          </h2>
          <p className="text-gray-600">Get preventive legal guidance for your concerns</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-gray-600">Total Queries</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <div className="text-gray-600">Completed</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
            <div className="text-gray-600">Pending</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white p-8 rounded-lg shadow mb-8">
          <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
          <Link
            to="/query"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
          >
            <FileQuestion className="w-5 h-5" />
            Ask Legal Question
          </Link>
        </div>

        {/* Recent Queries */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">Recent Queries</h3>
            <Link to="/history" className="text-blue-600 hover:text-blue-700 flex items-center gap-2">
              <History className="w-4 h-4" />
              View All
            </Link>
          </div>
          <div className="text-gray-600">No recent queries. Start by asking a legal question!</div>
        </div>
      </div>
    </div>
  )
}

