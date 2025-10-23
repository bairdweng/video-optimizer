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
    QPushButton, QLabel, QFileDialog, QMessageBox, QGroupBox, QProgressBar
)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont
import datetime

# 配置日志 - 使用安全的日志路径和容错机制
import os

def setup_safe_logging():
    """设置安全的日志记录，即使无法创建日志文件也不会导致程序崩溃"""
    # 创建logger实例
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 添加StreamHandler（总是可用）
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    # 尝试添加应用支持目录日志文件（但不中断程序）
    try:
        log_dir = os.path.expanduser("~/Library/Application Support/VideoConverter")
        # 使用更安全的目录创建方式
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except (OSError, PermissionError):
                # 如果无法创建目录，使用临时目录作为备选
                log_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                
        app_log_file = os.path.join(log_dir, "video_converter.log")
        file_handler = logging.FileHandler(app_log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"日志文件保存到: {app_log_file}")
    except Exception as e:
        logger.warning(f"无法创建应用日志文件: {str(e)}")
    
    # 尝试添加工作目录日志（但不中断程序）
    try:
        # 使用更安全的工作目录检查
        safe_cwd = os.getcwd() if os.access(os.getcwd(), os.W_OK) else os.path.expanduser("~")
        working_dir_log = os.path.join(safe_cwd, "video_converter_debug.log")
        working_handler = logging.FileHandler(working_dir_log)
        working_handler.setFormatter(formatter)
        logger.addHandler(working_handler)
        logger.info(f"调试日志同时保存到: {working_dir_log}")
    except Exception as e:
        logger.warning(f"无法创建工作目录日志文件: {str(e)}")
    
    return logger

# 设置安全的日志记录
logger = setup_safe_logging()

class SimpleVideoConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_file = None
        self.init_ui()
        self.check_ffmpeg_installed()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("小压工坊")
        self.setGeometry(100, 100, 600, 350)
        
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
        status_group = QGroupBox("转换状态")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("准备就绪")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        # 添加进度条
        progress_layout = QHBoxLayout()
        progress_label = QLabel("进度:")
        progress_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumWidth(400)
        self.progress_bar.setFormat("%p%")
        progress_layout.addWidget(self.progress_bar)
        
        status_layout.addLayout(progress_layout)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.convert_button = QPushButton("开始转换")
        self.convert_button.clicked.connect(self.start_conversion)
        button_layout.addWidget(self.convert_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel_conversion)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
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
        logger.debug(f"检查FFmpeg路径: {ffmpeg_path}")
        
        if ffmpeg_path:
            # 首先检查文件是否存在且可执行
            if not os.path.isfile(ffmpeg_path):
                self.status_label.setText("❌ FFmpeg文件不存在")
                self.status_label.setStyleSheet("color: red;")
                logger.error(f"FFmpeg文件不存在: {ffmpeg_path}")
                return False
            
            if not os.access(ffmpeg_path, os.X_OK):
                try:
                    # 尝试添加执行权限
                    os.chmod(ffmpeg_path, 0o755)
                    logger.info(f"已添加FFmpeg执行权限: {ffmpeg_path}")
                except Exception as e:
                    self.status_label.setText("❌ FFmpeg无执行权限")
                    self.status_label.setStyleSheet("color: red;")
                    logger.error(f"FFmpeg无执行权限: {str(e)}")
                    return False
            
            # 版本检查可能会超时，特别是在打包后的应用中
            # 增加超时时间并优化错误处理
            try:
                # 简化检查，只执行一个简单命令
                result = subprocess.run([ffmpeg_path, "-version"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      text=True,
                                      timeout=15)  # 增加超时时间
                
                # 即使没有完整输出，只要不超时就认为可用
                logger.info(f"FFmpeg基本功能检查通过")
                
                # 不要在启动时检查编解码器，避免额外的超时风险
                # 只简单标记FFmpeg可用
                self.status_label.setText("✅ FFmpeg可用")
                self.status_label.setStyleSheet("color: green;")
                return True
                
            except subprocess.TimeoutExpired:
                # 超时不应该导致应用失败，只记录警告
                logger.warning("FFmpeg版本检查超时，但将继续")
                self.status_label.setText("⚠️  FFmpeg检查超时，但将继续尝试")
                self.status_label.setStyleSheet("color: orange;")
                # 即使超时也返回True，让应用继续运行
                return True
            except (FileNotFoundError, OSError) as e:
                error_msg = f"FFmpeg执行错误: {str(e)}"
                self.status_label.setText("❌ FFmpeg无法执行")
                self.status_label.setStyleSheet("color: red;")
                logger.error(error_msg)
                return False
        else:
            self.status_label.setText("❌ 未找到FFmpeg")
            self.status_label.setStyleSheet("color: red;")
            logger.error("未找到可用的FFmpeg")
            return False
    
    def start_conversion(self):
        """开始转换 - 使用QProcess实时更新进度条"""
        # 检查输入文件
        if not self.input_file or not os.path.exists(self.input_file):
            QMessageBox.warning(self, "警告", "请选择有效的视频文件")
            return
        
        # 检查FFmpeg
        if not self.check_ffmpeg_installed():
            # 提供更友好的错误提示，包含可能的解决方案
            QMessageBox.critical(self, 
                               "FFmpeg检查失败", 
                               "无法找到或执行FFmpeg。请尝试以下解决方案：\n"\
                               "1. 确保应用有足够的权限\n"\
                               "2. 尝试重新安装应用\n"\
                               "3. 确保您的系统上已安装FFmpeg")
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
        
        # 初始化进度条和状态
        self.status_label.setText("🔄 正在转换中...")
        self.status_label.setStyleSheet("color: orange;")
        self.progress_bar.setValue(0)
        
        # 禁用开始按钮，启用取消按钮
        self.convert_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        
        # 获取FFmpeg路径
        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            self.reset_ui_state()
            QMessageBox.critical(self, "错误", "未找到FFmpeg，无法进行转换")
            self.status_label.setText("❌ 未找到FFmpeg")
            self.status_label.setStyleSheet("color: red;")
            return
        
        # 构建FFmpeg命令 - 使用完整的参数集，确保视频流正确处理
        # 添加-progress参数以获取进度信息
        # 获取输入文件大小，用于计算压缩比例
        self.original_size = os.path.getsize(self.input_file)
        
        # 构建适合抖音的FFmpeg参数，优化画质和兼容性
        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",                       # 覆盖输出文件
            "-i", self.input_file,
            "-map", "0:v",              # 明确映射视频流
            "-map", "0:a",              # 明确映射音频流
            "-c:v", "libx265",          # 视频编码器
            "-crf", "26",               # 降低CRF值以提高画质（26比28质量更好）
            "-preset", "medium",        # 编码预设
            "-pix_fmt", "yuv420p",      # 像素格式确保兼容性
            "-color_range", "tv",       # 标准色彩范围
            "-colorspace", "bt709",     # 标准色彩空间
            "-color_trc", "bt709",      # 色彩传输特性
            "-color_primaries", "bt709", # 色彩原色
            "-maxrate", "5M",           # 最大比特率限制，适合抖音
            "-bufsize", "10M",          # 缓冲区大小
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", # 确保分辨率为偶数
            "-c:a", "aac",              # 音频编码器
            "-b:a", "192k",             # 提高音频比特率以获得更好音质
            "-ac", "2",                 # 确保是立体声
            "-ar", "44100",             # 标准音频采样率
            "-movflags", "+faststart",  # 优化MP4文件，快速开始播放
            "-threads", "0",            # 自动使用所有CPU核心
            "-tag:v", "hvc1",           # 使用hvc1标签提高兼容性
            "-progress", "pipe:1",      # 输出进度信息到标准输出
            self.output_file
        ]
        # 记录完整的FFmpeg命令到日志
        logger.debug(f"执行FFmpeg命令: {' '.join(ffmpeg_cmd)}")
        
        # 创建QProcess
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.process_finished)
        
        try:
            # 开始转换
            self.status_label.setText("🔄 转换进行中，请稍候...")
            logger.debug(f"开始转换: {self.input_file} -> {self.output_file}")
            self.process.start(ffmpeg_cmd[0], ffmpeg_cmd[1:])
            
        except Exception as e:
            error_msg = f"启动转换进程失败: {str(e)}"
            self.reset_ui_state()
            self.status_label.setText("❌ 转换失败")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "转换失败", error_msg)
            logger.error(error_msg)
    
    def handle_output(self):
        """处理FFmpeg输出并更新进度条"""
        try:
            output = self.process.readAllStandardOutput().data().decode()
            
            # 记录输出
            logger.debug(f"FFmpeg输出片段: {output[:200]}...")
            
            # 解析进度信息
            progress_data = {}
            for line in output.splitlines():
                if '=' in line:
                    key, value = line.split('=', 1)
                    progress_data[key.strip()] = value.strip()
            
            # 更新进度
            if 'out_time_ms' in progress_data and 'total_duration' in progress_data:
                try:
                    current_time = float(progress_data['out_time_ms'])
                    total_time = float(progress_data['total_duration'])
                    if total_time > 0:
                        percent = int((current_time / total_time) * 100)
                        self.progress_bar.setValue(percent)
                except ValueError:
                    pass
            
            # 尝试从输出中提取frame信息来估计进度
            elif 'frame=' in output:
                # 简单的基于文本的进度解析
                try:
                    for line in output.splitlines():
                        if 'frame=' in line and 'fps=' in line:
                            # 这里我们没有总帧数信息，所以只是更新状态文本
                            frame_info = line.strip()
                            self.status_label.setText(f"🔄 转换中: {frame_info[:50]}")
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"处理FFmpeg输出时出错: {str(e)}")
    
    def process_finished(self, exit_code, exit_status):
        """处理进程完成后的操作"""
        try:
            # 重置UI状态
            self.reset_ui_state()
            
            if exit_code == 0 and exit_status == QProcess.NormalExit:
                # 检查输出文件
                if os.path.exists(self.output_file):
                    self.status_label.setText("✅ 转换成功！")
                    self.status_label.setStyleSheet("color: green;")
                    self.progress_bar.setValue(100)
                    
                    # 计算压缩后的文件大小和压缩比例
                    try:
                        new_size = os.path.getsize(self.output_file)
                        reduction_percent = ((self.original_size - new_size) / self.original_size) * 100
                        
                        # 格式化文件大小显示
                        original_size_mb = round(self.original_size / (1024 * 1024), 2)
                        new_size_mb = round(new_size / (1024 * 1024), 2)
                        
                        # 显示包含压缩信息的成功消息
                        message = (
                            f"视频转换成功！\n输出文件: {os.path.basename(self.output_file)}\n\n" 
                            f"压缩前大小：{original_size_mb} MB\n" 
                            f"压缩后大小：{new_size_mb} MB\n" 
                            f"压缩比例：{round(reduction_percent, 2)}%"
                        )
                        QMessageBox.information(self, "成功", message)
                    except Exception as e:
                        # 即使计算大小失败也显示基本成功信息
                        QMessageBox.information(
                            self, "成功", 
                            f"视频转换成功！\n输出文件: {os.path.basename(self.output_file)}"
                        )
                        logger.warning(f"计算压缩信息失败: {str(e)}")
                        
                    logger.info(f"转换成功: {self.output_file}")
                else:
                    raise Exception("输出文件未生成")
            else:
                error_msg = f"FFmpeg进程退出，返回码: {exit_code}"
                self.status_label.setText("❌ 转换失败")
                self.status_label.setStyleSheet("color: red;")
                QMessageBox.critical(self, "转换失败", f"视频转换失败，请查看日志获取详细信息")
                logger.error(error_msg)
        except Exception as e:
            error_msg = f"处理转换结果时出错: {str(e)}"
            self.status_label.setText("❌ 转换失败")
            self.status_label.setStyleSheet("color: red;")
            logger.error(error_msg)
    
    def cancel_conversion(self):
        """取消转换"""
        if hasattr(self, 'process') and self.process.state() == QProcess.Running:
            confirm = QMessageBox.question(
                self, "确认取消", 
                "确定要取消当前转换吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.process.kill()
                self.reset_ui_state()
                self.status_label.setText("⚠️  转换已取消")
                self.status_label.setStyleSheet("color: orange;")
                logger.info("转换已取消")
    
    def reset_ui_state(self):
        """重置UI状态"""
        self.convert_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

def main():
    """主函数 - 添加更健壮的错误处理和macOS安全特性支持"""
    # 确保正确设置工作目录，避免权限问题
    try:
        # 获取可执行文件所在目录作为基础目录
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            base_dir = os.path.dirname(sys.executable)
            # 在Mac应用中，实际工作目录应该在Resources目录
            if base_dir.endswith('/Contents/MacOS'):
                # 切换到Resources目录
                resources_dir = os.path.join(os.path.dirname(base_dir), 'Resources')
                if os.path.exists(resources_dir) and os.access(resources_dir, os.X_OK):
                    os.chdir(resources_dir)
        
        # 创建应用程序实例
        app = QApplication(sys.argv)
        # 设置应用名称
        app.setApplicationName("小压工坊")
        
        # 添加对macOS安全编码特性的支持
        try:
            # 在PyQt5中，我们可以通过设置应用属性来支持macOS的安全恢复功能
            app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            logger.info("已启用高DPI支持和安全编码属性")
        except Exception as e:
            logger.warning(f"设置应用属性时出错: {str(e)}")
        
        # 尝试创建并显示主窗口
        try:
            # 创建并显示窗口
            window = SimpleVideoConverter()
            window.show()
            logger.info("主窗口已创建并显示")
            
            # 运行应用程序主循环
            sys.exit(app.exec_())
        except Exception as window_error:
            error_msg = f"窗口创建或显示失败: {str(window_error)}"
            logger.error(error_msg)
            print(error_msg)
            # 尝试显示一个简单的错误对话框，即使主窗口无法创建
            try:
                QMessageBox.critical(None, "应用程序错误", 
                                   "窗口创建失败，请尝试重新启动应用。\n" + 
                                   f"错误信息: {str(window_error)}")
            except:
                pass
            sys.exit(1)
            
    except Exception as e:
        # 捕获所有其他异常
        error_msg = f"应用程序启动失败: {str(e)}"
        logger.error(error_msg)
        print(error_msg)
        
        # 使用安全的日志文件路径
        try:
            # 确保错误日志保存在用户可访问的位置
            safe_log_path = os.path.join(os.path.expanduser("~"), "Desktop", "video_converter_crash.log")
            import traceback
            with open(safe_log_path, "w") as f:
                f.write(f"崩溃时间: {datetime.datetime.now()}\n")
                f.write(f"错误信息: {str(e)}\n")
                f.write("\n堆栈跟踪:\n")
                f.write(traceback.format_exc())
            logger.info(f"崩溃信息已保存到: {safe_log_path}")
        except Exception as log_error:
            print(f"保存崩溃日志失败: {str(log_error)}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()