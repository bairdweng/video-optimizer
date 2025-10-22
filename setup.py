#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频转换工具打包配置
简单版本，假设用户自己安装FFmpeg依赖
"""

import os
import sys
import platform
from setuptools import setup

# 应用程序信息
APP_NAME = "视频H264转H265工具"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Video Optimizer"
APP_DESCRIPTION = "使用HandBrakeCLI或FFmpeg将H264视频批量转换为H265格式"

# 主要脚本文件
MAIN_SCRIPT = "index.py"

# 检查操作系统
IS_WINDOWS = sys.platform.startswith('win')
IS_MACOS = sys.platform.startswith('darwin')
IS_LINUX = sys.platform.startswith('linux')

# 打包要求
install_requires = [
    'ffmpeg-python>=0.2.0',
]

# 添加打包选项
options = {
    'py2app': {
        'argv_emulation': True,
        'plist': {
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleVersion': APP_VERSION,
            'CFBundleShortVersionString': APP_VERSION,
            'CFBundleIdentifier': 'com.videooptimizer.h265converter',
            'NSHumanReadableCopyright': f"Copyright © 2023 {APP_AUTHOR}. All rights reserved.",
        },
        'includes': ['ffmpeg', 'ffmpeg._run', 'platform', 'sys'],
    },
    'py2exe': {
        'dist_dir': 'dist',
        'includes': ['ffmpeg', 'ffmpeg._run', 'platform', 'sys'],
        'excludes': ['numpy', 'matplotlib'],  # 排除不需要的库
    }
}

# 为Linux添加cx_Freeze支持选项
try:
    import cx_Freeze
    build_exe_options = {
        'packages': ['ffmpeg', 'ffmpeg._run', 'platform', 'sys'],
        'excludes': ['numpy', 'matplotlib'],
        'include_msvcr': True if IS_WINDOWS else False,
    }
    options['build_exe'] = build_exe_options
except ImportError:
    pass

# 打包函数
def build_app():
    """
    构建应用程序
    注意：用户需要自行安装FFmpeg和/或HandBrakeCLI
    """
    setup(
        name=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        author=APP_AUTHOR,
        install_requires=install_requires,
        options=options,
        app=[MAIN_SCRIPT] if IS_MACOS else None,
        windows=[{
            'script': MAIN_SCRIPT,
            'dest_base': 'VideoConverter'
        }] if IS_WINDOWS else None,
        console=[MAIN_SCRIPT] if IS_LINUX else None,
    )

if __name__ == '__main__':
    build_app()