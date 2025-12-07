# 环境变量配置指南

本指南说明如何使用 `.env` 文件来安全地管理 API 密钥和其他敏感配置。

## 📋 为什么使用环境变量？

- ✅ **安全性**：API 密钥不会提交到 Git 仓库
- ✅ **灵活性**：不同环境可以使用不同的配置
- ✅ **便捷性**：无需修改 `conf.yaml` 文件

## 🚀 快速开始

### 1. 安装依赖

确保已安装 `python-dotenv`：

```bash
pip install python-dotenv
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 创建 .env 文件

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
nano .env  # 或使用你喜欢的编辑器
```

### 3. 配置 API 密钥

编辑 `.env` 文件，填入你的实际 API 密钥：

```bash
# .env 文件示例
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here
```

### 4. 在 conf.yaml 中使用环境变量

在 `conf.yaml` 中，使用 `${环境变量名}` 来引用环境变量：

```yaml
llm_configs:
  openai_llm:
    base_url: 'https://api.openai.com/v1'
    llm_api_key: '${OPENAI_API_KEY}'  # 从环境变量读取
    model: 'gpt-3.5-turbo'
```

## 📝 支持的环境变量

### LLM API 密钥

| 环境变量 | 说明 | 使用场景 |
|---------|------|---------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 使用 OpenAI 模型时 |
| `CLAUDE_API_KEY` | Claude API 密钥 | 使用 Claude 模型时 |
| `GROQ_API_KEY` | Groq API 密钥 | 使用 Groq 模型时 |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 使用 DeepSeek 模型时 |
| `ZHIPU_API_KEY` | 智谱 API 密钥 | 使用智谱模型时 |
| `MISTRAL_API_KEY` | Mistral API 密钥 | 使用 Mistral 模型时 |

### TTS 服务配置

| 环境变量 | 说明 | 使用场景 |
|---------|------|---------|
| `AZURE_TTS_API_KEY` | Azure TTS API 密钥 | 使用 Azure TTS 时 |
| `AZURE_TTS_REGION` | Azure 区域 | 使用 Azure TTS 时 |
| `MINIMAX_GROUP_ID` | Minimax 组 ID | 使用 Minimax TTS 时 |
| `MINIMAX_API_KEY` | Minimax API 密钥 | 使用 Minimax TTS 时 |
| `FISH_API_KEY` | Fish API 密钥 | 使用 Fish API TTS 时 |

### ASR 服务配置

| 环境变量 | 说明 | 使用场景 |
|---------|------|---------|
| `AZURE_ASR_API_KEY` | Azure ASR API 密钥 | 使用 Azure ASR 时 |
| `GROQ_WHISPER_API_KEY` | Groq Whisper API 密钥 | 使用 Groq Whisper 时 |

### 其他服务

| 环境变量 | 说明 | 使用场景 |
|---------|------|---------|
| `HUME_AI_API_KEY` | Hume AI API 密钥 | 使用 Hume AI Agent 时 |

## 🔧 使用方法

### 方法 1：在 conf.yaml 中使用环境变量（推荐）

```yaml
llm_configs:
  openai_llm:
    base_url: 'https://api.openai.com/v1'
    llm_api_key: '${OPENAI_API_KEY}'  # 自动从 .env 文件读取
```

### 方法 2：直接在代码中读取

```python
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

api_key = os.getenv("OPENAI_API_KEY")
```

## 📁 文件说明

- **`.env.example`**：环境变量模板文件（可以提交到 Git）
- **`.env`**：实际的环境变量文件（**不要提交到 Git**，已在 `.gitignore` 中）

## ⚠️ 重要提示

1. **不要提交 `.env` 文件到 Git**
   - `.env` 文件已在 `.gitignore` 中
   - 只提交 `.env.example` 作为模板

2. **服务器部署时**
   - 在服务器上创建 `.env` 文件
   - 或使用环境变量注入工具（如 AWS Secrets Manager）

3. **优先级**
   - 如果 `conf.yaml` 中直接写了 API 密钥，会优先使用配置文件中的值
   - 环境变量只在配置文件中使用 `${VAR_NAME}` 时生效

## 🔍 验证配置

启动服务器时，检查日志确认环境变量已加载：

```bash
python run_server.py
```

如果看到类似以下日志，说明环境变量已成功加载：

```
Loaded environment variables from /path/to/.env
```

## 🆘 常见问题

### Q1: 环境变量没有生效？

**检查清单**：
1. ✅ 确认已安装 `python-dotenv`：`pip install python-dotenv`
2. ✅ 确认 `.env` 文件在项目根目录
3. ✅ 确认 `conf.yaml` 中使用 `${VAR_NAME}` 格式
4. ✅ 检查环境变量名称是否正确（区分大小写）

### Q2: 如何在不同环境使用不同配置？

**解决方案**：
- 开发环境：使用 `.env` 文件
- 生产环境：使用系统环境变量或密钥管理服务
- 测试环境：使用 `.env.test` 文件（需要修改代码加载不同文件）

### Q3: 可以在 conf.yaml 中混合使用环境变量和直接值吗？

**可以**：
```yaml
llm_configs:
  openai_llm:
    base_url: 'https://api.openai.com/v1'  # 直接值
    llm_api_key: '${OPENAI_API_KEY}'        # 环境变量
    model: 'gpt-3.5-turbo'                  # 直接值
```

## 📚 更多信息

- [python-dotenv 文档](https://github.com/theskumar/python-dotenv)
- [环境变量最佳实践](https://12factor.net/config)

