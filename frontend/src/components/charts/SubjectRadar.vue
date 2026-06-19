<template>
  <div class="subject-radar-container">
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
import { RadarChart } from 'echarts/charts'
import { 
  TooltipComponent, 
  LegendComponent,
  TitleComponent 
} from 'echarts/components'
import { useChartTheme } from '../../composables/useChartTheme'

use([
  CanvasRenderer, 
  RadarChart, 
  TooltipComponent, 
  LegendComponent,
  TitleComponent
])

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  subjects: {
    type: Array,
    default: () => ['行测', '申论', '数学', '英语', '专业课']
  }
})

const { darkTheme } = useChartTheme()

// 构建雷达图指标
const indicators = computed(() => {
  return props.subjects.map(subject => ({
    name: subject,
    max: 100
  }))
})

// 构建雷达图数据
const radarData = computed(() => {
  if (!props.data || props.data.length === 0) {
    // 默认数据
    return [{
      value: props.subjects.map(() => 0),
      name: '掌握度'
    }]
  }
  
  return [{
    value: props.data.map(item => item.value || 0),
    name: '掌握度',
    areaStyle: {
      color: {
        type: 'radial',
        x: 0.5,
        y: 0.5,
        r: 0.5,
        colorStops: [
          { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
          { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
        ]
      }
    }
  }]
})

const chartOption = computed(() => ({
  ...darkTheme,
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    borderColor: 'rgba(255, 255, 255, 0.2)',
    borderWidth: 1,
    textStyle: {
      color: '#fff'
    },
    formatter: (params) => {
      const data = params.data
      let result = `${data.name}<br/>`
      data.value.forEach((val, idx) => {
        result += `${indicators.value[idx].name}: ${val}%<br/>`
      })
      return result
    }
  },
  radar: {
    indicator: indicators.value,
    shape: 'polygon',
    center: ['50%', '50%'],
    radius: '70%',
    splitNumber: 4,
    name: {
      textStyle: {
        color: 'rgba(255, 255, 255, 0.8)',
        fontSize: 12
      }
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    splitArea: {
      show: true,
      areaStyle: {
        color: [
          'rgba(255, 255, 255, 0.02)',
          'rgba(255, 255, 255, 0.04)'
        ]
      }
    },
    axisLine: {
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.2)'
      }
    }
  },
  series: [{
    type: 'radar',
    data: radarData.value,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: {
      width: 2,
      color: '#667eea'
    },
    itemStyle: {
      color: '#667eea',
      borderColor: '#fff',
      borderWidth: 2
    },
    emphasis: {
      lineStyle: {
        width: 3
      },
      itemStyle: {
        borderWidth: 3
      }
    },
    animation: true,
    animationDuration: 1500,
    animationEasing: 'cubicOut'
  }]
}))
</script>

<style scoped>
.subject-radar-container {
  width: 100%;
  height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
