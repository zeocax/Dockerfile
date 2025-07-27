#!/usr/bin/env python3
import os
import subprocess
import sys

def process_config(config_file):
    """处理配置文件，添加 SSR 节点并启动代理"""
    if not os.path.exists(config_file):
        print(f"配置文件不存在: {config_file}")
        return False
    
    print(f"\n正在处理配置文件: {config_file}")
    
    # 读取所有 SSR URLs
    with open(config_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("配置文件为空")
        return False
    
    # 添加每个 SSR 节点
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 添加 SSR 节点...")
        try:
            subprocess.run(['shadowsocksr-cli', '--add-ssr', url], 
                         check=True, capture_output=True, text=True)
            print(f"✓ 成功添加节点 {i}")
        except subprocess.CalledProcessError as e:
            print(f"✗ 添加节点 {i} 失败: {e}")
    
    # 测试第一个节点
    print(f"\n[1/1] 测试节点 0...")
    try:
        subprocess.run(['shadowsocksr-cli', '--test-again', '0'], 
                     check=True, capture_output=True, text=True)
        print(f"✓ 节点 0 测试完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 节点 0 测试失败: {e}")
    
    # 显示节点列表
    print("\n" + "="*80)
    print("当前 SSR 节点列表:")
    print("="*80)
    result = subprocess.run(['shadowsocksr-cli', '-l'], capture_output=True, text=True)
    print(result.stdout)
    
    # 启动第一个节点作为代理
    print(f"\n启动节点 0 作为代理...")
    try:
        # 获取本地端口设置
        local_port = os.environ.get('SSR_LOCAL_PORT', '1080')
        http_proxy_port = os.environ.get('HTTP_PROXY_PORT', '7890')
        #  shadowsocksr-cli -p 1080 --http-proxy start --http-proxy-port 7890
        subprocess.run(['shadowsocksr-cli', '-p', local_port, '--http', 'start', '--http-port', http_proxy_port], 
                     check=True, capture_output=True, text=True)
        print(f"✓ 代理已启动")
        print(f"  节点 ID: 0")
        print(f"  SOCKS5 代理: 127.0.0.1:{local_port}")
        print(f"  HTTP 代理: 127.0.0.1:{http_proxy_port}")
        print(f"  代理已在后台运行，可以开始使用")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 启动代理失败: {e}")
        return False

def main():
    config_file = os.environ.get('SSR_CONFIG_FILE', '/etc/shadowsocksr/urls.txt')
    
    print("SSR 管理器启动")
    print(f"配置文件: {config_file}")
    print(f"代理端口: {os.environ.get('SSR_LOCAL_PORT', '1080')}")
    
    # 处理配置并启动代理
    success = process_config(config_file)
    
    if success:
        print("\n✓ SSR 代理启动完成！")
        print("容器将保持运行状态，代理服务已可用。")
        print("使用 Ctrl+C 停止容器。")
        
        # 保持容器运行
        try:
            while True:
                import time
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n正在停止代理...")
            try:
                subprocess.run(['shadowsocksr-cli', '-S', '0'])
            except:
                pass
            print("SSR 管理器已停止")
    else:
        print("\n✗ SSR 代理启动失败")
        sys.exit(1)

if __name__ == '__main__':
    main() 