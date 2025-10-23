# 视频H264转H265转换工具

一个使用Python开发的命令行工具，支持使用HandBrakeCLI或FFmpeg将H264编码的视频转换为H265编码，以减小文件体积并保持良好的视频质量。

## 功能特点

- **双引擎支持**：可以选择使用HandBrakeCLI或FFmpeg作为转换引擎
- **单文件转换**：将单个视频文件从H264转换为H265
- **批量转换**：处理整个目录中的所有视频文件
- **递归处理**：支持递归扫描子目录
- **自定义参数**：可调整视频质量、编码预设、音频编码等
- **进度显示**：实时显示转换进度和预计完成时间
- **日志记录**：详细记录转换过程和结果

## 安装要求

### 作为Python脚本运行
- Python 3.6或更高版本
- HandBrakeCLI（用于HandBrake引擎）
- FFmpeg（用于FFmpeg引擎，推荐）

### 作为独立应用运行
- 无需安装Python
- 无需单独安装HandBrakeCLI或FFmpeg（应用内置）

### 作为脚本使用时的依赖安装

**安装Python**

需要Python 3.6或更高版本。

**安装转换引擎（选择以下其中一个）**

- **FFmpeg**（推荐）
  - **macOS**：
    ```bash
    brew install ffmpeg
    ```
  - **Windows**：
    从[FFmpeg官网](https://ffmpeg.org/download.html)下载并安装
  - **Linux**：
    ```bash
    # Ubuntu/Debian
    sudo apt-get install ffmpeg
    ```

- **HandBrakeCLI**
  - **macOS**：
    ```bash
    brew install handbrake-cli
    ```
  - **Windows**：
    从[HandBrake官方网站](https://handbrake.fr/)下载并安装
  - **Linux**：
    ```bash
    # Ubuntu/Debian
    sudo apt-get install handbrake-cli
    
    # Fedora
    sudo dnf install handbrake-cli
    ```

## 使用方法

### 命令行使用

```bash
# 单个文件转换（使用默认引擎FFmpeg）
python3 index.py -i test.mov -o test3.mp4

# 使用特定引擎
python index.py --engine handbrake -i 输入文件.mp4
python index.py --engine ffmpeg -i 输入文件.mp4

# 批量转换目录中的所有视频
python index.py -d 视频目录路径

# 递归转换所有子目录中的视频
python index.py -d 视频目录路径 -r

# 自定义FFmpeg参数
python index.py -i 输入文件.mp4 --crf 28 --preset medium --audio-bitrate 128k

# 自定义HandBrakeCLI参数
python index.py --engine handbrake -i 输入文件.mp4 -q 20 -p medium --audio-quality 192 --subtitle
```

### 参数说明

#### 通用参数

- `--engine`: 选择转换引擎（handbrake/ffmpeg），默认为ffmpeg
- `-i, --input`: 输入视频文件路径
- `-o, --output`: 输出视频文件路径（单文件转换时可选）
- `-d, --directory`: 要批量转换的目录路径
- `-r, --recursive`: 递归处理子目录

#### HandBrakeCLI特定参数

- `-q, --quality`: 视频质量（0-51，值越小质量越高），默认22
- `--subtitle`: 包含字幕

#### FFmpeg特定参数

- `--crf`: 恒定速率因子，范围0-51，H.265推荐28-31，默认28
- `--threads`: 使用的线程数，0表示使用所有可用线程，默认0
- `--audio-bitrate`: 音频比特率，如'128k'，默认'128k'

#### 通用参数（两种引擎都适用）

- `-p, --preset`: 编码预设
  - HandBrakeCLI: 默认为"veryfast"
  - FFmpeg: 可选值["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]，默认为"medium"
- `--audio-codec`: 音频编码器，默认"aac"
- `--audio-quality`: 音频比特率(HandBrake)，单位kbps，默认160

## 示例

### 使用FFmpeg引擎的高级参数

```bash
# 使用较低的CRF值获得更高质量
python index.py -i input.mp4 --crf 26 --preset slow --audio-bitrate 192k

# 批量处理并限制线程数
python index.py -d /path/to/videos -r --threads 4
```

### 使用HandBrakeCLI引擎的高级参数

```bash
# 高质量转换并包含字幕
python index.py --engine handbrake -i input.mp4 -q 20 --preset slow --subtitle
```

## 选择引擎的建议

- **FFmpeg**：当你需要更灵活的参数控制、更广泛的格式支持，或者想在不同平台上获得一致的体验时。
- **HandBrakeCLI**：当你需要包含字幕、想要更多预设选项，或者已经熟悉HandBrake的参数体系时。

## 打包独立应用程序

### 打包步骤

1. **安装打包工具**：
   ```bash
   pip install pyinstaller setuptools wheel
   ```

2. **使用PyInstaller打包**（推荐）：
   ```bash
   # 打包为单文件
   pyinstaller --onefile --name "视频H264转H265工具" index.py
   
   # 或打包为文件夹
   pyinstaller --onedir --name "视频H264转H265工具" index.py
   ```

3. **或使用setup.py**：
   ```bash
   python setup.py py2app  # macOS
   python setup.py py2exe  # Windows
   python setup.py build_exe  # Linux (需要安装cx_Freeze)
   ```

### 打包后的使用

- **macOS**: 得到 `dist/视频H264转H265工具.app` 或 `dist/视频H264转H265工具`
- **Windows**: 得到 `dist/视频H264转H265工具.exe`
- **Linux**: 得到 `dist/视频H264转H265工具`

### 重要说明

- **依赖要求**：打包后的应用需要用户系统中已安装FFmpeg和/或HandBrakeCLI
- **跨平台打包**：需要在目标系统上进行打包
- **单文件模式**：首次启动可能较慢，因为需要解压资源

详细打包指南请参考 `PACKAGING_GUIDE.md` 文件。

详细打包指南请参考 `PACKAGING_GUIDE.md` 文件。

## 注意事项

1. 转换视频可能需要较长时间，具体取决于视频长度和您的计算机性能。

2. H.265编码通常比H.264编码慢，但可以在相同质量下获得更小的文件大小。

3. 打包后的应用程序仍然需要在目标计算机上安装所选的引擎（FFmpeg或HandBrakeCLI）。

4. 对于FFmpeg，推荐的CRF值范围是28-31，值越低质量越高但文件越大；对于HandBrakeCLI，质量值范围是0-51，同样值越低质量越高。

## 网站部署

本仓库包含视频H264转H265转换工具的官方网站源码，用于展示工具功能、提供下载链接。

### 网站结构

```
/
├── index.html           # 主页面HTML文件
├── resources/           # 资源文件夹
│   ├── favicon.ico      # 网站图标
│   └── screenshots/     # 应用界面截图
└── README.md           # 本说明文件
```

### 部署步骤

1. 创建代码托管平台仓库（如GitHub、Gitee等）
2. 上传网站文件（index.html和resources文件夹）
3. 开启Pages服务
4. 配置部署分支和目录

详细部署步骤请参考网站源码。

## 许可证

MIT