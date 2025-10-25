# Open-LLM-VTuber-Core 版本控制管理指南

## 概述

本文档描述了 Open-LLM-VTuber-Core 项目的版本控制管理策略，包括 Git 工作流程、分支管理、版本号规则和发布流程。

## 版本号管理策略

### 语义化版本控制 (Semantic Versioning)

项目采用语义化版本控制，格式为：`MAJOR.MINOR.PATCH`

- **MAJOR**: 主版本号，不兼容的API修改
- **MINOR**: 次版本号，向下兼容的功能性新增
- **PATCH**: 修订号，向下兼容的问题修正

### 当前版本
- **当前版本**: v1.2.0
- **下一个版本**: v1.2.1 (bug修复) 或 v1.3.0 (新功能)

### 版本号规则

1. **主版本号 (MAJOR)**
   - 重大架构变更
   - 不兼容的API修改
   - 核心功能重构

2. **次版本号 (MINOR)**
   - 新功能添加
   - 新模型支持
   - 新角色添加
   - 性能优化

3. **修订号 (PATCH)**
   - Bug修复
   - 文档更新
   - 配置优化
   - 依赖更新

## 分支管理策略

### 主要分支

1. **main** (主分支)
   - 生产环境代码
   - 稳定版本
   - 受保护分支

2. **develop** (开发分支)
   - 集成开发分支
   - 功能开发合并点
   - 测试版本

3. **feature/** (功能分支)
   - 新功能开发
   - 命名规则: `feature/功能名称`
   - 从 develop 分支创建

4. **hotfix/** (热修复分支)
   - 紧急bug修复
   - 命名规则: `hotfix/问题描述`
   - 从 main 分支创建

5. **release/** (发布分支)
   - 版本发布准备
   - 命名规则: `release/v版本号`
   - 从 develop 分支创建

### 分支工作流程

```
main ←── hotfix/v1.2.1
 ↑
develop ←── feature/new-model-support
 ↑
feature/character-customization
```

## Git 工作流程

### 1. 功能开发流程

```bash
# 1. 从 develop 分支创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 开发功能
# ... 编写代码 ...

# 3. 提交更改
git add .
git commit -m "feat: 添加新功能描述"

# 4. 推送到远程
git push origin feature/new-feature

# 5. 创建 Pull Request 到 develop 分支
```

### 2. 热修复流程

```bash
# 1. 从 main 分支创建热修复分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# 2. 修复问题
# ... 修复代码 ...

# 3. 提交更改
git add .
git commit -m "fix: 修复关键问题描述"

# 4. 推送到远程
git push origin hotfix/critical-bug-fix

# 5. 创建 Pull Request 到 main 和 develop 分支
```

### 3. 发布流程

```bash
# 1. 从 develop 分支创建发布分支
git checkout develop
git pull origin develop
git checkout -b release/v1.3.0

# 2. 准备发布
# ... 更新版本号、文档等 ...

# 3. 合并到 main 分支
git checkout main
git merge release/v1.3.0
git tag v1.3.0
git push origin main --tags

# 4. 合并回 develop 分支
git checkout develop
git merge release/v1.3.0
git push origin develop

# 5. 删除发布分支
git branch -d release/v1.3.0
git push origin --delete release/v1.3.0
```

## 提交信息规范

### 提交信息格式

```
<类型>(<范围>): <描述>

[可选的正文]

[可选的脚注]
```

### 提交类型

- **feat**: 新功能
- **fix**: Bug修复
- **docs**: 文档更新
- **style**: 代码格式修改
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动
- **perf**: 性能优化
- **ci**: CI/CD相关

### 示例

```
feat(tts): 添加Edge TTS支持
fix(asr): 修复语音识别超时问题
docs(readme): 更新安装说明
style(config): 格式化配置文件
refactor(agent): 重构Agent架构
test(api): 添加API测试用例
chore(deps): 更新依赖版本
perf(llm): 优化LLM响应速度
ci(github): 配置GitHub Actions
```

## 文件管理策略

### 敏感信息处理

1. **配置文件模板**
   - `conf.yaml.example`: 配置文件模板
   - 不包含真实的API密钥
   - 包含所有必要的配置项

2. **实际配置文件**
   - `conf.yaml`: 实际配置文件
   - 包含真实的API密钥
   - 添加到 `.gitignore` 中

3. **环境变量**
   - 使用 `.env` 文件存储敏感信息
   - 添加到 `.gitignore` 中
   - 提供 `.env.example` 模板

### 大文件管理

1. **模型文件**
   - 不提交到Git仓库
   - 使用Git LFS或外部存储
   - 提供下载脚本

2. **缓存文件**
   - 添加到 `.gitignore`
   - 定期清理

3. **日志文件**
   - 添加到 `.gitignore`
   - 使用日志轮转

## 标签管理

### 版本标签

```bash
# 创建版本标签
git tag -a v1.2.0 -m "Release version 1.2.0"

# 推送标签
git push origin v1.2.0

# 查看所有标签
git tag -l

# 删除标签
git tag -d v1.2.0
git push origin --delete v1.2.0
```

### 标签命名规则

- **版本标签**: `v1.2.0`
- **预发布标签**: `v1.3.0-beta.1`
- **开发标签**: `v1.3.0-dev.1`

## 发布管理

### 发布检查清单

- [ ] 所有测试通过
- [ ] 文档更新完成
- [ ] 版本号更新
- [ ] CHANGELOG.md 更新
- [ ] 依赖检查完成
- [ ] 配置文件模板更新
- [ ] 发布说明准备

### 发布流程

1. **准备发布**
   - 更新版本号
   - 更新文档
   - 运行测试

2. **创建发布分支**
   - 从 develop 创建 release 分支
   - 进行最终测试

3. **合并到主分支**
   - 合并到 main 分支
   - 创建版本标签

4. **发布到GitHub**
   - 创建 GitHub Release
   - 上传发布包
   - 发布说明

## 最佳实践

### 1. 提交频率
- 小步快跑，频繁提交
- 每个提交解决一个问题
- 提交前进行代码检查

### 2. 分支保护
- 主分支设置保护规则
- 要求代码审查
- 要求状态检查通过

### 3. 代码质量
- 使用 pre-commit hooks
- 代码格式化
- 静态代码分析

### 4. 文档维护
- 及时更新文档
- 保持文档与代码同步
- 使用清晰的文档结构

## 工具推荐

### Git 工具
- **GitHub Desktop**: 图形化Git客户端
- **SourceTree**: Atlassian的Git客户端
- **VS Code Git**: 集成在VS Code中

### 代码质量
- **pre-commit**: Git hooks管理
- **ruff**: Python代码检查
- **black**: Python代码格式化

### 持续集成
- **GitHub Actions**: CI/CD自动化
- **Travis CI**: 持续集成服务
- **CircleCI**: 持续集成平台

## 故障排除

### 常见问题

1. **合并冲突**
   ```bash
   git status
   git diff
   # 手动解决冲突
   git add .
   git commit
   ```

2. **提交历史混乱**
   ```bash
   git rebase -i HEAD~3
   # 交互式重写提交历史
   ```

3. **误删文件**
   ```bash
   git checkout HEAD -- <文件名>
   # 恢复文件
   ```

4. **撤销提交**
   ```bash
   git reset --soft HEAD~1
   # 撤销最后一次提交，保留更改
   ```

## 总结

本版本控制管理策略旨在：
- 确保代码质量和稳定性
- 提高开发效率
- 便于团队协作
- 支持持续集成和部署

遵循这些规范将帮助您更好地管理 Open-LLM-VTuber-Core 项目的版本控制。
