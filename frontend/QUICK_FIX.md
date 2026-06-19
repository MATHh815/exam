# 快速修复指南

## 🚨 遇到错误？按照以下步骤操作

---

## 错误 1: dompurify 导入失败

**错误信息**: `Failed to resolve import 'dompurify'`

**快速修复**:
```bash
cd exam/frontend
npm install
# 重启 Vite 服务器
```

---

## 错误 2: lucide-vue-next 导入失败

**错误信息**: `Failed to resolve import "lucide-vue-next"`

**快速修复**:
```bash
cd exam/frontend
npm install lucide-vue-next
# 重启 Vite 服务器
```

或者双击运行 `install_lucide.bat`

---

## 错误 3: Vite 开发服务器无法启动

**快速修复**:
```bash
cd exam/frontend
# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json
# 重新安装
npm install
# 启动服务器
npm run dev
```

---

## 错误 4: 页面空白或组件不显示

**快速修复**:
1. 按 `F12` 打开浏览器控制台
2. 查看错误信息
3. 按 `Ctrl + Shift + R` 强制刷新
4. 清除浏览器缓存

---

## 错误 5: API 请求失败

**快速修复**:
1. 确认后端服务器正在运行
2. 检查 API 地址配置
3. 查看浏览器控制台的网络请求
4. 检查 CORS 配置

---

## 通用解决步骤

### 1. 重启 Vite 开发服务器

```bash
# 停止服务器: Ctrl + C
# 重新启动
npm run dev
```

### 2. 清除缓存

```bash
# 删除 Vite 缓存
rm -rf node_modules/.vite

# 重启服务器
npm run dev
```

### 3. 重新安装依赖

```bash
# 删除依赖
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 启动服务器
npm run dev
```

### 4. 强制刷新浏览器

- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

---

## 需要帮助？

查看详细文档：
- `TROUBLESHOOTING.md` - 完整的故障排除指南
- `LUCIDE_INSTALL_GUIDE.md` - Lucide 图标库安装指南
- `FRONTEND_QUICK_START.md` - 前端快速开始指南

---

**创建时间**: 2024-12-26  
**维护者**: Kiro AI Assistant

