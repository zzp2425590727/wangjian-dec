# 简易物体识别系统开发文档

## 1. 文档目的

本文档用于指导前端、后端工程师共同开发一个简易物体识别系统。系统包含基础用户登录，支持登录用户上传图片，并通过外接百度图像识别 API 完成物体识别，最终在页面中展示识别关键词、类别、置信度和任务状态。

本文档重点约定系统边界、模块职责、接口设计、数据结构、开发流程和测试要求，便于前后端并行开发。

## 2. 系统目标

### 2.1 核心功能

- 支持图片上传并执行物体识别。
- 支持基础用户登录和退出。
- 图片识别完成后展示原图、识别关键词、类别和置信度。
- 支持登录用户查看自己的识别任务列表和单个任务详情。
- 后端统一对接百度图像识别 API，前端不直接调用外部识别服务。

### 2.2 非目标功能

- 不在本系统内训练图像识别模型。
- 不在本系统内维护复杂用户权限体系。
- 不做注册、找回密码、角色权限、管理员后台等复杂账号功能。
- 不支持视频识别、实时摄像头识别和批量识别。
- 不要求多模型管理。

## 3. 技术栈

### 3.1 前端

- 框架：Vue 3
- 构建工具：Vite
- 语言：TypeScript
- 状态管理：Pinia
- 路由：Vue Router
- HTTP 请求：Axios
- UI 组件库：Element Plus 或 Ant Design Vue

### 3.2 后端

- 语言：Python 3.10+
- Web 框架：FastAPI
- 数据校验：Pydantic
- 登录认证：JWT
- HTTP 客户端：httpx
- 数据存储：SQLite
- 文件存储：本地文件目录

### 3.3 外部服务

- 百度图像识别 API：使用百度 AI 开放平台的通用物体和场景识别接口。
- 本系统通过后端适配层调用该 API。
- API Key、Secret Key、access_token 缓存时间、超时时间通过后端配置管理。
- 注意：本文档按当前项目要求直接写入 API Key 和 Secret Key，便于简易项目开发调试。正式部署或提交公开仓库前，应改回环境变量占位值。

## 4. 总体架构

系统采用前后端分离架构。

前端负责登录、图片选择、上传、任务状态展示、识别结果可视化和用户交互。后端负责用户认证、图片文件接收、任务创建、百度 API 调用、结果保存和接口响应。

```text
用户浏览器
  |
  | 登录、上传图片、查询任务
  v
Vue 前端应用
  |
  | REST API
  v
Python FastAPI 后端
  |
  | 调用适配层
  v
百度图像识别 API
```

## 5. 业务流程

### 5.1 登录流程

1. 用户输入用户名和密码。
2. 前端调用后端登录接口。
3. 后端校验账号密码。
4. 校验通过后返回访问 token。
5. 前端保存 token，并在后续接口请求中携带该 token。
6. 用户点击退出时，前端清除 token 并返回登录页。

简易项目可以预置一个测试账号，也可以在数据库中初始化少量账号。不要求实现注册和找回密码。

### 5.2 图片识别流程

1. 登录用户在前端选择图片文件。
2. 前端校验文件类型和大小。
3. 前端携带 token 调用后端上传接口。
4. 后端校验登录状态，保存图片文件并创建识别任务。
5. 后端调用百度图像识别 API。
6. 后端解析识别结果并保存。
7. 前端查询任务详情并展示识别关键词、类别和置信度。

## 6. 功能模块

### 6.1 前端模块

#### 6.1.1 登录模块

职责：

- 提供用户名、密码输入表单。
- 调用登录接口并保存 token。
- 登录失败时展示错误提示。
- 未登录访问业务页面时跳转到登录页。
- 提供退出登录入口。

#### 6.1.2 上传模块

职责：

- 提供图片、视频上传入口。
- 限制文件类型和大小。
- 展示上传进度。
- 上传成功后跳转到任务详情页。
- 请求后端时携带登录 token。

