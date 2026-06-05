# 简易物体识别系统 — 教学文档

> 本文档面向本科生，系统讲解本项目涉及的后端核心技术与物体识别基础知识。每个知识点均配合项目代码实例说明。

---

## 目录

- [第一部分：后端基础知识](#第一部分后端基础知识)
  - [1. Web 框架与 FastAPI](#1-web-框架与-fastapi)
  - [2. RESTful API 设计](#2-restful-api-设计)
  - [3. 数据库与 ORM](#3-数据库与-orm)
  - [4. 用户认证与 JWT](#4-用户认证与-jwt)
  - [5. 文件上传与存储](#5-文件上传与存储)
  - [6. 中间件与 CORS](#6-中间件与-cors)
  - [7. 异步编程与后台任务](#7-异步编程与后台任务)
  - [8. 配置管理与环境变量](#8-配置管理与环境变量)
- [第二部分：物体识别基础知识](#第二部分物体识别基础知识)
  - [9. 什么是图像识别](#9-什么是图像识别)
  - [10. 图像分类 vs 目标检测](#10-图像分类-vs-目标检测)
  - [11. 卷积神经网络 (CNN)](#11-卷积神经网络-cnn)
  - [12. 经典图像分类模型](#12-经典图像分类模型)
  - [13. 置信度与 Softmax](#13-置信度与-softmax)
  - [14. 百度 AI 开放平台接入](#14-百度-ai-开放平台接入)
  - [15. 图像预处理与 Base64 编码](#15-图像预处理与-base64-编码)
- [第三部分：动手实践](#第三部分动手实践)
  - [练习 1：理解 API 请求流程](#练习-1理解-api-请求流程)
  - [练习 2：手动调用百度 API](#练习-2手动调用百度-api)
  - [练习 3：修改识别结果展示](#练习-3修改识别结果展示)
  - [练习 4：扩展系统功能](#练习-4扩展系统功能)

---

## 第一部分：后端基础知识

---

### 1. Web 框架与 FastAPI

#### 1.1 什么是 Web 框架

Web 框架是一套帮助开发者快速构建 Web 应用的工具库。它封装了底层的网络通信、请求解析、路由分发等重复性工作，让开发者专注于业务逻辑。

Python 常见的 Web 框架：

| 框架 | 特点 | 适用场景 |
|------|------|----------|
| Flask | 轻量、灵活 | 小型项目、API 服务 |
| Django | 全家桶、功能完善 | 大型 Web 应用 |
| **FastAPI** | 高性能、自动文档、类型校验 | API 服务、微服务 |

#### 1.2 为什么选择 FastAPI

FastAPI 是本项目选用的后端框架，它有以下核心优势：

**① 基于类型提示自动生成文档**

```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
def login(req: LoginRequest):
    # FastAPI 自动校验请求体是否符合 LoginRequest 的结构
    # 如果缺少字段或类型错误，自动返回 422 错误
    ...
```

你只需要定义好数据模型的类型，FastAPI 就会：
- 自动校验请求数据
- 自动生成 API 文档（访问 `/docs` 即可看到 Swagger UI）
- 自动进行 JSON 序列化和反序列化

**② 异步支持**

```python
import httpx

@app.post("/api/tasks")
async def create_task(file: UploadFile):
    # async/await 语法，遇到 IO 操作时自动让出 CPU
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=image_data)
    return resp.json()
```

`async` 函数在等待网络响应时不会阻塞整个服务器，可以同时处理其他请求。这对调用外部 API（如百度识别接口）的场景非常重要。

**③ 依赖注入系统**

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/tasks")
def list_tasks(db: Session = Depends(get_db)):
    # db 由 FastAPI 自动注入，请求结束后自动关闭
    tasks = db.query(DetectionTask).all()
    return tasks
```

`Depends` 是 FastAPI 的依赖注入机制。它会自动帮你在请求开始时创建资源（如数据库连接），在请求结束时清理资源。

#### 1.3 本项目中的 FastAPI 应用

本项目的入口文件 `backend/app/main.py`：

```python
app = FastAPI(lifespan=lifespan)     # 创建应用实例
app.include_router(routes_auth)      # 注册认证路由
app.include_router(routes_tasks)     # 注册任务路由
app.include_router(routes_files)     # 注册文件路由
```

每个路由模块用 `APIRouter` 组织，最后在 `main.py` 中统一注册，这是一种良好的代码组织方式。

---

### 2. RESTful API 设计

#### 2.1 什么是 REST

REST（Representational State Transfer）是一种 API 设计风格，核心思想是：**用 URL 表示资源，用 HTTP 方法表示操作**。

| HTTP 方法 | 操作 | 示例 | 说明 |
|-----------|------|------|------|
| GET | 查询 | `GET /api/tasks` | 获取任务列表 |
| POST | 创建 | `POST /api/tasks` | 创建新任务 |
| GET | 查询单个 | `GET /api/tasks/123` | 获取 ID 为 123 的任务 |
| PUT | 更新 | `PUT /api/tasks/123` | 更新任务信息 |
| DELETE | 删除 | `DELETE /api/tasks/123` | 删除任务 |

#### 2.2 状态码约定

HTTP 状态码告诉客户端请求的结果：

```
200 OK                  — 请求成功
201 Created             — 资源创建成功
400 Bad Request         — 请求参数错误（如文件类型不支持）
401 Unauthorized        — 未登录或 token 无效
403 Forbidden           — 无权限访问
404 Not Found           — 资源不存在
422 Unprocessable Entity — 数据校验失败（FastAPI 自动返回）
500 Internal Server Error — 服务器内部错误
```

#### 2.3 本项目的 API 设计

以任务接口为例：

```
POST   /api/tasks          — 上传图片，创建识别任务（multipart/form-data）
GET    /api/tasks           — 获取当前用户的任务列表（支持分页）
GET    /api/tasks/{task_id} — 获取单个任务详情（含识别结果）
```

请求头统一使用 `Authorization: Bearer {token}` 携带认证信息。

---

### 3. 数据库与 ORM

#### 3.1 什么是数据库

数据库是持久化存储数据的系统。本项目使用 **SQLite**，它是一个轻量级的嵌入式数据库，数据存储在单个文件中（`data/app.db`），无需安装额外的数据库服务。

适合学习和小型项目。生产环境通常使用 MySQL 或 PostgreSQL。

#### 3.2 什么是 ORM

ORM（Object-Relational Mapping，对象关系映射）是一种技术，让你可以用 Python 类和对象来操作数据库，而不需要写 SQL 语句。

**不用 ORM（直接写 SQL）：**
```python
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
row = cursor.fetchone()
```

**用 ORM（本项目的方式）：**
```python
user = db.query(User).filter(User.username == username).first()
```

两种方式效果相同，但 ORM 更安全（自动防 SQL 注入）、更 Pythonic。

#### 3.3 SQLAlchemy 模型定义

本项目使用 SQLAlchemy 作为 ORM 框架。定义一个数据表就是定义一个 Python 类：

```python
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"           # 对应数据库中的表名

    id: Mapped[str] = mapped_column(  # 定义字段
        String, primary_key=True      # 主键
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True  # 唯一且建立索引
    )
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
```

- `__tablename__`：对应数据库中的表名
- `Mapped[type]`：Python 类型注解，声明字段类型
- `mapped_column()`：定义列的属性（是否主键、是否有索引、默认值等）
- `relationship()`：定义表之间的关联关系

#### 3.4 数据库会话

数据库操作通过「会话」（Session）进行。会话就像是你和数据库之间的一次对话：

```python
# 创建会话
db = SessionLocal()

# 查询用户
user = db.query(User).filter(User.username == "demo").first()

# 创建新记录
new_task = DetectionTask(user_id="user_001", file_name="photo.jpg")
db.add(new_task)      # 添加到会话
db.commit()           # 提交到数据库（此时才真正写入）
db.refresh(new_task)  # 刷新获取自动生成的字段（如 id）

# 关闭会话
db.close()
```

在 FastAPI 中，我们用依赖注入自动管理会话的生命周期：

```python
def get_db():
    db = SessionLocal()
    try:
        yield db          # yield 把 db 交给路由函数使用
    finally:
        db.close()        # 请求结束后自动关闭

@app.get("/api/tasks")
def list_tasks(db: Session = Depends(get_db)):
    # 使用完毕后 db 会被自动关闭
    ...
```

#### 3.5 本项目的数据模型

```
┌─────────────┐       ┌─────────────────┐       ┌──────────────────┐
│    User      │ 1   N │  DetectionTask   │ 1   1 │ DetectionResult  │
│─────────────│───────│─────────────────│───────│──────────────────│
│ id (PK)     │       │ id (PK)         │       │ id (PK)          │
│ username     │       │ user_id (FK)    │       │ task_id (FK)     │
│ password_hash│       │ file_name       │       │ result_num       │
│ created_at   │       │ status          │       │ items_json       │
└─────────────┘       │ created_at      │       │ raw_log_id       │
                       └─────────────────┘       └──────────────────┘
```

- 一个用户可以有多个任务（一对多）
- 一个任务对应一个识别结果（一对一）
- 识别结果以 JSON 字符串存储在 `items_json` 字段中

---

### 4. 用户认证与 JWT

#### 4.1 认证的基本概念

认证（Authentication）回答的问题是：**你是谁？** 系统需要确认请求来自合法用户。

常见的认证方式：

| 方式 | 原理 | 特点 |
|------|------|------|
| Session-Cookie | 服务端存储会话，客户端通过 Cookie 传递会话 ID | 传统方式，需要服务端存储状态 |
| **JWT Token** | 服务端签发令牌，客户端每次请求携带令牌 | **无状态**，适合前后端分离架构 |
| OAuth 2.0 | 第三方授权（如微信登录） | 适合第三方登录场景 |

#### 4.2 JWT 是什么

JWT（JSON Web Token）是一种紧凑的、自包含的令牌格式。它由三部分组成：

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzAwMSJ9.xxx_signature
├──── Header ─────┤ ├── Payload ───┤ ├─ Signature ─┤
     (算法信息)         (用户信息)        (签名验证)
```

**Header**：声明使用的签名算法（如 HS256）
**Payload**：携带数据（如用户 ID、用户名、过期时间）
**Signature**：用密钥对前两部分签名，防止篡改

#### 4.3 JWT 工作流程

```
          登录请求 (用户名+密码)
用户 ──────────────────────────→ 后端
  │                               │
  │                               ├─ 验证用户名密码
  │                               ├─ 生成 JWT (含 user_id)
  │                               │
  │  ←── 返回 access_token ────────┘
  │
  │  后续请求 (Authorization: Bearer token)
  │────────────────────────────→ │
  │                               ├─ 解析 token
  │                               ├─ 验证签名和过期时间
  │                               ├─ 提取 user_id
  │  ←── 返回业务数据 ─────────────┘
```

#### 4.4 本项目的 JWT 实现

**签发 Token：**
```python
from jose import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(user_id: str, username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": user_id,        # subject，标准字段，表示令牌主体
        "username": username,
        "exp": expire,         # expiration，过期时间
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
```

**验证 Token：**
```python
def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload    # 验证通过，返回 payload
    except JWTError:
        return None       # 验证失败（签名错误或已过期）
```

**保护需要登录的接口：**
```python
from fastapi.security import HTTPBearer

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# 使用：任何需要登录的接口，只需注入 get_current_user
@app.get("/api/tasks")
def list_tasks(current_user: User = Depends(get_current_user)):
    # current_user 已经是经过认证的用户对象
    ...
```

#### 4.5 密码安全：哈希与加盐

密码**绝不能明文存储**。本项目使用 bcrypt 算法进行密码哈希：

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 存储密码时：明文 → 哈希值
password_hash = pwd_context.hash("123456")
# 结果类似：$2b$12$LJ3m4ys3Lz0YBSrYqK...

# 验证密码时：比对明文和哈希值
is_valid = pwd_context.verify("123456", password_hash)  # True
is_valid = pwd_context.verify("wrong", password_hash)   # False
```

bcrypt 的特点：
- **单向性**：无法从哈希值反推出原始密码
- **加盐（Salt）**：每个密码自动生成随机盐值，相同密码的哈希结果不同
- **慢哈希**：故意设计得很慢，暴力破解成本极高

---

### 5. 文件上传与存储

#### 5.1 HTTP 文件上传机制

文件上传使用 `multipart/form-data` 编码格式，它允许在一个请求中同时传递文件和普通表单字段。

```http
POST /api/tasks HTTP/1.1
Content-Type: multipart/form-data; boundary=----boundary123

------boundary123
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg

(二进制图片数据)
------boundary123
Content-Disposition: form-data; name="media_type"

image
------boundary123--
```

在 FastAPI 中接收文件上传：

```python
@app.post("/api/tasks")
async def create_task(
    file: UploadFile = File(...),         # 接收文件
    media_type: str = Form("image"),      # 接收表单字段
):
    content = await file.read()           # 读取文件内容（字节）
    file_name = file.filename             # 原始文件名
    content_type = file.content_type      # MIME 类型
    ...
```

#### 5.2 文件校验

上传文件必须进行安全校验：

```python
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

def validate_image_file(file: UploadFile):
    # 1. 校验 MIME 类型
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Unsupported file type")

    # 2. 校验文件扩展名
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Unsupported file extension")

    # 3. 校验文件大小（在读取后检查）
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(400, "File too large")
```

为什么要双重校验扩展名和 MIME 类型？因为用户可能修改文件扩展名来绕过检查。

#### 5.3 文件存储策略

本项目的文件存储结构：

```
data/uploads/
  ├── task_abc123/
  │   └── original.jpg      # 用户上传的原始图片
  ├── task_def456/
  │   └── original.png
  └── ...
```

- 每个任务一个独立目录，以任务 ID 命名
- 文件名由后端重新生成（`original` + 原始扩展名），避免用户上传的文件名包含恶意字符
- 通过任务 ID 和文件名组合访问，防止路径穿越攻击

#### 5.4 路径穿越防护

路径穿越是一种常见的安全攻击。攻击者可能构造类似 `../../../etc/passwd` 的路径来读取系统文件。

```python
def get_file_path(task_id: str, file_name: str) -> Path:
    task_dir = Path(settings.UPLOAD_DIR) / task_id
    file_path = (task_dir / file_name).resolve()  # resolve() 解析为绝对路径

    # 关键检查：解析后的路径必须在任务目录内
    if not str(file_path).startswith(str(task_dir.resolve())):
        raise HTTPException(403, "Access denied")

    return file_path
```

---

### 6. 中间件与 CORS

#### 6.1 什么是中间件

中间件（Middleware）是请求处理管线中的一个环节。每个请求在到达路由函数之前，都会经过所有中间件；响应在返回客户端之前，也会经过中间件。

```
请求 → [中间件A] → [中间件B] → 路由函数 → [中间件B] → [中间件A] → 响应
```

常见用途：日志记录、认证校验、跨域处理、请求限流等。

#### 6.2 CORS（跨域资源共享）

当前端（`localhost:5173`）向后端（`localhost:8000`）发请求时，浏览器会认为这是「跨域请求」，默认会阻止。

CORS 中间件告诉浏览器：「这些来源的请求是我允许的」。

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[                    # 允许的前端地址
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,            # 允许携带 Cookie
    allow_methods=["*"],               # 允许所有 HTTP 方法
    allow_headers=["*"],               # 允许所有请求头
)
```

> 生产环境中 `allow_origins` 不应设为 `*`，应只允许你的前端域名。

---

### 7. 异步编程与后台任务

#### 7.1 同步 vs 异步

**同步**：代码按顺序执行，遇到 IO 操作（如网络请求）时，线程会等待，不能做其他事。

```python
# 同步方式：调用百度 API 要等几秒，期间整个线程被阻塞
result = requests.post(url, data=image)  # 阻塞等待
```

**异步**：遇到 IO 操作时，让出 CPU 去处理其他请求，IO 完成后再回来继续。

```python
# 异步方式：等待期间可以处理其他请求
result = await client.post(url, data=image)  # 非阻塞
```

#### 7.2 async/await 语法

```python
import httpx

async def call_baidu_api(image_base64: str):
    async with httpx.AsyncClient() as client:    # 创建异步 HTTP 客户端
        resp = await client.post(url, data=...)   # await 等待异步操作
        return resp.json()
```

- `async def`：声明异步函数
- `await`：等待一个异步操作完成
- `async with`：异步上下文管理器

#### 7.3 FastAPI 后台任务

图片上传后，识别过程可能需要几秒。如果让用户等待，体验很差。FastAPI 的 `BackgroundTasks` 可以把耗时操作放到后台执行：

```python
from fastapi import BackgroundTasks

@app.post("/api/tasks")
async def create_task(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    # 1. 先保存文件、创建任务记录
    task = create_task_record(...)

    # 2. 把识别任务放到后台执行
    background_tasks.add_task(run_detection, task.id)

    # 3. 立即返回任务 ID 给前端（不等待识别完成）
    return {"id": task.id, "status": "pending"}
```

前端拿到任务 ID 后，可以轮询查询任务状态，直到识别完成。

---

### 8. 配置管理与环境变量

#### 8.1 为什么需要配置管理

不同的环境（开发、测试、生产）需要不同的配置：
- 开发环境用本地 SQLite，生产环境用 MySQL
- API Key、密钥等敏感信息不能硬编码在代码中
- 不同开发者可能需要不同的端口配置

#### 8.2 环境变量

环境变量是操作系统级别的键值对，程序在运行时可以读取：

```bash
# Linux/Mac
export BAIDU_API_KEY=your_key_here

# Windows PowerShell
$env:BAIDU_API_KEY = "your_key_here"
```

```python
import os
api_key = os.environ.get("BAIDU_API_KEY")
```

#### 8.3 .env 文件与 pydantic-settings

手动设置环境变量很麻烦。本项目使用 `.env` 文件 + `pydantic-settings` 自动加载：

```python
# .env 文件
BAIDU_API_KEY=LqawwYAjyB0JQxIa0Q04cfHu
BAIDU_SECRET_KEY=S6jCO8z1RCGeuO3vIDBDEHdYNQhkCkMi
```

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BAIDU_API_KEY: str = ""           # 默认值为空字符串
    BAIDU_SECRET_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./data/app.db"

    class Config:
        env_file = ".env"             # 自动读取 .env 文件

settings = Settings()
# settings.BAIDU_API_KEY 会自动读取 .env 中的值
```

> 安全提示：`.env` 文件不应提交到 Git 仓库。应将其加入 `.gitignore`。

---

## 第二部分：物体识别基础知识

---

### 9. 什么是图像识别

#### 9.1 基本概念

图像识别（Image Recognition）是计算机视觉的核心任务之一，目标是让计算机理解图像中的内容。

人类看到一张猫的照片，能立刻认出「这是一只猫」。但对计算机来说，图像只是一个数字矩阵：

```
一张 224×224 的彩色图片
= 224 × 224 × 3 个数字（RGB 三通道）
= 150,528 个 0~255 的整数
```

图像识别的任务就是：**从这 15 万个数字中，提取出有意义的特征，判断图像的内容。**

#### 9.2 发展历程

| 时期 | 方法 | 代表 | 准确率（ImageNet） |
|------|------|------|-------------------|
| 2012 年前 | 手工特征 | SIFT + SVM | ~70% |
| 2012 | 深度学习 | AlexNet | ~80% |
| 2014 | 更深网络 | VGGNet, GoogLeNet | ~90% |
| 2015 | 残差网络 | ResNet | ~95% |
| 2020+ | 预训练大模型 | ViT, CLIP | ~98% |

2012 年的 AlexNet 是深度学习在图像识别领域的「爆发点」，之后深度学习方法迅速超越了所有传统方法。

---

### 10. 图像分类 vs 目标检测

这是两个容易混淆的概念：

#### 10.1 图像分类（Image Classification）

**回答：这张图里是什么？**

输入一张图片，输出一个类别标签（及其概率）。

```
输入: 🐱 的照片
输出: 猫 (95%), 兔子 (3%), 狗 (2%)
```

**本项目使用的百度 `advanced_general` 接口就是图像分类任务。** 它返回的是一组 `(关键词, 类别, 置信度)` 列表。

#### 10.2 目标检测（Object Detection）

**回答：这张图里有什么？在哪里？**

输入一张图片，输出每个目标的类别、位置（用边界框表示）和概率。

```
输入: 🐱🐶 的合照
输出:
  - 猫 (95%) 位置: (10, 20, 150, 200)
  - 狗 (90%) 位置: (200, 50, 400, 300)
```

边界框（Bounding Box）通常用 `(x_min, y_min, x_max, y_max)` 四个坐标表示。

#### 10.3 两者对比

| 特性 | 图像分类 | 目标检测 |
|------|---------|---------|
| 输出 | 类别 + 概率 | 类别 + 概率 + 位置 |
| 适用场景 | 整张图属于某个类别 | 图中有多个不同目标 |
| 典型模型 | ResNet, VGG | YOLO, Faster R-CNN |
| 本项目 | ✅ 百度 advanced_general | ❌ 不涉及 |

#### 10.4 更多计算机视觉任务

```
图像分类 → 目标检测 → 语义分割 → 实例分割
  (是什么)    (在哪)     (每个像素)    (每个实例的每个像素)
```

---

### 11. 卷积神经网络 (CNN)

#### 11.1 为什么需要 CNN

如果用普通的全连接网络处理一张 224×224×3 的图片，第一层就需要 224×224×3×N 个参数，参数量巨大且容易过拟合。

CNN 通过两个关键思想解决了这个问题：
- **局部连接**：每个神经元只看图像的一小块区域
- **权值共享**：同一个卷积核在整个图像上滑动，共享参数

#### 11.2 卷积操作

卷积核（Filter/Kernel）是一个小矩阵（如 3×3），在图像上滑动，每个位置做元素相乘再求和：

```
输入图像片段 (3×3):      卷积核 (3×3):         输出值:
[1  0  1]                [1  0  1]             1×1 + 0×0 + 1×1
[0  1  0]      ×         [0  1  0]      =      + 0×0 + 1×1 + 0×0
[1  0  1]                [1  0  1]             + 1×1 + 0×0 + 1×1
                                                = 4
```

不同的卷积核可以检测不同的特征：
- 边缘检测核：`[[−1 −1 −1], [−1 8 −1], [−1 −1 −1]]`
- 模糊核：`[[1/9 1/9 1/9], [1/9 1/9 1/9], [1/9 1/9 1/9]]`

#### 11.3 CNN 的典型结构

```
输入图像
  ↓
[卷积层 + ReLU] → 提取低级特征（边缘、纹理）
  ↓
[池化层] → 降低空间维度，减少计算量
  ↓
[卷积层 + ReLU] → 提取高级特征（形状、部件）
  ↓
[池化层]
  ↓
[全连接层] → 综合所有特征，做出分类决策
  ↓
[Softmax] → 输出各类别的概率
  ↓
输出：猫 (95%), 狗 (3%), 兔 (2%)
```

**关键层说明：**

| 层 | 作用 | 类比 |
|----|------|------|
| 卷积层 | 提取局部特征 | 用放大镜看图像的每个小区域 |
| ReLU | 引入非线性（负值变零） | 过滤掉不重要的信息 |
| 池化层 | 缩小特征图尺寸 | 把图片缩小，保留主要信息 |
| 全连接层 | 综合特征做决策 | 根据所有线索得出结论 |

---

### 12. 经典图像分类模型

#### 12.1 AlexNet (2012)

深度学习在图像识别的开山之作。首次使用 ReLU 激活函数和 Dropout 正则化，在 ImageNet 竞赛中大幅领先传统方法。

#### 12.2 VGGNet (2014)

核心思想：用多个 3×3 小卷积核代替大卷积核，通过增加网络深度来提升性能。

```
VGG-16 的结构：
2×[Conv3-64] → Pool → 2×[Conv3-128] → Pool →
3×[Conv3-256] → Pool → 3×[Conv3-512] → Pool →
3×[Conv3-512] → Pool → FC-4096 → FC-4096 → FC-1000
```

#### 12.3 ResNet (2015)

引入了**残差连接**（Skip Connection），解决了深层网络的梯度消失问题，使得训练上百层的网络成为可能。

```python
# 残差块的核心思想
def residual_block(x):
    identity = x                        # 保存输入
    x = conv(x)                         # 卷积
    x = batch_norm(x)                   # 批归一化
    x = relu(x)                         # 激活
    x = conv(x)
    x = batch_norm(x)
    x = x + identity                    # 残差连接：输出 = 变换后的x + 原始x
    return relu(x)
```

为什么有效？网络只需要学习「输入和输出之间的差异」（残差），而不是从零学习完整的映射，这大大降低了学习难度。

#### 12.4 模型对比

| 模型 | 年份 | 层数 | 参数量 | Top-5 错误率 |
|------|------|------|--------|-------------|
| AlexNet | 2012 | 8 | 60M | 16.4% |
| VGG-16 | 2014 | 16 | 138M | 7.3% |
| ResNet-50 | 2015 | 50 | 25M | 5.3% |
| ResNet-152 | 2015 | 152 | 60M | 4.5% |

---

### 13. 置信度与 Softmax

#### 13.1 Softmax 函数

神经网络的最后一层输出的是一个「分数向量」（logits），如 `[2.0, 1.0, 0.1]`。

Softmax 把这个分数向量转换为概率分布：

$$\text{Softmax}(z_i) = \frac{e^{z_i}}{\sum_{j} e^{z_j}}$$

```
原始分数: [2.0, 1.0, 0.1]
e^2.0 = 7.39, e^1.0 = 2.72, e^0.1 = 1.11
总和 = 7.39 + 2.72 + 1.11 = 11.22

Softmax 后: [7.39/11.22, 2.72/11.22, 1.11/11.22]
          = [0.659, 0.242, 0.099]
          ≈ [66%, 24%, 10%]
```

性质：
- 所有值在 0~1 之间
- 所有值之和为 1
- 原始分数越大，对应的概率越高

#### 13.2 本项目中的置信度

百度 API 返回的 `score` 就是经过 Softmax 处理后的置信度：

```json
{
  "result": [
    { "keyword": "卡通动漫人物", "root": "非自然图像-彩色动漫", "score": 0.381 },
    { "keyword": "彩色动漫",     "root": "非自然图像-彩色动漫", "score": 0.323 },
    { "keyword": "二次元",       "root": "非自然图像-彩色动漫", "score": 0.122 }
  ]
}
```

- `score` 越高，模型对这个分类越确信
- 所有 `score` 之和通常接近 1（但不一定严格等于 1，因为百度可能只返回 Top-N 结果）
- `root` 是更粗粒度的类别，`keyword` 是更细粒度的识别结果

#### 13.3 如何解读置信度

| 置信度范围 | 含义 | 建议 |
|-----------|------|------|
| > 0.8 | 高度确信 | 可以信赖结果 |
| 0.5 ~ 0.8 | 中等确信 | 大概率正确，需人工复核 |
| 0.2 ~ 0.5 | 低确信 | 可能正确，建议人工确认 |
| < 0.2 | 不确定 | 结果仅供参考 |

---

### 14. 百度 AI 开放平台接入

#### 14.1 百度 AI 图像识别服务

百度 AI 开放平台提供了「通用物体和场景识别」接口（`advanced_general`），可以识别图片中的物体、场景、标志等，并返回关键词、类别和置信度。

#### 14.2 认证机制

百度 API 使用 OAuth 2.0 的 Client Credentials 模式：

```
1. 用 API Key + Secret Key 换取 access_token
   POST https://aip.baidubce.com/oauth/2.0/token
   参数: grant_type=client_credentials
         client_id={API_KEY}
         client_secret={SECRET_KEY}

2. 用 access_token 调用识别接口
   POST https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token={token}
```

access_token 有效期通常为 30 天，应缓存复用，避免每次都重新获取。

#### 14.3 请求格式

```python
import base64
import httpx

# 读取图片并 Base64 编码
with open("photo.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# 发送请求
async with httpx.AsyncClient() as client:
    resp = await client.post(
        f"{BAIDU_DETECT_URL}?access_token={token}",
        data={"image": image_base64},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    result = resp.json()
```

#### 14.4 响应格式

```json
{
  "result": [
    { "score": 0.381, "root": "非自然图像-彩色动漫", "keyword": "卡通动漫人物" },
    { "score": 0.323, "root": "非自然图像-彩色动漫", "keyword": "彩色动漫" },
    { "score": 0.122, "root": "非自然图像-彩色动漫", "keyword": "二次元" }
  ],
  "result_num": 5,
  "log_id": "2062765136368451022"
}
```

| 字段 | 含义 |
|------|------|
| `result` | 识别结果数组，按置信度降序排列 |
| `result_num` | 返回的结果数量 |
| `log_id` | 请求日志 ID，排查问题时使用 |
| `error_code` | 错误码（仅失败时出现） |
| `error_msg` | 错误信息（仅失败时出现） |

---

### 15. 图像预处理与 Base64 编码

#### 15.1 为什么需要 Base64 编码

HTTP 请求的 body 通常是文本格式。图片是二进制数据，不能直接放在 `application/x-www-form-urlencoded` 格式的请求体中。

Base64 编码把任意二进制数据转换为 ASCII 字符串：

```
原始字节: [0x89, 0x50, 0x4E, 0x47, ...]
Base64:   "iVBORw0KGgo..."（纯文本，可在 HTTP 中传输）
```

代价：编码后数据体积增大约 33%。

#### 15.2 Python 中的 Base64 操作

```python
import base64

# 编码：二进制 → Base64 字符串
with open("photo.jpg", "rb") as f:
    image_bytes = f.read()
image_base64 = base64.b64encode(image_bytes).decode("utf-8")

# 解码：Base64 字符串 → 二进制
image_bytes = base64.b64decode(image_base64)
```

#### 15.3 图像预处理流程

在调用识别 API 之前，通常需要对图像进行预处理：

```
原始图片 → 校验格式/大小 → 读取为字节 → Base64 编码 → 发送 API 请求
```

更复杂的场景还可能包括：
- **缩放**：统一到模型要求的输入尺寸（如 224×224）
- **归一化**：像素值从 0~255 缩放到 0~1 或 -1~1
- **通道转换**：BGR ↔ RGB
- **裁剪**：去除无关区域

百度 API 内部会自动处理这些预处理，所以本项目只需要提供原始图片即可。

---

## 第三部分：动手实践

---

### 练习 1：理解 API 请求流程

**目标**：用 curl 或 Postman 手动调用后端 API，理解完整的请求-响应流程。

**步骤**：

1. 启动后端服务
2. 调用登录接口获取 token：
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"demo","password":"123456"}'
   ```
3. 用返回的 token 调用任务列表：
   ```bash
   curl http://localhost:8000/api/tasks \
     -H "Authorization: Bearer {你的token}"
   ```
4. 用浏览器访问 `http://localhost:8000/docs` 查看自动生成的 API 文档

**思考**：
- 如果 token 过期了，请求会返回什么状态码？
- 如果不带 Authorization 头，会发生什么？
- API 文档是如何自动生成的？

---

### 练习 2：手动调用百度 API

**目标**：绕过本系统，直接用 Python 脚本调用百度 API，理解原始的 API 交互。

**代码**：

```python
import base64
import httpx
import asyncio

API_KEY = "你的API Key"
SECRET_KEY = "你的Secret Key"

async def main():
    async with httpx.AsyncClient() as client:
        # 1. 获取 access_token
        resp = await client.post(
            "https://aip.baidubce.com/oauth/2.0/token",
            params={
                "grant_type": "client_credentials",
                "client_id": API_KEY,
                "client_secret": SECRET_KEY,
            },
        )
        token = resp.json()["access_token"]
        print(f"Token: {token[:20]}...")

        # 2. 读取图片并编码
        with open("test.jpg", "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        # 3. 调用识别接口
        resp = await client.post(
            f"https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token={token}",
            data={"image": image_base64},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        result = resp.json()

        # 4. 解析结果
        for item in result.get("result", []):
            print(f"关键词: {item['keyword']}, 类别: {item['root']}, 置信度: {item['score']:.2%}")

asyncio.run(main())
```

**思考**：
- access_token 的有效期是多久？如何判断 token 是否过期？
- 如果图片很大（如 5MB），Base64 编码后有多大？
- 百度 API 的响应时间大概是多少？

---

### 练习 3：修改识别结果展示

**目标**：修改前端 `ResultList.vue` 组件，添加新的展示方式。

**任务 A**：添加置信度颜色渐变

修改 `getScoreColor` 函数，使用更平滑的颜色过渡：

```typescript
function getScoreColor(score: number): string {
  // 从红色(低) → 黄色(中) → 绿色(高)
  if (score >= 0.6) return '#67c23a'  // 绿色
  if (score >= 0.4) return '#e6a23c'  // 黄色
  return '#f56c6c'                     // 红色
}
```

**任务 B**：添加结果统计摘要

在结果表格上方添加统计信息：

```vue
<div class="result-summary">
  <el-statistic title="识别数量" :value="items.length" />
  <el-statistic title="最高置信度" :value="formatScore(items[0]?.score || 0)" />
  <el-statistic title="主要类别" :value="items[0]?.root || '-'" />
</div>
```

---

### 练习 4：扩展系统功能

选择以下任一任务进行扩展：

**A. 添加图片大小限制提示**

在上传页面显示文件大小进度条，当文件超过 5MB 时变色警告。

**B. 添加识别历史统计**

在任务列表页面上方添加统计卡片：总任务数、成功率、最近一次识别时间。

**C. 实现识别结果导出**

在任务详情页添加「导出为 JSON」按钮，将识别结果下载为 JSON 文件。

```typescript
function exportResult(result: DetectionResult) {
  const data = JSON.stringify(result, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `result_${result.task_id}.json`
  a.click()
  URL.revokeObjectURL(url)
}
```

**D. 使用 httpx 同步客户端替代异步**

思考：如果把 `detection_api.py` 中的 `httpx.AsyncClient` 改为 `httpx.Client`（同步），在什么场景下会出问题？为什么本项目要在后台任务中使用同步调用？

---

## 附录

### 常见问题

**Q: 为什么不用 WebSocket 实时推送识别结果，而用轮询？**

A: 轮询实现简单，适合识别耗时较短（几秒）的场景。WebSocket 适合需要实时双向通信的场景（如聊天、协同编辑），实现复杂度更高。

**Q: SQLite 在并发场景下会有问题吗？**

A: 会。SQLite 使用文件锁，同一时刻只允许一个写操作。本项目是学习项目，使用 SQLite 足够。生产环境应使用 MySQL 或 PostgreSQL。

**Q: 为什么用 JWT 而不用 Session？**

A: 前后端分离架构下，JWT 更合适。后端不需要存储会话状态（无状态），更容易水平扩展。缺点是 JWT 签发后无法主动失效（需要配合黑名单机制）。

### 推荐阅读

- [FastAPI 官方文档](https://fastapi.tiangolo.com/zh/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/)
- [百度 AI 开放平台文档](https://ai.baidu.com/ai-doc)
- [CS231n: 卷积神经网络视觉识别](https://cs231n.stanford.edu/)
- [动手学深度学习 (d2l.ai)](https://zh.d2l.ai/)
