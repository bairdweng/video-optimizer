#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频H264转H265工具 - 主入口
使用FFmpeg引擎进行视频转码
"""

import os
import sys
import argparse
import logging
import subprocess
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("video_conversion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """
    打印程序横幅
    """
    banner = """
    ====================================================
            视频H264转H265转换工具 v1.0
    ====================================================
    使用FFmpeg引擎进行视频转码
    """
    print(banner)

def check_ffmpeg_installed():
    """
    检查系统是否安装了FFmpeg
    
    Returns:
        bool: 如果安装了FFmpeg返回True，否则返回False
    """
    try:
        # 直接运行命令并捕获输出
        subprocess.run(["ffmpeg", "-version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      timeout=5)  # 添加超时，避免命令卡住
        logger.info("FFmpeg已正确安装")
        print("✅ FFmpeg检查通过")
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("FFmpeg未找到或命令超时")
        return False

def get_video_info(input_file):
    """
    获取视频文件信息
    
    Args:
        input_file: 输入文件路径
    
    Returns:
        dict: 包含视频信息的字典，如果获取失败返回None
    """
    try:
        # 获取文件大小
        file_size = os.path.getsize(input_file)
        
        # 尝试使用ffprobe获取详细信息
        try:
            result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", 
                                    "-show_entries", "stream=codec_name,width,height", 
                                    "-of", "json", input_file],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                if "streams" in data and len(data["streams"]) > 0:
                    stream = data["streams"][0]
                    return {
                        "codec": stream.get("codec_name", "未知"),
                        "width": stream.get("width", 0),
                        "height": stream.get("height", 0),
                        "file_size": file_size,
                        "human_size": f"{file_size/1024/1024:.2f} MB"
                    }
        except Exception:
            logger.warning("ffprobe不可用，使用基本文件信息")
        
        # 返回基本信息
        return {
            "codec": "未知",
            "width": 0,
            "height": 0,
            "file_size": file_size,
            "human_size": f"{file_size/1024/1024:.2f} MB"
        }
    except Exception as e:
        logger.error(f"获取视频信息失败: {str(e)}")
        return None

def convert_h264_to_h265(input_file, output_file, 
                       crf=28, 
                       preset="medium",
                       audio_codec="aac",
                       audio_bitrate="128k",
                       threads=0):
    """
    使用ffmpeg将H264视频转换为H265
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        crf: 恒定速率因子，范围0-51，值越小质量越高，H.265推荐28-31
        preset: 编码预设(slow, medium, fast等)，越慢压缩率越高
        audio_codec: 音频编码器
        audio_bitrate: 音频比特率
        threads: 使用的线程数，0表示使用所有可用线程
    
    Returns:
        bool: 如果转换成功返回True，否则返回False
    """
    logger.info(f"开始转换函数处理，输入文件: {input_file}, 输出文件: {output_file}")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        logger.error(f"输入文件不存在: {input_file}")
        print(f"❌ 错误: 输入文件不存在: {input_file}")
        return False
    
    logger.info(f"输入文件存在，大小: {os.path.getsize(input_file)/1024/1024:.2f} MB")
    
    # 检查输出目录是否存在，如果不存在则创建
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
        except Exception as e:
            logger.error(f"创建输出目录失败: {str(e)}")
            print(f"❌ 错误: 创建输出目录失败: {str(e)}")
            return False
    
    # 获取输入文件信息
    input_info = get_video_info(input_file)
    if input_info:
        logger.info(f"输入文件信息: {input_info['codec']}, {input_info['width']}x{input_info['height']}, {input_info['human_size']}")
    
    # 构建ffmpeg命令
    cmd = ["ffmpeg", "-i", input_file]
    
    # 添加视频参数
    cmd.extend(["-c:v", "libx265", "-crf", str(crf), "-preset", preset, "-tag:v", "hvc1"])
    
    # 添加线程参数
    if threads > 0:
        cmd.extend(["-threads", str(threads)])
    
    # 添加音频参数
    cmd.extend(["-c:a", audio_codec, "-b:a", audio_bitrate])
    
    # 简化处理，不使用ffprobe检查字幕流
    logger.info("跳过字幕流检查，简化处理")
    
    # 添加输出文件和覆盖参数
    cmd.extend(["-y", output_file])
    
    logger.info(f"开始转换: {input_file} -> {output_file}")
    logger.info(f"使用参数: CRF={crf}, 预设={preset}, 音频={audio_codec}@{audio_bitrate}")
    logger.info(f"执行的FFmpeg命令: {' '.join(cmd)}")
    print(f"🔄 开始转换: {input_file} -> {output_file}")
    print(f"   参数: CRF={crf}, 预设={preset}, 音频={audio_codec}@{audio_bitrate}")
    
    start_time = time.time()
    try:
        # 执行ffmpeg命令，并显示输出
        process = subprocess.run(cmd, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        
        if process.returncode != 0:
            logger.error(f"FFmpeg执行失败，返回码: {process.returncode}")
            logger.error(f"FFmpeg输出: {process.stderr}")
            print(f"❌ 转换失败！FFmpeg返回码: {process.returncode}")
            print(f"   错误信息: {process.stderr[:200]}...")
            return False
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 检查输出文件是否存在
        if not os.path.exists(output_file):
            logger.error(f"输出文件未生成: {output_file}")
            print(f"❌ 错误: 输出文件未生成: {output_file}")
            return False
        
        # 获取输出文件信息
        output_info = get_video_info(output_file)
        if output_info:
            # 计算压缩率
            compression_ratio = (1 - output_info['file_size'] / input_info['file_size']) * 100 if input_info else 0
            logger.info(f"转换成功完成！耗时: {duration:.2f} 秒")
            logger.info(f"输出文件信息: {output_info['codec']}, {output_info['human_size']}, 压缩率: {compression_ratio:.2f}%")
            print(f"✅ 转换成功完成！耗时: {duration:.2f} 秒")
            print(f"   输出文件大小: {output_info['human_size']}, 压缩率: {compression_ratio:.2f}%")
        else:
            logger.info(f"转换成功完成！耗时: {duration:.2f} 秒")
            print(f"✅ 转换成功完成！耗时: {duration:.2f} 秒")
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"转换失败，返回代码: {e.returncode}")
        logger.error(f"错误输出: {e.stderr}")
        print(f"❌ 转换失败！返回代码: {e.returncode}")
        return False
    except KeyboardInterrupt:
        logger.warning("转换被用户中断")
        print(f"⚠️  转换被用户中断")
        return False
    except Exception as e:
        logger.error(f"转换过程中出错: {str(e)}")
        print(f"❌ 转换过程中出错: {str(e)}")
        return False

def batch_convert(directory, recursive=False, **kwargs):
    """
    批量转换目录中的视频文件
    
    Args:
        directory: 要扫描的目录
        recursive: 是否递归扫描子目录
        **kwargs: 传递给convert_h264_to_h265的其他参数
    
    Returns:
        int: 成功转换的文件数量
    """
    if not os.path.isdir(directory):
        logger.error(f"目录不存在: {directory}")
        return 0
    
    # 支持的视频文件扩展名
    video_extensions = {'.mp4', '.mkv', '.mov', '.avi', '.wmv', '.flv', '.webm'}
    
    # 收集所有视频文件
    video_files = []
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in video_extensions:
                    video_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file)
                if ext.lower() in video_extensions:
                    video_files.append(file_path)
    
    logger.info(f"找到 {len(video_files)} 个视频文件")
    success_count = 0
    
    for idx, input_file in enumerate(video_files, 1):
        # 检查是否已经是H.265编码
        info = get_video_info(input_file)
        if info and info['codec'] == 'hevc':  # HEVC就是H.265
            logger.info(f"跳过已使用H.265编码的文件: {input_file}")
            continue
        
        # 生成输出文件名
        base_name, ext = os.path.splitext(input_file)
        output_file = f"{base_name}_h265{ext}"
        
        # 避免覆盖已存在的文件
        counter = 1
        while os.path.exists(output_file):
            output_file = f"{base_name}_h265_{counter}{ext}"
            counter += 1
        
        # 转换文件
        logger.info(f"\n处理文件 {idx}/{len(video_files)}: {input_file}")
        if convert_h264_to_h265(input_file, output_file, **kwargs):
            success_count += 1
    
    logger.info(f"\n批量转换完成！成功转换 {success_count}/{len(video_files)} 个文件")
    return success_count

def main():
    """
    主函数 - 程序入口点
    """
    print_banner()
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="视频H264转H265转换工具（使用FFmpeg引擎）")
    
    # 添加互斥组，用于选择单个文件转换还是批量转换
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--input", help="输入视频文件路径")
    group.add_argument("-d", "--directory", help="要批量转换的目录路径")
    
    # 通用参数
    parser.add_argument("-o", "--output", help="输出视频文件路径（仅单个文件转换时需要）")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子目录（仅批量转换时有效）")
    
    # FFmpeg参数
    parser.add_argument("--crf", type=int, default=28, help="恒定速率因子，范围0-51，H.265推荐28-31")
    parser.add_argument("--preset", default="medium", 
                       choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"], 
                       help="编码预设")
    parser.add_argument("--audio-codec", default="aac", help="音频编码器")
    parser.add_argument("--audio-bitrate", default="128k", help="音频比特率，如'128k'")
    parser.add_argument("--threads", type=int, default=0, help="使用的线程数，0表示使用所有可用线程")
    
    # 解析命令行参数
    args = parser.parse_args()
    print(f"命令行参数解析完成，输入文件: {args.input}, 输出文件: {args.output}")
    
    # 检查FFmpeg是否安装
    if not check_ffmpeg_installed():
        logger.error("错误: 未找到FFmpeg。请先安装FFmpeg工具。")
        logger.error("macOS用户可以使用Homebrew安装: brew install ffmpeg")
        logger.error("Windows用户可以从官方网站下载: https://ffmpeg.org/download.html")
        logger.error("Linux用户可以使用包管理器安装: sudo apt-get install ffmpeg")
        sys.exit(1)
    
    # 提取FFmpeg参数
    ffmpeg_args = {
        "crf": args.crf,
        "preset": args.preset,
        "audio_codec": args.audio_codec,
        "audio_bitrate": args.audio_bitrate,
        "threads": args.threads
    }
    
    logger.info(f"使用FFmpeg引擎进行转换")
    
    # 执行转换
    if args.input:
        # 单个文件转换模式
        if not args.output:
            # 如果未指定输出文件，自动生成
            base_name, ext = os.path.splitext(args.input)
            args.output = f"{base_name}_h265{ext}"
        
        logger.info(f"单个文件转换模式")
        success = convert_h264_to_h265(args.input, args.output, **ffmpeg_args)
        
        if success:
            logger.info("转换完成！")
            print(f"\n✅ 转换成功！")
            print(f"输入文件: {args.input}")
            print(f"输出文件: {args.output}")
        else:
            logger.error("转换失败！")
            print(f"\n❌ 转换失败！请查看日志获取详细信息。")
            sys.exit(1)
    elif args.directory:
        # 批量转换模式
        logger.info(f"批量转换模式 - 目录: {args.directory}, 递归: {args.recursive}")
        success_count = batch_convert(args.directory, args.recursive, **ffmpeg_args)
        
        print(f"\n📊 批量转换统计:")
        print(f"目录: {args.directory}")
        print(f"递归扫描: {'是' if args.recursive else '否'}")
        print(f"成功转换: {success_count} 个文件")
        
        if success_count > 0:
            print("\n✅ 批量转换完成！")
        else:
            logger.warning("没有成功转换的文件")
            print("\n⚠️  没有成功转换的文件，请查看日志获取详细信息。")
            sys.exit(1)

if __name__ == "__main__":
    main()