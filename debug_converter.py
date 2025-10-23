#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试视频转换脚本，直接运行转换逻辑并在工作目录生成详细日志
"""

import os
import sys
import subprocess
import logging
import time
import platform

# 配置详细日志到工作目录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_conversion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_ffmpeg_path():
    """获取FFmpeg路径，优先使用内置的FFmpeg"""
    logger.debug("开始获取FFmpeg路径")
    
    # 获取当前系统架构
    system_arch = platform.machine()
    logger.debug(f"当前系统架构: {system_arch}")
    
    # 尝试使用内置FFmpeg路径
    if system_arch == 'arm64':
        ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg_bin', 'ffmpeg_macos_arm64', 'ffmpeg')
    else:
        ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg_bin', 'ffmpeg_macos_x64', 'ffmpeg')
    
    logger.debug(f"尝试内置FFmpeg路径: {ffmpeg_path}")
    
    # 检查文件是否存在且可执行
    if os.path.isfile(ffmpeg_path) and os.access(ffmpeg_path, os.X_OK):
        logger.debug(f"找到可用的内置FFmpeg: {ffmpeg_path}")
        return ffmpeg_path
    else:
        logger.warning(f"未找到可用的内置FFmpeg，尝试使用系统FFmpeg")
        # 尝试使用系统FFmpeg
        try:
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True, check=True)
            system_ffmpeg = result.stdout.strip()
            logger.debug(f"找到系统FFmpeg: {system_ffmpeg}")
            return system_ffmpeg
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"未找到系统FFmpeg: {str(e)}")
            return None

def check_ffmpeg_installed(ffmpeg_path):
    """检查FFmpeg是否正确安装并支持H265编码"""
    if not ffmpeg_path:
        logger.error("FFmpeg路径为空")
        return False
    
    try:
        # 检查FFmpeg版本
        result = subprocess.run([ffmpeg_path, '-version'], capture_output=True, text=True, timeout=10)
        logger.debug(f"FFmpeg版本信息:\n{result.stdout}")
        
        # 检查libx265编码器
        encoders_result = subprocess.run([ffmpeg_path, '-encoders'], capture_output=True, text=True, timeout=10)
        logger.debug(f"FFmpeg编码器列表中包含x265: {'libx265' in encoders_result.stdout}")
        
        # 测试简单的编码命令
        test_cmd = [ffmpeg_path, '-f', 'lavfi', '-i', 'color=c=black:s=128x72:d=1', 
                   '-c:v', 'libx265', '-preset', 'ultrafast', '-crf', '30', 
                   '-f', 'mp4', '-y', '/dev/null']
        test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=15)
        logger.debug(f"H265编码测试输出:\n{test_result.stdout}")
        logger.debug(f"H265编码测试错误:\n{test_result.stderr}")
        
        return test_result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, TimeoutError) as e:
        logger.error(f"FFmpeg检查失败: {str(e)}")
        return False

def convert_video(input_path, output_path, ffmpeg_path):
    """执行视频转换"""
    logger.info(f"开始转换视频: {input_path} -> {output_path}")
    
    # 检查输入文件是否存在
    if not os.path.isfile(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        return False
    
    # 获取输入文件信息
    try:
        probe_cmd = [ffmpeg_path, '-i', input_path]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        logger.debug(f"输入文件信息:\n{probe_result.stderr}")  # ffprobe信息输出到stderr
    except subprocess.SubprocessError as e:
        logger.error(f"获取输入文件信息失败: {str(e)}")
    
    # 构建FFmpeg转换命令
    ffmpeg_cmd = [
        ffmpeg_path,
        '-i', input_path,           # 输入文件
        '-map', '0',               # 映射所有流
        '-c:v', 'libx265',         # 视频编码器
        '-crf', '28',              # 恒定质量因子
        '-preset', 'medium',       # 编码预设
        '-pix_fmt', 'yuv420p',     # 像素格式确保兼容性
        '-c:a', 'aac',             # 音频编码器
        '-b:a', '128k',            # 音频比特率
        '-movflags', '+faststart', # 优化MP4文件
        '-strict', 'experimental', # 启用实验性功能
        '-x265-params', 'log-level=info', # x265详细日志
        '-y',                      # 覆盖输出文件
        output_path                # 输出文件
    ]
    
    logger.debug(f"执行FFmpeg命令: {' '.join(ffmpeg_cmd)}")
    
    # 执行转换命令
    try:
        start_time = time.time()
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 实时捕获输出
        stdout_lines = []
        stderr_lines = []
        
        for line in process.stdout:
            line = line.strip()
            stdout_lines.append(line)
            logger.debug(f"FFmpeg stdout: {line}")
        
        for line in process.stderr:
            line = line.strip()
            stderr_lines.append(line)
            logger.debug(f"FFmpeg stderr: {line}")
        
        return_code = process.wait()
        elapsed_time = time.time() - start_time
        
        logger.info(f"FFmpeg命令执行完成，返回码: {return_code}，耗时: {elapsed_time:.2f}秒")
        
        if return_code != 0:
            logger.error(f"FFmpeg执行失败，返回码: {return_code}")
            logger.error(f"FFmpeg错误输出:\n{''.join(stderr_lines)}")
            return False
        else:
            logger.info(f"视频转换成功: {output_path}")
            # 检查输出文件
            if os.path.isfile(output_path):
                output_size = os.path.getsize(output_path)
                logger.info(f"输出文件大小: {output_size / (1024*1024):.2f} MB")
                # 检查输出文件信息
                try:
                    output_probe = subprocess.run([ffmpeg_path, '-i', output_path], capture_output=True, text=True)
                    logger.debug(f"输出文件信息:\n{output_probe.stderr}")
                except subprocess.SubprocessError as e:
                    logger.error(f"获取输出文件信息失败: {str(e)}")
            else:
                logger.error("输出文件未生成")
                return False
            
            return True
    except subprocess.SubprocessError as e:
        logger.error(f"执行FFmpeg命令时出错: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("===== 视频转换调试程序启动 =====")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"操作系统: {platform.system()} {platform.release()} {platform.machine()}")
    
    # 获取FFmpeg路径
    ffmpeg_path = get_ffmpeg_path()
    logger.info(f"使用FFmpeg路径: {ffmpeg_path}")
    
    # 检查FFmpeg
    if not check_ffmpeg_installed(ffmpeg_path):
        logger.error("FFmpeg检查失败，请确保FFmpeg正确安装并支持H265编码")
        return 1
    
    # 明确使用指定的测试文件
    test_input = "跑量优质.mov"
    
    if not os.path.isfile(test_input):
        logger.error(f"指定的测试文件不存在: {test_input}")
        return 1
    
    test_output = f"debug_output_优质视频_{int(time.time())}.mp4"
    
    logger.info(f"使用测试输入文件: {test_input}")
    logger.info(f"将输出到: {test_output}")
    
    # 执行转换
    success = convert_video(test_input, test_output, ffmpeg_path)
    
    if success:
        logger.info("转换完成，请检查输出文件是否有画面")
        return 0
    else:
        logger.error("转换失败，请查看详细日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())