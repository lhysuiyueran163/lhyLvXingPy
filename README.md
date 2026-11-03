# 旅途 AI 旅行规划助手 - 后端服务

本目录包含「旅途」项目的后端代码，负责 AI Agent 的编排、工具调用、对话状态管理以及行程数据的持久化。

## 🏗️ 技术架构

- **FastAPI**: 提供高性能的异步 Web 服务。
- **LangGraph**: 用于构建循环图结构的 AI 工作流，支持复杂的逻辑判断与状态管理。
- **LangChain**: 封装了与 LLM（大语言模型）的交互逻辑。
- **Ollama**: 本地模型运行时，默认使用 `qwen2.5:7b`。
- **SQLite**: 使用 Python 内置的 `sqlite3` 实现轻量级数据存储。

## 📂 目录结构

```text
backend/
├── app/
│   ├── agent/          # Agent 核心实现
│   │   ├── agent_service.py   # LangGraph 工作流定义
│   │   └── agent_router.py    # 对话接口路由 (SSE)
│   ├── tools/          # 插件工具集
│   │   ├── weather_tool.py    # 天气插件
│   │   ├── budget_tool.py     # 预算插件
│   │   └── ...                # 其他工具 (景点、签证、翻译等)
│   ├── memory/         # 会话记忆管理
│   ├── trips.py        # 行程管理业务逻辑 (CRUD)
│   ├── llm.py          # LLM 实例初始化工厂
│   ├── config.py       # 环境变量与配置项
│   └── main.py         # 服务入口
├── data/               # 数据存储目录 (trips.sqlite3)
├── .env.example        # 环境配置模板
└── requirements.txt    # 依赖清单
```

## 🛠️ 插件工具详情

Agent 能够根据用户需求自动调度以下工具：

| 工具名称 | 功能描述 | 核心逻辑 |
| :--- | :--- | :--- |
| `get_weather` | 查询目的地天气 | 调用外部 API 或返回模拟数据 |
| `get_attractions` | 推荐热门景点 | 提供景点介绍与特色 |
| `generate_itinerary` | 生成逐日行程 | 按天规划活动建议 |
| `calculate_budget` | 估算旅行开销 | 包含交通、餐饮、住宿及景点门票 |
| `check_visa` | 查询签证政策 | 提供目标国家的基本签证要求 |
| `convert_currency` | 汇率转换 | 实时计算不同货币间的价值 |
| `generate_packing_list` | 行李打包建议 | 根据目的地气候生成清单 |
| `translate_phrases` | 旅行常用语翻译 | 支持多语言常用短语翻译 |

## 🚀 启动与配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 环境配置
复制 `.env.example` 为 `.env` 并填写相关配置：
- `OLLAMA_BASE_URL`: 本地 Ollama 服务地址。
- `LLM_PROVIDER`: 选择 `ollama` 或 `deepseek`。
- `DEEPSEEK_API_KEY`: 若使用云端模型，请填写 Key。

### 3. 运行服务
```bash
python app/main.py
```
默认监听 `http://localhost:3000`。

## 📡 API 接口说明

- **对话接口 (SSE)**: `POST /api/chat` - 支持流式输出的 AI 对话接口。
- **工具调用**: `GET /api/tools` - 获取当前已注册的工具列表。
- **行程管理**:
    - `POST /api/trips`: 创建新行程。
    - `GET /api/trips`: 获取所有行程列表。
    - `DELETE /api/trips/{id}`: 删除指定行程。

详细接口文档请启动服务后访问: [http://localhost:3000/docs](http://localhost:3000/docs)

---

## 🔒 注意事项
- 本后端采用跨域 (CORS) 允许机制，默认信任 `http://localhost:5173`。
- 本地开发建议配合 Ollama 使用以获得最佳响应速度。
