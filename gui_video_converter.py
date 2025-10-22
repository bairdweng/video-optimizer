#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频H264转H265工具 - GUI版本
使用PyQt5创建图形界面，使用FFmpeg引擎进行视频转码
仅支持单个文件转换
"""

import os
import sys
import logging
import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QComboBox, QSlider, QMessageBox,
    QProgressBar, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("video_conversion_gui.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConversionThread(QThread):
    """转换线程，用于在后台执行视频转换，避免界面卡顿"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str, float, str)
    
    def __init__(self, input_file, output_file, crf, preset, audio_codec, audio_bitrate, threads):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.crf = crf
        self.preset = preset
        self.audio_codec = audio_codec
        self.audio_bitrate = audio_bitrate
        self.threads = threads
    
    def run(self):
        try:
            # 获取文件信息
            input_info = self.get_video_info(self.input_file)
            if not input_info:
                self.finished.emit(False, "无法获取输入文件信息", 0, "")
                return
            
            # 构建ffmpeg命令
            cmd = ["ffmpeg", "-i", self.input_file]
            cmd.extend(["-c:v", "libx265", "-crf", str(self.crf), "-preset", self.preset, "-tag:v", "hvc1"])
            
            # 添加线程参数
            if self.threads > 0:
                cmd.extend(["-threads", str(self.threads)])
            
            # 添加音频参数
            cmd.extend(["-c:a", self.audio_codec, "-b:a", self.audio_bitrate])
            cmd.extend(["-y", self.output_file])
            
            logger.info(f"开始转换: {self.input_file} -> {self.output_file}")
            logger.info(f"使用参数: CRF={self.crf}, 预设={self.preset}, 音频={self.audio_codec}@{self.audio_bitrate}")
            logger.info(f"执行的FFmpeg命令: {' '.join(cmd)}")
            
            start_time = time.time()
            
            # 执行ffmpeg命令
            process = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if process.returncode != 0:
                error_msg = f"FFmpeg执行失败，返回码: {process.returncode}\n错误信息: {process.stderr[:200]}..."
                logger.error(error_msg)
                self.finished.emit(False, error_msg, duration, "")
                return
            
            # 检查输出文件是否存在
            if not os.path.exists(self.output_file):
                error_msg = "输出文件未生成"
                logger.error(error_msg)
                self.finished.emit(False, error_msg, duration, "")
                return
            
            # 获取输出文件信息
            output_info = self.get_video_info(self.output_file)
            if output_info:
                # 计算压缩率
                compression_ratio = (1 - output_info['file_size'] / input_info['file_size']) * 100
                output_size = output_info['human_size']
                logger.info(f"转换成功完成！耗时: {duration:.2f} 秒")
                logger.info(f"输出文件信息: {output_size}, 压缩率: {compression_ratio:.2f}%")
                self.finished.emit(True, "转换成功", duration, output_size)
            else:
                self.finished.emit(True, "转换成功", duration, "未知")
                
        except Exception as e:
            error_msg = f"转换过程中出错: {str(e)}"
            logger.error(error_msg)
            self.finished.emit(False, error_msg, 0, "")
    
    def get_video_info(self, file_path):
        """获取视频文件信息"""
        try:
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            return {
                "file_size": file_size,
                "human_size": f"{file_size/1024/1024:.2f} MB"
            }
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return None

