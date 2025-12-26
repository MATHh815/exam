#!/bin/bash
# macOS/Linux 快速启动脚本

echo "========================================"
echo "考公考研考编系统 - 后端启动"
echo "========================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[错误] 虚拟环境不存在，请先运行: python -m venv venv"
    exit 1
fi

# 激活虚拟环境
echo "[1/3] 激活虚拟环境..."
source venv/bin/activate

# 检查数据库
if [ ! -f "instance/exam.db" ]; then
    echo "[2/3] 初始化数据库..."
    python init_db.py
else
    echo "[2/3] 数据库已存在，跳过初始化"
fi

# 启动服务器
echo "[3/3] 启动开发服务器..."
echo ""
echo "服务器将在 http://127.0.0.1:5000 运行"
echo "按 Ctrl+C 停止服务器"
echo ""
python run.py
