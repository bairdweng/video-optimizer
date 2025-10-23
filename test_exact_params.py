#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用完全优化的参数测试视频转换
"""

import os
import subprocess
import time

input_file = "跑量优质.mov"
output_file = f"test_exact_output_{int(time.time())}.mp4"

# 检查文件是否存在
if not os.path.isfile(input_file):
    print(f"错误：输入文件 {input_file} 不存在")
    exit(1)

# 获取FFmpeg路径
ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          'ffmpeg_bin', 'ffmpeg_macos_arm64', 'ffmpeg')

if not os.path.isfile(ffmpeg_path):
    print(f"错误：未找到FFmpeg: {ffmpeg_path}")
    exit(1)

print(f"使用FFmpeg: {ffmpeg_path}")
print(f"输入文件: {input_file}")
print(f"输出文件: {output_file}")

# 构建完整的FFmpeg命令，添加额外的兼容性参数
ffmpeg_cmd = [
    ffmpeg_path,
    '-y',                      # 覆盖输出
    '-i', input_file,          # 输入文件
    '-map', '0:v',             # 明确映射视频流
    '-map', '0:a',             # 明确映射音频流
    '-c:v', 'libx265',         # H265视频编码
    '-crf', '28',              # 质量设置
    '-preset', 'medium',       # 编码速度/质量预设
    '-pix_fmt', 'yuv420p',     # 兼容性像素格式
    '-color_range', 'tv',      # 标准色彩范围
    '-colorspace', 'bt709',    # 标准色彩空间
    '-color_trc', 'bt709',     # 色彩传输特性
    '-color_primaries', 'bt709', # 色彩原色
    '-c:a', 'aac',             # AAC音频编码
    '-b:a', '128k',            # 音频比特率
    '-movflags', '+faststart', # 网页播放优化
    '-strict', 'experimental', # 启用实验性功能
    '-threads', '0',           # 自动使用所有CPU核心
    output_file                # 输出文件
]

print("\n执行命令:")
print(' '.join(ffmpeg_cmd))

# 执行转换
print("\n开始转换...")
try:
    process = subprocess.run(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    
    print("\n转换完成!")
    
    # 检查输出文件
    if os.path.isfile(output_file):
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"输出文件大小: {size_mb:.2f} MB")
        
        # 查看输出文件信息
        print("\n输出文件信息:")
        info_cmd = [ffmpeg_path, '-i', output_file]
        info_result = subprocess.run(
            info_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(info_result.stderr)
    
    # 将成功的参数保存到文件
    with open('working_params.txt', 'w') as f:
        f.write('# 成功的FFmpeg参数\n')
        f.write(' '.join(ffmpeg_cmd[3:]) + '\n')  # 跳过ffmpeg路径和-y参数
        
    print("\n成功的参数已保存到 working_params.txt")
    
    exit(0)
except subprocess.CalledProcessError as e:
    print(f"\n转换失败！返回码: {e.returncode}")
    print("\n错误输出:")
    print(e.stderr)
    exit(1)