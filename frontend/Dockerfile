# 使用官方Node镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 使用国内npm镜像源加速安装
RUN npm config set registry https://registry.npmmirror.com && \
    npm install

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5173

# 启动命令（在docker-compose中覆盖）
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
