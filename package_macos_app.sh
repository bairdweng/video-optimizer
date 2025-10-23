#!/bin/bash

# macOS专用视频转换器打包脚本
# 这个脚本优化了macOS环境下的打包过程，创建稳定的.app应用

set -e

echo "=== 小压工坊 macOS打包脚本 ==="
echo "开始准备打包环境..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python 3，请先安装Python 3"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip3"
    exit 1
fi

# 更新依赖
echo "更新依赖包..."
pip3 install --upgrade pip
pip3 install --upgrade PyQt5 pyinstaller --no-cache-dir

# 清理旧的构建文件
echo "清理旧的构建文件..."
rm -rf build dist

# 创建应用图标目录
mkdir -p resources

# 检查并下载FFmpeg二进制文件
echo "检查FFmpeg二进制文件..."
# 为两种架构都创建目录
mkdir -p ffmpeg_bin/ffmpeg_macos_arm64
mkdir -p ffmpeg_bin/ffmpeg_macos_x64

MACOS_ARCH=$(uname -m)
if [ "$MACOS_ARCH" = "arm64" ]; then
    FFMPEG_DIR="ffmpeg_bin/ffmpeg_macos_arm64"
    # 为x64架构创建空的假文件以避免PyInstaller错误
    touch ffmpeg_bin/ffmpeg_macos_x64/ffmpeg
    touch ffmpeg_bin/ffmpeg_macos_x64/ffprobe
    chmod +x ffmpeg_bin/ffmpeg_macos_x64/ffmpeg
    chmod +x ffmpeg_bin/ffmpeg_macos_x64/ffprobe
else
    FFMPEG_DIR="ffmpeg_bin/ffmpeg_macos_x64"
    # 为arm64架构创建空的假文件以避免PyInstaller错误
    touch ffmpeg_bin/ffmpeg_macos_arm64/ffmpeg
    touch ffmpeg_bin/ffmpeg_macos_arm64/ffprobe
    chmod +x ffmpeg_bin/ffmpeg_macos_arm64/ffmpeg
    chmod +x ffmpeg_bin/ffmpeg_macos_arm64/ffprobe
fi

# 检查当前架构的FFmpeg是否已存在且非空
if [ ! -f "$FFMPEG_DIR/ffmpeg" ] || [ ! -s "$FFMPEG_DIR/ffmpeg" ]; then
    echo "正在下载FFmpeg二进制文件..."
    # 下载FFmpeg (使用evermeet.cx提供的版本)
    if command -v curl &> /dev/null; then
        echo "使用curl下载FFmpeg..."
        curl -L https://evermeet.cx/ffmpeg/getrelease/zip -o /tmp/ffmpeg.zip
    else
        echo "使用wget下载FFmpeg..."
        wget -O /tmp/ffmpeg.zip https://evermeet.cx/ffmpeg/getrelease/zip
    fi
    
    # 解压文件
    echo "解压FFmpeg..."
    mkdir -p /tmp/ffmpeg_temp
    unzip -o /tmp/ffmpeg.zip -d /tmp/ffmpeg_temp
    
    # 复制文件到正确位置
    cp /tmp/ffmpeg_temp/ffmpeg "$FFMPEG_DIR/"
    cp /tmp/ffmpeg_temp/ffprobe "$FFMPEG_DIR/"
    
    # 设置执行权限
    chmod +x "$FFMPEG_DIR/ffmpeg"
    chmod +x "$FFMPEG_DIR/ffprobe"
    
    # 清理临时文件
    rm -rf /tmp/ffmpeg.zip /tmp/ffmpeg_temp
    
    echo "✅ FFmpeg下载并安装成功！"
else
    echo "✅ FFmpeg已存在，跳过下载"
fi

# 确保所有需要的文件都存在
echo "确保所有FFmpeg文件都存在..."

# 创建一个简单的图标文件（使用base64编码的SVG图标）
echo "创建应用图标..."
cat > resources/icon.svg << EOF
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <rect width="512" height="512" rx="100" fill="#4CAF50"/>
  <path d="M128 128L384 256L128 384Z" fill="white" opacity="0.8"/>
  <circle cx="256" cy="256" r="60" fill="white"/>
  <circle cx="256" cy="256" r="30" fill="#4CAF50"/>
</svg>
EOF

# 转换SVG为icns（需要inkscape）
if command -v inkscape &> /dev/null; then
    echo "使用inkscape创建图标..."
    mkdir -p /tmp/icon.iconset
    inkscape -z -w 16 -h 16 -o /tmp/icon.iconset/icon_16x16.png resources/icon.svg
    inkscape -z -w 32 -h 32 -o /tmp/icon.iconset/icon_16x16@2x.png resources/icon.svg
    inkscape -z -w 32 -h 32 -o /tmp/icon.iconset/icon_32x32.png resources/icon.svg
    inkscape -z -w 64 -h 64 -o /tmp/icon.iconset/icon_32x32@2x.png resources/icon.svg
    inkscape -z -w 128 -h 128 -o /tmp/icon.iconset/icon_128x128.png resources/icon.svg
    inkscape -z -w 256 -h 256 -o /tmp/icon.iconset/icon_128x128@2x.png resources/icon.svg
    inkscape -z -w 256 -h 256 -o /tmp/icon.iconset/icon_256x256.png resources/icon.svg
    inkscape -z -w 512 -h 512 -o /tmp/icon.iconset/icon_256x256@2x.png resources/icon.svg
    inkscape -z -w 512 -h 512 -o /tmp/icon.iconset/icon_512x512.png resources/icon.svg
    inkscape -z -w 1024 -h 1024 -o /tmp/icon.iconset/icon_512x512@2x.png resources/icon.svg
    iconutil -c icns -o resources/icon.icns /tmp/icon.iconset
    rm -rf /tmp/icon.iconset
