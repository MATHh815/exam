<template>
  <div class="starry-background">
    <!-- 深空背景 -->
    <div class="deep-space"></div>
    
    <!-- 流动星云层 -->
    <div class="nebula-layer">
      <div class="nebula nebula-1"></div>
      <div class="nebula nebula-2"></div>
      <div class="nebula nebula-3"></div>
    </div>
    
    <!-- 星星层 -->
    <div class="stars-layer">
      <div class="stars stars-small"></div>
      <div class="stars stars-medium"></div>
      <div class="stars stars-large"></div>
    </div>
    
    <!-- 流动粒子 -->
    <div class="particles-layer">
      <div class="particle particle-1"></div>
      <div class="particle particle-2"></div>
      <div class="particle particle-3"></div>
      <div class="particle particle-4"></div>
      <div class="particle particle-5"></div>
      <div class="particle particle-6"></div>
    </div>
    
    <!-- 流星 -->
    <div class="shooting-stars">
      <div class="shooting-star"></div>
      <div class="shooting-star"></div>
      <div class="shooting-star"></div>
      <div class="shooting-star"></div>
    </div>
    
    <!-- 光晕效果 -->
    <div class="glow-layer">
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
    </div>
  </div>
</template>

<script setup>
// 纯CSS实现的动态星空背景
</script>

<style scoped>
.starry-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: -1;
}

/* 深空背景 - 缓慢变化的渐变 */
.deep-space {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    125deg,
    #0a0a1a 0%,
    #0d1033 15%,
    #1a0a2e 30%,
    #0f1a3d 45%,
    #16213e 60%,
    #1a0a2e 75%,
    #0c1445 90%,
    #0a0a1a 100%
  );
  background-size: 400% 400%;
  animation: deep-space-flow 30s ease-in-out infinite;
}

@keyframes deep-space-flow {
  0% { background-position: 0% 50%; }
  25% { background-position: 50% 100%; }
  50% { background-position: 100% 50%; }
  75% { background-position: 50% 0%; }
  100% { background-position: 0% 50%; }
}

/* 星云层 */
.nebula-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.nebula {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.4;
}

.nebula-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.5) 0%, transparent 70%);
  top: -10%;
  left: -10%;
  animation: nebula-drift-1 40s ease-in-out infinite;
}

.nebula-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(118, 75, 162, 0.4) 0%, transparent 70%);
  bottom: -15%;
  right: -10%;
  animation: nebula-drift-2 35s ease-in-out infinite;
}

.nebula-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.3) 0%, transparent 70%);
  top: 40%;
  left: 30%;
  animation: nebula-drift-3 45s ease-in-out infinite;
}

@keyframes nebula-drift-1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(100px, 50px) scale(1.1); }
  50% { transform: translate(50px, 100px) scale(0.9); }
  75% { transform: translate(-50px, 50px) scale(1.05); }
}

@keyframes nebula-drift-2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-80px, -60px) scale(1.15); }
  66% { transform: translate(-40px, 40px) scale(0.95); }
}

@keyframes nebula-drift-3 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(60px, -40px) rotate(180deg); }
}

/* 星星层 */
.stars-layer {
  position: absolute;
  width: 100%;
  height: 100%;
}

.stars {
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
}

