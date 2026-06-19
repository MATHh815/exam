<template>
  <div class="progress-ring-container">
    <v-chart 
      class="chart" 
      :option="chartOption" 
      :autoresize="true"
      @click="handleClick"
    />
    <div class="ring-center-text">
      <div class="center-value">{{ displayValue }}%</div>
      <div class="center-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { useChartTheme } from '../../composables/useChartTheme'
import { useCountUp } from '../../composables/useCountUp'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const props = defineProps({
  value: {
    type: Number,
    default: 0
  },
  total: {
    type: Number,
    default: 100
  },
  label: {
    type: String,
    default: '完成度'
  },
  color: {
    type: Array,
    default: () => ['#667eea', '#764ba2']
  }
})

const emit = defineEmits(['click'])

const { darkTheme } = useChartTheme()

const percentage = computed(() => {
  return props.total > 0 ? Math.min((props.value / props.total) * 100, 100) : 0
})

const { displayValue } = useCountUp(percentage, { decimals: 1 })

const chartOption = computed(() => ({
  ...darkTheme,
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}%'
  },
  series: [
    {
      type: 'pie',
      radius: ['70%', '90%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      label: {
        show: false
      },
      labelLine: {
        show: false
      },
      data: [
        {
          value: percentage.value,
          name: '已完成',
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: props.color[0] },
                { offset: 1, color: props.color[1] }
              ]
            }
          }
        },
        {
          value: 100 - percentage.value,
          name: '未完成',
          itemStyle: {
            color: 'rgba(255, 255, 255, 0.05)'
          }
        }
      ],
      emphasis: {
        scale: false
      },
      animation: true,
      animationDuration: 1500,
      animationEasing: 'cubicOut'
    }
  ]
}))

function handleClick() {
  emit('click')
}
</script>

<style scoped>
.progress-ring-container {
  position: relative;
  width: 100%;
  height: 200px;
}

.chart {
  width: 100%;
  height: 100%;
}

.ring-center-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.center-value {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
}

.center-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}
</style>