else
    echo "警告: 未找到inkscape，使用默认图标"
    # 创建一个简单的PNG图标作为后备
    python3 -c "from PIL import Image, ImageDraw; img = Image.new('RGB', (512, 512), color='#4CAF50'); d = ImageDraw.Draw(img); d.rounded_rectangle([(0,0), (512,512)], radius=100, fill='#4CAF50'); d.polygon([(128,128), (384,256), (128,384)], fill='white', outline=''); d.ellipse([(196,196), (316,316)], fill='white'); d.ellipse([(226,226), (286,286)], fill='#4CAF50'); img.save('resources/icon.png')" 2>/dev/null || echo "未能创建图标，将使用默认图标"
fi

# 创建优化的.spec文件
echo "创建优化的打包配置..."
cat > video_converter_macos.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 导入必要的模块用于.spec文件
import os
import sys

# 确保所有文件路径都存在
def ensure_file_exists(src_path):
    if not os.path.exists(src_path):
        # 创建空文件
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        open(src_path, 'w').close()
        os.chmod(src_path, 0o755)

# 确保所有需要的FFmpeg文件都存在
ensure_file_exists('ffmpeg_bin/ffmpeg_macos_arm64/ffmpeg')
ensure_file_exists('ffmpeg_bin/ffmpeg_macos_arm64/ffprobe')
ensure_file_exists('ffmpeg_bin/ffmpeg_macos_x64/ffmpeg')
ensure_file_exists('ffmpeg_bin/ffmpeg_macos_x64/ffprobe')

a = Analysis(['simple_gui_converter.py'],
             pathex=['$PWD'],
             binaries=[],
             datas=[
                 ('ffmpeg_bin/ffmpeg_macos_arm64/ffmpeg', 'ffmpeg/ffmpeg_macos_arm64'),
                 ('ffmpeg_bin/ffmpeg_macos_arm64/ffprobe', 'ffmpeg/ffmpeg_macos_arm64'),
                 ('ffmpeg_bin/ffmpeg_macos_x64/ffmpeg', 'ffmpeg/ffmpeg_macos_x64'),
                 ('ffmpeg_bin/ffmpeg_macos_x64/ffprobe', 'ffmpeg/ffmpeg_macos_x64'),
             ],
             hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'shutil', 'platform', 'os'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=['PyQt5.QtNetwork'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='视频H264转H265工具',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='小压工坊')

app = BUNDLE(coll,
             name='小压工坊.app',
             icon='resources/icon.icns' if os.path.exists('resources/icon.icns') else None,
             bundle_identifier='com.videooptimizer.converter',
             info_plist={
                 'NSHighResolutionCapable': True,
                 'CFBundleName': '小压工坊',
                 'CFBundleDisplayName': '小压工坊',
                 'CFBundleVersion': '1.0',
                 'CFBundleShortVersionString': '1.0',
                 'LSMinimumSystemVersion': '10.13',
                 'NSCameraUsageDescription': '该应用需要访问视频文件进行转换',
                 'NSMicrophoneUsageDescription': '该应用需要访问音频流进行处理',
                 'CFBundleDocumentTypes': [
                     {
                         'CFBundleTypeName': '视频文件',
                         'CFBundleTypeRole': 'Viewer',
                         'LSItemContentTypes': ['public.movie', 'public.video'],
                         'LSHandlerRank': 'Owner'
                     }
                 ]
             })
EOF

# 使用PyInstaller打包
echo "开始打包应用..."
PYTHONPATH=$(python3 -c "import sys; print(':'.join(sys.path))") pyinstaller video_converter_macos.spec

# 检查打包结果
if [ -d "dist/小压工坊.app" ]; then
    echo "✅ 应用打包成功！"
    echo "📁 应用位置: dist/小压工坊.app"
    echo "\n📝 使用说明:"
    echo "1. 请将应用拖拽到Applications文件夹以完成安装"
    echo "2. 首次打开时，右键点击应用并选择'打开'"
    echo "3. 在弹出的对话框中点击'打开'以确认"
    echo "4. 应用已内置FFmpeg，无需单独安装依赖"
    echo "\n💡 注意事项:"
    echo "- 应用已配置为支持高分辨率显示"
    echo "- 已添加视频文件关联"
    echo "- 日志文件保存在: ~/Library/Application Support/VideoConverter/"
    echo "- 如有问题，请查看日志文件了解详情"
else
    echo "❌ 应用打包失败，请检查错误信息"
    exit 1
fi

# 清理临时文件
echo "清理临时文件..."
rm -f video_converter_macos.spec

echo "\n=== 打包完成！==="