建议限制：

- 图片格式：jpg、jpeg、png、webp
- 图片大小：不超过 10 MB

#### 6.1.3 任务列表模块

职责：

- 展示当前登录用户的历史识别任务。
- 展示任务类型、文件名、状态、创建时间。
- 支持进入任务详情。

任务状态：

- pending：等待处理
- processing：处理中
- success：处理成功
- failed：处理失败

#### 6.1.4 任务详情模块

职责：

- 展示任务基础信息。
- 展示图片识别结果。
- 处理任务失败信息展示。
- 对处理中任务进行轮询。

图片结果展示：

- 原图预览。
- 识别结果列表。
- 每条结果展示 keyword、root 和 score。

#### 6.1.5 API 服务模块

职责：

- 封装后端 API 请求。
- 统一处理请求错误。
- 统一注入登录 token。
- 统一管理接口类型定义。

### 6.2 后端模块

#### 6.2.1 API 路由模块

职责：

- 接收前端请求。
- 校验需要登录的接口。
- 返回任务状态、任务详情和文件访问地址。
- 不直接包含复杂识别逻辑。

#### 6.2.2 认证模块

职责：

- 校验用户名和密码。
- 签发访问 token。
- 从请求头中解析当前登录用户。
- 为任务接口和文件接口提供登录校验。

#### 6.2.3 任务服务模块

职责：

- 创建识别任务。
- 记录任务所属用户。
- 更新任务状态。
- 保存识别结果。
- 提供当前登录用户的任务查询能力。

#### 6.2.4 文件服务模块

职责：

- 保存上传文件。
- 生成文件访问路径。
- 校验文件类型和大小。
- 管理原始图片文件和识别结果文件。

#### 6.2.5 识别适配器模块

职责：

- 封装百度图像识别 API。
- 处理鉴权、超时、重试和响应解析。
- 将外部 API 响应转换为系统内部统一结果格式。

## 7. 数据模型

### 7.1 User

```json
{
  "id": "user_001",
  "username": "demo",
  "password_hash": "hashed_password",
  "created_at": "2026-06-05T12:00:00+08:00"
}
```

字段说明：

- id：用户唯一标识。
- username：登录用户名。
- password_hash：密码哈希值，后端不得保存明文密码。
- created_at：用户创建时间。

### 7.2 LoginResponse

```json
{
  "access_token": "token_string",
  "token_type": "bearer",
  "user": {
    "id": "user_001",
    "username": "demo"
  }
}
```

### 7.3 DetectionTask

```json
{
  "id": "task_001",
  "user_id": "user_001",
  "file_name": "demo.jpg",
  "media_type": "image",
  "status": "success",
  "created_at": "2026-06-05T12:00:00+08:00",
  "updated_at": "2026-06-05T12:00:10+08:00",
  "original_file_url": "/files/task_001/original.jpg",
  "result_file_url": "/files/task_001/result.jpg",
  "error_message": null
}
```

字段说明：

- id：任务唯一标识。
- user_id：任务所属用户。
- file_name：用户上传的原始文件名。
- media_type：固定为 image。
- status：任务状态。
- original_file_url：原始文件访问地址。
- result_file_url：结果文件访问地址，可为空。
- error_message：失败原因，可为空。

### 7.4 ClassificationItem

```json
{
  "keyword": "卡通动漫人物",
  "root": "非自然图像-彩色动漫",
  "score": 0.381087
}
```

字段说明：

- keyword：识别关键词。
- root：识别结果所属大类。
- score：置信度分数，范围通常为 0 到 1。

### 7.5 ImageDetectionResult

```json
{
  "task_id": "task_001",
  "result_num": 5,
  "items": [
    {
      "keyword": "卡通动漫人物",
      "root": "非自然图像-彩色动漫",
      "score": 0.381087
    }
  ],
  "raw_log_id": "2062765136368451022"
}
```

字段说明：

