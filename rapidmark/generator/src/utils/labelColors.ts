export interface LabelColors {
  bg: string
  bgDeep: string
  border: string
  dot: string
  ink: string
}

export function getLabelColors(hue: number, style: 'tinted' | 'underline' = 'tinted'): LabelColors {
  const bg = `oklch(0.93 0.07 ${hue})`
  const bgDeep = `oklch(0.86 0.10 ${hue})`
  const border = `oklch(0.78 0.13 ${hue})`
  const dot = `oklch(0.62 0.16 ${hue})`
  const ink = `oklch(0.32 0.07 ${hue})`
  if (style === 'underline') {
    return { bg: 'transparent', bgDeep: 'transparent', border: dot, dot, ink: 'inherit' }
  }
  return { bg, bgDeep, border, dot, ink }
}

// backward compat
export const getLabelBackgroundColor = (labelId: string, allLabels: { id: string }[]): string => {
  const index = allLabels.findIndex(l => l.id === labelId)
  const n = allLabels.length
  if (index === -1 || n === 0) return 'hsl(0, 0%, 50%)'
  return `hsl(${Math.round((index / n) * 360)}, 70%, 50%)`
}
