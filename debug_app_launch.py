#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试脚本：用于捕获应用启动时的详细错误信息
"""

import os
import subprocess
import sys
import traceback

# 定义应用路径
app_path = os.path.join(os.getcwd(), 'dist', '视频H264转H265工具.app', 'Contents', 'MacOS', '视频H264转H265工具')

def main():
    print(f"开始调试应用启动...")
    print(f"应用路径: {app_path}")
    
    # 检查应用文件是否存在
    if not os.path.exists(app_path):
        print(f"错误: 应用文件不存在 - {app_path}")
        print("请先成功打包应用")
        return 1
    
    # 检查文件权限
    if not os.access(app_path, os.X_OK):
        print(f"警告: 应用文件没有执行权限，正在添加...")
        try:
            os.chmod(app_path, 0o755)
            print("✅ 已添加执行权限")
        except Exception as e:
            print(f"❌ 添加执行权限失败: {e}")
    
    print("\n=== 尝试直接运行应用并捕获错误 ===\n")
    
    try:
        # 运行应用并捕获所有输出
        process = subprocess.Popen(
            [app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 设置一个较短的超时，因为我们只是想捕获启动错误
        try:
            stdout, stderr = process.communicate(timeout=10)
            
            print("\n=== 标准输出 ===")
            if stdout:
                print(stdout)
            else:
                print("(无标准输出)")
            
            print("\n=== 标准错误 ===")
            if stderr:
                print(stderr)
            else:
                print("(无标准错误)")
                
            print(f"\n=== 进程返回码: {process.returncode} ===")
            
            # 如果有错误输出，很可能是闪退的原因
            if stderr:
                print("\n⚠️  检测到错误输出，这可能是闪退的原因")
                
        except subprocess.TimeoutExpired:
            print("\n⚠️  应用启动超时，但这可能是正常的，因为GUI应用通常会持续运行")
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=2)
                print("\n=== 超时前的标准输出 ===")
                print(stdout if stdout else "(无)")
                print("\n=== 超时前的标准错误 ===")
                print(stderr if stderr else "(无)")
            except:
                pass
    
    except Exception as e:
        print(f"\n❌ 运行应用时出错: {e}")
        traceback.print_exc()
    
    print("\n=== 检查应用内部日志 ===\n")
    
    # 检查应用日志文件
    log_dir = os.path.expanduser("~/Library/Application Support/VideoConverter")
    log_file = os.path.join(log_dir, "video_converter.log")
    debug_log = os.path.join(os.getcwd(), "video_converter_debug.log")
    error_log = os.path.join(os.getcwd(), "simple_gui_error.log")
    
    for log_path, log_name in [(log_file, "应用日志"), (debug_log, "调试日志"), (error_log, "错误日志")]:
        if os.path.exists(log_path):
            print(f"\n--- {log_name} ({log_path}) ---\n")
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # 只显示最后100行，避免输出过多
                    lines = f.readlines()
                    if len(lines) > 100:
                        print("[显示最后100行]")
                        lines = lines[-100:]
                    print(''.join(lines))
            except Exception as e:
                print(f"无法读取日志文件: {e}")
        else:
            print(f"{log_name}不存在: {log_path}")
    
    print("\n=== 调试完成 ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())