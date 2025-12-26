<template>
  <div class="statistics-chart">
    <v-chart 
      :option="chartOption" 
      :style="{ height: height, width: '100%' }"
      autoresize
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

// 注册必要的组件
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const props = defineProps({
  // 图表类型：bar, line, pie
  type: {
    type: String,
    default: 'bar',
    validator: (value) => ['bar', 'line', 'pie'].includes(value)
  },
  // 图表标题
  title: {
    type: String,
    default: ''
  },
  // 图表数据
  data: {
    type: Object,
    required: true
  },
  // 图表高度
  height: {
    type: String,
    default: '400px'
  },
  // 是否显示图例
  showLegend: {
    type: Boolean,
    default: true
  }
})

// 计算图表配置
const chartOption = computed(() => {
  const baseOption = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: props.type === 'pie' ? 'item' : 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      show: props.showLegend,
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    }
  }

  // 根据图表类型生成配置
  if (props.type === 'bar') {
    return {
      ...baseOption,
      xAxis: {
        type: 'category',
        data: props.data.xAxis || [],
        axisLabel: {
          rotate: 45,
          interval: 0
        }
      },
      yAxis: {
        type: 'value'
      },
      series: props.data.series || []
    }
  } else if (props.type === 'line') {
    return {
      ...baseOption,
      xAxis: {
        type: 'category',
        data: props.data.xAxis || [],
        boundaryGap: false
      },
      yAxis: {
        type: 'value'
      },
      series: props.data.series || []
    }
  } else if (props.type === 'pie') {
    return {
      ...baseOption,
      series: [
        {
          type: 'pie',
          radius: '60%',
          data: props.data.data || [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            formatter: '{b}: {c} ({d}%)'
          }
        }
      ]
    }
  }

  return baseOption
})
</script>

<style scoped>
.statistics-chart {
  width: 100%;
}
</style>
