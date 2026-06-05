# 简易物体识别系统

基于 Vue 3 + FastAPI + 百度 AI 的简易物体识别系统，支持图片上传、物体识别、结果展示等完整流程。

## 功能特性

- 🔐 用户登录 / 退出（JWT 认证）
- 📷 图片上传（支持 JPG、PNG、WebP，最大 10MB）
- 🤖 百度 AI 通用物体识别
- 📊 识别结果展示（关键词、类别、置信度）
- 📋 历史任务列表与详情查看
- 🔄 处理中任务自动轮询刷新

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Vue 3 + TypeScript |
| 构建工具 | Vite 5 |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| UI 组件 | Element Plus |
| HTTP 请求 | Axios |
| 后端框架 | FastAPI |
| 数据校验 | Pydantic v2 |
| 数据库 | SQLite + SQLAlchemy |
| 认证方案 | JWT (python-jose) |
| 外部服务 | 百度 AI 图像识别 API |

## 快速启动

### 环境要求

- Node.js >= 18
- Python >= 3.10

### 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后会自动创建 SQLite 数据库并初始化测试账号。

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 测试账号

| 用户名 | 密码 |
|--------|------|
| demo   | 123456 |

## 项目结构

```
wangjian-dec/
├── README.md
├── docs/
│   ├── system-development.md        # 系统开发文档
│   └── teaching-guide.md            # 教学文档
├── backend/
│   ├── requirements.txt
│   ├── .env                         # 环境变量配置
│   └── app/
│       ├── main.py                  # 应用入口
│       ├── core/
│       │   ├── config.py            # 配置管理
│       │   └── security.py          # JWT 认证
│       ├── db/session.py            # 数据库连接
│       ├── models/                  # 数据模型
│       ├── services/                # 业务逻辑
│       ├── adapters/                # 外部 API 适配
│       └── api/                     # 路由接口
└── frontend/
    ├── index.html
    ├── vite.config.ts
    └── src/
        ├── main.ts                  # 应用入口
        ├── App.vue                  # 根组件
        ├── api/                     # 接口封装
        ├── stores/                  # 状态管理
        ├── types/                   # 类型定义
        ├── router/                  # 路由配置
        ├── pages/                   # 页面组件
        └── components/              # 公共组件
```

## 核心接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/login` | 用户登录 | ❌ |
| GET | `/api/auth/me` | 获取当前用户 | ✅ |
| POST | `/api/tasks` | 上传图片创建任务 | ✅ |
| GET | `/api/tasks` | 获取任务列表 | ✅ |
| GET | `/api/tasks/{id}` | 获取任务详情 | ✅ |
| GET | `/api/files/{id}/original/raw` | 获取任务图片 | ✅ |

## 业务流程

```
用户登录 → 上传图片 → 后端保存文件 → 调用百度 API → 保存识别结果 → 前端轮询展示
```

## 配置说明

后端配置通过 `backend/.env` 文件管理：

```env
BAIDU_API_KEY=你的API Key
BAIDU_SECRET_KEY=你的Secret Key
JWT_SECRET_KEY=替换为随机密钥
```

> ⚠️ 注意：正式部署前请更换百度 API Key 和 JWT 密钥，不要提交到公开仓库。

## 免费部署

本项目支持一键部署到免费云平台：

| 组件 | 平台 | 说明 |
|------|------|------|
| 前端 | [Vercel](https://vercel.com) | 全球 CDN，免费，速度快 |
| 后端 | [Render](https://render.com) | 免费套餐，支持持久化存储 |

详细步骤请参考 [部署指南](docs/deployment.md)。

**快速流程：**

```bash
# 1. 推送代码到 GitHub
git init && git add . && git commit -m "deploy"
git remote add origin https://github.com/你的用户名/你的仓库.git
git push -u origin main

# 2. 在 Render 创建 Web Service，配置环境变量和持久化磁盘
# 3. 在 Vercel 导入项目，设置 VITE_API_BASE_URL 为 Render 后端 URL
```

## License

MIT

MIT
