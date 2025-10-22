#!/bin/bash

# macOS FFmpeg安装脚本
# 此脚本用于在macOS上安装FFmpeg，解决ffmpeg和ffprobe命令依赖问题

echo "=== macOS FFmpeg安装助手 ==="
echo "此脚本将帮助您在macOS上安装FFmpeg（包含ffprobe）"
echo

# 检查是否为macOS
echo "检查操作系统..."
if [[ "$(uname)" != "Darwin" ]]; then
    echo "错误: 此脚本仅适用于macOS系统"
    exit 1
fi

# 检查是否有Homebrew
echo "检查Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "未找到Homebrew，建议使用Homebrew安装FFmpeg"
    echo "您可以先安装Homebrew，然后再运行此脚本"
    echo "安装Homebrew命令: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    
    read -p "是否要继续使用其他方法安装？(y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "退出安装"
        exit 0
    fi
    
    # 提供二进制安装选项
    echo "请选择FFmpeg安装方式："
    echo "1. 通过Homebrew安装（推荐）"
    echo "2. 下载预编译的二进制文件"
    echo "3. 退出"
    
    read -p "请输入选择 [1-3]: " choice
    
    case $choice in
        1)
            echo "请先安装Homebrew："
            echo "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "安装完成后再次运行此脚本"
            exit 0
            ;;
        2)
            echo "准备下载预编译的FFmpeg二进制文件..."
            # 创建临时目录
            TEMP_DIR=$(mktemp -d)
            cd "$TEMP_DIR"
            
            # 下载FFmpeg二进制文件
            echo "从官网下载FFmpeg..."
            curl -L -o ffmpeg-macos.zip https://evermeet.cx/ffmpeg/getrelease/zip
            
            if [ $? -ne 0 ]; then
                echo "下载失败，尝试备用链接..."
                curl -L -o ffmpeg-macos.zip https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
            fi
            
            if [ ! -f "ffmpeg-macos.zip" ]; then
                echo "错误: 下载FFmpeg失败，请手动从 https://ffmpeg.org/download.html 下载"
                exit 1
            fi
            
            # 解压并安装
            echo "解压并安装FFmpeg..."
            unzip ffmpeg-macos.zip || tar -xf ffmpeg-macos.zip
            
            # 检查解压是否成功
            if [ ! -d "ffmpeg-macos" ] && [ ! -d "ffmpeg-*-static" ]; then
                echo "错误: 解压失败，请检查下载的文件"
                exit 1
            fi
            
            # 复制二进制文件到/usr/local/bin
            echo "复制二进制文件到/usr/local/bin（需要管理员权限）..."
            if [ -d "ffmpeg-macos" ]; then
                sudo cp ffmpeg-macos/ffmpeg /usr/local/bin/
                sudo cp ffmpeg-macos/ffprobe /usr/local/bin/
            else
                FFMPEG_DIR=$(ls -d ffmpeg-*-static)
                sudo cp "$FFMPEG_DIR/ffmpeg" /usr/local/bin/
                sudo cp "$FFMPEG_DIR/ffprobe" /usr/local/bin/
            fi
            
            # 设置执行权限
            sudo chmod +x /usr/local/bin/ffmpeg
            sudo chmod +x /usr/local/bin/ffprobe
            
            # 清理临时文件
            cd ..
            rm -rf "$TEMP_DIR"
            ;;
        3)
            echo "退出安装"
            exit 0
            ;;
        *)
            echo "无效选择，退出安装"
            exit 1
            ;;
    esac
else
    # 使用Homebrew安装FFmpeg
            echo "使用Homebrew安装FFmpeg..."
            echo "这将安装ffmpeg和ffprobe"
            echo
            
            read -p "是否跳过Homebrew自动更新以加快安装？(y/n) " -n 1 -r
            echo
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "跳过自动更新，直接安装FFmpeg..."
                export HOMEBREW_NO_AUTO_UPDATE=1
            fi
            
            echo "开始安装FFmpeg..."
            brew install ffmpeg
            
            if [ $? -eq 0 ]; then
                echo "✅ FFmpeg安装成功！"
            else
                echo "❌ FFmpeg安装失败，请检查错误信息"
                exit 1
            fi
fi

# 验证安装
echo
 echo "验证安装..."
if command -v ffmpeg &> /dev/null && command -v ffprobe &> /dev/null; then
    echo "✅ ffmpeg 命令已安装: $(ffmpeg -version | head -n 1)"
    echo "✅ ffprobe 命令已安装: $(ffprobe -version | head -n 1)"
    echo
    echo "🎉 安装完成！您现在可以使用FFmpeg引擎运行视频转换工具了。"
    echo "运行命令: python index.py --engine ffmpeg [其他参数]"
    exit 0
else
    echo "❌ 安装验证失败"
    
    if command -v ffmpeg &> /dev/null; then
        echo "  - ffmpeg 可用"
    else
        echo "  - ffmpeg 不可用，请检查PATH环境变量"
    fi
    
    if command -v ffprobe &> /dev/null; then
        echo "  - ffprobe 可用"
    else
        echo "  - ffprobe 不可用，请检查PATH环境变量"
    fi
    
    echo
    echo "请确保/usr/local/bin在您的PATH环境变量中，或尝试重新安装"
    exit 1
fi