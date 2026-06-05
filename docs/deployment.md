# 部署指南

本指南帮助你将物体识别系统部署到免费云服务器：
- **前端** → Vercel（免费，全球 CDN）
- **后端** → Render（免费套餐，支持持久化存储）

---

## 前置准备

1. 注册 [GitHub](https://github.com) 账号（或 [Gitee](https://gitee.com)）
2. 注册 [Vercel](https://vercel.com) 账号（可用 GitHub 登录）
3. 注册 [Render](https://render.com) 账号（可用 GitHub 登录）

---

## 第一步：将代码推送到 GitHub

### 1.1 初始化 Git 仓库

```bash
cd wangjian-dec
git init
git add .
git commit -m "Initial commit"
```

### 1.2 创建 GitHub 仓库并推送

在 GitHub 上创建一个新仓库（如 `object-detection-system`），然后：

```bash
git remote add origin https://github.com/你的用户名/object-detection-system.git
git branch -M main
git push -u origin main
```

---

## 第二步：部署后端到 Render

### 2.1 创建 Web Service

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 **New** → **Web Service**
3. 选择 **Build and deploy from a Git repository**
4. 连接你的 GitHub 仓库

### 2.2 配置构建选项

| 配置项 | 值 |
|--------|-----|
| **Name** | `object-detection-backend` |
| **Region** | Singapore（离国内最近） |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

### 2.3 添加持久化磁盘

Render 免费套餐的文件系统是临时的（重启会丢失数据）。需要添加磁盘：

1. 在 Web Service 设置页面，找到 **Disks** 部分
2. 点击 **Add Disk**
3. 配置：
   - **Name**: `data-disk`
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: 1 GB（免费最大）
4. 保存

### 2.4 配置环境变量

在 Render 的 **Environment** 页面添加以下变量：

| Key | Value | 说明 |
|-----|-------|------|
| `APP_ENV` | `production` | 运行环境 |
| `DATABASE_URL` | `sqlite:///./data/app.db` | 数据库路径 |
| `UPLOAD_DIR` | `./data/uploads` | 上传文件目录 |
| `JWT_SECRET_KEY` | （点 Generate 生成随机值） | JWT 密钥 |
| `JWT_EXPIRE_HOURS` | `24` | Token 过期时间 |
| `BAIDU_API_KEY` | 你的百度 API Key | 百度 API 密钥 |
| `BAIDU_SECRET_KEY` | 你的百度 Secret Key | 百度 Secret 密钥 |
| `BAIDU_TOKEN_URL` | `https://aip.baidubce.com/oauth/2.0/token` | 百度 Token 地址 |
| `BAIDU_DETECT_URL` | `https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general` | 百度识别地址 |
| `BAIDU_API_TIMEOUT_SECONDS` | `30` | API 超时时间 |
| `MAX_IMAGE_SIZE_MB` | `10` | 最大上传大小 |

### 2.5 部署

点击 **Create Web Service**，Render 会自动构建和部署。

部署完成后，你会得到一个 URL，类似：
```
https://object-detection-backend.onrender.com
```

> ⚠️ **注意**：Render 免费套餐有冷启动延迟（约 30-60 秒无请求后休眠），首次访问会较慢。

### 2.6 验证后端

访问以下 URL 确认后端正常：
```
https://object-detection-backend.onrender.com/
```
应该返回：`{"message":"Simple Object Detection System API","version":"1.0.0"}`

---

## 第三步：部署前端到 Vercel

### 3.1 导入项目

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 **Add New...** → **Project**
3. 选择你的 GitHub 仓库
4. 点击 **Import**

### 3.2 配置构建选项

| 配置项 | 值 |
|--------|-----|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### 3.3 配置环境变量

在 **Environment Variables** 中添加：

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://object-detection-backend.onrender.com` |

> 将上面的 URL 替换为你实际的 Render 后端地址。

### 3.4 部署

点击 **Deploy**，Vercel 会自动构建和部署。

部署完成后，你会得到一个 URL，类似：
```
https://object-detection-system.vercel.app
```

---

## 第四步：测试

1. 打开 Vercel 前端 URL
2. 使用测试账号 `demo` / `123456` 登录
3. 上传一张图片进行识别
4. 查看识别结果

---

## 配置 CORS（重要）

部署后，前端和后端在不同域名下，需要确保后端 CORS 配置允许你的 Vercel 域名。

修改 `backend/app/main.py`：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://你的域名.vercel.app",  # ← 添加这一行
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

或者更灵活地通过环境变量配置：

```python
import os

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

然后在 Render 环境变量中添加：
```
ALLOWED_ORIGINS=https://你的域名.vercel.app,http://localhost:5173
```

---

## 常见问题

### Q: Render 后端首次访问很慢？

Render 免费套餐在无请求 15 分钟后会休眠，首次唤醒需要 30-60 秒。这是正常现象。可以使用 UptimeRobot 等免费服务定期 ping 来保持活跃。

### Q: 上传图片后识别失败？

检查 Render 的 **Logs** 页面查看错误日志。常见原因：
- 百度 API Key/Secret Key 配置错误
- 百度 API 调用次数用尽
- 网络超时（可增大 `BAIDU_API_TIMEOUT_SECONDS`）

### Q: 前端显示网络错误？

确认 `VITE_API_BASE_URL` 环境变量是否正确设置为 Render 后端 URL。修改环境变量后需要在 Vercel 重新部署。

### Q: 数据会丢失吗？

只要持久化磁盘正常挂载，SQLite 数据库和上传的图片在 Render 重启后不会丢失。但如果删除并重新创建 Service，磁盘数据会丢失。

### Q: 如何更新部署？

推送代码到 GitHub 后，Render 和 Vercel 会自动检测并重新部署。

```bash
git add .
git commit -m "Update something"
git push
```

---

## 本地开发 vs 生产环境

| 配置 | 本地开发 | 生产环境（Render） |
|------|---------|-------------------|
| `DATABASE_URL` | `sqlite:///./data/app.db` | `sqlite:///./data/app.db` |
| `UPLOAD_DIR` | `./data/uploads` | `./data/uploads` |
| `JWT_SECRET_KEY` | `replace-with-random-secret` | 随机生成的安全密钥 |
| `APP_ENV` | `development` | `production` |
| `VITE_API_BASE_URL` | `http://localhost:8000` | `https://xxx.onrender.com` |

---

## 部署架构图

```
┌─────────────────┐         ┌─────────────────────┐
│   用户浏览器      │         │   百度 AI 开放平台    │
│                  │         │                     │
│  Vercel CDN      │  REST   │  图像识别 API        │
│  (Vue 前端)      │ ◄─────► │                     │
│                  │  API    │                     │
└────────┬─────────┘         └──────────┬──────────┘
         │                              │
         │ HTTPS                        │ HTTPS
         │                              │
         ▼                              │
┌─────────────────┐                     │
│   Render 免费    │                     │
│   (FastAPI)      │ ◄──────────────────┘
│                  │
│  ┌────────────┐  │
│  │ 持久化磁盘  │  │  ← SQLite + 上传图片
│  │  data/     │  │
│  └────────────┘  │
└──────────────────┘
```
