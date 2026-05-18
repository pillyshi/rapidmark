import { ref } from 'vue'

export interface PopoverData {
  start: number
  end: number
  quote: string
  x: number
  y: number
}

const popover = ref<PopoverData | null>(null)

export function usePopover() {
  const setPopover = (p: PopoverData | null) => { popover.value = p }
  const clearPopover = () => { popover.value = null }
  return { popover, setPopover, clearPopover }
}
