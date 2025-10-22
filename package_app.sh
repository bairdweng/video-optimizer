#!/bin/bash

# 视频转换工具打包脚本（macOS版）
# 自动下载FFmpeg并使用PyInstaller打包独立应用

echo "=== 视频转换工具打包助手（macOS）==="
echo "此脚本将自动下载FFmpeg并打包独立应用程序"
echo ""

# 检查是否为macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "错误: 此脚本仅适用于macOS系统"
    exit 1
fi

# 创建必要的目录结构
echo "创建FFmpeg二进制文件目录结构..."
mkdir -p ffmpeg_bin/ffmpeg_macos_x64
mkdir -p ffmpeg_bin/ffmpeg_macos_arm64

# 获取系统架构
ARCH=$(uname -m)
echo "检测到系统架构: $ARCH"

# 根据架构选择下载URL
if [[ "$ARCH" == "arm64" ]]; then
    echo "准备下载macOS (Apple Silicon)版本的FFmpeg..."
    BIN_DIR="ffmpeg_macos_arm64"
    # 注意：这里使用的是通用下载链接，实际使用时需要替换为正确的URL
    echo "开始下载FFmpeg二进制文件..."
    # 尝试从evermeet.cx下载（Apple Silicon版本）
    curl -L -o ffmpeg_macos.zip https://evermeet.cx/ffmpeg/getrelease/zip
    
    if [ $? -ne 0 ]; then
        echo "下载失败，尝试替代方案..."
        # 提示用户手动下载
        echo "请从 https://evermeet.cx/ffmpeg/ 手动下载适合Apple Silicon的FFmpeg"
        exit 1
    fi
else
    echo "准备下载macOS (Intel)版本的FFmpeg..."
    BIN_DIR="ffmpeg_macos_x64"
    # 尝试从evermeet.cx下载（Intel版本）
    curl -L -o ffmpeg_macos.zip https://evermeet.cx/ffmpeg/getrelease/zip
    
    if [ $? -ne 0 ]; then
        echo "下载失败，尝试替代方案..."
        # 提示用户手动下载
        echo "请从 https://evermeet.cx/ffmpeg/ 手动下载适合Intel的FFmpeg"
        exit 1
    fi
fi

# 解压FFmpeg
echo "解压FFmpeg..."
unzip ffmpeg_macos.zip -d temp_ffmpeg

if [ $? -ne 0 ]; then
    echo "解压失败，请手动下载并解压FFmpeg"
    exit 1
fi

# 复制二进制文件到正确位置
echo "复制FFmpeg二进制文件..."
cp temp_ffmpeg/ffmpeg ffmpeg_bin/$BIN_DIR/
cp temp_ffmpeg/ffprobe ffmpeg_bin/$BIN_DIR/

# 设置执行权限
echo "设置执行权限..."
chmod +x ffmpeg_bin/$BIN_DIR/ffmpeg
chmod +x ffmpeg_bin/$BIN_DIR/ffprobe

# 清理临时文件
echo "清理临时文件..."
rm -rf temp_ffmpeg
rm ffmpeg_macos.zip

# 检查FFmpeg是否正确安装
echo "验证FFmpeg安装..."
if [ -f "ffmpeg_bin/$BIN_DIR/ffmpeg" ] && [ -f "ffmpeg_bin/$BIN_DIR/ffprobe" ]; then
    echo "✅ FFmpeg二进制文件已成功准备"
else
    echo "❌ FFmpeg二进制文件准备失败"
    exit 1
fi

# 开始打包应用
echo ""
echo "开始使用PyInstaller打包应用..."
echo "此过程可能需要几分钟时间..."

# 使用PyInstaller打包
pyinstaller --onedir \
    --name "视频H264转H265工具" \
    --hidden-import ffmpeg \
    --hidden-import ffmpeg._run \
    --hidden-import platform \
    --hidden-import sys \
    --add-data "ffmpeg_bin:ffmpeg_bin" \
    --clean \
    --noconfirm \
    index.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 应用打包成功！"
    echo "打包后的应用位置: dist/视频H264转H265工具/"
    echo ""
    echo "使用说明:"
    echo "1. 打开dist目录"
    echo "2. 运行'视频H264转H265工具'可执行文件"
    echo "3. 应用已内置FFmpeg，无需额外安装依赖"
    echo ""
    echo "示例命令:"
    echo "cd dist/视频H264转H265工具"
    echo "./视频H264转H265工具 --engine ffmpeg --input 你的视频文件.mp4 --output 输出文件.mp4"
else
    echo ""
    echo "❌ 应用打包失败，请检查错误信息"
    exit 1
fi