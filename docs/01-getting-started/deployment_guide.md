# 部署指南 (Deployment Guide)

本指南旨在帮助您将 **PharmaAgentSystem** 通过 Docker 部署到服务器或本地机器上，使其能够通过 IP 地址供其他人访问。

## 1. 原理解析

您提到的几个文件共同构成了容器化部署的基础：

* **`docker-compose.yml`**: 编排文件，它定义了如何同时启动 Frontend（前端）和 Backend（后端）两个服务，并建立它们之间的网络连接。
* **`backend/Dockerfile`**: 定义后端环境（Python 3.9），安装依赖并启动 API 服务。
* **`frontend/Dockerfile`**: 定义前端构建流程（Node.js 构建 -> Nginx 托管）。
* **`backend/.dockerignore`**: 告诉 Docker 在构建镜像时忽略哪些文件（如虚拟环境、缓存等）。

### 关于“内存” (Memory/Persistence)

您问到 **“内存是在哪里？”**，实际上是在问 **“我的数据存在哪里？”**。

在 `docker-compose.yml` 中有这样一行配置：

```yaml
volumes:
  - ./backend/pharma.db:/app/pharma.db
```

这意味着：

* **容器内**：后端程序认为数据库文件在 `/app/pharma.db`。
* **物理机（宿主机）**：实际上这个文件被映射到了您项目目录下的 **`backend/pharma.db`**。

✅ **结论**：您的所有数据（医生画像、账号信息等）都持久化存储在您电脑/服务器的 `backend/pharma.db` 文件中。即使您删除容器、重启电脑，只要这个文件还在，数据就在。

## 2. 部署步骤 (How to Deploy)

### 前置条件

确保您的机器上已安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) 或 Docker Engine (Linux)。

### 启动服务

在项目根目录（包含 `docker-compose.yml` 的目录）打开终端，运行：

```bash
docker-compose up -d --build
```

* `up`: 启动服务。
* `-d`: 后台运行 (Detached mode)。
* `--build`: 强制重新构建镜像（确保您的最新代码生效）。

等待命令执行完毕，您看到 `Started` 字样即可。

## 3. 如何供他人访问

### 获取您的 IP 地址

在终端运行 `ipconfig` (Windows) 或 `ifconfig` (Mac/Linux)，找到您的 **IPv4 地址**（通常是以 `192.168.x.x` 或 `10.x.x.x` 开头的局域网地址）。

### 访问方式

假设您的 IP 是 `192.168.1.100`：

* **他人（同事/用户）**：在浏览器输入 `http://192.168.1.100`
* **您自己**：可以使用 `http://localhost` 或 `http://192.168.1.100`

### 注意事项 (Troubleshooting)

1. **防火墙**: 如果其他人无法访问，请检查您的 Windows 防火墙设置，确保放行了 **80 端口**（Docker Desktop 通常会请求此权限，请允许）。
2. **API 连接**: 我已帮您修改了 Nginx 配置。前端请求 `/api/xxx` 会自动转发给后端。无论用户通过什么 IP 访问，都能正常连接后端。

## 4. 常用维护命令

* **停止服务**:

    ```bash
    docker-compose down
    ```

* **查看日志** (如果报错):

    ```bash
    docker-compose logs -f
    ```

    (按 `Ctrl+C` 退出日志查看)

## 5. 常见问题与故障排除 (Troubleshooting)

### 1. 端口冲突 (Port 80 is already allocated)

**现象**：启动时报错 `Bind for 0.0.0.0:80 failed: port is already allocated`。
**原因**：Windows 的 System 进程、IIS 或 Skype 占用了 80 端口。
**解决**：
我们已将默认配置修改为 **8080** 端口。如果仍有冲突，请修改 `docker-compose.yml`：

```yaml
frontend:
  ports:
    - "8081:80"  # 改为 8081 或其他空闲端口
```

### 2. 后端构建失败 (gcc / zlib 错误)

**现象**：`fatal error: zlib.h: No such file or directory` 或 `command 'gcc' failed`。
**原因**：Python 依赖库 `pyreadstat` 需要编译 C 扩展，需要系统安装 `gcc` 和 `zlib` 开发库。
**解决**：
确保 `backend/Dockerfile` 包含以下安装命令（已修复）：

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
```

### 3. 前端构建失败 (Vite requires Node.js 20+)

**现象**：`crypto.hash is not a function` 或 `Vite requires Node.js version 20+`。
**原因**：新版 Vite 对 Node.js 版本有更高要求。
**解决**：
确保 `frontend/Dockerfile` 使用 `node:22-alpine` 或更高版本：

```dockerfile
FROM node:22-alpine as build-stage
```

### 4. 外网访问

**需求**：希望其他人也能访问系统。
**解决**：请参考项目文档 `docs/public_access_guide.md`，推荐使用 **cpolar** 进行内网穿透。