class VideoConverterApp(QMainWindow):
    """视频转换工具主窗口"""
    
    def __init__(self):
        super().__init__()
        self.input_file = ""
        self.output_file = ""
        self.conversion_thread = None
        self.init_ui()
        self.check_ffmpeg_installed()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("视频H264转H265转换工具")
        self.setGeometry(300, 300, 600, 450)
        
        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("视频H264转H265转换工具")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        
        # 输入文件选择
        input_layout = QHBoxLayout()
        self.input_label = QLabel("未选择文件")
        self.input_label.setFixedHeight(30)
        self.input_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        input_button = QPushButton("选择输入文件")
        input_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(self.input_label, 1)
        input_layout.addWidget(input_button)
        
        # 输出文件选择
        output_layout = QHBoxLayout()
        self.output_label = QLabel("自动生成")
        self.output_label.setFixedHeight(30)
        self.output_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        output_button = QPushButton("选择输出文件")
        output_button.clicked.connect(self.select_output_file)
        output_layout.addWidget(self.output_label, 1)
        output_layout.addWidget(output_button)
        
        file_layout.addLayout(input_layout)
        file_layout.addLayout(output_layout)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # 参数设置区域
        params_group = QGroupBox("参数设置")
        params_layout = QVBoxLayout()
        
        # CRF设置
        crf_layout = QHBoxLayout()
        crf_label = QLabel("视频质量 (CRF):")
        self.crf_value_label = QLabel("28")
        self.crf_slider = QSlider(Qt.Horizontal)
        self.crf_slider.setMinimum(0)
        self.crf_slider.setMaximum(51)
        self.crf_slider.setValue(28)
        self.crf_slider.valueChanged.connect(self.update_crf_label)
        crf_layout.addWidget(crf_label)
        crf_layout.addWidget(self.crf_slider, 1)
        crf_layout.addWidget(self.crf_value_label)
        
        # 预设设置
        preset_layout = QHBoxLayout()
        preset_label = QLabel("编码预设:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"])
        self.preset_combo.setCurrentText("medium")
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo, 1)
        
        # 音频设置
        audio_layout = QHBoxLayout()
        audio_label = QLabel("音频比特率:")
        self.audio_combo = QComboBox()
        self.audio_combo.addItems(["64k", "96k", "128k", "192k", "256k", "320k"])
        self.audio_combo.setCurrentText("128k")
        audio_layout.addWidget(audio_label)
        audio_layout.addWidget(self.audio_combo, 1)
        
        params_layout.addLayout(crf_layout)
        params_layout.addLayout(preset_layout)
        params_layout.addLayout(audio_layout)
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # 进度条区域
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(25)
        main_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        self.convert_button = QPushButton("开始转换")
        self.convert_button.setFixedHeight(40)
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        cancel_button = QPushButton("取消")
        cancel_button.setFixedHeight(40)
        cancel_button.clicked.connect(self.cancel_conversion)
        
        buttons_layout.addWidget(self.convert_button, 2)
        buttons_layout.addWidget(cancel_button, 1)
        main_layout.addLayout(buttons_layout)
    
    def update_crf_label(self):
        """更新CRF值显示"""
        self.crf_value_label.setText(str(self.crf_slider.value()))
    
    def select_input_file(self):
        """选择输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.mov *.mkv *.avi *.wmv *.flv *.webm)"
        )
        if file_path:
            self.input_file = file_path
            self.input_label.setText(os.path.basename(file_path))
            
            # 自动生成输出文件名
            base_name, ext = os.path.splitext(file_path)
            self.output_file = f"{base_name}_h265{ext}"
            self.output_label.setText(os.path.basename(self.output_file))
    
    def select_output_file(self):
        """选择输出文件"""
        if not self.input_file:
            QMessageBox.warning(self, "警告", "请先选择输入文件")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存输出文件", self.output_file,
            "MP4文件 (*.mp4);;所有文件 (*)"
        )
        if file_path:
            self.output_file = file_path
            self.output_label.setText(os.path.basename(file_path))
    
    def check_ffmpeg_installed(self):
        """检查FFmpeg是否安装"""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         timeout=5)
            self.status_label.setText("FFmpeg检查通过")
            self.status_label.setStyleSheet("color: green;")
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.status_label.setText("⚠️  未找到FFmpeg，请先安装")
            self.status_label.setStyleSheet("color: red;")
            # 显示警告但不阻止应用继续运行
            QMessageBox.warning(
                self, "FFmpeg未找到", 
                "未找到FFmpeg。请先安装FFmpeg工具，否则无法进行转换。\n" \
                "macOS用户: brew install ffmpeg\n" \
                "Windows用户: 从官网下载并安装\n" \
                "Linux用户: sudo apt-get install ffmpeg"
            )
            return False
    
    def start_conversion(self):
        """开始转换"""
        # 检查输入文件
        if not self.input_file or not os.path.exists(self.input_file):
            QMessageBox.warning(self, "警告", "请选择有效的输入文件")
            return
        
        # 检查FFmpeg
        if not self.check_ffmpeg_installed():
            QMessageBox.critical(self, "无法开始转换", "FFmpeg未安装，无法进行视频转换。\n请按照提示安装FFmpeg后再重试。")
            return
        
        # 检查输出目录
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建输出目录失败: {str(e)}")
                return
        
        # 准备转换参数
        crf = self.crf_slider.value()
        preset = self.preset_combo.currentText()
        audio_codec = "aac"  # 固定使用AAC编码器
        audio_bitrate = self.audio_combo.currentText()
        threads = 0  # 使用所有可用线程
        
        # 禁用按钮
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在转换中...")
        
        # 创建并启动转换线程
        self.conversion_thread = ConversionThread(
            self.input_file, self.output_file, crf, preset, audio_codec, audio_bitrate, threads
        )
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.start()
    
    def cancel_conversion(self):
        """取消转换"""
        if self.conversion_thread and self.conversion_thread.isRunning():
            # 这里可以尝试终止ffmpeg进程，但通常不建议强制终止
            # 可以提示用户等待完成，或者实现更优雅的终止方式
            QMessageBox.information(self, "提示", "转换已提交，请等待完成")
        else:
            # 如果不在转换中，重置界面
            self.reset_ui()
    
    def conversion_finished(self, success, message, duration, output_size):
        """转换完成后的处理"""
        # 更新进度条和状态
        self.progress_bar.setValue(100)
        
        if success:
            self.status_label.setText(f"转换成功！耗时: {duration:.2f}秒, 输出大小: {output_size}")
            self.status_label.setStyleSheet("color: green;")
            QMessageBox.information(
                self, "成功", 
                f"转换成功完成！\n" \
                f"耗时: {duration:.2f}秒\n" \
                f"输出文件: {os.path.basename(self.output_file)}\n" \
                f"输出大小: {output_size}"
            )
        else:
            self.status_label.setText(f"转换失败: {message}")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "失败", message)
        
        # 启用按钮
        self.convert_button.setEnabled(True)
    
    def reset_ui(self):
        """重置界面状态"""
        self.status_label.setText("准备就绪")
        self.status_label.setStyleSheet("")
        self.progress_bar.setValue(0)

def main():
    """主函数"""
    try:
        # 确保中文显示正常
        font = QFont("SimHei")
        QApplication.setFont(font)
        
        # 创建应用程序和窗口
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # 设置全局样式
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f5;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: #333333;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #cccccc;
                height: 8px;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QSlider::handle:horizontal {
                background-color: #4CAF50;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)
        
        # 创建并显示窗口
        window = VideoConverterApp()
        window.show()
        
        # 运行应用程序
        sys.exit(app.exec_())
    except Exception as e:
        # 捕获所有异常并写入日志
        logger.error(f"应用程序启动失败: {str(e)}")
        # 显示错误消息框
        import traceback
        error_detail = traceback.format_exc()
        with open("gui_error.log", "w") as f:
            f.write(error_detail)
        # 如果无法启动GUI，至少在终端显示错误
        print(f"应用程序启动失败: {str(e)}")
        print("详细错误信息已写入 gui_error.log")
        sys.exit(1)

if __name__ == "__main__":
    main()