# ShadowsocksR 容器化管理器

这是一个基于 Alpine Linux 的最小化 ShadowsocksR 客户端容器，支持动态监视配置文件并自动管理节点。

## 功能特性

- 基于 Python 3.10-alpine 最小镜像（约 100MB）
- 自动读取配置文件中的 SSR URLs
- 动态监视配置文件变化，自动更新节点
- 自动测试所有节点延迟
- 显示节点列表和状态

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

### 3. 使用 Docker 命令

```bash
# 构建镜像
docker build -t shadowsocksr-manager .

# 运行容器
docker run -d \
  --name ssr-manager \
  -v $(pwd)/urls.txt:/etc/shadowsocksr/urls.txt \
  -v $(pwd)/data:/root/.shadowsocksr \
  shadowsocksr-manager

# 查看日志
docker logs -f ssr-manager
```

## 配置说明

### 环境变量

- `SSR_CONFIG_FILE`: 配置文件路径（默认：`/etc/shadowsocksr/urls.txt`）

### 配置文件格式

`urls.txt` 文件格式：
```
ssr://base64_encoded_url_1
ssr://base64_encoded_url_2
ssr://base64_encoded_url_3
```

### 启动代理服务

如果需要在容器内启动代理服务，可以执行：

```bash
# 查看可用节点
docker exec ssr-manager shadowsocksr-cli -l

# 启动指定节点（例如节点 1）
docker exec ssr-manager shadowsocksr-cli -s 1

# 启动最快节点
docker exec ssr-manager shadowsocksr-cli --fast-node
```

然后在 `docker-compose.yml` 中取消端口映射的注释。

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

## 注意事项

1. 配置文件更新后会自动重新加载
2. 节点测试可能需要一些时间，请耐心等待
3. 数据目录 `data/` 用于持久化节点信息
4. 容器重启后会自动恢复之前的节点列表 