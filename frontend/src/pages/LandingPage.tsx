import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Scale, Users, GraduationCap, FileText, Shield, Globe, MessageCircle, Search, CheckCircle2, ArrowRight, ChevronDown, Mic, MicOff, Camera, Image as ImageIcon, X } from 'lucide-react'
import Chatbot from '../components/Chatbot'
import api from '../lib/api'

export default function LandingPage() {
  const [showChatbot, setShowChatbot] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [openFaq, setOpenFaq] = useState<number | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const [isProcessingImage, setIsProcessingImage] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      setShowChatbot(true)
      // The chatbot will handle the query
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await handleAudioTranscription(audioBlob)
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Microphone access denied. Please enable microphone permissions to use voice search.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleAudioTranscription = async (audioBlob: Blob) => {
    setIsTranscribing(true)
    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.webm')
      formData.append('language_hint', 'hi') // Default to Hindi, can be made dynamic

      const response = await api.post('/ai/transcribe', formData)

      if (response.data.text) {
        setSearchQuery(response.data.text)
        // Auto-open chatbot with transcribed text
        setShowChatbot(true)
      }
    } catch (error) {
      console.error('Transcription error:', error)
      alert('Failed to transcribe audio. Please try typing your question instead.')
    } finally {
      setIsTranscribing(false)
    }
  }

  const startCamera = async () => {
    try {
      // First, try to enumerate devices to find external/USB cameras
      let videoConstraints: MediaTrackConstraints = {
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }

      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        const videoInputs = devices.filter(device => device.kind === 'videoinput')
        
        // Prefer external/USB cameras (usually have longer labels or specific names)
        // On Jetson Nano, USB cameras are typically listed separately
        const externalCamera = videoInputs.find(device => 
          device.label && (
            device.label.toLowerCase().includes('usb') ||
            device.label.toLowerCase().includes('external') ||
            device.label.toLowerCase().includes('camera') ||
            device.label.toLowerCase().includes('webcam') ||
            device.label.toLowerCase().includes('logitech') ||
            device.label.toLowerCase().includes('hd') ||
            // Jetson Nano specific camera names
            device.label.toLowerCase().includes('uvc') ||
            device.label.toLowerCase().includes('video')
          )
        )

        if (externalCamera && externalCamera.deviceId) {
          // Use external camera device ID
          videoConstraints.deviceId = { exact: externalCamera.deviceId }
          console.log('Using external camera:', externalCamera.label)
        } else if (videoInputs.length > 1) {
          // If multiple cameras, prefer the last one (usually external on Jetson Nano)
          const lastCamera = videoInputs[videoInputs.length - 1]
          if (lastCamera.deviceId) {
            videoConstraints.deviceId = { exact: lastCamera.deviceId }
            console.log('Using camera:', lastCamera.label || 'Camera ' + videoInputs.length)
          }
        } else if (videoInputs.length === 1 && videoInputs[0].deviceId) {
          // Only one camera available
          videoConstraints.deviceId = { exact: videoInputs[0].deviceId }
          console.log('Using available camera:', videoInputs[0].label || 'Camera')
        } else {
          // Fallback to facingMode for mobile devices
          videoConstraints.facingMode = 'environment'
        }
      } catch (enumError) {
        console.warn('Could not enumerate devices, using default camera:', enumError)
        // Fallback to facingMode
        videoConstraints.facingMode = 'environment'
      }

      // Request camera access with selected constraints
      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints
      })
      
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.onloadedmetadata = () => {
          if (videoRef.current) {
            videoRef.current.play().catch(err => {
              console.error('Error playing video:', err)
            })
          }
        }
      }
      setShowCamera(true)
    } catch (error: any) {
      console.error('Error accessing camera:', error)
      if (error.name === 'NotAllowedError') {
        alert('Camera access denied. Please enable camera permissions in your browser settings.')
      } else if (error.name === 'NotFoundError') {
        alert('No camera found. Please connect a camera and try again.')
      } else {
        alert(`Camera error: ${error.message || 'Unable to access camera'}`)
      }
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
      videoRef.current.pause()
    }
    setShowCamera(false)
  }

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) {
      console.error('Video or canvas ref not available')
      return
    }

    const video = videoRef.current
    const canvas = canvasRef.current

    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.error('Video not ready')
      alert('Please wait for camera to be ready')
      return
    }

    const context = canvas.getContext('2d')
    if (!context) {
      console.error('Could not get canvas context')
      return
    }

    const videoWidth = video.videoWidth || 640
    const videoHeight = video.videoHeight || 480
    
    if (videoWidth === 0 || videoHeight === 0) {
      console.error('Invalid video dimensions')
      alert('Camera not ready. Please try again.')
      return
    }

    canvas.width = videoWidth
    canvas.height = videoHeight

    try {
      context.drawImage(video, 0, 0, videoWidth, videoHeight)
    } catch (error) {
      console.error('Error drawing video to canvas:', error)
      alert('Failed to capture image. Please try again.')
      return
    }

    canvas.toBlob(async (blob) => {
      if (blob) {
        stopCamera()
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
        await handleImageUpload(file)
      } else {
        console.error('Failed to create blob from canvas')
        alert('Failed to process captured image. Please try again.')
      }
    }, 'image/jpeg', 0.9)
  }

  const handleImageUpload = async (file: File) => {
    if (!file) return

    if (file.size > 10 * 1024 * 1024) {
      alert('Image size must be less than 10MB')
      return
    }

    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file (JPG, PNG, etc.)')
      return
    }

    setIsProcessingImage(true)

    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('domain', 'civil') // Default domain
      formData.append('language', 'en') // Default language
      formData.append('analyze', 'true')

      const response = await api.post('/public/ocr', formData, {
        timeout: 60000,
      })

      const ocrData = response.data

      // Set extracted text as search query and open chatbot
      if (ocrData.extracted_text && ocrData.extracted_text.trim()) {
        setSearchQuery(ocrData.extracted_text)
        setShowChatbot(true)
      } else {
        alert('No text could be extracted from this image. Please ensure the image is clear and contains readable text.')
      }
    } catch (error: any) {
      console.error('Image processing error:', error)
      alert(`Failed to process image: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsProcessingImage(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.type.startsWith('image/')) {
      await handleImageUpload(file)
      return
    }

    alert('Please upload an image file for OCR.')
  }

  // Cleanup camera stream on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
        streamRef.current = null
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null
      }
    }
  }, [])

  const faqs = [
    {
      question: 'Is my legal query confidential?',
      answer: 'Yes, all queries are processed anonymously. We do not store personal information and your data is encrypted in transit.',
    },
    {
      question: 'Is this service free?',
      answer: 'Yes, VU Legal AID is completely free to use. Our mission is to make legal guidance accessible to everyone.',
    },
    {
      question: 'Can this replace a lawyer?',
      answer: 'No, this service provides preventive guidance and information only. For complex legal matters, we recommend consulting a qualified lawyer.',
    },
    {
      question: 'What languages are supported?',
      answer: 'We support Hindi, English, Tamil, Telugu, Bengali, and Marathi. You can ask questions in any of these languages.',
    },
    {
      question: 'How accurate is the legal advice?',
      answer: 'Our AI is trained on verified legal databases and Indian legal documents. However, this is advisory only and not legal representation.',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#EFF3F6] via-white to-[#F8FAFC] dark:from-[#0D1117] dark:via-[#161B22] dark:to-[#0D1117]">
      {/* Header */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-white/80 dark:bg-[#161B22]/80 border-b border-gray-200/50 dark:border-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex justify-between items-center h-16">
            <div className="text-2xl font-bold bg-gradient-to-r from-red-600 to-blue-600 bg-clip-text text-transparent">
              VU Legal AID
            </div>
            <div className="flex gap-4">
              <Link 
                to="/login" 
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              >
                Login
              </Link>
              <Link
                to="/signup"
                className="px-4 py-2 bg-gradient-to-r from-red-500 to-blue-500 text-white rounded-lg hover:from-red-600 hover:to-blue-600 transition-all shadow-sm"
              >
                Get Started
              </Link>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 sm:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            {/* Trust Badges */}
            <div className="flex flex-wrap justify-center gap-4 mb-6">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-white/60 dark:bg-[#161B22]/60 backdrop-blur-sm rounded-full border border-gray-200/50 dark:border-gray-800/50 text-xs text-gray-700 dark:text-gray-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-green-600 dark:text-green-400" />
                <span>Powered by Verified Legal Databases</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-white/60 dark:bg-[#161B22]/60 backdrop-blur-sm rounded-full border border-gray-200/50 dark:border-gray-800/50 text-xs text-gray-700 dark:text-gray-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                <span>Designed with Lawyers & Researchers</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-white/60 dark:bg-[#161B22]/60 backdrop-blur-sm rounded-full border border-gray-200/50 dark:border-gray-800/50 text-xs text-gray-700 dark:text-gray-300">
                <Shield className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
                <span>100% Anonymous | No Data Stored</span>
              </div>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 bg-gradient-to-r from-red-600 via-blue-600 to-cyan-600 bg-clip-text text-transparent leading-tight">
              Get Legal Guidance Before Conflicts Arise
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto leading-relaxed">
              AI-powered preventive legal assistance for rural citizens, farmers, and university
              students in India. Understand your legal rights and prevent disputes before they start.
            </p>

            {/* Inline Search Bar */}
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-8">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500 z-10" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search your legal query or speak..."
                  className="w-full pl-12 pr-36 py-4 bg-white dark:bg-[#161B22] border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 dark:focus:ring-red-400/20 dark:focus:border-red-400 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
                  {/* Camera Button */}
                  <button
                    type="button"
                    onClick={startCamera}
                    className="p-2.5 rounded-xl bg-gray-100 dark:bg-[#0D1117] hover:bg-gray-200 dark:hover:bg-[#161B22] text-gray-600 dark:text-gray-400 hover:text-blue-500 dark:hover:text-blue-400 transition-all"
                    title="Capture image with camera"
                    disabled={isTranscribing || isProcessingImage || showCamera}
                  >
                    <Camera className="w-5 h-5" />
                  </button>
                  {/* Document/Image Upload Button */}
                  <label className="p-2.5 rounded-xl bg-gray-100 dark:bg-[#0D1117] hover:bg-gray-200 dark:hover:bg-[#161B22] text-gray-600 dark:text-gray-400 hover:text-green-500 dark:hover:text-green-400 transition-all cursor-pointer" title="Upload image or document">
                    <ImageIcon className="w-5 h-5" />
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*,.jpg,.jpeg,.png,.gif,.webp"
                      onChange={handleFileUpload}
                      className="hidden"
                      disabled={isTranscribing || isProcessingImage || showCamera}
                    />
                  </label>
                  {/* Microphone Button */}
                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`p-2.5 rounded-xl transition-all ${
                      isRecording
                        ? 'bg-red-500 text-white animate-pulse shadow-lg'
                        : 'bg-gray-100 dark:bg-[#0D1117] hover:bg-gray-200 dark:hover:bg-[#161B22] text-gray-600 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400'
                    }`}
                    title={isRecording ? 'Stop recording' : 'Start voice search'}
                    disabled={isTranscribing || isProcessingImage || showCamera}
                  >
                    {isRecording ? (
                      <MicOff className="w-5 h-5" />
                    ) : isTranscribing ? (
                      <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Mic className="w-5 h-5" />
                    )}
                  </button>
                  {/* Ask AI Button */}
                  <button
                    type="submit"
                    disabled={!searchQuery.trim() || isTranscribing || isProcessingImage}
                    className="px-6 py-2.5 bg-gradient-to-r from-red-500 to-blue-500 text-white rounded-xl hover:from-red-600 hover:to-blue-600 transition-all font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                  >
                    {isTranscribing ? 'Transcribing...' : isProcessingImage ? 'Processing...' : 'Ask AI'}
                  </button>
                </div>
              </div>
              {isRecording && (
                <div className="mt-3 text-center">
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-full">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-red-600 dark:text-red-400 font-medium">
                      Recording... Click mic again to stop
                    </span>
                  </div>
                </div>
              )}
              {isTranscribing && !isRecording && (
                <div className="mt-3 text-center">
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-full">
                    <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                      Transcribing your voice...
                    </span>
                  </div>
                </div>
              )}
              {isProcessingImage && (
                <div className="mt-3 text-center">
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-full">
                    <div className="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm text-green-600 dark:text-green-400 font-medium">
                      Processing image...
                    </span>
                  </div>
                </div>
              )}
            </form>

            {/* Camera Modal */}
            {showCamera && (
              <div className="fixed inset-0 bg-black/80 z-50 flex flex-col items-center justify-center p-4">
                <div className="bg-white dark:bg-[#161B22] rounded-2xl p-4 w-full max-w-md">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Capture Image</h3>
                    <button
                      onClick={stopCamera}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-[#0D1117] rounded-lg"
                    >
                      <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                  </div>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full rounded-lg mb-4 bg-black"
                    style={{ maxHeight: '60vh', objectFit: 'contain' }}
                    onLoadedMetadata={() => {
                      if (videoRef.current) {
                        videoRef.current.play().catch(err => {
                          console.error('Error playing video:', err)
                        })
                      }
                    }}
                  />
                  <canvas ref={canvasRef} className="hidden" />
                  <div className="flex gap-2">
                    <button
                      onClick={stopCamera}
                      className="flex-1 px-4 py-2 bg-gray-200 dark:bg-[#0D1117] text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-[#161B22] transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={captureImage}
                      className="flex-1 px-4 py-2 bg-gradient-to-r from-red-500 to-blue-500 text-white rounded-lg hover:from-red-600 hover:to-blue-600 transition-all"
                    >
                      Capture
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="flex flex-wrap gap-4 justify-center">
              <Link
                to="/signup"
                className="px-8 py-3 bg-gradient-to-r from-red-500 to-blue-500 text-white rounded-xl text-lg font-semibold hover:from-red-600 hover:to-blue-600 transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5" />
              </Link>
              <button
                onClick={() => setShowChatbot(true)}
                className="px-8 py-3 bg-white dark:bg-[#161B22] border-2 border-cyan-500 text-cyan-600 dark:text-cyan-400 rounded-xl text-lg font-semibold hover:bg-cyan-50 dark:hover:bg-cyan-900/20 transition-all flex items-center gap-2"
              >
                <MessageCircle className="w-5 h-5" />
                Chat Now (Free)
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid - Modern Cards */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4 bg-gradient-to-r from-red-600 to-blue-600 bg-clip-text text-transparent">
            Legal Domains We Cover
          </h2>
          <p className="text-center text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            Comprehensive legal guidance across four key domains
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: Scale,
                title: 'Agriculture Law',
                description: 'Land leasing, tenant rights, crop insurance, and agricultural regulations',
                color: 'red',
                gradient: 'from-red-100 to-red-50 dark:from-red-900/20 dark:to-red-800/10',
                borderColor: 'border-red-200 dark:border-red-800/50',
                iconColor: 'text-red-600 dark:text-red-400',
              },
              {
                icon: FileText,
                title: 'Civil Law',
                description: 'Contracts, property disputes, consumer rights, and civil procedures',
                color: 'blue',
                gradient: 'from-blue-100 to-blue-50 dark:from-blue-900/20 dark:to-blue-800/10',
                borderColor: 'border-blue-200 dark:border-blue-800/50',
                iconColor: 'text-blue-600 dark:text-blue-400',
              },
              {
                icon: Users,
                title: 'Family & Marriage',
                description: 'Marriage laws, divorce, inheritance, and family dispute resolution',
                color: 'cyan',
                gradient: 'from-cyan-100 to-cyan-50 dark:from-cyan-900/20 dark:to-cyan-800/10',
                borderColor: 'border-cyan-200 dark:border-cyan-800/50',
                iconColor: 'text-cyan-600 dark:text-cyan-400',
              },
              {
                icon: GraduationCap,
                title: 'University Legal Aid',
                description: 'Student rights, harassment policies, hostel rules, and campus disputes',
                color: 'turquoise',
                gradient: 'from-turquoise-100 to-turquoise-50 dark:from-turquoise-900/20 dark:to-turquoise-800/10',
                borderColor: 'border-turquoise-200 dark:border-turquoise-800/50',
                iconColor: 'text-turquoise-600 dark:text-turquoise-400',
              },
            ].map((feature, idx) => {
              const Icon = feature.icon
              return (
                <div
                  key={idx}
                  className="group relative bg-white dark:bg-[#161B22] rounded-2xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
                >
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 border ${feature.borderColor}`}>
                    <Icon className={`w-7 h-7 ${feature.iconColor}`} />
                  </div>
                  <h3 className={`text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100`}>
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* How It Works - Timeline Style */}
      <section className="py-20 bg-white/50 dark:bg-[#161B22]/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4 bg-gradient-to-r from-red-600 to-blue-600 bg-clip-text text-transparent">
            How It Works
          </h2>
          <p className="text-center text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            Get legal guidance in three simple steps
          </p>
          <div className="relative max-w-5xl mx-auto">
            {/* Timeline Line */}
            <div className="hidden md:block absolute top-16 left-0 right-0 h-0.5 bg-gradient-to-r from-red-200 via-blue-200 to-cyan-200 dark:from-red-800/50 dark:via-blue-800/50 dark:to-cyan-800/50"></div>
            
            <div className="grid md:grid-cols-3 gap-8 relative">
              {[
                { num: 1, title: 'Describe Issue', desc: 'Tell us about your legal concern in your preferred language - text or voice' },
                { num: 2, title: 'AI Analyzes', desc: 'Our AI searches legal databases and provides comprehensive risk assessment' },
                { num: 3, title: 'Get Guidance', desc: 'Receive preventive roadmap, legal references, and actionable next steps' },
              ].map((step, idx) => (
                <div key={idx} className="relative">
                  <div className="flex flex-col items-center text-center">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-red-500 to-blue-500 flex items-center justify-center text-white font-bold text-xl mb-4 shadow-lg relative z-10">
                      {step.num}
                    </div>
                    <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">
                      {step.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4 bg-gradient-to-r from-red-600 to-blue-600 bg-clip-text text-transparent">
            Why Choose VU Legal AID?
          </h2>
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            {[
              {
                icon: Shield,
                title: '100% Confidential',
                description: 'Your queries are processed anonymously. We never store personal information.',
                color: 'red',
              },
              {
                icon: Globe,
                title: 'Multilingual Support',
                description: 'Ask questions in Hindi, English, Tamil, Telugu, Bengali, or Marathi.',
                color: 'blue',
              },
              {
                icon: CheckCircle2,
                title: 'Verified Legal Sources',
                description: 'Powered by verified legal databases and Indian legal documents.',
                color: 'cyan',
              },
            ].map((feature, idx) => {
              const Icon = feature.icon
              return (
                <div
                  key={idx}
                  className="bg-white dark:bg-[#161B22] rounded-2xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm hover:shadow-lg transition-all duration-300"
                >
                  <div className={`w-12 h-12 rounded-xl bg-${feature.color}-100 dark:bg-${feature.color}-900/20 flex items-center justify-center mb-4`}>
                    <Icon className={`w-6 h-6 text-${feature.color}-600 dark:text-${feature.color}-400`} />
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    {feature.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-white/50 dark:bg-[#161B22]/50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4 bg-gradient-to-r from-red-600 to-blue-600 bg-clip-text text-transparent">
            Frequently Asked Questions
          </h2>
          <div className="mt-12 space-y-4">
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                className="bg-white dark:bg-[#161B22] rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full px-6 py-4 flex justify-between items-center text-left hover:bg-gray-50 dark:hover:bg-[#0D1117] transition-colors"
                >
                  <span className="font-semibold text-gray-900 dark:text-gray-100">
                    {faq.question}
                  </span>
                  <ChevronDown
                    className={`w-5 h-5 text-gray-400 transition-transform ${
                      openFaq === idx ? 'transform rotate-180' : ''
                    }`}
                  />
                </button>
                {openFaq === idx && (
                  <div className="px-6 py-4 text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-800">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Lawyer Disclaimer */}
      <section className="py-12 bg-gradient-to-r from-red-50 to-blue-50 dark:from-red-900/10 dark:to-blue-900/10 border-y border-gray-200 dark:border-gray-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-3">
            <Shield className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
            <span className="font-semibold text-gray-900 dark:text-gray-100">Transparency Notice</span>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            VU Legal AID provides AI-powered preventive legal guidance and information only. This service does not constitute legal representation, 
            legal advice, or attorney-client relationship. For complex legal matters, please consult a qualified lawyer. 
            All information is provided "as is" without warranty of any kind.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-600 dark:text-gray-400 mb-4 md:mb-0">
              © 2024 VU Legal AID. All rights reserved.
            </div>
            <div className="flex gap-6 text-gray-600 dark:text-gray-400">
              <a href="#" className="hover:text-red-600 dark:hover:text-red-400 transition-colors">
                Privacy
              </a>
              <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                Terms
              </a>
              <a href="#" className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Chatbot */}
      {showChatbot && (
        <Chatbot 
          onClose={() => {
            setShowChatbot(false)
            setSearchQuery('') // Clear search when closing
          }} 
          initialQuery={searchQuery}
        />
      )}
      
      {/* Floating Chat Button - Glassmorphism */}
      {!showChatbot && (
        <button
          onClick={() => setShowChatbot(true)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-red-500 to-blue-500 text-white rounded-full shadow-2xl hover:from-red-600 hover:to-blue-600 transition-all flex items-center justify-center z-50 backdrop-blur-md border border-white/20 animate-pulse-slow"
          title="Open Chat"
          style={{
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(255, 255, 255, 0.1)',
          }}
        >
          <MessageCircle className="w-8 h-8" />
        </button>
      )}

      <style jsx>{`
        @keyframes pulse-slow {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.9;
            transform: scale(1.05);
          }
        }
        .animate-pulse-slow {
          animation: pulse-slow 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
}