- result_num：百度接口返回的识别结果数量。
- items：统一后的识别结果列表。
- raw_log_id：百度接口返回的 log_id，便于排查问题。

## 8. 后端接口设计

除登录接口外，业务接口都需要携带请求头：

```http
Authorization: Bearer {access_token}
```

### 8.1 用户登录

```http
POST /api/auth/login
Content-Type: application/json
```

请求：

```json
{
  "username": "demo",
  "password": "123456"
}
```

响应：

```json
{
  "access_token": "token_string",
  "token_type": "bearer",
  "user": {
    "id": "user_001",
    "username": "demo"
  }
}
```

处理规则：

- 用户名或密码错误时返回 401。
- 简易项目可以在数据库初始化时预置测试账号。
- token 过期时间建议设置为 24 小时。

### 8.2 获取当前用户

```http
GET /api/auth/me
```

响应：

```json
{
  "id": "user_001",
  "username": "demo"
}
```

### 8.3 上传并创建识别任务

```http
POST /api/tasks
Content-Type: multipart/form-data
```

请求参数：

- file：图片文件。
- media_type：固定为 image。

响应：

```json
{
  "id": "task_001",
  "status": "pending",
  "media_type": "image"
}
```

处理规则：

- 图片任务可同步处理，也可创建任务后立即异步处理。
- 任务必须绑定当前登录用户。

### 8.4 获取任务列表

```http
GET /api/tasks
```

查询参数：

- page：页码，默认 1。
- page_size：每页数量，默认 20。
- status：可选，按任务状态过滤。

响应：

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

处理规则：

- 只返回当前登录用户创建的任务。

### 8.5 获取任务详情

```http
GET /api/tasks/{task_id}
```

响应：

```json
{
  "task": {},
  "result": {}
}
```

处理规则：

- 只能查询当前登录用户自己的任务。
- 查询其他用户任务时返回 404 或 403，推荐返回 404 减少信息暴露。

### 8.6 获取文件

```http
GET /api/files/{task_id}/{file_path}
```

说明：

- 用于访问原始图片和结果相关文件。
- 后端必须限制访问路径，避免任意文件读取。
- 只能访问当前登录用户自己的任务文件。

## 9. 百度图像识别 API 约定

后端通过识别适配器调用百度 AI 开放平台接口。前端不得直接调用百度接口，也不得接触 API Key 和 Secret Key。

### 9.1 获取百度 access_token

```http
POST https://aip.baidubce.com/oauth/2.0/token
```

请求参数：

- grant_type：固定为 client_credentials。
- client_id：百度 API Key，从环境变量 BAIDU_API_KEY 读取。
- client_secret：百度 Secret Key，从环境变量 BAIDU_SECRET_KEY 读取。

处理规则：

- 后端启动后可按需获取 access_token。
- access_token 应缓存，避免每次识别都重新获取。
- access_token 失效或接口返回鉴权失败时，重新获取一次并重试。

### 9.2 图像识别请求

```http
POST https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token={access_token}
Content-Type: application/x-www-form-urlencoded
Accept: application/json
```

请求参数二选一：

- image：图片文件的 Base64 编码，适合本系统上传到后端的本地文件。
- url：可公网访问的图片地址，适合已有公网图片链接。

本系统推荐使用 image 参数。因为用户上传文件保存在后端本地，通常没有公网 URL。

请求示例：

```text
image={urlencoded_base64_image}
```

### 9.3 百度 API 响应

```json
{
  "result": [
    {
      "score": 0.381087,
      "root": "非自然图像-彩色动漫",
      "keyword": "卡通动漫人物"
    },
    {
      "score": 0.323093,
      "root": "非自然图像-彩色动漫",
      "keyword": "彩色动漫"
    }
  ],
  "result_num": 5,
  "log_id": "2062765136368451022"
}
```

### 9.4 适配规则

