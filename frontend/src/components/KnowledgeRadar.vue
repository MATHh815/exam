<template>
  <div class="knowledge-radar">
    <v-chart 
      :option="radarOption" 
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
import { RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  RadarComponent
} from 'echarts/components'

// 注册必要的组件
use([
  CanvasRenderer,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  RadarComponent
])

const props = defineProps({
  // 图表标题
  title: {
    type: String,
    default: '知识点掌握情况'
  },
  // 知识点数据
  knowledgePoints: {
    type: Array,
    required: true,
    default: () => []
  },
  // 图表高度
  height: {
    type: String,
    default: '500px'
  }
})

// 计算雷达图配置
const radarOption = computed(() => {
  // 从知识点数据中提取指标
  const indicators = props.knowledgePoints.map(point => ({
    name: `${point.subject}-${point.chapter}`,
    max: 100
  }))

  // 提取正确率数据
  const accuracyData = props.knowledgePoints.map(point => 
    point.accuracy || 0
  )

  return {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const data = params.data
        let result = `${params.name}<br/>`
        data.value.forEach((val, idx) => {
          const point = props.knowledgePoints[idx]
          result += `${indicators[idx].name}: ${val.toFixed(1)}%<br/>`
          result += `答题数: ${point.total_count}<br/>`
          result += `正确数: ${point.correct_count}<br/>`
        })
        return result
      }
    },
    legend: {
      bottom: 10,
      data: ['正确率']
    },
    radar: {
      indicator: indicators,
      radius: '60%',
      splitNumber: 5,
      name: {
        textStyle: {
          fontSize: 12
        }
      },
      splitArea: {
        areaStyle: {
          color: [
            'rgba(114, 172, 209, 0.1)',
            'rgba(114, 172, 209, 0.2)',
            'rgba(114, 172, 209, 0.3)',
            'rgba(114, 172, 209, 0.4)',
            'rgba(114, 172, 209, 0.5)'
          ]
        }
      }
    },
    series: [
      {
        name: '知识点分析',
        type: 'radar',
        data: [
          {
            value: accuracyData,
            name: '正确率',
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.3)'
            },
            lineStyle: {
              color: '#409EFF',
              width: 2
            },
            itemStyle: {
              color: '#409EFF'
            }
          }
        ]
      }
    ]
  }
})
</script>

<style scoped>
.knowledge-radar {
  width: 100%;
}
</style>
