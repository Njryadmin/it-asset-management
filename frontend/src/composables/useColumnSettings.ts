import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

export interface ColumnOption {
  key: string
  label: string
  visible: boolean
  fixed?: boolean
}

export function useColumnSettings(storageKey: string, defaultColumns: ColumnOption[]) {
  const columns = ref<ColumnOption[]>([])
  const draggingIndex = ref<number | null>(null)

  // Load from localStorage
  function loadSettings() {
    try {
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        const parsed: ColumnOption[] = JSON.parse(saved)
        // Merge with defaults to handle new columns
        const savedMap = new Map<string, ColumnOption>(parsed.map((c) => [c.key, c]))
        columns.value = defaultColumns.map(col => ({
          ...col,
          visible: savedMap.get(col.key)?.visible ?? col.visible
        }))
        // Restore order from saved
        const ordered = parsed
          .filter((c) => columns.value.some(cc => cc.key === c.key))
          .map((c) => ({
            ...columns.value.find(cc => cc.key === c.key)!,
            visible: c.visible
          }))
        // Add any new columns not in saved
        const newCols = columns.value.filter(c => !parsed.some((s) => s.key === c.key))
        columns.value = [...ordered, ...newCols]
      } else {
        columns.value = [...defaultColumns]
      }
    } catch {
      columns.value = [...defaultColumns]
    }
  }

  // Save to localStorage
  function saveSettings() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(columns.value))
    } catch {
      // Storage full or unavailable
    }
  }

  // Watch for changes and save
  watch(columns, saveSettings, { deep: true })

  // Drag handlers
  function onDragStart(index: number) {
    draggingIndex.value = index
  }

  function onDragOver(event: DragEvent, index: number) {
    event.preventDefault()
    if (draggingIndex.value === null || draggingIndex.value === index) return
    
    const draggedCol = columns.value[draggingIndex.value]
    const targetCol = columns.value[index]
    
    // Don't allow dragging fixed columns
    if (draggedCol.fixed || targetCol.fixed) return
    
    const newColumns = [...columns.value]
    newColumns.splice(draggingIndex.value, 1)
    newColumns.splice(index, 0, draggedCol)
    columns.value = newColumns
    draggingIndex.value = index
  }

  function onDragEnd() {
    draggingIndex.value = null
  }

  // Toggle column visibility with validation
  function toggleColumn(index: number) {
    const col = columns.value[index]
    if (!col.visible) {
      // Check if this is the last visible non-fixed column
      const visibleCount = columns.value.filter(c => c.visible && !c.fixed).length
      if (visibleCount <= 1) {
        ElMessage.warning('至少保留一列可见')
        return
      }
    }
    col.visible = !col.visible
  }

  // Check if at least one non-fixed column is visible
  function canHide(index: number): boolean {
    if (columns.value[index].fixed) return false
    const visibleCount = columns.value.filter(c => c.visible && !c.fixed).length
    return visibleCount > 1 || !columns.value[index].visible
  }

  // Get visible columns in order
  function getVisibleColumns() {
    return columns.value.filter(c => c.visible)
  }

  // Reset to defaults
  function resetToDefaults() {
    columns.value = [...defaultColumns]
    ElMessage.success('已重置为默认设置')
  }

  // Initialize
  loadSettings()

  return {
    columns,
    draggingIndex,
    onDragStart,
    onDragOver,
    onDragEnd,
    toggleColumn,
    canHide,
    getVisibleColumns,
    resetToDefaults,
    loadSettings
  }
}
