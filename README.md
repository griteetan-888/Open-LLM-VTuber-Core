# Open-LLM-VTuber Core

这是一个精简版的Open-LLM-VTuber项目，包含了运行VTuber系统所需的核心文件。

## 项目结构

```
Open-LLM-VTuber-Core/
├── src/                    # 核心源代码
│   └── open_llm_vtuber/   # 主要模块
├── frontend/              # 前端文件
├── live2d-models/         # Live2D模型
├── avatars/               # 角色头像
├── characters/            # 角色配置
├── backgrounds/           # 背景图片
├── models/                # AI模型文件
├── logs/                  # 日志文件
├── cache/                 # 缓存文件
├── chat_history/          # 聊天历史
├── conf.yaml              # 配置文件
├── model_dict.json        # 模型字典
├── run_server.py          # 启动脚本
├── requirements.txt       # 依赖文件
└── README.md             # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置

#### 方法 1：使用环境变量（推荐，更安全）

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API 密钥：
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

3. 在 `conf.yaml` 中使用环境变量：
```yaml
character_config:
  agent_config:
    agent_settings:
      basic_memory_agent:
        llm_provider: 'openai_llm'  # 或 'ollama_llm'
    
    llm_configs:
      openai_llm:
        base_url: 'https://api.openai.com/v1'
        llm_api_key: '${OPENAI_API_KEY}'  # 从环境变量读取
        model: 'gpt-3.5-turbo'  # 使用标准GPT-3.5模型
```

**详细说明请查看 [ENV_SETUP_GUIDE.md](./ENV_SETUP_GUIDE.md)**

#### 方法 2：直接在 conf.yaml 中配置

编辑 `conf.yaml` 文件，直接填入 API 密钥：

```yaml
character_config:
  agent_config:
    agent_settings:
      basic_memory_agent:
        llm_provider: 'openai_llm'  # 或 'ollama_llm'
    
    llm_configs:
      openai_llm:
        base_url: 'https://api.openai.com/v1'
        llm_api_key: 'YOUR_OPENAI_API_KEY'  # 请替换为你的API密钥
        model: 'gpt-3.5-turbo'  # 使用标准GPT-3.5模型
```

### 3. 启动服务器

```bash
python run_server.py
```

### 4. 访问界面

打开浏览器访问：http://localhost:12393

## 主要功能

- 🎭 **Live2D角色**：支持多种Live2D模型
- 🎤 **语音识别**：支持多种ASR引擎
- 🔊 **语音合成**：支持多种TTS引擎
- 🤖 **AI对话**：支持多种LLM提供商
- 💬 **实时交互**：WebSocket实时通信

## 支持的模型

### LLM提供商
- OpenAI GPT
- Anthropic Claude
- Groq
- Ollama (本地)

### TTS引擎
- Edge TTS
- Azure TTS
- pyttsx3

### ASR引擎
- sherpa-onnx
- Whisper

## 配置说明

### 基本配置
- `system_config`: 系统设置（端口、主机等）
- `character_config`: 角色设置（人格、模型等）
- `asr_config`: 语音识别设置
- `tts_config`: 语音合成设置

### 角色配置
在 `characters/` 目录下可以添加自定义角色配置文件。

## 注意事项

1. 首次运行需要下载模型文件，请确保网络连接正常
2. 某些模型需要GPU支持，请根据你的硬件配置选择合适的模型
3. API密钥请妥善保管，不要泄露给他人

## 故障排除

如果遇到问题，请检查：
1. 依赖是否正确安装
2. 配置文件是否正确
3. 网络连接是否正常
4. 查看日志文件获取详细错误信息

## 许可证

本项目基于MIT许可证开源。
