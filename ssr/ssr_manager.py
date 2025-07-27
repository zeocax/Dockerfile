#!/usr/bin/env python3
import os
import time
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SSRConfigHandler(FileSystemEventHandler):
    def __init__(self, config_file):
        self.config_file = config_file
        self.current_proxy_id = None
        self.process_config()
    
    def on_modified(self, event):
        if event.src_path == self.config_file:
            print(f"\n配置文件已更新: {self.config_file}")
            self.process_config()
    
    def process_config(self):
        """处理配置文件，添加 SSR 节点"""
        if not os.path.exists(self.config_file):
            print(f"配置文件不存在: {self.config_file}")
            return
        
        print(f"\n正在处理配置文件: {self.config_file}")
        
        # 停止当前代理（如果有）
        if self.current_proxy_id:
            print(f"\n停止当前代理节点 {self.current_proxy_id}...")
            try:
                subprocess.run(['shadowsocksr-cli', '-S', self.current_proxy_id], 
                             check=True, capture_output=True, text=True)
                self.current_proxy_id = None
            except subprocess.CalledProcessError:
                pass
        
        # 读取所有 SSR URLs
        with open(self.config_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not urls:
            print("配置文件为空")
            return
        
        # 添加每个 SSR 节点
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 添加 SSR 节点...")
            try:
                subprocess.run(['shadowsocksr-cli', '--add-ssr', url], 
                             check=True, capture_output=True, text=True)
                print(f"✓ 成功添加节点 {i}")
            except subprocess.CalledProcessError as e:
                print(f"✗ 添加节点 {i} 失败: {e}")
        
        # 获取所有节点并逐一测试
        print("\n获取节点列表...")
        result = subprocess.run(['shadowsocksr-cli', '-l'], 
                              capture_output=True, text=True)
        
        # 解析节点 ID（通常在输出的第一列）
        lines = result.stdout.strip().split('\n')
        node_ids = []
        
        for line in lines[1:]:  # 跳过标题行
            if line.strip():
                parts = line.split()
                if parts and parts[0].isdigit():
                    node_ids.append(parts[0])
        
        # 逐一测试节点
        if node_ids:
            print(f"\n开始测试 {len(node_ids)} 个节点...")
            for i, node_id in enumerate(node_ids, 1):
                print(f"\n[{i}/{len(node_ids)}] 测试节点 {node_id}...")
                try:
                    subprocess.run(['shadowsocksr-cli', '--test-again', node_id], 
                                 check=True, capture_output=True, text=True)
                    print(f"✓ 节点 {node_id} 测试完成")
                except subprocess.CalledProcessError as e:
                    print(f"✗ 节点 {node_id} 测试失败")
        
        # 显示最终的节点列表
        print("\n" + "="*80)
        print("当前 SSR 节点列表:")
        print("="*80)
        subprocess.run(['shadowsocksr-cli', '-l'])
        
        # 启动第一个节点作为代理
        if node_ids:
            first_node = node_ids[0]
            print(f"\n启动节点 {first_node} 作为代理...")
            try:
                # 获取本地端口设置
                local_port = os.environ.get('SSR_LOCAL_PORT', '1080')
                subprocess.run(['shadowsocksr-cli', '-s', first_node, '-p', local_port], 
                             check=True, capture_output=True, text=True)
                self.current_proxy_id = first_node
                print(f"✓ 代理已启动")
                print(f"  节点 ID: {first_node}")
                print(f"  SOCKS5 代理: 127.0.0.1:{local_port}")
                
                # 显示代理状态
                print("\n代理状态:")
                subprocess.run(['shadowsocksr-cli', '-S'])
            except subprocess.CalledProcessError as e:
                print(f"✗ 启动代理失败: {e}")

def main():
    config_file = os.environ.get('SSR_CONFIG_FILE', '/etc/shadowsocksr/urls.txt')
    
    print(f"SSR 管理器启动")
    print(f"配置文件: {config_file}")
    print(f"代理端口: {os.environ.get('SSR_LOCAL_PORT', '1080')}")
    print(f"开始监视文件变化...\n")
    
    # 创建事件处理器和观察者
    handler = SSRConfigHandler(config_file)
    observer = Observer()
    
    # 监视配置文件所在的目录
    config_dir = os.path.dirname(config_file)
    observer.schedule(handler, config_dir, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n停止代理...")
        if handler.current_proxy_id:
            subprocess.run(['shadowsocksr-cli', '-S', handler.current_proxy_id])
        print("SSR 管理器已停止")
    
    observer.join()

if __name__ == '__main__':
    main() 