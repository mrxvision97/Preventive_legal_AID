import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, Shield } from 'lucide-react'
import api from '../lib/api'
import { useAuthStore } from '../store/authStore'

const signupSchema = z
  .object({
    full_name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Invalid email address'),
    phone: z.string().optional(),
    password: z.string().min(6, 'Password must be at least 6 characters'),
    confirm_password: z.string(),
    user_type: z.enum(['farmer', 'student', 'citizen']),
    language_preference: z.string().default('hi'),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
  })

type SignupForm = z.infer<typeof signupSchema>

export default function SignupPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<SignupForm>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      user_type: 'citizen',
      language_preference: 'hi',
    },
  })

  const watchedValues = watch()

  const onSubmit = async (data: SignupForm) => {
    setLoading(true)
    setError(null)
    try {
      const { confirm_password, ...signupData } = data
      const response = await api.post('/auth/register', signupData)
      const { user, access_token, refresh_token } = response.data
      setAuth(user, access_token, refresh_token)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignup = () => {
    // Placeholder for Google OAuth
    alert('Google sign-up coming soon!')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#F7F9FB] via-[#FFFFFF] to-[#F0F4F8] p-4">
      <div className="w-full max-w-md">
        {/* Authentication Card */}
        <div className="bg-white/80 backdrop-blur-xl rounded-3xl border border-gray-200/50 shadow-xl shadow-gray-200/50 p-8 sm:p-10">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 mb-4 shadow-lg">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2 tracking-tight">
              Create Your Account
            </h1>
            <p className="text-gray-600 text-sm">
              Start receiving personalized legal guidance.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Google Sign Up Button */}
          <button
            onClick={handleGoogleSignup}
            className="w-full mb-6 px-4 py-3 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200 flex items-center justify-center gap-3 text-sm font-medium text-gray-700 shadow-sm hover:shadow-md"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Continue with Google
          </button>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-4 bg-white text-gray-500">Or continue with email</span>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Full Name */}
            <div className="relative">
              <div
                className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-200 ${
                  focusedField === 'full_name' || watchedValues.full_name
                    ? 'text-blue-500'
                    : 'text-gray-400'
                }`}
              >
                <User className="w-5 h-5" />
              </div>
              <input
                {...register('full_name')}
                type="text"
                onFocus={() => setFocusedField('full_name')}
                onBlur={() => setFocusedField(null)}
                className={`w-full pl-12 pr-4 py-3.5 bg-gray-50 border-2 rounded-xl transition-all duration-200 focus:outline-none focus:bg-white ${
                  errors.full_name
                    ? 'border-red-300 focus:border-red-500'
                    : focusedField === 'full_name'
                    ? 'border-blue-300 focus:border-blue-500'
                    : 'border-gray-200 focus:border-gray-300'
                } text-gray-900 placeholder-transparent`}
                placeholder=" "
              />
              <label
                className={`absolute left-12 transition-all duration-200 pointer-events-none ${
                  focusedField === 'full_name' || watchedValues.full_name
                    ? 'top-2 text-xs text-blue-600'
                    : 'top-1/2 -translate-y-1/2 text-sm text-gray-500'
                }`}
              >
                {focusedField === 'full_name' || watchedValues.full_name ? 'Full Name' : 'Full Name'}
              </label>
              {errors.full_name && (
                <p className="mt-1.5 text-xs text-red-600 ml-1">{errors.full_name.message}</p>
              )}
            </div>

            {/* Email */}
            <div className="relative">
              <div
                className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-200 ${
                  focusedField === 'email' || watchedValues.email
                    ? 'text-blue-500'
                    : 'text-gray-400'
                }`}
              >
                <Mail className="w-5 h-5" />
              </div>
              <input
                {...register('email')}
                type="email"
                onFocus={() => setFocusedField('email')}
                onBlur={() => setFocusedField(null)}
                className={`w-full pl-12 pr-4 py-3.5 bg-gray-50 border-2 rounded-xl transition-all duration-200 focus:outline-none focus:bg-white ${
                  errors.email
                    ? 'border-red-300 focus:border-red-500'
                    : focusedField === 'email'
                    ? 'border-blue-300 focus:border-blue-500'
                    : 'border-gray-200 focus:border-gray-300'
                } text-gray-900 placeholder-transparent`}
                placeholder=" "
              />
              <label
                className={`absolute left-12 transition-all duration-200 pointer-events-none ${
                  focusedField === 'email' || watchedValues.email
                    ? 'top-2 text-xs text-blue-600'
                    : 'top-1/2 -translate-y-1/2 text-sm text-gray-500'
                }`}
              >
                {focusedField === 'email' || watchedValues.email ? 'Email' : 'Email'}
              </label>
              {errors.email && (
                <p className="mt-1.5 text-xs text-red-600 ml-1">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div className="relative">
              <div
                className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-200 ${
                  focusedField === 'password' || watchedValues.password
                    ? 'text-blue-500'
                    : 'text-gray-400'
                }`}
              >
                <Lock className="w-5 h-5" />
              </div>
              <input
                {...register('password')}
                type={showPassword ? 'text' : 'password'}
                onFocus={() => setFocusedField('password')}
                onBlur={() => setFocusedField(null)}
                className={`w-full pl-12 pr-12 py-3.5 bg-gray-50 border-2 rounded-xl transition-all duration-200 focus:outline-none focus:bg-white ${
                  errors.password
                    ? 'border-red-300 focus:border-red-500'
                    : focusedField === 'password'
                    ? 'border-blue-300 focus:border-blue-500'
                    : 'border-gray-200 focus:border-gray-300'
                } text-gray-900 placeholder-transparent`}
                placeholder=" "
              />
              <label
                className={`absolute left-12 transition-all duration-200 pointer-events-none ${
                  focusedField === 'password' || watchedValues.password
                    ? 'top-2 text-xs text-blue-600'
                    : 'top-1/2 -translate-y-1/2 text-sm text-gray-500'
                }`}
              >
                {focusedField === 'password' || watchedValues.password ? 'Password' : 'Password'}
              </label>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
              {errors.password && (
                <p className="mt-1.5 text-xs text-red-600 ml-1">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div className="relative">
              <div
                className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-200 ${
                  focusedField === 'confirm_password' || watchedValues.confirm_password
                    ? 'text-blue-500'
                    : 'text-gray-400'
                }`}
              >
                <Lock className="w-5 h-5" />
              </div>
              <input
                {...register('confirm_password')}
                type={showConfirmPassword ? 'text' : 'password'}
                onFocus={() => setFocusedField('confirm_password')}
                onBlur={() => setFocusedField(null)}
                className={`w-full pl-12 pr-12 py-3.5 bg-gray-50 border-2 rounded-xl transition-all duration-200 focus:outline-none focus:bg-white ${
                  errors.confirm_password
                    ? 'border-red-300 focus:border-red-500'
                    : focusedField === 'confirm_password'
                    ? 'border-blue-300 focus:border-blue-500'
                    : 'border-gray-200 focus:border-gray-300'
                } text-gray-900 placeholder-transparent`}
                placeholder=" "
              />
              <label
                className={`absolute left-12 transition-all duration-200 pointer-events-none ${
                  focusedField === 'confirm_password' || watchedValues.confirm_password
                    ? 'top-2 text-xs text-blue-600'
                    : 'top-1/2 -translate-y-1/2 text-sm text-gray-500'
                }`}
              >
                {focusedField === 'confirm_password' || watchedValues.confirm_password
                  ? 'Confirm Password'
                  : 'Confirm Password'}
              </label>
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
              {errors.confirm_password && (
                <p className="mt-1.5 text-xs text-red-600 ml-1">
                  {errors.confirm_password.message}
                </p>
              )}
            </div>

            {/* User Type */}
            <div className="relative">
              <select
                {...register('user_type')}
                className="w-full pl-4 pr-4 py-3.5 bg-gray-50 border-2 border-gray-200 rounded-xl transition-all duration-200 focus:outline-none focus:bg-white focus:border-blue-500 text-gray-900 text-sm appearance-none cursor-pointer"
              >
                <option value="citizen">I am a Citizen</option>
                <option value="farmer">I am a Farmer</option>
                <option value="student">I am a Student</option>
              </select>
              <ArrowRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none rotate-90" />
            </div>

            {/* Legal Disclaimer */}
            <p className="text-xs text-gray-500 text-center leading-relaxed">
              By signing up, you agree to our{' '}
              <Link to="/terms" className="text-blue-600 hover:text-blue-700 font-medium">
                Terms
              </Link>{' '}
              &{' '}
              <Link to="/privacy" className="text-blue-600 hover:text-blue-700 font-medium">
                Privacy Policy
              </Link>
            </p>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Sign Up for Free</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Sign In Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-blue-600 hover:text-blue-700 font-semibold transition-colors"
              >
                Sign In
              </Link>
            </p>
          </div>
        </div>

        {/* Additional Trust Indicators */}
        <div className="mt-6 flex items-center justify-center gap-6 text-xs text-gray-500">
          <div className="flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-green-500" />
            <span>Secure</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Lock className="w-4 h-4 text-blue-500" />
            <span>Encrypted</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-purple-500">✓</span>
            <span>Free Forever</span>
          </div>
        </div>
      </div>
    </div>
  )
}
