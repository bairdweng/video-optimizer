# 小压工坊网站 - Gitee部署指南

本指南详细介绍如何将小压工坊的官方网站部署到Gitee Pages，让更多用户可以访问和下载工具。

## 准备工作

确保您已经准备好以下内容：

1. Gitee账号（[注册地址](https://gitee.com/signup)）
2. 网站文件（index.html和resources文件夹）
3. 小压工坊应用程序（用于发布下载）

## 步骤一：创建Gitee仓库

1. 登录您的Gitee账号
2. 点击右上角的「+」图标，选择「新建仓库」
3. 填写仓库信息：
   - **仓库名称**：建议使用 `video-optimizer-website` 或 `xiaoyagongfang`
   - **路径**：与仓库名称保持一致
   - **选择公开**（必须公开才能使用Gitee Pages服务）
   - 勾选「使用README文件初始化仓库」
4. 点击「创建」按钮

## 步骤二：上传网站文件

### 方法一：通过网页上传（简单）

1. 进入刚创建的仓库页面
2. 点击「上传文件」按钮
3. 将以下文件拖拽到上传区域或点击选择文件：
   - `index.html`
   - 整个 `resources` 文件夹（包含所有资源文件）
4. 填写提交信息，如「添加小压工坊网站文件」
5. 点击「提交」按钮

### 方法二：通过Git命令上传（推荐，适合开发者）

```bash
# 克隆仓库到本地
git clone https://gitee.com/您的用户名/仓库名称.git

# 进入仓库目录
cd 仓库名称

# 复制网站文件
cp -r /Users/bairdweng/Desktop/myproject/video-optimizer/index.html .
cp -r /Users/bairdweng/Desktop/myproject/video-optimizer/resources .

# 提交并推送更改
git add .
git commit -m "添加小压工坊网站文件"
git push origin master
```

## 步骤三：上传应用程序（用于下载）

1. 在仓库页面点击「发布」按钮
2. 点击「新建发布」
3. 填写版本信息：
   - 版本号：如 `v1.0.0`
   - 发布标题：如「小压工坊第一版发布」
   - 发布说明：简要介绍工具功能
4. 上传文件：选择打包好的 `.app` 应用程序或压缩包
5. 点击「发布」按钮

## 步骤四：配置Gitee Pages

1. 在仓库页面点击「服务」→「Gitee Pages」
2. 选择部署选项：
   - **部署分支**：选择 `master` 或您的主分支
   - **部署目录**：保持为空（表示根目录）
3. 点击「启动服务」按钮
4. 等待部署完成，页面会显示访问地址

## 步骤五：更新下载链接

1. 在Gitee上找到您发布的应用程序下载链接
2. 编辑仓库中的 `index.html` 文件
3. 找到下载链接部分：
   ```html
   <a href="https://gitee.com/yourusername/video-optimizer/releases" class="download-btn">下载 macOS 版本</a>
   ```
4. 将链接替换为您的实际下载地址
5. 提交并推送更改

## 验证部署

1. 访问Gitee Pages提供的网址
2. 检查网站是否正常显示
3. 测试下载链接是否可以正常下载
4. 确认打赏二维码是否显示正确

## 网站更新方法

1. 修改本地的网站文件
2. 上传到Gitee仓库
3. Gitee Pages会自动重新部署

## 常见问题

### 1. 网站访问出现404错误

- 检查仓库是否公开
- 确认Gitee Pages服务已正确启动
- 验证文件路径是否正确

### 2. 图片资源无法显示

- 检查图片文件是否已上传
- 确认HTML中的图片路径是否正确
- 等待缓存更新

### 3. 应用程序无法下载

- 确认已正确发布应用程序
- 验证下载链接是否正确
- 检查文件大小是否超过Gitee限制

## 更多资源

- [Gitee Pages官方文档](https://gitee.com/help/articles/4136)
- [Gitee发布功能使用指南](https://gitee.com/help/articles/4085)

## 联系我们

如有任何问题，请在Gitee仓库中提交Issues或联系开发者。