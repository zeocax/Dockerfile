# ShadowsocksR 容器化管理器

这是一个基于 Alpine Linux 的最小化 ShadowsocksR 客户端容器，支持动态监视配置文件并自动管理节点。

## 功能特性

- 基于 Python 3.10-alpine 最小镜像（约 100MB）
- 自动读取配置文件中的 SSR URLs
- 动态监视配置文件变化，自动更新节点
- 自动测试所有节点延迟
- 显示节点列表和状态
- **自动启动第一个节点作为 SOCKS5 代理**

## 快速开始

### 1. 准备配置文件

创建 `urls.txt` 文件，每行放置一个 SSR URL：

```bash
cp urls.txt.example urls.txt
# 编辑 urls.txt，添加你的 SSR URLs
```

### 2. 使用 Docker Compose（推荐）

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

容器启动后会自动：
1. 读取并添加所有 SSR 节点
2. 测试每个节点的连接延迟
3. 显示完整的节点列表
4. **自动启动第一个节点作为 SOCKS5 代理（端口 1080）**

### 3. 使用 Docker 命令

```bash
# 构建镜像
docker build -t shadowsocksr-manager .

# 运行容器
docker run -d \
  --name ssr-manager \
  -v $(pwd)/urls.txt:/etc/shadowsocksr/urls.txt \
  -v $(pwd)/data:/root/.shadowsocksr \
  -p 1080:1080 \
  -e SSR_LOCAL_PORT=1080 \
  shadowsocksr-manager

# 查看日志
docker logs -f ssr-manager
```

## 配置说明

### 环境变量

- `SSR_CONFIG_FILE`: 配置文件路径（默认：`/etc/shadowsocksr/urls.txt`）
- `SSR_LOCAL_PORT`: 本地 SOCKS5 代理端口（默认：`1080`）

### 配置文件格式

`urls.txt` 文件格式：
```
# 注释行会被忽略
ssr://base64_encoded_url_1
ssr://base64_encoded_url_2
ssr://base64_encoded_url_3
```

### 代理使用

容器启动后会自动在 `localhost:1080` 启动 SOCKS5 代理。你可以：

1. **浏览器使用**：配置浏览器的 SOCKS5 代理为 `127.0.0.1:1080`
2. **系统代理**：在系统网络设置中配置 SOCKS5 代理
3. **命令行使用**：
   ```bash
   # 使用 proxychains
   proxychains4 curl ipinfo.io
   
   # 使用 curl 的代理参数
   curl --socks5 127.0.0.1:1080 ipinfo.io
   ```

### 管理代理节点

虽然容器会自动启动第一个节点，你也可以手动切换：

```bash
# 查看当前代理状态
docker exec ssr-manager shadowsocksr-cli -S

# 切换到其他节点（例如节点 2）
docker exec ssr-manager shadowsocksr-cli -s 2

# 停止代理
docker exec ssr-manager shadowsocksr-cli -S

# 使用最快的节点
docker exec ssr-manager shadowsocksr-cli --fast-node
```

## 文件结构

```
ssr/
├── Dockerfile           # 容器构建文件
├── docker-compose.yml   # Docker Compose 配置
├── ssr_manager.py       # 管理脚本
├── urls.txt.example     # 配置文件示例
├── urls.txt            # 实际配置文件（需创建）
└── data/               # 数据持久化目录（自动创建）
```

## 工作流程

1. 容器启动时读取 `urls.txt` 文件
2. 自动添加所有 SSR 节点到节点列表
3. 逐一测试每个节点的延迟
4. 显示所有节点的状态列表
5. **自动启动第一个节点作为 SOCKS5 代理**
6. 持续监视配置文件变化，如有更新则重复上述流程

## 注意事项

1. 配置文件更新后会自动重新加载并重启代理
2. 节点测试可能需要一些时间，请耐心等待
3. 数据目录 `data/` 用于持久化节点信息
4. 容器重启后会自动恢复之前的节点列表并启动代理
5. 默认 SOCKS5 代理端口为 1080，可通过环境变量修改 