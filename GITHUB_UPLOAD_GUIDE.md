# GitHub 上传指南

## 方法1: 使用GitHub Desktop（推荐新手）

### 1. 下载并安装 GitHub Desktop
- 访问: https://desktop.github.com/
- 下载并安装

### 2. 登录GitHub账号
- 打开GitHub Desktop
- File → Options → Accounts
- 登录你的GitHub账号

### 3. 创建新仓库
- File → New Repository
- 或者 File → Add Local Repository（如果已有git仓库）

### 4. 填写仓库信息
- Name: `exam-system` （或你喜欢的名字）
- Description: `考公考研考编智能学习系统`
- Local Path: 选择exam项目所在目录
- Initialize with README: 不勾选（我们已经有了）
- Git Ignore: None（我们已经有.gitignore）
- License: MIT（我们已经有LICENSE）

### 5. 发布到GitHub
- 点击 "Publish repository"
- 选择是否设为私有仓库
- 点击 "Publish Repository"

完成！你的项目已经上传到GitHub了。

---

## 方法2: 使用命令行

### 1. 初始化Git仓库（如果还没有）

```bash
cd exam
git init
```

### 2. 添加所有文件

```bash
git add .
```

### 3. 创建第一次提交

```bash
git commit -m "Initial commit: 考公考研考编智能学习系统"
```

### 4. 在GitHub上创建新仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - Repository name: `exam-system`
   - Description: `考公考研考编智能学习系统 - 支持智能练习、模拟考试、错题本、学习统计`
   - Public 或 Private（根据需要选择）
   - 不要勾选 "Initialize this repository with a README"
3. 点击 "Create repository"

### 5. 关联远程仓库

```bash
# 替换 YOUR_USERNAME 为你的GitHub用户名
git remote add origin https://github.com/YOUR_USERNAME/exam-system.git
```

### 6. 推送代码

```bash
# 推送到main分支
git branch -M main
git push -u origin main
```

完成！

---

## 方法3: 使用GitHub CLI

### 1. 安装GitHub CLI

访问: https://cli.github.com/

### 2. 登录

```bash
gh auth login
```

### 3. 创建仓库并推送

```bash
cd exam
git init
git add .
git commit -m "Initial commit: 考公考研考编智能学习系统"

# 创建GitHub仓库并推送
gh repo create exam-system --public --source=. --push
```

---

## 上传前检查清单

在上传之前，确保：

- [ ] 已删除敏感信息（密码、API密钥等）
- [ ] .env 文件已在 .gitignore 中
- [ ] 数据库文件（*.db）已在 .gitignore 中
- [ ] node_modules 已在 .gitignore 中
- [ ] venv 已在 .gitignore 中
- [ ] 日志文件已在 .gitignore 中
- [ ] README.md 内容完整
- [ ] LICENSE 文件已创建

## 检查敏感信息

运行以下命令检查是否有敏感信息：

```bash
# 检查.env文件
git status

# 确保.env不在待提交列表中
# 如果在，运行：
git rm --cached .env
```

## 推荐的仓库设置

### 仓库描述
```
考公考研考编智能学习系统 - 支持智能练习、模拟考试、错题本、学习统计、AI分析等功能
```

### Topics（标签）
```
python
flask
vue
education
exam-system
learning-platform
study-tool
chinese
```

### README Badges

在README.md顶部添加徽章：

```markdown
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

## 后续维护

### 更新代码

```bash
# 查看修改
git status

# 添加修改
git add .

# 提交
git commit -m "描述你的修改"

# 推送
git push
```

### 创建分支

```bash
# 创建新功能分支
git checkout -b feature/new-feature

# 开发完成后合并
git checkout main
git merge feature/new-feature
git push
```

### 标签版本

```bash
# 创建版本标签
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

## 常见问题

### 问题1: 推送失败 - 认证错误

**解决**: 使用Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token
3. 选择权限：repo
4. 复制token
5. 推送时使用token作为密码

### 问题2: 文件太大

**解决**: 使用Git LFS

```bash
# 安装Git LFS
git lfs install

# 追踪大文件
git lfs track "*.db"
git add .gitattributes
git commit -m "Add Git LFS"
```

### 问题3: 历史中有敏感信息

**解决**: 使用BFG Repo-Cleaner

```bash
# 下载BFG
# https://rtyley.github.io/bfg-repo-cleaner/

# 删除敏感文件
java -jar bfg.jar --delete-files .env

# 清理历史
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## 项目展示

上传后，你可以：

1. **添加项目截图** - 在README中展示界面
2. **编写详细文档** - 帮助其他人使用
3. **设置GitHub Pages** - 部署在线演示
4. **启用Issues** - 接收反馈和bug报告
5. **添加贡献指南** - CONTRIBUTING.md

## 下一步

- [ ] 上传到GitHub
- [ ] 添加项目截图
- [ ] 完善README文档
- [ ] 设置GitHub Actions（CI/CD）
- [ ] 添加在线演示链接
- [ ] 分享给朋友和社区

祝你的项目获得更多star！⭐
