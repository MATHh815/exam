<template>
  <div class="accuracy-trend-container">
    <v-chart 
      class="chart" 
      :option="chartOption" 
      :autoresize="true"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { 
  TooltipComponent, 
  GridComponent,
  LegendComponent 
} from 'echarts/components'
import { useChartTheme } from '../../composables/useChartTheme'
import { getTooltipConfig, getGridConfig } from '../../utils/chartConfig'

use([
  CanvasRenderer, 
  LineChart, 
  TooltipComponent, 
  GridComponent,
  LegendComponent
])

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  days: {
    type: Number,
    default: 7
  }
})

const { darkTheme, gradientColors } = useChartTheme()

const dates = computed(() => {
  return props.data.map(item => item.date || item.label)
})

const accuracyData = computed(() => {
  return props.data.map(item => (item.accuracy * 100).toFixed(1))
})

const chartOption = computed(() => ({
  ...darkTheme,
  tooltip: {
    ...getTooltipConfig(),
    formatter: (params) => {
      const data = params[0]
      return `${data.name}<br/>正确率: ${data.value}%`
    }
  },
  grid: getGridConfig({ top: 30, right: 20, bottom: 30, left: 45 }),
  xAxis: {
    type: 'category',
    data: dates.value,
    boundaryGap: false,
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.2)'
      }
    },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.6)',
      fontSize: 11
    },
    axisTick: {
      show: false
    }
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLine: {
      show: false
    },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.6)',
      fontSize: 11,
      formatter: '{value}%'
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.05)'
      }
    }
  },
  series: [
    {
      type: 'line',
      data: accuracyData.value,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 3,
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        }
      },
      itemStyle: {
        color: '#667eea',
        borderColor: '#fff',
        borderWidth: 2
      },
      areaStyle: {
        color: gradientColors.primary
      },
      emphasis: {
        scale: true,
        focus: 'series'
      },
      animation: true,
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    }
  ]
}))
</script>

<style scoped>
.accuracy-trend-container {
  width: 100%;
  height: 250px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
