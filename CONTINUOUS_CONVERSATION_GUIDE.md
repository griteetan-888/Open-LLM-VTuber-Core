# 连续性对话功能使用指南

## 🎉 功能已成功配置！

你的Open-LLM-VTuber系统现在已经支持连续性对话功能，Kiyo可以自动继续对话，无需用户每次都输入。

## 🚀 功能特性

### ✅ 已配置的功能

1. **自动对话继续**
   - 当用户消息以 `]` 结尾时，Kiyo会自动继续对话
   - Kiyo会主动提问，保持对话流畅
   - 对话会自然延续，无需用户每次都输入

2. **智能对话流程**
   - 基于用户分享的内容进行后续提问
   - 使用机智的评论和观察
   - 分享相关经验或想法
   - 提出有趣的挑战或场景

3. **自然对话示例**
   - 交通抱怨 → "Traffic? The universe's way of testing your patience. What's your go-to car karaoke song?"
   - 暗恋对象 → "A Leo? Bold choice. Fire signs are like emotional fireworks — beautiful but potentially explosive. What's your move?"
   - 发短信问题 → "Text first? Depends. Are you feeling confident or just emotionally brave today?"

## 📝 使用方法

### 1. 触发连续性对话

**方法一：使用 `]` 结尾**
```
用户: I was stuck in traffic and it's so annoying!]
Kiyo: Traffic? The universe's way of testing your patience. What's your go-to car karaoke song?
```

**方法二：自然对话流程**
```
用户: I met my crush today and froze.. He is a Leo..
Kiyo: A Leo? Bold choice. Fire signs are like emotional fireworks — beautiful but potentially explosive. What's your move?
```

### 2. 对话示例

```
用户: Good Morning.
Kiyo: You are up early, did the sun bribe you or something?

用户: I am up early to chat with you. I wonder why are you here with me?]
Kiyo: I'm here to study human emotions, obviously. But mostly to try out delicious snacks and gossip. What's the most interesting thing that happened to you this week?

用户: So..where are you from exactly?]
Kiyo: I am from Planet Nota, it's a place where emotions shatter into stars and can be collected. Want to hear about the time I accidentally collected someone's breakup emotions? It was... intense.

用户: That's interesting. Would you bring me to planet Nota someday?]
Kiyo: Ha! You'd last five minutes before getting roasted by my siblings. But maybe I'd sneak you in anyway. What's your tolerance for emotional chaos?

用户: Ok, that's just kidding anyways. I was stuck in traffic and it's so annoying!]
Kiyo: Traffic? The universe's way of testing your patience. What's your go-to car karaoke song?

用户: I met my crush today and froze..]
Kiyo: Frozen? Like Elsa but with more awkwardness. What's the move here — play it cool or embrace the chaos?

用户: He is a Leo..]
Kiyo: A Leo? Bold choice. Fire signs are like emotional fireworks — beautiful but potentially explosive. What's your move?

用户: Should I text him first?]
Kiyo: Text first? Depends. Are you feeling confident or just emotionally brave today?
```

## ⚙️ 配置参数

### 在 `conf.yaml` 中的配置

```yaml
agent_settings:
  basic_memory_agent:
    # 连续性对话配置
    enable_continuous_conversation: True  # 启用连续性对话
    conversation_continuation_threshold: 0.7  # 对话继续阈值
    auto_continue_delay: 2  # 自动继续延迟(秒)
    max_consecutive_responses: 5  # 最大连续回复数
```

### 系统提示配置

```yaml
tool_prompts:
  continuous_conversation_prompt: 'continuous_conversation_prompt'
```

## 🧪 测试功能

运行测试脚本验证功能：

```bash
python3 test_continuous_conversation.py
```

## 💡 使用技巧

### 1. 最佳实践

- **自然结尾**: 在消息末尾加上 `]` 来触发连续性对话
- **分享情感**: 分享你的感受，Kiyo会基于此继续对话
- **保持开放**: 让Kiyo知道你想要继续聊天的意愿

### 2. 对话技巧

- **具体描述**: 详细描述你的情况，Kiyo会有更好的回应
- **情感表达**: 表达你的情感状态，Kiyo会相应调整语气
- **问题引导**: 提出开放性问题，让对话自然延续

### 3. 示例对话模式

```
用户: [分享经历] + ]
Kiyo: [机智回应] + [后续问题]

用户: [表达情感] + ]
Kiyo: [情感支持] + [深入探讨]

用户: [提出问题] + ]
Kiyo: [有趣回答] + [新的话题]
```

## 🔧 高级配置

### 自定义连续性对话参数

你可以在 `conf.yaml` 中调整以下参数：

- `conversation_continuation_threshold`: 对话继续的敏感度 (0.0-1.0)
- `auto_continue_delay`: 自动继续的延迟时间 (秒)
- `max_consecutive_responses`: 最大连续回复次数

### 个性化提示

你可以在 `prompts/prompt_loader.py` 中自定义连续性对话的提示内容。

## 🎯 效果展示

**传统对话模式**:
```
用户: I was stuck in traffic.
Kiyo: That sounds frustrating.
[对话结束，需要用户再次输入]
```

**连续性对话模式**:
```
用户: I was stuck in traffic.]
Kiyo: Traffic? The universe's way of testing your patience. What's your go-to car karaoke song?
[对话自然延续，Kiyo主动提问]
```

## 📊 功能状态

- ✅ 连续性对话提示: 已配置
- ✅ 对话流程: 正常工作
- ✅ 配置集成: 已完成
- ✅ 测试验证: 全部通过

## 🚀 开始使用

1. 启动系统: `python3 main.py`
2. 开始对话，在消息末尾加上 `]`
3. 享受Kiyo的连续性对话！

---

**配置完成时间**: 2024-10-25  
**功能状态**: ✅ 完全可用  
**测试状态**: ✅ 全部通过
