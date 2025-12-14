# 阶段 1: 构建阶段
FROM node:18-alpine as build-stage

WORKDIR /app

# 复制 package.json 并安装依赖
COPY package*.json ./
RUN npm install --registry=https://registry.npmmirror.com

# 复制源代码并构建
COPY . .
RUN npm run build

# 阶段 2: 生产环境运行阶段 (使用 Nginx)
FROM nginx:stable-alpine as production-stage

# 复制构建产物到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置 (可选，用于处理 SPA 路由)
# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]