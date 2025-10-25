# 配置指南

## OpenAI API 配置

### 1. 获取API密钥

1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册或登录账户
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制生成的密钥（格式：`sk-...`）

### 2. 配置API密钥

编辑 `conf.yaml` 文件，找到以下部分：

```yaml
llm_configs:
  openai_llm:
    base_url: 'https://api.openai.com/v1'
    llm_api_key: 'YOUR_OPENAI_API_KEY_HERE'  # 替换为你的API密钥
    model: 'gpt-3.5-turbo'
    temperature: 0.8
    max_tokens: 1000
```

将 `YOUR_OPENAI_API_KEY_HERE` 替换为你的实际API密钥。

### 3. 模型选择

当前配置使用标准的 `gpt-3.5-turbo` 模型，你也可以选择其他模型：

- `gpt-3.5-turbo` - 标准GPT-3.5模型（推荐）
- `gpt-4` - GPT-4模型（更强大但更昂贵）
- `gpt-4-turbo` - GPT-4 Turbo模型

### 4. 参数调整

- `temperature`: 控制回复的随机性（0.0-2.0）
  - 0.0: 完全确定性的回复
  - 1.0: 平衡的创造性
  - 2.0: 高度随机

- `max_tokens`: 最大回复长度
  - 建议值：500-2000
  - 更长的回复需要更多token

## 其他LLM配置

### Ollama（本地模型）

如果你想使用本地模型，可以配置Ollama：

```yaml
llm_configs:
  ollama_llm:
    base_url: 'http://127.0.0.1:11434/v1'
    model: 'llama3.1:8b'  # 或其他模型
    api_key: "dummy"
    temperature: 1.2
    max_tokens: 2000
```

然后修改agent设置：

```yaml
agent_settings:
  basic_memory_agent:
    llm_provider: 'ollama_llm'  # 改为使用Ollama
```

### Claude（Anthropic）

```yaml
llm_configs:
  claude_llm:
    base_url: 'https://api.anthropic.com'
    llm_api_key: 'YOUR_CLAUDE_API_KEY'
    model: 'claude-3-haiku-20240307'
```

## 语音配置

### TTS（文本转语音）

当前使用Edge TTS（免费）：

```yaml
tts_config:
  tts_model: 'edge_tts'
  edge_tts:
    voice: 'en-US-AvaMultilingualNeural'  # 可以更换其他声音
```

### ASR（语音识别）

当前使用sherpa-onnx（本地）：

```yaml
asr_config:
  asr_model: 'sherpa_onnx_asr'
  sherpa_onnx_asr:
    model_type: 'sense_voice'
    sense_voice: './models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17/model.int8.onnx'
    tokens: './models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17/tokens.txt'
    num_threads: 4
    use_itn: True
    provider: 'cpu'
```

## 角色配置

### 修改角色人格

编辑 `persona_prompt` 部分来自定义角色：

```yaml
persona_prompt: |
  You are **Kiyo**, the seventh princess of Planet Nota...
  # 在这里修改角色的背景故事和性格
```

### 更换角色

1. 在 `characters/` 目录下创建新的角色配置文件
2. 修改 `conf.yaml` 中的角色设置：

```yaml
character_config:
  conf_name: 'your_character'  # 角色配置文件名
  character_name: 'Your Character'  # 角色显示名称
  avatar: 'your_avatar.png'  # 头像文件
```

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查密钥是否正确复制
   - 确认账户有足够的余额

2. **模型加载失败**
   - 检查网络连接
   - 确认模型名称正确

3. **语音识别不工作**
   - 检查麦克风权限
   - 确认ASR模型文件存在

### 日志查看

查看日志文件获取详细错误信息：

```bash
tail -f logs/debug_$(date +%Y-%m-%d).log
```

## 性能优化

### 降低延迟

1. 使用更快的模型（如GPT-3.5）
2. 减少max_tokens
3. 启用faster_first_response

### 节省成本

1. 使用本地模型（Ollama）
2. 降低temperature
3. 减少max_tokens

## 安全注意事项

1. **不要提交API密钥到版本控制**
2. **使用环境变量存储敏感信息**
3. **定期轮换API密钥**
4. **监控API使用量**