/* 小星星 - 快速移动 */
.stars-small {
  background-image: 
    radial-gradient(1px 1px at 100px 50px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 200px 150px, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(1px 1px at 300px 250px, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1px 1px at 400px 100px, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 500px 300px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 600px 200px, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(1px 1px at 700px 350px, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1px 1px at 800px 50px, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 150px 400px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 250px 500px, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(1px 1px at 350px 450px, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1px 1px at 450px 550px, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 550px 480px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 650px 520px, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(1px 1px at 750px 600px, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1px 1px at 850px 420px, rgba(255, 255, 255, 0.5), transparent);
  animation: stars-flow 80s linear infinite, twinkle-small 3s ease-in-out infinite;
}

/* 中等星星 */
.stars-medium {
  background-image: 
    radial-gradient(2px 2px at 120px 80px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(2px 2px at 280px 180px, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(2px 2px at 420px 320px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(2px 2px at 580px 120px, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(2px 2px at 720px 280px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(2px 2px at 180px 450px, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(2px 2px at 380px 520px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(2px 2px at 620px 480px, rgba(255, 255, 255, 0.6), transparent);
  animation: stars-flow 120s linear infinite reverse, twinkle-medium 4s ease-in-out infinite;
}

/* 大星星 - 慢速移动 */
.stars-large {
  background-image: 
    radial-gradient(3px 3px at 200px 150px, rgba(255, 255, 255, 1), transparent),
    radial-gradient(3px 3px at 500px 250px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(3px 3px at 750px 400px, rgba(255, 255, 255, 1), transparent),
    radial-gradient(3px 3px at 350px 500px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(4px 4px at 600px 100px, rgba(255, 255, 255, 1), transparent);
  animation: stars-flow 150s linear infinite, twinkle-large 5s ease-in-out infinite;
}

@keyframes stars-flow {
  0% { transform: translateX(0) translateY(0); }
  100% { transform: translateX(-50%) translateY(-50%); }
}

@keyframes twinkle-small {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

@keyframes twinkle-medium {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes twinkle-large {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

/* 流动粒子 */
.particles-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.particle-1 {
  width: 4px;
  height: 4px;
  top: 20%;
  animation: particle-float-1 25s linear infinite;
}

.particle-2 {
  width: 3px;
  height: 3px;
  top: 40%;
  animation: particle-float-2 30s linear infinite;
}

.particle-3 {
  width: 5px;
  height: 5px;
  top: 60%;
  animation: particle-float-3 20s linear infinite;
}

.particle-4 {
  width: 3px;
  height: 3px;
  top: 80%;
  animation: particle-float-4 35s linear infinite;
}

.particle-5 {
  width: 4px;
  height: 4px;
  top: 30%;
  animation: particle-float-5 28s linear infinite;
}

.particle-6 {
  width: 3px;
  height: 3px;
  top: 70%;
  animation: particle-float-6 32s linear infinite;
}

@keyframes particle-float-1 {
  0% { left: -5%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { left: 105%; opacity: 0; transform: translateY(100px); }
}

@keyframes particle-float-2 {
  0% { left: 105%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { left: -5%; opacity: 0; transform: translateY(-80px); }
}

@keyframes particle-float-3 {
  0% { left: -5%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { left: 105%; opacity: 0; transform: translateY(-120px); }
}

@keyframes particle-float-4 {
  0% { left: 105%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { left: -5%; opacity: 0; transform: translateY(60px); }
}

@keyframes particle-float-5 {
  0% { left: -5%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { left: 105%; opacity: 0; transform: translateY(150px); }
}

@keyframes particle-float-6 {
  0% { left: 105%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { left: -5%; opacity: 0; transform: translateY(-100px); }
}

/* 流星 */
.shooting-stars {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.shooting-star {
  position: absolute;
  width: 150px;
  height: 2px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.8) 50%, rgba(255, 255, 255, 0) 100%);
  border-radius: 50%;
  opacity: 0;
  transform: rotate(-45deg);
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.8));
}

.shooting-star:nth-child(1) {
  top: 5%;
  left: 70%;
  animation: shooting 6s ease-in-out infinite;
}

.shooting-star:nth-child(2) {
  top: 25%;
  left: 85%;
  animation: shooting 9s ease-in-out infinite 3s;
}

.shooting-star:nth-child(3) {
  top: 45%;
  left: 75%;
  animation: shooting 7s ease-in-out infinite 5s;
}

.shooting-star:nth-child(4) {
  top: 15%;
  left: 60%;
  animation: shooting 11s ease-in-out infinite 8s;
}

@keyframes shooting {
  0% {
    opacity: 0;
    transform: translateX(0) translateY(0) rotate(-45deg);
  }
  2% {
    opacity: 1;
  }
  10% {
    opacity: 0;
    transform: translateX(-400px) translateY(400px) rotate(-45deg);
  }
  100% {
    opacity: 0;
    transform: translateX(-400px) translateY(400px) rotate(-45deg);
  }
}

/* 光晕效果 */
.glow-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.glow-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.2) 0%, transparent 70%);
  top: 10%;
  right: 10%;
  animation: glow-pulse-1 8s ease-in-out infinite;
}

.glow-2 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(118, 75, 162, 0.15) 0%, transparent 70%);
  bottom: 20%;
  left: 15%;
  animation: glow-pulse-2 10s ease-in-out infinite;
}

@keyframes glow-pulse-1 {
  0%, 100% { 
    opacity: 0.5; 
    transform: scale(1);
  }
  50% { 
    opacity: 0.8; 
    transform: scale(1.2);
  }
}

@keyframes glow-pulse-2 {
  0%, 100% { 
    opacity: 0.4; 
    transform: scale(1);
  }
  50% { 
    opacity: 0.7; 
    transform: scale(1.3);
  }
}

/* 性能优化 - 减少重绘 */
.nebula, .stars, .particle, .shooting-star, .glow {
  will-change: transform, opacity;
}
</style>
