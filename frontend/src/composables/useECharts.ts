import { onMounted, onBeforeUnmount, type Ref } from 'vue'
import * as echarts from 'echarts'

export function useECharts(containerRef: Ref<HTMLElement | null>, options: echarts.EChartsOption) {
  let chart: echarts.ECharts | null = null

  function init() {
    if (!containerRef.value) return
    chart = echarts.init(containerRef.value)
    chart.setOption(options)
  }

  function setOption(opts: echarts.EChartsOption) {
    chart?.setOption(opts)
  }

  function resize() {
    chart?.resize()
  }

  onMounted(() => {
    init()
    window.addEventListener('resize', resize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', resize)
    chart?.dispose()
    chart = null
  })

  return { chart, setOption, resize }
}
