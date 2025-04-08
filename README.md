# 图片大小修改工具

这是一个简单的图片大小修改工具，可以在不改变图片格式的前提下，调整图片的文件大小（占用的存储空间）。

## 功能特点

- 保持原始图片格式不变
- 通过调整图片质量减小文件大小
- 通过调整图片尺寸减小文件大小
- 支持设置目标文件大小（KB）
- 支持保持原始宽高比
- 实时预览原始图片和处理后的图片
- 显示详细的图片信息（大小、尺寸）

## 安装要求

- Python 3.6 或更高版本
- Pillow 库（用于图像处理）
- tkinter 库（用于图形界面，通常随Python一起安装）

## 安装步骤

1. 确保已安装Python 3.6+
2. 安装必要的依赖项：

```bash
pip install pillow
```

3. 或者使用虚拟环境（推荐）：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install pillow
```

## 如何运行程序

请按照以下步骤运行图片大小修改工具：

1. 打开终端，进入项目目录：
   ```bash
   cd "项目目录路径"
   ```

2. 如果使用虚拟环境，激活它：
   ```bash
   source venv/bin/activate  # macOS/Linux
   ```
   激活后，终端前面会出现 `(venv)` 前缀。

3. 运行图片大小修改工具：
   ```bash
   python image_resizer_gui.py
   ```

4. 使用完毕后，可以通过以下命令退出虚拟环境：
   ```bash
   deactivate
   ```

## 使用方法

### 图形界面版本（推荐）

1. 运行GUI程序：

```bash
python image_resizer_gui.py
```

2. 点击「选择图片」按钮，选择要处理的图片文件
3. 选择调整方法：
   - 「调整质量」：通过降低图片质量来减小文件大小（适用于JPEG等支持质量调整的格式）
   - 「调整尺寸」：通过缩小图片尺寸来减小文件大小
4. 根据选择的方法，设置相应参数：
   - 质量值（1-100）
   - 新的宽度和高度
   - 是否保持宽高比
5. 可以设置目标大小（KB），程序会尝试自动调整参数以达到目标大小
6. 可以设置保存路径，指定处理后图片的保存位置（留空则保存到原图所在文件夹）
7. 点击「处理图片」按钮进行处理
8. 处理完成后，可以预览处理结果并查看新的文件大小
9. 点击「保存图片」按钮保存处理后的图片

### 命令行版本

```bash
python image_resizer.py [图片路径] [参数]
```

参数说明：
- `-o, --output`：输出图片路径
- `-m, --method`：处理方法（quality或dimensions）
- `-q, --quality`：JPEG质量值（1-100）
- `-t, --target-size`：目标文件大小（KB）
- `-w, --width`：调整后的宽度
- `-ht, --height`：调整后的高度
- `-k, --keep-ratio`：保持宽高比（默认）
- `-nk, --no-keep-ratio`：不保持宽高比

## 支持的图片格式

- JPEG/JPG
- PNG
- BMP
- GIF
- WebP

## 关于PNG格式图片处理

程序已优化对PNG格式图片的处理能力：

- PNG是无损压缩格式，调整质量参数对其影响有限
- 当设置目标大小时，程序会尝试通过以下方式处理PNG图片：
  - 移除Alpha通道（如果存在）
  - 调整色彩深度（转换为8位调色板模式）
  - 调整图片尺寸
- 如果需要精确控制PNG图片的大小，建议：
  - 使用调整尺寸方法而不是调整质量
  - 考虑将图片保存为JPEG格式（如果不需要透明度）

## 注意事项

- 对于PNG等无损格式，调整质量可能效果有限，建议使用调整尺寸的方法
- 过度降低质量可能导致图片出现明显的质量下降
- 目标大小功能是通过二分查找算法实现的，可能无法精确达到目标大小，但会尽可能接近
- 每次运行程序前都需要先激活虚拟环境（如果使用）
- 如果将来需要安装其他Python库，请在激活虚拟环境后使用pip安装

## 常见问题

### ModuleNotFoundError: No module named 'PIL'

这个错误表示缺少Pillow库。解决方法：

1. **确保已安装Pillow**：
   ```bash
   # 如果不使用虚拟环境
   pip install pillow
   
   # 如果使用虚拟环境
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate    # Windows
   pip install pillow
   ```

2. **检查Python路径**：确保使用的是安装了Pillow的Python环境
   ```bash
   # 查看当前Python路径
   which python  # macOS/Linux
   where python  # Windows
   
   # 查看已安装的包
   pip list
   ```

### 虚拟环境激活问题

1. **虚拟环境无法激活**：
   - Windows上可能需要修改PowerShell执行策略：
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```
   - 确保在正确的目录中：
     ```bash
     cd "项目目录路径"
     ```

2. **找不到虚拟环境目录**：
   - 重新创建虚拟环境：
     ```bash
     python -m venv venv
     ```

### GUI界面布局问题

1. **界面元素显示不全或错位**：
   - 调整窗口大小，程序支持窗口缩放
   - 确保屏幕分辨率至少为1024x768
   - 如果使用高DPI显示器，可能需要调整系统的缩放设置

2. **预览图片显示异常**：
   - 检查图片格式是否受支持
   - 对于非常大的图片，预览可能需要较长时间加载
   - 如果图片包含特殊颜色配置文件，可能无法正确预览

### 批量处理问题

1. **批量处理速度慢**：
   - 处理大量图片时，特别是高分辨率图片，需要较长时间
   - 关闭其他占用CPU和内存的程序可提高处理速度
   - 考虑分批处理大量图片

2. **部分图片处理失败**：
   - 检查图片是否已损坏
   - 检查是否有足够的磁盘空间
   - 检查是否有文件权限问题

### 启动脚本问题

1. **启动脚本无法执行**：
   - 确保脚本有执行权限：
     ```bash
     chmod +x start.sh  # macOS/Linux
     ```
   - Windows上可能需要右键点击start.bat，选择"以管理员身份运行"

2. **启动脚本报错**：
   - 确保Python已正确安装
   - 确保脚本与项目文件在同一目录
   - 检查脚本中的路径是否正确