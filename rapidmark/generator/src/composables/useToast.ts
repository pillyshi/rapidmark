import { ref } from 'vue'

const toast = ref<string | null>(null)
const importError = ref<string | null>(null)
let toastTimer: ReturnType<typeof setTimeout> | null = null

export function useToast() {
  const showToast = (msg: string) => {
    toast.value = msg
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { toast.value = null }, 2200)
  }

  const showError = (msg: string) => { importError.value = msg }
  const clearError = () => { importError.value = null }

  return { toast, importError, showToast, showError, clearError }
}
