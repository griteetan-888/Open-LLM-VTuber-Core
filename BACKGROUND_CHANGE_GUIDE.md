# VTuber背景图更换指南

## 🎨 如何更换VTuber的背景图

### 📁 背景图文件位置

背景图文件存放在 `backgrounds/` 目录中：

```
backgrounds/
├── cartoon-night-landscape-moon.jpeg
├── ceiling-window-room-night.jpeg
├── cityscape.jpeg
├── computer-room-illustration.jpeg
├── congress.jpg
├── field-night-painting-moon.jpeg
├── lernado-diff-classroom-center.jpeg
├── moon-over-mountain.jpeg
├── mountain-range-illustration.jpeg
├── night-landscape-grass-moon.jpeg
├── night-scene-cartoon-moon.jpeg
├── painting-valley-night-sky. 2.jpeg
├── room-interior-illustration.jpeg
└── sdxl-classroom-door-view.jpeg
```

## 🔄 更换背景图的方法

### 方法1: 通过前端界面切换 (推荐)

1. **启动系统**:
   ```bash
   python3 start.py
   ```

2. **打开前端界面**:
   - 在浏览器中访问 `http://localhost:12393`
   - 登录到VTuber界面

3. **切换背景图**:
   - 在前端界面中找到背景设置选项
   - 点击背景切换按钮
   - 选择你想要的背景图
   - 背景图会立即切换

### 方法2: 添加新的背景图文件

1. **准备背景图**:
   - 支持的格式: `.jpg`, `.jpeg`, `.png`, `.gif`
   - 建议尺寸: 1920x1080 或更高分辨率
   - 文件大小: 建议不超过5MB

2. **添加背景图**:
   ```bash
   # 将新的背景图文件复制到backgrounds目录
   cp your_new_background.jpg backgrounds/
   ```

3. **重启系统**:
   ```bash
   # 重启系统以加载新的背景图
   python3 start.py
   ```

### 方法3: 替换现有背景图

1. **备份原文件**:
   ```bash
   cp backgrounds/cityscape.jpeg backgrounds/cityscape_backup.jpeg
   ```

2. **替换文件**:
   ```bash
   # 用新文件替换现有背景图
   cp your_new_background.jpg backgrounds/cityscape.jpeg
   ```

3. **重启系统**:
   ```bash
   python3 start.py
   ```

## 🛠️ 技术实现细节

### 后端API支持

系统提供了完整的背景图API支持：

1. **背景图服务**:
   ```python
   # 在server.py中
   self.app.mount(
       "/bg",
       CORSStaticFiles(directory="backgrounds"),
       name="backgrounds",
   )
   ```

2. **背景图列表API**:
   ```python
   # 获取可用背景图列表
   async def _handle_fetch_backgrounds(self, websocket, client_uid, data):
       bg_files = scan_bg_directory()
       await websocket.send_text(
           json.dumps({"type": "background-files", "files": bg_files})
       )
   ```

3. **背景图扫描**:
   ```python
   def scan_bg_directory() -> list[str]:
       bg_files = []
       bg_dir = "backgrounds"
       for root, _, files in os.walk(bg_dir):
           for file in files:
               if file.endswith((".jpg", ".jpeg", ".png", ".gif")):
                   bg_files.append(file)
       return bg_files
   ```

### 前端集成

前端通过WebSocket与后端通信：

1. **获取背景图列表**:
   ```javascript
   // 发送获取背景图列表的请求
   websocket.send(JSON.stringify({
       type: "fetch-backgrounds"
   }));
   ```

2. **切换背景图**:
   ```javascript
   // 切换背景图的请求
   websocket.send(JSON.stringify({
       type: "switch-background",
       background: "your_background.jpg"
   }));
   ```

## 📋 背景图要求

### 文件格式
- **支持格式**: `.jpg`, `.jpeg`, `.png`, `.gif`
- **推荐格式**: `.jpg` 或 `.png`
- **文件大小**: 建议不超过5MB

### 图片规格
- **分辨率**: 建议1920x1080或更高
- **宽高比**: 16:9 或 4:3
- **颜色模式**: RGB
- **压缩**: 适中的压缩率以平衡质量和文件大小

### 内容建议
- **主题**: 适合VTuber角色的背景
- **风格**: 与角色形象匹配
- **亮度**: 适中，不影响角色显示
- **复杂度**: 不要过于复杂，避免干扰角色

## 🎯 使用技巧

### 1. 背景图选择
- 选择与VTuber角色风格匹配的背景
- 考虑不同时间段的背景（白天/夜晚）
- 准备多个背景图以便切换

### 2. 性能优化
- 压缩背景图文件大小
- 使用合适的图片格式
- 避免过大的文件影响加载速度

### 3. 主题搭配
- **Kiyo角色**: 适合星空、月亮、梦幻风格的背景
- **Mao角色**: 适合现代、科技风格的背景
- **Shizuku角色**: 适合自然、清新风格的背景

## 🔧 故障排除

### 常见问题

1. **背景图不显示**:
   - 检查文件格式是否支持
   - 确认文件路径正确
   - 重启系统

2. **背景图加载慢**:
   - 压缩图片文件
   - 检查网络连接
   - 优化图片尺寸

3. **背景图切换失败**:
   - 检查WebSocket连接
   - 查看浏览器控制台错误
   - 重启前端页面

### 调试方法

1. **检查文件**:
   ```bash
   ls -la backgrounds/
   ```

2. **查看日志**:
   ```bash
   tail -f logs/debug_*.log
   ```

3. **测试API**:
   ```bash
   curl http://localhost:12393/bg/your_background.jpg
   ```

## 📚 相关文件

- **背景图目录**: `backgrounds/`
- **服务器配置**: `src/open_llm_vtuber/server.py`
- **WebSocket处理**: `src/open_llm_vtuber/websocket_handler.py`
- **工具函数**: `src/open_llm_vtuber/config_manager/utils.py`
- **前端界面**: `frontend/`

## 🎉 总结

更换VTuber背景图非常简单：

1. **添加新背景图** → 将图片文件放入 `backgrounds/` 目录
2. **通过前端切换** → 在界面中选择背景图
3. **重启系统** → 确保新背景图被加载

系统提供了完整的背景图管理功能，支持动态切换和实时预览！

---

**支持格式**: JPG, JPEG, PNG, GIF  
**推荐尺寸**: 1920x1080  
**文件大小**: < 5MB  
**切换方式**: 前端界面 / API调用
