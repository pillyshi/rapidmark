export const getLabelBackgroundColor = (
  labelId: string,
  allLabels: { id: string }[]
): string => {
  const index = allLabels.findIndex(l => l.id === labelId)
  const n = allLabels.length
  if (index === -1 || n === 0) return 'hsl(0, 0%, 50%)'
  const hue = (index / n) * 360
  return `hsl(${hue}, 70%, 50%)`
}