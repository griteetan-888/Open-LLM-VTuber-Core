# Open-LLM-VTuber-Core 快速开始指南

## 🚀 版本控制管理快速设置

### 1. 初始化版本控制（已完成）

您的项目已经完成了以下版本控制基础设置：

- ✅ Git仓库初始化
- ✅ 用户信息配置
- ✅ .gitignore文件创建
- ✅ 配置文件模板创建
- ✅ 版本控制文档编写
- ✅ 初始提交完成

### 2. 设置GitHub远程仓库

运行以下命令设置GitHub仓库：

```bash
# 运行GitHub设置脚本
./setup_github.sh
```

或者手动设置：

```bash
# 1. 在GitHub上创建新仓库
# 访问: https://github.com/new
# 仓库名: Open-LLM-VTuber-Core
# 描述: Open-LLM-VTuber Core - 精简版VTuber AI聊天系统
# 设置为公开仓库

# 2. 添加远程仓库
git remote add origin https://github.com/griteetan-888/Open-LLM-VTuber-Core.git

# 3. 推送代码
git push -u origin main

# 4. 创建版本标签
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0

# 5. 创建develop分支
git checkout -b develop
git push -u origin develop
git checkout main
```

### 3. 日常开发工作流程

#### 开发新功能

```bash
# 1. 切换到develop分支
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/新功能名称

# 3. 开发功能
# ... 编写代码 ...

# 4. 提交更改
git add .
git commit -m "feat: 添加新功能描述"

# 5. 推送分支
git push origin feature/新功能名称

# 6. 在GitHub上创建Pull Request
```

#### 修复Bug

```bash
# 1. 从main分支创建热修复分支
git checkout main
git pull origin main
git checkout -b hotfix/问题描述

# 2. 修复问题
# ... 修复代码 ...

# 3. 提交更改
git add .
git commit -m "fix: 修复问题描述"

# 4. 推送分支
git push origin hotfix/问题描述

# 5. 创建Pull Request到main和develop分支
```

#### 发布新版本

```bash
# 1. 从develop创建发布分支
git checkout develop
git pull origin develop
git checkout -b release/v1.3.0

# 2. 准备发布
# - 更新版本号
# - 更新文档
# - 运行测试

# 3. 合并到main
git checkout main
git merge release/v1.3.0
git tag v1.3.0
git push origin main --tags

# 4. 合并回develop
git checkout develop
git merge release/v1.3.0
git push origin develop

# 5. 删除发布分支
git branch -d release/v1.3.0
git push origin --delete release/v1.3.0
```

### 4. 配置文件管理

#### 保护敏感信息

1. **使用配置文件模板**：
   - `conf.yaml.example` - 不包含真实API密钥的模板
   - `conf.yaml` - 包含真实配置的文件（已添加到.gitignore）

2. **设置环境变量**：
   ```bash
   # 创建.env文件（已添加到.gitignore）
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

3. **团队协作**：
   - 新成员复制 `conf.yaml.example` 为 `conf.yaml`
   - 填入自己的API密钥
   - 不要提交包含真实密钥的配置文件

### 5. 分支管理策略

#### 主要分支

- **main**: 生产环境代码，稳定版本
- **develop**: 开发分支，功能集成点
- **feature/**: 功能开发分支
- **hotfix/**: 紧急修复分支
- **release/**: 版本发布分支

#### 分支命名规范

```bash
# 功能分支
feature/user-authentication
feature/live2d-integration
feature/new-tts-engine

# 修复分支
hotfix/memory-leak-fix
hotfix/audio-sync-issue

# 发布分支
release/v1.3.0
release/v2.0.0
```

### 6. 提交信息规范

#### 提交格式

```
<类型>(<范围>): <描述>

[可选的正文]

[可选的脚注]
```

#### 提交类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式修改
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `ci`: CI/CD相关

#### 示例

```bash
git commit -m "feat(tts): 添加Edge TTS支持"
git commit -m "fix(asr): 修复语音识别超时问题"
git commit -m "docs(readme): 更新安装说明"
git commit -m "style(config): 格式化配置文件"
git commit -m "refactor(agent): 重构Agent架构"
```

### 7. 版本号管理

#### 语义化版本控制

- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

#### 版本号示例

- `v1.2.0` - 当前版本
- `v1.2.1` - Bug修复版本
- `v1.3.0` - 新功能版本
- `v2.0.0` - 重大更新版本

### 8. 常用命令

```bash
# 查看状态
git status

# 查看分支
git branch -a

# 切换分支
git checkout 分支名称

# 创建并切换分支
git checkout -b 新分支名称

# 添加文件
git add .

# 提交更改
git commit -m "提交信息"

# 推送分支
git push origin 分支名称

# 拉取更新
git pull origin 分支名称

# 查看提交历史
git log --oneline

# 查看标签
git tag -l

# 创建标签
git tag -a v1.2.0 -m "版本说明"

# 推送标签
git push origin v1.2.0
```

### 9. 团队协作

#### 代码审查

1. 创建Pull Request
2. 请求代码审查
3. 通过审查后合并
4. 删除功能分支

#### 冲突解决

```bash
# 拉取最新代码
git pull origin main

# 解决冲突
# 编辑冲突文件
# 添加解决后的文件
git add .

# 提交解决
git commit -m "resolve: 解决合并冲突"
```

### 10. 最佳实践

#### 开发前

- 确保在正确的分支上工作
- 拉取最新的代码
- 创建功能分支

#### 开发中

- 频繁提交，小步快跑
- 使用清晰的提交信息
- 保持代码整洁

#### 开发后

- 运行测试
- 更新文档
- 创建Pull Request
- 进行代码审查

### 11. 故障排除

#### 常见问题

1. **提交被拒绝**：
   ```bash
   git pull origin main
   # 解决冲突后重新提交
   ```

2. **误删文件**：
   ```bash
   git checkout HEAD -- 文件名
   ```

3. **撤销提交**：
   ```bash
   git reset --soft HEAD~1
   ```

4. **修改提交信息**：
   ```bash
   git commit --amend -m "新的提交信息"
   ```

### 12. 获取帮助

- 📖 详细文档: `VERSION_CONTROL.md`
- 🐛 问题报告: GitHub Issues
- 💬 讨论交流: GitHub Discussions
- 📧 联系维护者: 通过GitHub

---

## 🎯 下一步

1. **设置GitHub仓库**: 运行 `./setup_github.sh`
2. **开始开发**: 创建第一个功能分支
3. **团队协作**: 邀请协作者
4. **持续集成**: 设置GitHub Actions
5. **发布管理**: 创建第一个Release

祝您开发愉快！🚀
