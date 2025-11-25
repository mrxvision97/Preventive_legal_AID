/**
 * Cloud Connection Manager
 * Handles switching between cloud and local backend
 */

const CLOUD_API_URL = import.meta.env.VITE_API_URL || 'https://your-cloud-backend.com';
const FALLBACK_API_URL = import.meta.env.VITE_FALLBACK_API_URL || 'http://localhost:8000';
const CONNECTION_TIMEOUT = 3000; // 3 seconds

let currentApiUrl = CLOUD_API_URL;
let isCloudAvailable = false;
let lastCheckTime = 0;
const CHECK_INTERVAL = 60000; // Check every minute

/**
 * Check if cloud backend is available
 */
export async function checkCloudConnection(): Promise<boolean> {
  const now = Date.now();
  
  // Use cached result if checked recently
  if (now - lastCheckTime < CHECK_INTERVAL && lastCheckTime > 0) {
    return isCloudAvailable;
  }
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT);
    
    const response = await fetch(`${CLOUD_API_URL}/health`, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      },
    });
    
    clearTimeout(timeoutId);
    isCloudAvailable = response.ok;
    lastCheckTime = now;
    
    if (isCloudAvailable) {
      currentApiUrl = CLOUD_API_URL;
      console.log('✅ Cloud backend is available');
    } else {
      console.warn('⚠️ Cloud backend returned non-OK status');
    }
    
    return isCloudAvailable;
  } catch (error) {
    isCloudAvailable = false;
    lastCheckTime = now;
    console.warn('⚠️ Cloud backend unavailable, using local fallback:', error);
    return false;
  }
}

/**
 * Get current API URL
 */
export function getApiUrl(): string {
  return currentApiUrl;
}

/**
 * Switch to fallback (local) backend
 */
export function switchToFallback(): void {
  currentApiUrl = FALLBACK_API_URL;
  isCloudAvailable = false;
  console.log('🔄 Switched to local backend (offline mode)');
}

/**
 * Switch to cloud backend
 */
export function switchToCloud(): void {
  currentApiUrl = CLOUD_API_URL;
  console.log('☁️ Switched to cloud backend');
}

/**
 * Initialize connection manager
 * Auto-detects best backend on startup
 */
export async function initializeConnection(): Promise<void> {
  console.log('🔍 Checking backend availability...');
  
  const cloudAvailable = await checkCloudConnection();
  
  if (!cloudAvailable) {
    switchToFallback();
    console.log('📡 Using local backend (offline mode)');
  } else {
    console.log('☁️ Using cloud backend');
  }
  
  // Periodically check cloud availability
  setInterval(async () => {
    if (currentApiUrl === FALLBACK_API_URL) {
      // Try to reconnect to cloud
      const available = await checkCloudConnection();
      if (available) {
        switchToCloud();
      }
    }
  }, CHECK_INTERVAL);
}

/**
 * Make API request with automatic fallback
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${currentApiUrl}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });
    
    if (response.ok) {
      return await response.json();
    }
    
    // If cloud fails and we're using cloud, try fallback
    if (currentApiUrl === CLOUD_API_URL && response.status >= 500) {
      console.warn('Cloud backend error, switching to fallback...');
      switchToFallback();
      
      // Retry with fallback
      const fallbackResponse = await fetch(`${FALLBACK_API_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      
      if (fallbackResponse.ok) {
        return await fallbackResponse.json();
      }
    }
    
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  } catch (error) {
    // If using cloud and request fails, try fallback
    if (currentApiUrl === CLOUD_API_URL && error instanceof Error) {
      console.warn('Request failed, trying fallback...', error.message);
      switchToFallback();
      
      try {
        const fallbackResponse = await fetch(`${FALLBACK_API_URL}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });
        
        if (fallbackResponse.ok) {
          return await fallbackResponse.json();
        }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
    }
    
    throw error;
  }
}

/**
 * Get connection status
 */
export function getConnectionStatus(): {
  isCloudAvailable: boolean;
  currentUrl: string;
  isOnline: boolean;
} {
  return {
    isCloudAvailable,
    currentUrl: currentApiUrl,
    isOnline: currentApiUrl === CLOUD_API_URL,
  };
}

