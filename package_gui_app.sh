#!/bin/bash

# 视频H264转H265工具 - GUI版本打包脚本

echo "=== 开始打包视频H264转H265工具(GUI)版本 ==="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 安装必要的依赖
echo "🔧 安装必要的依赖..."
pip3 install PyQt5 pyinstaller --upgrade --no-cache-dir

# 创建dist和build目录（如果不存在）
mkdir -p dist build

# 清理之前的构建
rm -rf build dist *.spec

# 打包应用程序（简化版本，提高兼容性）
echo "🔧 正在打包应用程序..."
pyinstaller --windowed \
    --name "视频H264转H265工具(GUI)" \
    --clean \
    --onedir \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    gui_video_converter.py

# 检查打包是否成功
if [ $? -eq 0 ]; then
    echo "✅ 打包成功！"
    echo "输出文件位于: dist/视频H264转H265工具(GUI)"
    echo ""
    echo "使用说明:"
    echo "1. 由于macOS的限制，打包后的GUI应用可能仍有兼容性问题"
    echo "2. 推荐使用的运行方式：直接从终端运行Python脚本"
    echo "   命令: python3 gui_video_converter.py"
    echo "3. 运行可执行文件前，请确保已安装FFmpeg"
    echo "4. macOS用户可能需要授权运行: 右键点击文件 -> 打开 -> 允许"
else
    echo "❌ 打包失败，请检查错误信息"
    echo "建议直接使用Python脚本方式运行: python3 gui_video_converter.py"
fi