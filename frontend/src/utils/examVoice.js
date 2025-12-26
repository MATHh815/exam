/**
 * 考试语音提醒工具
 * 
 * 使用 Web Speech API 实现语音播报功能
 * 模拟真实考试场景的语音提醒
 */

class ExamVoice {
  constructor() {
    this.synth = window.speechSynthesis
    this.enabled = true
    this.speaking = false
    this.voiceReady = false
    this.voices = []
    
    // 初始化语音
    this.initVoices()
  }
  
  /**
   * 初始化语音列表
   */
  initVoices() {
    // 获取可用语音
    const loadVoices = () => {
      this.voices = this.synth.getVoices()
      this.voiceReady = this.voices.length > 0
    }
    
    loadVoices()
    
    // 某些浏览器需要等待 voiceschanged 事件
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = loadVoices
    }
  }
  
  /**
   * 获取中文语音
   */
  getChineseVoice() {
    // 优先选择中文语音
    const chineseVoice = this.voices.find(voice => 
      voice.lang.includes('zh') || 
      voice.lang.includes('CN') ||
      voice.name.includes('Chinese') ||
      voice.name.includes('中文')
    )
    
    return chineseVoice || this.voices[0]
  }
  
  /**
   * 播放语音
   * @param {string} text - 要播放的文本
   * @param {Object} options - 配置选项
   */
  speak(text, options = {}) {
    if (!this.enabled || !this.synth) {
      console.warn('[ExamVoice] 语音功能未启用或不支持')
      return Promise.resolve()
    }
    
    return new Promise((resolve, reject) => {
      // 取消之前的语音
      this.synth.cancel()
      
      const utterance = new SpeechSynthesisUtterance(text)
      
      // 设置语音参数
      utterance.voice = this.getChineseVoice()
      utterance.lang = 'zh-CN'
      utterance.rate = options.rate || 0.9  // 语速
      utterance.pitch = options.pitch || 1  // 音调
      utterance.volume = options.volume || 1  // 音量
      
      utterance.onstart = () => {
        this.speaking = true
        console.log('[ExamVoice] 开始播放:', text)
      }
      
      utterance.onend = () => {
        this.speaking = false
        console.log('[ExamVoice] 播放完成')
        resolve()
      }
      
      utterance.onerror = (event) => {
        this.speaking = false
        console.error('[ExamVoice] 播放错误:', event.error)
        reject(event.error)
      }
      
      this.synth.speak(utterance)
    })
  }
  
  /**
   * 停止播放
   */
  stop() {
    if (this.synth) {
      this.synth.cancel()
      this.speaking = false
    }
  }
  
  /**
   * 启用/禁用语音
   */
  setEnabled(enabled) {
    this.enabled = enabled
    if (!enabled) {
      this.stop()
    }
  }
  
  /**
   * 检查是否支持语音
   */
  isSupported() {
    return 'speechSynthesis' in window
  }
  
  // ========== 预设语音提醒 ==========
  
  /**
   * 考试开始提醒
   */
  announceExamStart() {
    return this.speak('各位考生请注意，考试现在开始，请认真答题。', { rate: 0.85 })
  }
  
  /**
   * 15分钟提醒
   */
  announce15Minutes() {
    return this.speak('各位考生请注意，距离考试结束还有十五分钟，请考生注意把握时间。', { rate: 0.85 })
  }
  
  /**
   * 10分钟提醒
   */
  announce10Minutes() {
    return this.speak('各位考生请注意，距离考试结束还有十分钟，请考生抓紧时间答题。', { rate: 0.85 })
  }
  
  /**
   * 5分钟提醒
   */
  announce5Minutes() {
    return this.speak('各位考生请注意，距离考试结束还有五分钟，请考生注意检查答题卡填涂情况。', { rate: 0.85 })
  }
  
  /**
   * 1分钟提醒
   */
  announce1Minute() {
    return this.speak('各位考生请注意，距离考试结束还有一分钟，请停止答题，准备交卷。', { rate: 0.85 })
  }
  
  /**
   * 考试结束提醒
   */
  announceExamEnd() {
    return this.speak('考试时间到，请考生停止答题，系统将自动提交试卷。', { rate: 0.85 })
  }
}

// 创建单例实例
const examVoice = new ExamVoice()

export default examVoice
export { ExamVoice }