- result 转换为系统内部的 items。
- keyword 保持为识别关键词。
- root 保持为识别大类。
- score 保持为置信度分数。
- result_num 保存为识别结果数量。
- log_id 保存为 raw_log_id，便于排查问题。
- 如果百度接口返回 error_code 或 error_msg，任务状态更新为 failed，并将 error_msg 记录到 error_message。
- 百度 advanced_general 接口不返回检测框坐标，因此首版前端不绘制 bbox 检测框，只展示识别结果列表和视频帧识别摘要。

## 10. 异常处理

### 10.1 前端异常处理

- 登录失败时，展示用户名或密码错误提示。
- token 失效时，清除本地 token 并跳转登录页。
- 上传文件类型不合法时，前端直接提示用户。
- 上传文件过大时，前端直接提示用户。
- 接口请求失败时，展示可读错误信息。
- 视频任务处理中，页面应展示 loading 状态。
- 任务失败时，展示后端返回的 error_message。

### 10.2 后端异常处理

- 用户名或密码错误：返回 401。
- 未登录或 token 无效：返回 401。
- 当前用户访问不属于自己的任务：返回 404 或 403。
- 文件保存失败：任务状态更新为 failed。
- 外部 API 超时：任务状态更新为 failed，并记录超时原因。
- 外部 API 响应格式异常：任务状态更新为 failed，并记录解析失败原因。
- 视频抽帧失败：任务状态更新为 failed。
- 未找到任务：返回 404。
- 文件类型不支持：返回 400。

## 11. 前后端协作约定

### 11.1 接口优先

前后端先根据本文档确认 API 请求和响应结构。后端可先提供登录接口和 mock 识别结果，前端基于 mock 数据开发页面。

### 11.2 类型一致

前端 TypeScript 类型应与后端 Pydantic 模型保持一致。接口字段变更时，后端需要同步通知前端并更新文档。

### 11.3 登录态约定

前端登录成功后保存 access_token。后续业务请求统一在请求头中加入 Authorization。退出登录时，前端清除 token 并跳转登录页。

### 11.4 识别结果展示约定

百度 advanced_general 接口返回分类识别结果，不返回检测框坐标。前端首版展示识别结果列表即可，按 score 从高到低排序，展示字段包括 keyword、root 和 score。

### 11.5 任务状态轮询

前端在任务状态为 pending 或 processing 时，每 2 秒查询一次任务详情。任务完成或失败后停止轮询。

## 12. 配置项

后端建议使用环境变量管理配置。

```text
APP_ENV=development
DATABASE_URL=sqlite:///./data/app.db
UPLOAD_DIR=./data/uploads
JWT_SECRET_KEY=replace-with-random-secret
JWT_EXPIRE_HOURS=24
BAIDU_API_KEY=LqawwYAjyB0JQxIa0Q04cfHu
BAIDU_SECRET_KEY=S6jCO8z1RCGeuO3vIDBDEHdYNQhkCkMi
BAIDU_TOKEN_URL=https://aip.baidubce.com/oauth/2.0/token
BAIDU_DETECT_URL=https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general
BAIDU_API_TIMEOUT_SECONDS=30
VIDEO_FRAME_INTERVAL_SECONDS=1
MAX_IMAGE_SIZE_MB=10
MAX_VIDEO_SIZE_MB=200
```

前端建议使用环境变量管理 API 地址。

```text
VITE_API_BASE_URL=http://localhost:8000
```

## 13. 推荐目录结构

### 13.1 前端目录

```text
frontend/
  src/
    api/
      authApi.ts
      taskApi.ts
    components/
      ResultList.vue
      FileUploader.vue
      TaskStatusTag.vue
    pages/
      LoginPage.vue
      UploadPage.vue
      TaskListPage.vue
      TaskDetailPage.vue
    stores/
      authStore.ts
      taskStore.ts
    types/
      auth.ts
      detection.ts
    router/
      index.ts
    main.ts
```

### 13.2 后端目录

