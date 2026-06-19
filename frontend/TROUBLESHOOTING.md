# 前端故障排除指南

## 问题：导入 dompurify 失败

### 错误信息
```
Failed to resolve import "dompurify" from "src/components/NoteEditor.vue". Does the file exist?
```

### 原因
1. node_modules 未安装或不完整
2. Vite 开发服务器缓存问题
3. 开发服务器需要重启

### 解决方案

#### 方案 1: 重启开发服务器（推荐）
1. 停止当前运行的开发服务器（Ctrl+C）
2. 重新启动：
```bash
cd exam/frontend
npm run dev
```

#### 方案 2: 清除缓存并重启
```bash
cd exam/frontend
# 删除 node_modules/.vite 缓存
rm -rf node_modules/.vite
# 重新启动
npm run dev
```

#### 方案 3: 重新安装依赖
```bash
cd exam/frontend
# 删除 node_modules
rm -rf node_modules
# 重新安装
npm install
# 启动
npm run dev
```

#### 方案 4: 使用批处理文件（Windows）
双击运行 `install_deps.bat` 文件，然后重启开发服务器。

### 验证安装
检查依赖是否已安装：
```bash
cd exam/frontend
npm list dompurify marked
```

应该看到：
```
exam-frontend@1.0.0
├── dompurify@3.0.6
└── marked@17.0.1
```

### 其他常见问题

#### 问题：PowerShell 执行策略错误
**错误**: `无法加载文件，因为在此系统上禁止运行脚本`

**解决**:
1. 以管理员身份运行 PowerShell
2. 执行：`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. 或者使用 cmd 代替：`cmd /c "npm install"`

#### 问题：端口被占用
**错误**: `Port 5173 is already in use`

**解决**:
1. 找到占用端口的进程：`netstat -ano | findstr :5173`
2. 结束进程：`taskkill /PID <进程ID> /F`
3. 或者使用其他端口：`npm run dev -- --port 5174`

#### 问题：模块版本冲突
**解决**:
```bash
cd exam/frontend
rm -rf node_modules package-lock.json
npm install
```

### 联系支持
如果问题仍然存在，请提供：
1. 错误的完整堆栈跟踪
2. Node.js 版本：`node --version`
3. npm 版本：`npm --version`
4. 操作系统版本

---

**最后更新**: 2025-12-26


---

## 问题 3: lucide-vue-next 导入失败

### 错误信息

```
Failed to resolve import "lucide-vue-next" from "src/components/PointsDisplay.vue"
```

### 原因

缺少 `lucide-vue-next` 图标库依赖。

### 解决方案

#### 方法 1: 使用安装脚本（推荐）

```bash
# 在 exam/frontend 目录下
双击运行 install_lucide.bat
```

#### 方法 2: 手动安装

```bash
cd exam/frontend
npm install lucide-vue-next
```

### 重启开发服务器

安装完成后，必须重启 Vite 开发服务器：

1. 按 `Ctrl + C` 停止当前服务器
2. 运行 `npm run dev` 重新启动
3. 按 `Ctrl + Shift + R` 强制刷新浏览器

### 验证

访问以下页面确认图标正常显示：
- `/achievements` - 成就系统
- `/daily-tasks` - 每日任务
- `/profile` - 个人中心（游戏化菜单）

### 详细文档

查看 `LUCIDE_INSTALL_GUIDE.md` 了解更多信息。

---

**最后更新**: 2024-12-26
