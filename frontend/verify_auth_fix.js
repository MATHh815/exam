/**
 * 认证修复验证脚本
 * 
 * 这个脚本会检查所有修改是否正确应用
 * 运行: node verify_auth_fix.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 开始验证认证修复...\n');

let allPassed = true;

// 检查项
const checks = [
  {
    name: 'Login.vue - 添加延迟',
    file: 'src/views/Login.vue',
    pattern: /await new Promise\(resolve => setTimeout\(resolve, 100\)\)/,
    description: '登录后添加100ms延迟确保token保存'
  },
  {
    name: 'user.js - 同步保存',
    file: 'src/stores/user.js',
    pattern: /localStorage\.setItem\('access_token', access_token\)/,
    description: '批量同步写入localStorage'
  },
  {
    name: 'user.js - 日志输出',
    file: 'src/stores/user.js',
    pattern: /console\.log\('登录成功，token和用户信息已保存'\)/,
    description: '添加成功日志'
  },
  {
    name: 'request.js - 请求日志',
    file: 'src/utils/request.js',
    pattern: /console\.log\('请求携带token:', config\.url\)/,
    description: '请求拦截器添加日志'
  },
  {
    name: 'request.js - 错误详情',
    file: 'src/utils/request.js',
    pattern: /console\.error\('错误详情:'/,
    description: '响应拦截器添加详细错误日志'
  },
  {
    name: 'router/index.js - 路由日志',
    file: 'src/router/index.js',
    pattern: /console\.log\('路由守卫检查token:'/,
    description: '路由守卫添加调试日志'
  },
  {
    name: 'router/index.js - 后台获取',
    file: 'src/router/index.js',
    pattern: /userStore\.fetchUserInfo\(\)\.catch/,
    description: '路由守卫改为后台异步获取用户信息'
  }
];

// 执行检查
checks.forEach((check, index) => {
  const filePath = path.join(__dirname, check.file);
  
  try {
    if (!fs.existsSync(filePath)) {
      console.log(`❌ ${index + 1}. ${check.name}`);
      console.log(`   文件不存在: ${check.file}\n`);
      allPassed = false;
      return;
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    
    if (check.pattern.test(content)) {
      console.log(`✅ ${index + 1}. ${check.name}`);
      console.log(`   ${check.description}\n`);
    } else {
      console.log(`❌ ${index + 1}. ${check.name}`);
      console.log(`   ${check.description}`);
      console.log(`   未找到预期的代码模式\n`);
      allPassed = false;
    }
  } catch (error) {
    console.log(`❌ ${index + 1}. ${check.name}`);
    console.log(`   错误: ${error.message}\n`);
    allPassed = false;
  }
});

// 检查修复指南文档
const guidePath = path.join(__dirname, 'AUTH_FIX_GUIDE.md');
if (fs.existsSync(guidePath)) {
  console.log(`✅ ${checks.length + 1}. AUTH_FIX_GUIDE.md`);
  console.log(`   修复指南文档已创建\n`);
} else {
  console.log(`❌ ${checks.length + 1}. AUTH_FIX_GUIDE.md`);
  console.log(`   修复指南文档不存在\n`);
  allPassed = false;
}

// 总结
console.log('='.repeat(50));
if (allPassed) {
  console.log('✅ 所有检查通过！认证修复已正确应用。');
  console.log('\n📝 下一步:');
  console.log('1. 提交代码到Git仓库');
  console.log('2. 在你的电脑上拉取最新代码');
  console.log('3. 按照 AUTH_FIX_GUIDE.md 进行测试');
  process.exit(0);
} else {
  console.log('❌ 部分检查失败，请检查上述错误。');
  process.exit(1);
}
