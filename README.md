# The Captain's Log

## 项目简介

"The Captain's Log" 是一个基于 FastAPI 框架构建的 Python 应用程序。它集成了数据存储、大型语言模型 (LLM) 和天气 API 功能，旨在提供一个多功能的日志记录和信息检索平台。

**主要功能:**
*   **RAG Agent:** 基于 LangGraph 实现端到端知识检索与生成，支持意图分类、时间窗、预过滤、向量+FTS 混合检索及带历史上下文的生成。
*   **RESTful API:** 提供一套完整的 RESTful API 接口，用于数据的创建、读取、更新和删除。
*   **数据库集成:** 支持 SQLite 和 PostgreSQL 数据库，用于持久化存储数据。
*   **LLM 集成:** 利用大型语言模型进行智能处理和分析。
*   **天气 API 集成:** 获取实时的天气信息。
*   **新闻API 集成：**  获取实时新闻信息
*   **CORS 支持:** 允许跨域请求，方便前端应用集成。

## 技术栈
*   **智能体:** LangGraph, pgvector, Sentence Transformers, RRF
*   **后端:** Python, FastAPI
*   **数据库:** SQLite, PostgreSQL
*   **其他库:** Uvicorn, Sentence Transformers, Pydantic Settings, Dotenv

## 运行项目

### 1. 环境准备

确保您的系统已安装 Python 3.10+ 和 pip。

### 2. 克隆仓库

```bash
git clone https://github.com/examplelala/the_captains_log.git
cd the_captains_log
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

项目使用环境变量来管理敏感信息和配置。请根据'.env.example' 创建一个 `.env` 文件在项目根目录，并根据 `config.py` 中的 `Settings` 类定义填写以下变量：

```ini
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=your_llm_base_url_here
LLM_MODEL_NAME=your_llm_model_name_here
# 如果使用 SQLite
SQLITE_URL=postgresql+asyncpg://user:password@localhost:5432/mydb
# 如果使用 PostgreSQL
# POSTGRES_URL=postgresql+asyncpg://user:password@localhost:5432/mydb 
```

**请务必替换占位符为您实际的 API 密钥、URL 和模型名称。**

### 5. 运行应用程序

```bash
python main.py
```

应用程序将会在 `http://0.0.0.0:18080` 上运行。您可以通过浏览器访问 `http://0.0.0.0:18080` 查看 "Hello World" 消息。

### 6. 访问 API 文档

当应用程序运行后，您可以访问以下 URL 查看自动生成的 API 文档：

*   **Swagger UI:** `http://0.0.0.0:18080/docs`
*   **ReDoc:** `http://0.0.0.0:18080/redoc`

## License

MIT License © 2025 Your Name
