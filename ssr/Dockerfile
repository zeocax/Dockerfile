# 使用最小的 Python 3.10 镜像 (基于 Alpine Linux)
FROM python:3.10-alpine

# 设置工作目录
WORKDIR /app

# 更新 pip 并安装 shadowsocksr-cli
RUN pip install --upgrade pip && \
    pip install shadowsocksr-cli

# 创建配置文件目录
RUN mkdir -p /etc/shadowsocksr

# 复制管理脚本
COPY ssr_manager.py /app/ssr_manager.py
RUN chmod +x /app/ssr_manager.py

# 设置环境变量（可被覆盖）
ENV SSR_CONFIG_FILE=/etc/shadowsocksr/urls.txt
# 禁用 Python 输出缓冲，确保日志实时显示
ENV PYTHONUNBUFFERED=1

# 设置默认命令运行管理脚本
CMD ["python", "-u", "/app/ssr_manager.py"]
