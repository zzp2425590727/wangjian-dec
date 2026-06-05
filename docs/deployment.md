# 部署指南

本指南帮助你将物体识别系统部署到免费云平台：
- **前端** → Vercel（免费，全球 CDN）
- **后端** → Render（免费套餐，支持 Python）

---

## 前置准备

1. 注册 [GitHub](https://github.com) 账号
2. 注册 [Vercel](https://vercel.com) 账号（可用 GitHub 登录）
3. 注册 [Render](https://render.com) 账号（可用 GitHub 登录）

---

## 第一步：将代码推送到 GitHub

### 1.1 在 GitHub 创建仓库

1. 打开 https://github.com/new
2. Repository name 填 `object-detection-system`
3. 选择 **Public**（免费用户私有仓库有限制）
4. 点击 **Create repository**

### 1.2 推送代码

```bash
cd wangjian-dec
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/object-detection-system.git
git branch -M main
git push -u origin main
```

---

## 第二步：部署后端到 Render

### 2.1 创建 Web Service

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击右上角 **+ New** 按钮
3. 选择 **Web Service**

![步骤示意]

```
+ New  ──→  Web Service  ──→  Connect your GitHub repo
```

### 2.2 连接 GitHub 仓库

1. 选择 **Build and deploy from a Git repository**
2. 点击 **Next**
3. 找到你刚才创建的仓库 `object-detection-system`
4. 点击 **Connect**

### 2.3 配置 Web Service

在配置页面填写以下信息：

| 配置项 | 填写内容 | 备注 |
|--------|---------|------|
| **Name** | `object-detection-backend` | 自定义名称 |
| **Region** | `Singapore (Southeast Asia)` | 离国内最近 |
| **Branch** | `main` | |
| **Root Directory** | `backend` | ⚠️ 必须填 |
| **Runtime** | `Python 3` | |
| **Build Command** | `pip install -r requirements.txt` | |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | |
| **Instance Type** | `Free` | 选择免费套餐 |

### 2.4 配置环境变量（重要）

在同一个页面往下滚，找到 **Environment Variables** 部分，点击 **Add Environment Variable**，逐个添加：

| Key | Value | 备注 |
|-----|-------|------|
| `APP_ENV` | `production` | |
| `DATABASE_URL` | `sqlite:///./data/app.db` | |
| `UPLOAD_DIR` | `./data/uploads` | |
| `JWT_SECRET_KEY` | 点右侧 **Generate** 按钮自动生成 | |
| `JWT_EXPIRE_HOURS` | `24` | |
| `BAIDU_API_KEY` | 你的百度 API Key | |
| `BAIDU_SECRET_KEY` | 你的百度 Secret Key | |
| `BAIDU_TOKEN_URL` | `https://aip.baidubce.com/oauth/2.0/token` | |
| `BAIDU_DETECT_URL` | `https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general` | |
| `BAIDU_API_TIMEOUT_SECONDS` | `30` | |
| `MAX_IMAGE_SIZE_MB` | `10` | |
| `ALLOWED_ORIGINS` | `https://你的Vercel域名.vercel.app,http://localhost:5173` | 后面再填 |

### 2.5 点击 Deploy

点击页面底部的 **Create Web Service** 按钮。

Render 会开始构建和部署，大约需要 2-5 分钟。可以在 **Logs** 标签页查看进度。

部署成功后，页面顶部会显示你的后端 URL，类似：
```
https://object-detection-backend.onrender.com
```

### 2.6 验证后端

在浏览器访问这个 URL，应该看到：
```json
{"message":"Simple Object Detection System API","version":"1.0.0"}
```

> ⚠️ **关于数据持久化**：Render 免费套餐的文件系统是临时的，每次重新部署或 Service 休眠唤醒后，SQLite 数据库和上传的图片会被重置。对于学习和演示完全够用。如需持久化存储，需升级到付费套餐（$7/月起）并添加 Persistent Disk。

---

## 第三步：部署前端到 Vercel

### 3.1 导入项目

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 **Add New...** → **Project**
3. 找到你的 GitHub 仓库，点击 **Import**

### 3.2 配置项目

| 配置项 | 填写内容 |
|--------|---------|
| **Framework Preset** | Vite（通常自动识别） |
| **Root Directory** | 点 **Edit**，改为 `frontend` |
| **Build Command** | `npm run build`（默认即可） |
| **Output Directory** | `dist`（默认即可） |

### 3.3 配置环境变量

展开 **Environment Variables** 部分，添加：

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://object-detection-backend.onrender.com` |

> ⚠️ 把上面的 URL 替换为你第二步中实际获得的 Render 后端地址！

### 3.4 点击 Deploy

Vercel 会自动构建和部署，大约 1-2 分钟。

部署成功后会显示你的前端 URL，类似：
```
https://object-detection-system.vercel.app
```

---

## 第四步：配置 CORS（让前后端互通）

前端在 `xxx.vercel.app`，后端在 `xxx.onrender.com`，域名不同，需要配置 CORS。

### 方法：在 Render 环境变量中添加

回到 Render Dashboard → 你的 Web Service → **Environment** 标签页：

1. 找到 `ALLOWED_ORIGINS` 这个环境变量
2. 把值改为你的实际 Vercel 域名：
   ```
   https://object-detection-system.vercel.app,http://localhost:5173
   ```
3. 保存后 Render 会自动重新部署

---

## 第五步：测试

1. 打开你的 Vercel 前端 URL
2. 用 `demo` / `123456` 登录
3. 上传一张图片
4. 查看识别结果

---

## 完整流程图

```
┌──────────────────────────────────────────────────────┐
│  1. 推送代码到 GitHub                                  │
│     git push → github.com/你的仓库                      │
└──────────────┬───────────────────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐  ┌─────────────┐
│  2. Render   │  │  3. Vercel   │
│  部署后端     │  │  部署前端     │
│             │  │             │
│  连接仓库    │  │  连接仓库    │
│  设 Root Dir │  │  设 Root Dir │
│  = backend  │  │  = frontend │
│  配置环境变量 │  │  设 API URL  │
│  Deploy!    │  │  Deploy!    │
│             │  │             │
│  得到 URL:   │  │  得到 URL:   │
│  xxx.onrender│  │  xxx.vercel │
└──────┬──────┘  └──────┬──────┘
       │                │
       │  4. 配置 CORS    │
       │  ALLOWED_ORIGINS │
       │  = Vercel URL    │
       │                │
       └───────┬────────┘
               ▼
       ┌──────────────┐
       │   5. 测试      │
       │  打开 Vercel   │
       │  URL 登录使用   │
       └──────────────┘
```

---

## 常见问题

### Q: Render 后端首次访问很慢？

Render 免费套餐在无请求约 15 分钟后会休眠。首次唤醒需要 30-60 秒，这是正常的。可以用 [UptimeRobot](https://uptimerobot.com)（免费）每 5 分钟 ping 一次来保持活跃。

### Q: 为什么重新部署后数据没了？

Render 免费套餐不支持持久化磁盘。每次重新部署，SQLite 数据库和上传的图片会被重置。这是免费方案的限制。解决方案：
- 学习演示：够用，无需处理
- 正式使用：升级 Render 付费套餐 + 添加 Persistent Disk，或改用外部数据库

### Q: 前端显示网络错误？

1. 确认 `VITE_API_BASE_URL` 是否正确（不要有末尾 `/`）
2. 确认 `ALLOWED_ORIGINS` 是否包含你的 Vercel 域名
3. 在浏览器按 F12 打开开发者工具，看 Console 和 Network 标签页的错误信息

### Q: 登录后提示 401？

JWT_SECRET_KEY 在每次 Render 重新部署时可能变化（如果你用了 generateValue）。确保前后端的 token 机制一致。

### Q: 上传图片后识别失败？

在 Render 的 **Logs** 标签页查看错误日志。常见原因：
- 百度 API Key 或 Secret Key 填写错误
- 百度 API 调用次数用尽
- 超时（可增大 `BAIDU_API_TIMEOUT_SECONDS`）

### Q: 如何更新代码？

```bash
git add .
git commit -m "update"
git push
```

Render 和 Vercel 会自动检测并重新部署。

---

## 免费方案对比

| 平台 | 用途 | 免费额度 | 限制 |
|------|------|---------|------|
| **Vercel** | 前端静态站点 | 无限 | 无明显限制 |
| **Render** | 后端 API | 750 小时/月 | 冷启动延迟，无持久化 |
