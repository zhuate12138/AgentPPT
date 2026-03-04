# AgentPPT

**用自然语言创建和编辑 PPT，让 Agent 帮你做幻灯片。**

AgentPPT 是一个基于大模型 Agent 的 PPT 创建与编辑工具。输入主题或编辑指令，Agent 自动生成或修改演示文稿；编辑时提供类似 Cursor 的交互：实时预览、同意/取消单次修改、多版本保存与恢复。

---

## ✨ 功能特性

### PPT 创建

- **主题驱动**：输入主题，Agent 自动生成大纲与各页内容
- **辅助材料**：支持上传与主题相关的文档辅助生成
- **双模式**：
  - **无模板模式**：由 Agent 自由排版与生成
  - **有模板模式**：上传或选择模板，Agent 在占位符内填充内容

### PPT 编辑

- **自然语言编辑**：用文字描述修改意图，Agent 理解并执行
- **实时预览**：缩略图列表 + 当前页大图，修改后即时刷新
- **同意 / 取消**：满意则确认保存，不满意则一键回退
- **多版本管理**：保存多个版本，可随时恢复到任意版本

---

## 🛠 技术栈

| 层级     | 技术 |
|----------|------|
| 后端     | Python 3.10+ · FastAPI · LangChain · python-pptx |
| 前端     | Vue 3 · TypeScript · Pinia |
| 大模型   | OpenAI / Anthropic / 国产大模型（通过环境变量配置） |

---

## 📦 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- LibreOffice（可选，用于生成预览图）

### 1. 克隆项目

```bash
git clone https://github.com/zhuate12138/AgentPPT.git
cd AgentPPT
```

### 2. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入你的 API Key：

```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# 或使用 Anthropic
# ANTHROPIC_API_KEY=your-anthropic-api-key
# LLM_PROVIDER=anthropic
```

### 3. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 即可使用。

---

## 📁 项目结构

```
AgentPPT/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/          # API 路由
│   │   ├── agents/          # LangChain Agent
│   │   ├── services/        # 业务服务层
│   │   ├── models/          # 数据模型
│   │   └── core/            # 配置
│   ├── main.py              # 入口文件
│   └── requirements.txt
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── api/             # API 调用
│   │   ├── stores/          # Pinia 状态
│   │   └── router/          # 路由配置
│   └── package.json
├── data/                    # 数据存储目录
│   ├── projects/            # 项目文件
│   └── templates/           # 模板文件
└── docs/                    # 文档
    ├── TECHNICAL_DESIGN.md  # 技术设计
    └── API.md               # API 文档
```

---

## 📚 文档

- [技术设计文档](docs/TECHNICAL_DESIGN.md) - 架构设计与实现细节
- [API 文档](docs/API.md) - RESTful API 接口说明
- [开发指南](docs/DEVELOPMENT.md) - 本地开发与调试

---

## 🔧 API 概览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/projects` | POST | 创建新 PPT |
| `/api/v1/projects` | GET | 获取项目列表 |
| `/api/v1/projects/{id}` | GET | 获取项目详情 |
| `/api/v1/projects/{id}/edit` | POST | 编辑 PPT |
| `/api/v1/projects/{id}/confirm` | POST | 确认编辑 |
| `/api/v1/projects/{id}/cancel` | POST | 取消编辑 |

完整 API 文档见 [docs/API.md](docs/API.md) 或启动后访问 `/docs`。

---

## 🚀 部署

### Docker 部署（推荐）

```bash
docker-compose up -d
```

### 手动部署

1. 构建前端：`cd frontend && npm run build`
2. 配置 Nginx 托管静态文件并代理 API
3. 使用 Gunicorn/Uvicorn 运行后端

---

## 🤝 参与贡献

欢迎提交 Issue 与 Pull Request！

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

---

## 📜 开源协议

MIT License