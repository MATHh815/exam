// 认证调试脚本 - 在浏览器控制台中运行

console.log('=== 认证状态调试 ===');

// 1. 检查当前存储状态
function checkStorage() {
    console.log('\n1. 当前存储状态:');
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const user = localStorage.getItem('user');
    
    console.log('Access Token:', token ? '存在' : '不存在');
    console.log('Refresh Token:', refreshToken ? '存在' : '不存在');
    console.log('User Data:', user ? '存在' : '不存在');
    
    if (user) {
        try {
            const userData = JSON.parse(user);
            console.log('用户信息:', userData);
        } catch (e) {
            console.error('用户信息解析失败:', e);
        }
    }
    
    return { token, refreshToken, user };
}

// 2. 测试登录API
async function testLogin(username = 'admin', password = '123456') {
    console.log('\n2. 测试登录API:');
    console.log(`尝试登录: ${username} / ${password}`);
    
    try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        console.log('响应状态:', response.status);
        const data = await response.json();
        console.log('响应数据:', data);
        
        if (data.success && data.data) {
            // 保存认证数据
            localStorage.setItem('access_token', data.data.access_token);
            localStorage.setItem('refresh_token', data.data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.data.user));
            console.log('认证数据已保存到localStorage');
        }
        
        return data;
    } catch (error) {
        console.error('登录请求失败:', error);
        return null;
    }
}

// 3. 测试Token验证
async function testTokenValidation() {
    console.log('\n3. 测试Token验证:');
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        console.log('没有Token，跳过验证');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/auth/profile', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        console.log('Token验证响应状态:', response.status);
        const data = await response.json();
        console.log('Token验证响应数据:', data);
        
        return data;
    } catch (error) {
        console.error('Token验证失败:', error);
        return null;
    }
}

// 4. 测试路由跳转
function testRouteNavigation() {
    console.log('\n4. 测试路由跳转:');
    console.log('当前路径:', window.location.pathname);
    
    // 检查Vue Router实例
    if (window.app && window.app.$router) {
        console.log('Vue Router可用');
        console.log('当前路由:', window.app.$route);
    } else {
        console.log('Vue Router不可用');
    }
}

// 5. 清除认证状态
function clearAuth() {
    console.log('\n5. 清除认证状态:');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    console.log('认证状态已清除');
}

// 6. 完整测试流程
async function runFullTest() {
    console.log('=== 开始完整认证测试 ===');
    
    // 清除旧状态
    clearAuth();
    
    // 检查初始状态
    checkStorage();
    
    // 测试登录
    const loginResult = await testLogin();
    if (!loginResult || !loginResult.success) {
        console.error('登录失败，停止测试');
        return;
    }
    
    // 检查登录后状态
    checkStorage();
    
    // 验证Token
    await testTokenValidation();
    
    // 测试路由
    testRouteNavigation();
    
    console.log('=== 测试完成 ===');
}

// 导出函数供手动调用
window.authDebug = {
    checkStorage,
    testLogin,
    testTokenValidation,
    testRouteNavigation,
    clearAuth,
    runFullTest
};

console.log('调试函数已加载，使用方法:');
console.log('- authDebug.checkStorage() - 检查存储状态');
console.log('- authDebug.testLogin() - 测试登录');
console.log('- authDebug.testTokenValidation() - 验证Token');
console.log('- authDebug.clearAuth() - 清除认证状态');
console.log('- authDebug.runFullTest() - 运行完整测试');

// 自动运行初始检查
checkStorage();