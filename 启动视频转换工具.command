#!/bin/bash

# 视频H264转H265工具启动脚本
# 这个脚本提供了一个双击运行的方式来启动Python版本的GUI工具

echo "=== 启动视频H264转H265工具 ==="
echo "正在初始化环境..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    osascript -e 'tell app "System Events" to display dialog "错误: 未找到Python3，请先安装Python3" buttons {"确定"} with icon caution'
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "正在检查依赖..."

# 检查PyQt5是否安装
if ! python3 -c "import PyQt5" &> /dev/null; then
    echo "正在安装必要的依赖PyQt5..."
    pip3 install PyQt5 --no-cache-dir
    if [ $? -ne 0 ]; then
        echo "安装PyQt5失败，请手动安装: pip3 install PyQt5"
        osascript -e 'tell app "System Events" to display dialog "安装PyQt5失败，请手动安装: pip3 install PyQt5" buttons {"确定"} with icon caution'
        exit 1
    fi
fi

echo "正在启动简化版GUI工具..."

# 运行简化版GUI工具
python3 simple_gui_converter.py

echo "程序已退出"
read -p "按任意键关闭窗口..."