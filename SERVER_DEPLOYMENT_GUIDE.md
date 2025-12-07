# 服务器部署指南

本指南将帮助您将 Open-LLM-VTuber 从本地部署到服务器上，使其可以通过公网访问。

## 📋 目录

1. [准备工作](#准备工作)
2. [修改配置](#修改配置)
3. [服务器部署](#服务器部署)
4. [使用 Nginx 反向代理（推荐）](#使用-nginx-反向代理推荐)
5. [使用 Systemd 管理服务（推荐）](#使用-systemd-管理服务推荐)
6. [防火墙配置](#防火墙配置)
7. [域名和 SSL 配置（可选）](#域名和-ssl-配置可选)
8. [常见问题](#常见问题)

---

## 准备工作

### 1. 服务器要求

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 7+ / Debian 10+)
- **Python**: 3.8+
- **内存**: 建议 4GB+（根据模型大小调整）
- **磁盘空间**: 根据模型大小，建议 20GB+
- **网络**: 公网 IP 或域名

### 2. 上传项目文件

将整个项目目录上传到服务器，可以使用以下方法：

**方法 1: 使用 Git（推荐）**
```bash
# 在服务器上克隆项目
git clone <your-repo-url>
cd Open-LLM-VTuber-Core
```

**方法 2: 使用 SCP**
```bash
# 在本地执行
scp -r /path/to/Open-LLM-VTuber-Core user@server:/path/to/destination/
```

**方法 3: 使用 rsync**
```bash
# 在本地执行
rsync -avz /path/to/Open-LLM-VTuber-Core user@server:/path/to/destination/
```

### 3. 安装依赖

在服务器上安装项目依赖：

```bash
cd Open-LLM-VTuber-Core

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## 修改配置

### 1. 修改 `conf.yaml`

编辑 `conf.yaml` 文件，将 `host` 从 `localhost` 改为 `0.0.0.0`：

```yaml
system_config:
  conf_version: 'v1.2.0'
  host: '0.0.0.0'  # 改为 0.0.0.0 允许外部访问
  port: 12393      # 端口号，可根据需要修改
```

**说明**：
- `host: 'localhost'`：只能本机访问
- `host: '0.0.0.0'`：允许所有网络接口访问（包括公网）
- `port: 12393`：默认端口，如果被占用可以改为其他端口（如 8080、8000 等）

### 2. 检查其他配置

确保以下配置正确：

- **API 密钥**: 检查 LLM API 密钥是否正确配置
- **模型路径**: 确保模型文件路径正确
- **资源路径**: 检查 avatars、backgrounds、live2d-models 等目录路径

---

## 服务器部署

### 方法 1: 直接运行（测试用）

适合快速测试，但不适合生产环境：

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行服务器
python run_server.py

# 或使用 start.py
python start.py --host 0.0.0.0 --port 12393
```

**访问地址**：
- 服务器本地: `http://localhost:12393`
- 公网访问: `http://服务器IP:12393`

### 方法 2: 后台运行（简单方式）

使用 `nohup` 或 `screen` 在后台运行：

```bash
# 使用 nohup
nohup python run_server.py > server.log 2>&1 &

# 或使用 screen
screen -S vtuber
python run_server.py
# 按 Ctrl+A 然后按 D 退出 screen
# 重新连接: screen -r vtuber
```

---

## 使用 Nginx 反向代理（推荐）

使用 Nginx 作为反向代理可以提供更好的性能和安全性。

### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 2. 配置 Nginx

创建 Nginx 配置文件：

```bash
sudo nano /etc/nginx/sites-available/vtuber
```

**如果没有 sites-available 目录（CentOS），使用：**
```bash
sudo nano /etc/nginx/conf.d/vtuber.conf
```

**配置文件内容**：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名或 IP

    # 日志文件
    access_log /var/log/nginx/vtuber_access.log;
    error_log /var/log/nginx/vtuber_error.log;

    # 客户端最大上传大小（用于音频文件）
    client_max_body_size 50M;

    # WebSocket 支持
    location / {
        proxy_pass http://127.0.0.1:12393;
        proxy_http_version 1.1;
        
        # WebSocket 升级头
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 基本代理头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置（WebSocket 需要较长超时）
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # 静态文件缓存（可选优化）
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://127.0.0.1:12393;
        proxy_cache_valid 200 1d;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. 启用配置

```bash
# Ubuntu/Debian
sudo ln -s /etc/nginx/sites-available/vtuber /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl reload nginx

# CentOS/RHEL（配置文件已在 conf.d 目录）
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 访问应用

现在可以通过以下地址访问：
- `http://your-domain.com` 或 `http://服务器IP`

---

## 使用 Systemd 管理服务（推荐）

使用 systemd 可以让服务自动启动，并在崩溃时自动重启。

### 1. 创建 systemd 服务文件

```bash
sudo nano /etc/systemd/system/vtuber.service
```

**服务文件内容**：

```ini
[Unit]
Description=Open-LLM-VTuber Server
After=network.target

[Service]
Type=simple
User=your-username  # 替换为您的用户名
WorkingDirectory=/path/to/Open-LLM-VTuber-Core  # 替换为项目路径
Environment="PATH=/path/to/Open-LLM-VTuber-Core/venv/bin"  # 替换为虚拟环境路径
ExecStart=/path/to/Open-LLM-VTuber-Core/venv/bin/python /path/to/Open-LLM-VTuber-Core/run_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**注意**：请替换以下路径：
- `your-username`: 您的 Linux 用户名
- `/path/to/Open-LLM-VTuber-Core`: 项目的实际路径

### 2. 启用和启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable vtuber

# 启动服务
sudo systemctl start vtuber

# 查看状态
sudo systemctl status vtuber

# 查看日志
sudo journalctl -u vtuber -f
```

### 3. 常用命令

```bash
# 启动服务
sudo systemctl start vtuber

# 停止服务
sudo systemctl stop vtuber

# 重启服务
sudo systemctl restart vtuber

# 查看状态
sudo systemctl status vtuber

# 查看日志
sudo journalctl -u vtuber -n 100  # 查看最近100行
sudo journalctl -u vtuber -f      # 实时查看
```

---

## 防火墙配置

### Ubuntu/Debian (UFW)

```bash
# 允许 HTTP 端口
sudo ufw allow 80/tcp

# 允许 HTTPS 端口（如果使用 SSL）
sudo ufw allow 443/tcp

# 如果直接访问应用端口（不使用 Nginx）
sudo ufw allow 12393/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### CentOS/RHEL (firewalld)

```bash
# 允许 HTTP 端口
sudo firewall-cmd --permanent --add-service=http

# 允许 HTTPS 端口
sudo firewall-cmd --permanent --add-service=https

# 如果直接访问应用端口
sudo firewall-cmd --permanent --add-port=12393/tcp

# 重新加载防火墙
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-all
```

---

## 域名和 SSL 配置（可选）

### 1. 配置域名

1. 在域名注册商处添加 A 记录，指向服务器 IP
2. 等待 DNS 解析生效（通常几分钟到几小时）

### 2. 使用 Let's Encrypt 配置 SSL

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu/Debian
sudo yum install certbot python3-certbot-nginx  # CentOS/RHEL

# 获取证书（自动配置 Nginx）
sudo certbot --nginx -d your-domain.com

# 或手动获取证书
sudo certbot certonly --nginx -d your-domain.com
```

### 3. 更新 Nginx 配置支持 HTTPS

Certbot 会自动更新 Nginx 配置，或手动添加：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 其他配置同 HTTP
    # ...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 4. 自动续期

Let's Encrypt 证书有效期 90 天，设置自动续期：

```bash
# 测试续期
sudo certbot renew --dry-run

# 证书会自动续期（systemd timer 已配置）
```

---

## 常见问题

### Q1: 无法从外部访问

**检查清单**：
1. ✅ 确认 `conf.yaml` 中 `host: '0.0.0.0'`
2. ✅ 检查防火墙是否开放端口
3. ✅ 检查服务器安全组（云服务器需要配置）
4. ✅ 确认服务正在运行：`sudo systemctl status vtuber`
5. ✅ 检查端口是否被占用：`netstat -tulpn | grep 12393`

### Q2: WebSocket 连接失败

**解决方案**：
1. 确保 Nginx 配置了 WebSocket 支持（见上方 Nginx 配置）
2. 检查 `proxy_read_timeout` 和 `proxy_send_timeout` 设置
3. 检查防火墙是否阻止 WebSocket 连接

### Q3: 服务启动失败

**排查步骤**：
```bash
# 查看详细日志
sudo journalctl -u vtuber -n 100

# 手动运行查看错误
cd /path/to/Open-LLM-VTuber-Core
source venv/bin/activate
python run_server.py
```

### Q4: 内存不足

**解决方案**：
1. 使用较小的模型
2. 增加服务器内存
3. 优化配置，减少并发连接

### Q5: 性能问题

**优化建议**：
1. 使用 Nginx 反向代理
2. 启用静态文件缓存
3. 使用 CDN 加速静态资源
4. 优化模型配置

### Q6: 如何更新代码

```bash
# 停止服务
sudo systemctl stop vtuber

# 更新代码
git pull  # 或重新上传文件

# 更新依赖（如果需要）
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start vtuber
```

---

## 安全建议

1. **使用 HTTPS**: 保护数据传输安全
2. **限制访问**: 使用防火墙限制访问来源
3. **定期更新**: 保持系统和依赖包更新
4. **备份配置**: 定期备份 `conf.yaml` 和重要数据
5. **监控日志**: 定期检查日志文件，发现异常
6. **API 密钥安全**: 不要将 API 密钥提交到 Git

---

## 快速部署脚本

创建一个快速部署脚本 `deploy.sh`：

```bash
#!/bin/bash

# 配置变量
PROJECT_DIR="/path/to/Open-LLM-VTuber-Core"
SERVICE_NAME="vtuber"
USER_NAME="your-username"

# 停止服务
sudo systemctl stop $SERVICE_NAME

# 更新代码（如果使用 Git）
cd $PROJECT_DIR
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start $SERVICE_NAME

# 查看状态
sudo systemctl status $SERVICE_NAME
```

使用：
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 总结

完成以上步骤后，您的 Open-LLM-VTuber 应该已经成功部署到服务器上，可以通过公网访问了。

**推荐的生产环境配置**：
- ✅ 使用 Nginx 反向代理
- ✅ 使用 systemd 管理服务
- ✅ 配置 SSL/HTTPS
- ✅ 配置防火墙
- ✅ 设置日志监控

如有问题，请查看日志文件或联系技术支持。

