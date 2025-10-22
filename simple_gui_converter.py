#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版视频H264转H265工具 (GUI版本)
这个版本更简单，专注于基本功能和稳定性
"""

import os
import sys
import subprocess
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont

# 配置日志 - 使用用户应用数据目录
import os
# 使用用户的应用支持目录存储日志，而不是桌面
log_dir = os.path.expanduser("~/Library/Application Support/VideoConverter")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "video_converter.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"日志文件保存到: {log_file}")

class SimpleVideoConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_file = None
        self.init_ui()
        self.check_ffmpeg_installed()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("视频H264转H265工具 (简化版)")
        self.setGeometry(100, 100, 600, 300)
        
        # 主窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 设置字体
        font = QFont("SimHei", 10)
        self.setFont(font)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        
        self.file_label = QLabel("未选择文件")
        self.file_label.setWordWrap(True)
        file_layout.addWidget(self.file_label)
        
        select_button = QPushButton("选择视频文件")
        select_button.clicked.connect(self.select_file)
        file_layout.addWidget(select_button)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # 状态区域
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("准备就绪")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        convert_button = QPushButton("开始转换")
        convert_button.clicked.connect(self.start_conversion)
        button_layout.addWidget(convert_button)
        
        exit_button = QPushButton("退出")
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)
        
        main_layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f0f0f0;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 10px 0;
                padding: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                margin: 5px 0;
            }
        """)
    
    def select_file(self):
        """选择视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", 
            "视频文件 (*.mp4 *.mov *.mkv *.avi *.flv *.wmv);;所有文件 (*)"
        )
        
        if file_path:
            self.input_file = file_path
            self.file_label.setText(f"已选择: {os.path.basename(file_path)}")
            # 自动生成输出文件名
            base_name = os.path.splitext(file_path)[0]
            self.output_file = f"{base_name}_h265.mp4"
            logger.info(f"选择文件: {file_path}")
    
    def get_ffmpeg_path(self):
        """获取FFmpeg可执行文件路径，优先使用内置版本"""
        import sys
        import platform
        
        # 尝试内置的FFmpeg
        # 获取当前可执行文件所在目录
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            base_dir = os.path.dirname(sys.executable)
            # 在Mac应用中，实际可执行文件在Contents/MacOS/目录
            if base_dir.endswith('/Contents/MacOS'):
                base_dir = os.path.dirname(os.path.dirname(base_dir))
                ffmpeg_dir = os.path.join(base_dir, 'Contents', 'Resources', 'ffmpeg')
            else:
                ffmpeg_dir = os.path.join(base_dir, 'ffmpeg')
        else:
            # 开发环境
            base_dir = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_dir = os.path.join(base_dir, 'ffmpeg_bin')
        
        # 根据系统架构选择对应的FFmpeg目录
        system = platform.system()
        architecture = platform.machine()
        
        if system == 'Darwin':
            if architecture in ['arm64', 'aarch64']:
                ffmpeg_dir = os.path.join(ffmpeg_dir, 'ffmpeg_macos_arm64')
            else:
                ffmpeg_dir = os.path.join(ffmpeg_dir, 'ffmpeg_macos_x64')
        elif system == 'Windows':
            ffmpeg_dir = os.path.join(ffmpeg_dir, 'ffmpeg_windows_x64')
        else:  # Linux
            ffmpeg_dir = os.path.join(ffmpeg_dir, 'ffmpeg_linux_x64')
        
        # 构建完整的FFmpeg路径
        if system == 'Windows':
            ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
        else:
            ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg')
        
        # 如果内置FFmpeg存在，返回它的路径
        if os.path.isfile(ffmpeg_path):
            logger.info(f"找到内置FFmpeg: {ffmpeg_path}")
            return ffmpeg_path
        
        # 否则尝试系统路径中的FFmpeg
        try:
            import shutil
            system_ffmpeg = shutil.which('ffmpeg')
            if system_ffmpeg:
                logger.info(f"找到系统FFmpeg: {system_ffmpeg}")
                return system_ffmpeg
        except Exception as e:
            logger.warning(f"检查系统FFmpeg时出错: {str(e)}")
        
        logger.error("未找到FFmpeg")
        return None
    
    def check_ffmpeg_installed(self):
        """检查FFmpeg是否可用（内置或系统安装）"""
        ffmpeg_path = self.get_ffmpeg_path()
        if ffmpeg_path:
            try:
                subprocess.run([ffmpeg_path, "-version"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             timeout=5)
                self.status_label.setText("✅ FFmpeg可用")
                self.status_label.setStyleSheet("color: green;")
                return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.status_label.setText("❌ FFmpeg文件存在但无法执行")
                self.status_label.setStyleSheet("color: red;")
                return False
        else:
            self.status_label.setText("❌ 未找到FFmpeg")
            self.status_label.setStyleSheet("color: red;")
            return False
    
    def start_conversion(self):
        """开始转换"""
        # 检查输入文件
        if not self.input_file or not os.path.exists(self.input_file):
            QMessageBox.warning(self, "警告", "请选择有效的视频文件")
            return
        
        # 检查FFmpeg
        if not self.check_ffmpeg_installed():
            QMessageBox.critical(self, "错误", "FFmpeg未安装，无法进行转换")
            return
        
        # 确认转换
        confirm = QMessageBox.question(
            self, "确认转换", 
            f"确定要将视频转换为H.265格式吗？\n"\
            f"输入: {os.path.basename(self.input_file)}\n"\
            f"输出: {os.path.basename(self.output_file)}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        self.status_label.setText("🔄 正在转换中...")
        self.status_label.setStyleSheet("color: orange;")
        
        # 获取FFmpeg路径
        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            QMessageBox.critical(self, "错误", "未找到FFmpeg，无法进行转换")
            self.status_label.setText("❌ 未找到FFmpeg")
            self.status_label.setStyleSheet("color: red;")
            return
        
        # 构建FFmpeg命令
        ffmpeg_cmd = [
            ffmpeg_path,
            "-i", self.input_file,
            "-c:v", "libx265",
            "-crf", "28",  # 默认CRF值
            "-preset", "medium",  # 默认预设
            "-c:a", "aac",  # 音频编码
            "-b:a", "128k",  # 音频比特率
            "-y",  # 覆盖已存在的文件
            self.output_file
        ]
        
        try:
            # 执行转换
            self.status_label.setText("🔄 转换进行中，请稍候...")
            process = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            # 检查输出文件
            if os.path.exists(self.output_file):
                self.status_label.setText("✅ 转换成功！")
                self.status_label.setStyleSheet("color: green;")
                QMessageBox.information(
                    self, "成功", 
                    f"视频转换成功！\n输出文件: {self.output_file}"
                )
                logger.info(f"转换成功: {self.output_file}")
            else:
                raise Exception("输出文件未生成")
                
        except subprocess.CalledProcessError as e:
            error_msg = f"转换失败: {e.stderr}"
            self.status_label.setText("❌ 转换失败")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "转换失败", 
                                f"FFmpeg执行出错:\n{e.stderr[:200]}...")
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"转换出错: {str(e)}"
            self.status_label.setText("❌ 转换失败")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "转换失败", error_msg)
            logger.error(error_msg)

def main():
    """主函数"""
    try:
        # 创建应用程序和窗口
        app = QApplication(sys.argv)
        
        # 创建并显示窗口
        window = SimpleVideoConverter()
        window.show()
        
        # 运行应用程序
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"应用程序启动失败: {str(e)}")
        print(f"应用程序启动失败: {str(e)}")
        import traceback
        with open("simple_gui_error.log", "w") as f:
            f.write(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()