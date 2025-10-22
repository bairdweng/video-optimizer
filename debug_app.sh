#!/bin/bash

# 视频转换工具调试脚本
# 用于捕获应用程序崩溃的错误日志

echo "=== 视频H264转H265工具 - 调试脚本 ==="
echo ""

# 设置日志文件
LOG_FILE="app_crash_debug.log"
echo "调试日志将保存到: $LOG_FILE"
echo "--------------------------------------------"

# 清理旧的日志文件
rm -f "$LOG_FILE"

# 输出系统信息
echo "[系统信息]" >> "$LOG_FILE"
echo "macOS 版本: $(sw_vers -productName) $(sw_vers -productVersion)" >> "$LOG_FILE"
echo "Python 版本: $(python3 --version 2>&1)" >> "$LOG_FILE"
echo "PyQt5 版本: $(python3 -c 'from PyQt5.QtCore import QT_VERSION_STR; print(f"Qt: {QT_VERSION_STR}"); from PyQt5 import __version__; print(f"PyQt5: {__version__}")' 2>&1)" >> "$LOG_FILE"
echo "FFmpeg 版本: $(ffmpeg -version 2>&1 | head -n 1)" >> "$LOG_FILE"
echo "--------------------------------------------" >> "$LOG_FILE"

# 检查应用程序是否存在
APP_PATH="dist/视频H264转H265工具.app"
if [ ! -d "$APP_PATH" ]; then
    echo "错误: 找不到应用程序 $APP_PATH"
    echo "请确保应用程序已正确打包" >> "$LOG_FILE"
    exit 1
fi

echo "[方法1: 从命令行运行应用程序]"
echo "将显示应用程序的标准输出和错误信息..."
echo "--------------------------------------------"
echo "[命令行运行结果]" >> "$LOG_FILE"

# 从命令行运行应用程序并捕获输出
"$APP_PATH/Contents/MacOS/视频H264转H265工具" 2>&1 | tee -a "$LOG_FILE"
echo "--------------------------------------------" >> "$LOG_FILE"

# 等待几秒钟让系统写入崩溃报告
echo ""
echo "正在检查系统崩溃报告..."
sleep 3

echo "[方法2: 检查系统控制台日志]"
echo "最近的应用程序崩溃信息:"
echo "--------------------------------------------"
echo "[控制台日志 - 最近的崩溃]" >> "$LOG_FILE"

# 从控制台日志中获取最近的崩溃信息
log show --predicate 'process == "视频H264转H265工具" AND (eventMessage CONTAINS "error" OR eventMessage CONTAINS "crash" OR eventMessage CONTAINS "exception" OR eventMessage CONTAINS "quit unexpectedly")' --last 5m --info >> "$LOG_FILE" 2>&1

# 检查崩溃报告目录
CRASH_REPORTS_DIR="$HOME/Library/Logs/DiagnosticReports"
if [ -d "$CRASH_REPORTS_DIR" ]; then
    echo "[崩溃报告文件]" >> "$LOG_FILE"
    echo "最近的崩溃报告文件:" >> "$LOG_FILE"
    ls -t "$CRASH_REPORTS_DIR"/视频* 2>/dev/null | head -n 3 >> "$LOG_FILE" 2>&1
fi

# 检查应用程序包的完整性
echo "--------------------------------------------"
echo "检查应用程序包的完整性..."
echo "[应用程序包信息]" >> "$LOG_FILE"

# 检查应用程序结构
find "$APP_PATH/Contents" -type f -name "*.so" | sort >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"
echo "Python 库:" >> "$LOG_FILE"
find "$APP_PATH/Contents" -path "*/lib/python*" -type f | grep -E "(PyQt5|Qt)" | sort >> "$LOG_FILE" 2>&1

# 检查DYLD_LIBRARY_PATH设置
echo "" >> "$LOG_FILE"
echo "[环境变量检查]" >> "$LOG_FILE"
echo "DYLD_LIBRARY_PATH: ${DYLD_LIBRARY_PATH:-未设置}" >> "$LOG_FILE"

# 提供调试建议
echo "--------------------------------------------"
echo "调试完成！"
echo "错误日志已保存到: $LOG_FILE"
echo ""
echo "📋 请检查以下几点:"
echo "1. 应用程序是否具有正确的权限"
echo "2. FFmpeg是否已正确安装并在系统PATH中"
echo "3. 尝试临时禁用系统完整性保护(SIP)进行测试"
echo "4. 检查是否有与PyQt5或Qt相关的兼容性问题"
echo ""
echo "🔍 错误日志可以帮助我们找出具体问题所在"