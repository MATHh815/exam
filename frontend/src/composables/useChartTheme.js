/**
 * ECharts 深色主题配置
 */
export function useChartTheme() {
  const darkTheme = {
    backgroundColor: 'transparent',
    textStyle: {
      color: 'rgba(255, 255, 255, 0.8)',
      fontSize: 12,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    title: {
      textStyle: {
        color: 'rgba(255, 255, 255, 0.9)',
        fontSize: 16,
        fontWeight: 600
      },
      subtextStyle: {
        color: 'rgba(255, 255, 255, 0.6)',
        fontSize: 12
      }
    },
    legend: {
      textStyle: {
        color: 'rgba(255, 255, 255, 0.7)'
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      borderWidth: 1,
      textStyle: {
        color: '#fff'
      }
    },
    grid: {
      borderColor: 'rgba(255, 255, 255, 0.1)'
    },
    categoryAxis: {
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      },
      axisTick: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.6)'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)'
        }
      }
    },
    valueAxis: {
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      },
      axisTick: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.6)'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)'
        }
      }
    },
    color: [
      '#667eea',
      '#764ba2',
      '#f093fb',
      '#4facfe',
      '#00f2fe',
      '#43e97b',
      '#38f9d7',
      '#fa709a',
      '#fee140'
    ]
  }

  const gradientColors = {
    primary: {
      type: 'linear',
      x: 0,
      y: 0,
      x2: 0,
      y2: 1,
      colorStops: [
        { offset: 0, color: 'rgba(102, 126, 234, 0.8)' },
        { offset: 1, color: 'rgba(118, 75, 162, 0.3)' }
      ]
    },
    success: {
      type: 'linear',
      x: 0,
      y: 0,
      x2: 0,
      y2: 1,
      colorStops: [
        { offset: 0, color: 'rgba(16, 185, 129, 0.8)' },
        { offset: 1, color: 'rgba(5, 150, 105, 0.3)' }
      ]
    },
    warning: {
      type: 'linear',
      x: 0,
      y: 0,
      x2: 0,
      y2: 1,
      colorStops: [
        { offset: 0, color: 'rgba(245, 158, 11, 0.8)' },
        { offset: 1, color: 'rgba(217, 119, 6, 0.3)' }
      ]
    }
  }

  return {
    darkTheme,
    gradientColors
  }
}
