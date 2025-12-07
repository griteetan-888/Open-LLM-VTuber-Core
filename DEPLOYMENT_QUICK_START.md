# 快速部署指南

## 🚀 快速开始

### 1. 修改配置文件

编辑 `conf.yaml`，将 `host` 改为 `0.0.0.0`：

```yaml
system_config:
  host: '0.0.0.0'  # 从 localhost 改为 0.0.0.0
  port: 12393
```

### 2. 上传到服务器

```bash
# 使用 Git
git clone <your-repo-url>
cd Open-LLM-VTuber-Core

# 或使用 SCP/rsync 上传整个目录
```

### 3. 在服务器上运行部署脚本

```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. 启动服务器

**简单方式（测试用）**：
```bash
source venv/bin/activate
python run_server.py
```

**生产环境（推荐）**：
```bash
# 1. 配置 systemd 服务
sudo cp vtuber.service.example /etc/systemd/system/vtuber.service
sudo nano /etc/systemd/system/vtuber.service  # 修改路径和用户名

# 2. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable vtuber
sudo systemctl start vtuber

# 3. 查看状态
sudo systemctl status vtuber
```

### 5. 配置 Nginx（可选但推荐）

```bash
# 1. 复制配置文件
sudo cp nginx-vtuber.conf.example /etc/nginx/sites-available/vtuber
sudo nano /etc/nginx/sites-available/vtuber  # 修改域名

# 2. 启用配置
sudo ln -s /etc/nginx/sites-available/vtuber /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📝 详细说明

完整部署指南请查看：[SERVER_DEPLOYMENT_GUIDE.md](./SERVER_DEPLOYMENT_GUIDE.md)

## 🔍 验证部署

1. **检查服务状态**：
   ```bash
   sudo systemctl status vtuber
   ```

2. **查看日志**：
   ```bash
   sudo journalctl -u vtuber -f
   ```

3. **访问应用**：
   - 直接访问: `http://服务器IP:12393`
   - 使用 Nginx: `http://服务器IP` 或 `http://your-domain.com`

## ⚠️ 注意事项

1. **API 密钥**: 确保在 `conf.yaml` 中配置了正确的 API 密钥
2. **端口占用**: 如果端口被占用，修改 `conf.yaml` 中的端口号
3. **防火墙**: 确保服务器安全组和防火墙开放了相应端口
4. **资源路径**: 确保所有资源文件（模型、头像等）路径正确

## 🆘 遇到问题？

查看 [SERVER_DEPLOYMENT_GUIDE.md](./SERVER_DEPLOYMENT_GUIDE.md) 中的"常见问题"部分。

