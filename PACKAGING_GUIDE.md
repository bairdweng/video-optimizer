# 视频转换工具打包指南

本指南将帮助您将H264到H265视频转换工具打包成可执行的桌面应用程序。本工具支持两种转换引擎：HandBrakeCLI和FFmpeg。

## 准备工作

### 1. 安装必要的依赖

```bash
# 安装打包工具
pip install pyinstaller setuptools wheel

# 如果需要为macOS打包
pip install py2app

# 如果需要为Windows打包
pip install py2exe
```

### 2. 确保转换引擎已安装

#### HandBrakeCLI安装
- **macOS**: 使用Homebrew安装
  ```bash
  brew install handbrake-cli
  ```
- **Windows**: 从[官方网站](https://handbrake.fr/)下载并安装
- **Linux**: 使用包管理器安装
  ```bash
  # Ubuntu/Debian
  sudo apt-get install handbrake-cli
  
  # Fedora
  sudo dnf install handbrake-cli
  ```

#### FFmpeg安装
- **macOS**: 使用Homebrew安装
  ```bash
  brew install ffmpeg
  ```
- **Windows**: 从[官方网站](https://ffmpeg.org/download.html)下载或使用包管理器安装
  ```bash
  # 使用winget
  winget install ffmpeg
  ```
- **Linux**: 使用包管理器安装
  ```bash
  # Ubuntu/Debian
  sudo apt-get install ffmpeg
  
  # Fedora
  sudo dnf install ffmpeg
  ```

## 方法一：使用PyInstaller（推荐）

PyInstaller可以在Windows、macOS和Linux上工作。

### 单个文件打包

```bash
# 基本打包
pyinstaller --onefile --console index.py

# Windows下添加图标
pyinstaller --onefile --console --icon=app_icon.ico index.py

# macOS下添加图标
pyinstaller --onefile --console --icon=app_icon.icns index.py
```

### 目录打包（包含所有依赖）

```bash
# 基本目录打包
pyinstaller --onedir --console index.py

# 添加图标
pyinstaller --onedir --console --icon=app_icon.ico index.py
```

## 方法二：使用setup.py配置

我已经创建了一个`setup.py`文件，可以根据不同平台进行打包。

### macOS打包

```bash
python setup.py py2app
```

### Windows打包

```bash
python setup.py py2exe
```

## 创建自定义图标

为了让应用程序看起来更专业，建议创建自定义图标：

- **macOS**: 需要`.icns`格式的图标
- **Windows**: 需要`.ico`格式的图标

您可以使用在线工具将PNG/JPG图像转换为这些格式。

## 注意事项

1. **转换引擎依赖**：打包后的应用程序仍然需要目标机器上安装所选的转换引擎（HandBrakeCLI或FFmpeg）。您可以：
   - 在应用程序文档中明确说明这一要求
   - 或者在安装程序中包含相应引擎（需要遵守其许可证）

2. **多平台支持**：每个平台需要在对应的操作系统上进行打包。

3. **权限问题**：确保应用程序有足够的权限访问输入和输出目录。

## 分发建议

1. **Windows**: 使用NSIS或Inno Setup创建安装程序，包含两种引擎的安装选项或说明
2. **macOS**: 创建DMG镜像文件，包含两种引擎的安装指南
3. **Linux**: 创建AppImage或各发行版的包格式，提供两种引擎的安装说明
4. **提供引擎选择指南**，帮助用户根据自己的需求选择合适的转换引擎

## 添加GUI界面（可选）

如果您希望添加图形界面，可以使用以下库之一修改脚本：

```bash
# 安装GUI库
pip install tkinter  # Python标准库的一部分，但某些Linux发行版需要单独安装
# 或
pip install pysimplegui
# 或
pip install pyqt5
```

然后修改代码以使用GUI替代命令行界面。