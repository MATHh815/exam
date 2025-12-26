<template>
  <div class="trend-line">
    <v-chart 
      :option="lineOption" 
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
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components'

// 注册必要的组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
])

const props = defineProps({
  // 图表标题
  title: {
    type: String,
    default: '学习趋势'
  },
  // 趋势数据
  trendData: {
    type: Array,
    required: true,
    default: () => []
  },
  // 图表高度
  height: {
    type: String,
    default: '400px'
  },
  // 是否显示数据缩放
  showDataZoom: {
    type: Boolean,
    default: false
  }
})

// 计算折线图配置
const lineOption = computed(() => {
  // 提取日期
  const dates = props.trendData.map(item => item.date)
  
  // 提取各项数据
  const practiceCount = props.trendData.map(item => item.practice_count || 0)
  const correctCount = props.trendData.map(item => item.correct_count || 0)
  const accuracy = props.trendData.map(item => item.accuracy || 0)
  const studyDuration = props.trendData.map(item => item.study_duration || 0)
  const examCount = props.trendData.map(item => item.exam_count || 0)

  const option = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params) => {
        let result = `${params[0].axisValue}<br/>`
        params.forEach(param => {
          result += `${param.marker} ${param.seriesName}: ${param.value}`
          if (param.seriesName === '正确率') {
            result += '%'
          } else if (param.seriesName === '学习时长') {
            result += '分钟'
          } else {
            result += '题'
          }
          result += '<br/>'
        })
        return result
      }
    },
    legend: {
      bottom: 10,
      data: ['练习题数', '正确题数', '正确率', '学习时长', '考试次数']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: props.showDataZoom ? '15%' : '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '题数/次数',
        position: 'left',
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: '正确率(%)/时长(分钟)',
        position: 'right',
        axisLabel: {
          formatter: '{value}'
        }
      }
    ],
    series: [
      {
        name: '练习题数',
        type: 'line',
        data: practiceCount,
        smooth: true,
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: 'rgba(64, 158, 255, 0.1)'
        }
      },
      {
        name: '正确题数',
        type: 'line',
        data: correctCount,
        smooth: true,
        itemStyle: {
          color: '#67C23A'
        },
        areaStyle: {
          color: 'rgba(103, 194, 58, 0.1)'
        }
      },
      {
        name: '正确率',
        type: 'line',
        yAxisIndex: 1,
        data: accuracy,
        smooth: true,
        itemStyle: {
          color: '#E6A23C'
        }
      },
      {
        name: '学习时长',
        type: 'line',
        yAxisIndex: 1,
        data: studyDuration,
        smooth: true,
        itemStyle: {
          color: '#F56C6C'
        }
      },
      {
        name: '考试次数',
        type: 'line',
        data: examCount,
        smooth: true,
        itemStyle: {
          color: '#909399'
        }
      }
    ]
  }

  // 如果需要数据缩放
  if (props.showDataZoom) {
    option.dataZoom = [
      {
        type: 'slider',
        start: 0,
        end: 100
      }
    ]
  }

  return option
})
</script>

<style scoped>
.trend-line {
  width: 100%;
}
</style>
