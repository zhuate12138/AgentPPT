# 开发指南

## 环境准备

### 必需软件

- **Python 3.10+**
- **Node.js 18+**
- **Git**

### 可选软件

- **LibreOffice** - 用于生成 PPT 预览图
- **Docker** - 容器化部署

---

## 本地开发

### 1. 克隆代码

```bash
git clone https://github.com/zhuate12138/AgentPPT.git
cd AgentPPT
```

### 2. 后端设置

```bash
# 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动开发服务器
uvicorn main:app --reload --port 8000
```

后端启动后：
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后：http://localhost:5173

---

## 项目架构

### 后端模块

```
backend/app/
├── api/v1/          # API 路由
│   ├── projects.py  # 项目相关接口
│   └── health.py    # 健康检查
├── agents/          # LangChain Agent
│   └── ppt_agents.py # PPT 创建/编辑 Agent
├── services/        # 业务服务
│   ├── ppt_service.py   # PPT 文件操作
│   └── preview_service.py # 预览图生成
├── models/          # Pydantic 数据模型
│   └── ppt.py
├── core/            # 配置
│   └── config.py
└── utils/           # 工具函数
```

### 前端模块

```
frontend/src/
├── views/           # 页面组件
│   ├── HomeView.vue     # 首页（创建 PPT）
│   ├── ProjectsView.vue # 项目列表
│   ├── ProjectView.vue  # 项目详情
│   └── EditView.vue     # 编辑页面
├── api/             # API 调用
│   └── index.ts
├── stores/          # Pinia 状态管理
│   └── projects.ts
├── router/          # Vue Router
│   └── index.ts
└── assets/          # 静态资源
    └── main.css
```

---

## 核心流程

### 创建 PPT 流程

```
用户输入主题
    ↓
前端 POST /projects
    ↓
后端调用 LangChain Agent 生成大纲
    ↓
python-pptx 生成 .pptx 文件
    ↓
生成预览图
    ↓
返回项目 ID 和预览
```

### 编辑 PPT 流程

```
用户输入编辑指令
    ↓
前端 POST /projects/{id}/edit
    ↓
后端组装上下文（摘要 + 当前页详情）
    ↓
LangChain Agent 生成编辑指令（JSON）
    ↓
执行指令修改 PPT
    ↓
生成新预览图
    ↓
用户确认/取消
```

---

## 调试技巧

### 查看 API 日志

后端使用 FastAPI，启动时添加 `--reload` 会自动重载。

```bash
uvicorn main:app --reload --log-level debug
```

### 测试 Agent

```python
# 在 backend/ 目录下
python -c "
from app.agents.ppt_agents import generate_ppt_outline
import asyncio

result = asyncio.run(generate_ppt_outline('人工智能'))
print(result.model_dump_json(indent=2))
"
```

### 测试 PPT 服务

```python
# 在 backend/ 目录下
python -c "
from app.services.ppt_service import PPTService

svc = PPTService()
project_id, _ = svc.create_project('Test', 'Test topic')
version, count = svc.create_pptx(project_id, [
    {'title': 'Hello', 'body': ['Point 1', 'Point 2']}
])
print(f'Created project {project_id}, version {version}, {count} slides')
"
```

---

## 常见问题

### Q: 预览图显示占位符？

A: 需要安装 LibreOffice：

```bash
# Ubuntu/Debian
sudo apt install libreoffice

# macOS
brew install libreoffice

# Windows
# 下载安装包：https://www.libreoffice.org/download/
```

### Q: LLM 调用失败？

A: 检查 `.env` 中的 API Key 配置：

```bash
# OpenAI
OPENAI_API_KEY=sk-xxx
LLM_PROVIDER=openai

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxx
LLM_PROVIDER=anthropic
```

### Q: 前端无法连接后端？

A: 检查 `frontend/vite.config.ts` 的代理配置：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

---

## 测试

### 后端测试

```bash
cd backend
pytest
```

### 前端测试

```bash
cd frontend
npm run test
```

---

## 构建与部署

### 构建前端

```bash
cd frontend
npm run build
# 输出到 frontend/dist/
```

### 生产运行

```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 贡献代码

1. Fork 仓库
2. 创建特性分支：`git checkout -b feature/xxx`
3. 提交代码：`git commit -m 'feat: xxx'`
4. 推送分支：`git push origin feature/xxx`
5. 创建 Pull Request

### 代码规范

- Python: 遵循 PEP 8
- TypeScript: ESLint + Prettier
- Commit: Conventional Commits