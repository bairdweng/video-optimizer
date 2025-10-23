#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：使用优化后的参数转换视频，确保与QuickTime Player兼容
"""

import os
import subprocess
import logging
import sys
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quicktime_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_ffmpeg_path():
    """获取FFmpeg路径"""
    # 检查内置FFmpeg路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查系统架构
    if sys.platform == 'darwin':  # macOS
        if 'arm64' in subprocess.check_output('uname -m', shell=True).decode():
            ffmpeg_path = os.path.join(base_dir, 'ffmpeg_bin', 'ffmpeg_macos_arm64', 'ffmpeg')
        else:
            ffmpeg_path = os.path.join(base_dir, 'ffmpeg_bin', 'ffmpeg_macos_x64', 'ffmpeg')
    else:
        # Windows或Linux路径（如果需要）
        ffmpeg_path = 'ffmpeg'
    
    # 如果内置路径不存在，尝试使用系统FFmpeg
    if not os.path.exists(ffmpeg_path):
        try:
            subprocess.run(['which', 'ffmpeg'], check=True, stdout=subprocess.PIPE)
            ffmpeg_path = 'ffmpeg'
            logger.info("使用系统FFmpeg")
        except:
            logger.error("未找到FFmpeg")
            return None
    
    logger.info(f"使用FFmpeg路径: {ffmpeg_path}")
    return ffmpeg_path

def convert_to_quicktime_compatible(input_file, output_file):
    """转换视频为QuickTime兼容格式"""
    if not os.path.exists(input_file):
        logger.error(f"输入文件不存在: {input_file}")
        return False
    
    # 获取FFmpeg路径
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return False
    
    # 使用优化后的FFmpeg参数
    ffmpeg_cmd = [
        ffmpeg_path,
        "-y",                       # 覆盖输出文件
        "-i", input_file,
        "-map", "0:v",              # 明确映射视频流
        "-map", "0:a",              # 明确映射音频流
        "-c:v", "libx265",          # 视频编码器
        "-crf", "28",               # 恒定质量因子
        "-preset", "medium",        # 编码预设
        "-pix_fmt", "yuv420p",      # 像素格式确保兼容性
        "-color_range", "tv",       # 标准色彩范围
        "-colorspace", "bt709",     # 标准色彩空间
        "-color_trc", "bt709",      # 色彩传输特性
        "-color_primaries", "bt709", # 色彩原色
        "-c:a", "aac",              # 音频编码器
        "-b:a", "128k",             # 音频比特率
        "-ac", "2",                 # 确保是立体声
        "-ar", "44100",             # 标准音频采样率
        "-movflags", "+faststart",  # 优化MP4文件
        "-threads", "0",            # 自动使用所有CPU核心
        "-tag:v", "hvc1",           # 使用hvc1标签提高QuickTime兼容性
        output_file
    ]
    
    logger.info(f"开始转换: {input_file} -> {output_file}")
    logger.debug(f"执行命令: {' '.join(ffmpeg_cmd)}")
    
    try:
        # 执行转换
        process = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode != 0:
            logger.error(f"FFmpeg转换失败: {process.stderr}")
            return False
        
        # 检查输出文件
        if os.path.exists(output_file):
            logger.info(f"转换成功，输出文件: {output_file}")
            logger.info(f"文件大小: {os.path.getsize(output_file) / (1024 * 1024):.2f} MB")
            return True
        else:
            logger.error("输出文件未生成")
            return False
            
    except Exception as e:
        logger.error(f"转换过程出错: {str(e)}")
        return False

def main():
    """主函数"""
    # 获取测试文件列表
    test_files = [f for f in os.listdir('.') if f.endswith(('.mov', '.mp4', '.mkv'))]
    
    if not test_files:
        logger.error("未找到测试视频文件")
        print("请将测试视频文件放在当前目录")
        return
    
    print("\n可用的测试文件:")
    for i, file in enumerate(test_files, 1):
        print(f"{i}. {file}")
    
    # 选择文件
    try:
        choice = int(input("\n请选择要转换的文件编号 (1-{}): ".format(len(test_files)))) - 1
        if 0 <= choice < len(test_files):
            input_file = test_files[choice]
        else:
            print("无效的选择")
            return
    except ValueError:
        print("请输入有效的数字")
        return
    
    # 生成输出文件名
    base_name = os.path.splitext(input_file)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{base_name}_quicktime_compatible_{timestamp}.mp4"
    
    print(f"\n开始转换文件: {input_file}")
    print(f"输出文件将保存为: {output_file}")
    
    # 开始转换
    if convert_to_quicktime_compatible(input_file, output_file):
        print("\n✅ 转换成功！")
        print(f"请尝试在QuickTime Player中打开: {output_file}")
        print("\n提示: 如果转换后的视频仍然无法在QuickTime Player中播放，")
        print("      您可能需要尝试以下解决方案:")
        print("      1. 更新QuickTime Player到最新版本")
        print("      2. 使用视频转码为H.264格式 (兼容性更好)")
        print("      3. 安装第三方解码器插件")
    else:
        print("\n❌ 转换失败，请查看日志了解详情")

if __name__ == "__main__":
    main()