```text
backend/
  app/
    main.py
    api/
      routes_auth.py
      routes_tasks.py
      routes_files.py
    core/
      config.py
      security.py
    models/
      user.py
      task.py
      detection.py
    services/
      task_service.py
      file_service.py
    adapters/
      detection_api.py
    db/
      session.py
      repository.py
  tests/
```

## 14. 测试要求

### 14.1 前端测试

- 登录成功后能保存 token 并进入上传页。
- 未登录访问业务页面时跳转登录页。
- 上传组件能正确限制文件类型。
- 上传成功后能进入任务详情页。
- 图片识别结果能按 score 从高到低显示。
- 任务处理中能展示轮询状态。
- 任务失败时能展示错误信息。

### 14.2 后端测试

- 用户登录成功返回 token。
- 用户名或密码错误返回 401。
- 创建图片任务成功。
- 未登录创建任务返回 401。
- 当前用户不能访问其他用户的任务。
- 不支持的文件类型返回 400。
- 外部 API 返回结果能正确转换为内部格式。
- 外部 API 超时能正确更新任务状态。
- 任务详情接口能返回任务和结果。
- 文件接口不能读取任务目录之外的文件。

### 14.3 联调测试

- 用户登录、退出流程。
- 图片上传、识别、展示完整流程。
- 外部 API 不可用时的失败流程。
- 大文件上传失败提示。

## 15. 开发里程碑

### 第一阶段：基础接口和页面

- 后端实现登录、当前用户、任务创建、任务列表、任务详情接口。
- 前端实现登录页、上传页、任务列表页、任务详情页。
- 使用 mock 识别结果完成前后端联调。

### 第二阶段：图片识别

- 后端接入百度图像识别 API。
- 后端保存图片识别结果。
- 前端实现图片识别结果列表展示。

### 第四阶段：稳定性完善

- 增加异常处理。
- 增加接口测试和核心前端测试。
- 优化文件访问安全。
- 补充本地运行和配置说明。

## 16. 部署说明

### 16.1 本地开发启动

前端：

```bash
cd frontend
npm install
npm run dev
```

后端：

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 16.2 生产部署建议

- 简易项目可先使用前端静态构建产物加单个 FastAPI 服务部署。
- 上传目录需要持久化。
- 本文档按项目要求写入百度 API Key 和 Secret Key；后续正式提交公开仓库或生产部署时，应改为通过安全配置注入。

## 17. 安全要求

- 后端必须校验文件扩展名和 MIME 类型。
- 后端必须限制上传文件大小。
- 文件访问接口必须防止路径穿越。
- 任务和文件必须校验当前登录用户。
- 密码不得明文存储。
- JWT_SECRET_KEY 不得使用默认值。
- 百度 API Key、Secret Key 和 access_token 必须通过环境变量或运行时缓存读取。
- 日志中不得打印完整 API Key、Secret Key 或 access_token。
- 上传文件名应由后端重新生成，避免直接使用用户原始文件名作为存储路径。

## 18. 可选后续扩展方向

- 增加注册、找回密码和角色权限。
- 增加模型选择能力。
- 增加实时摄像头识别。
- 增加识别结果导出，例如 CSV、JSON 或图片。
- 增加对象存储支持。

## 19. 开发分工建议

前端工程师：

- 搭建 Vue 项目。
- 实现登录页和登录态管理。
- 实现上传、列表、详情页面。
- 实现识别结果列表组件。
- 封装后端接口请求。
- 完成前端基础测试。

后端工程师：

- 搭建 FastAPI 项目。
- 实现登录认证和当前用户获取接口。
- 实现任务、文件、识别结果接口。
- 实现百度图像识别 API 适配器。
- 完成后端接口测试和异常处理。

共同确认事项：

- 是否使用预置账号，或由数据库初始化脚本创建账号。
- 百度图像识别 API 的真实请求和响应格式。
- 文件大小限制。
- 识别类别名称是否需要中文映射。
