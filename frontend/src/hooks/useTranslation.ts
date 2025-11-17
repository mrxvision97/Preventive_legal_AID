import { useAuthStore } from '../store/authStore'
import { getTranslation, Language } from '../lib/translations'

export function useTranslation() {
  const { user } = useAuthStore()
  const language = (user?.language_preference as Language) || 'en'

  const t = (key: string) => {
    return getTranslation(key, language)
  }

  return { t, language }
}

