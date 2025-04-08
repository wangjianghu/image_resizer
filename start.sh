#!/bin/bash

# 图片大小修改工具启动脚本 (macOS/Linux)

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到项目目录
cd "$SCRIPT_DIR"

# 检查虚拟环境是否存在
if [ -d "venv" ]; then
    echo "正在激活虚拟环境..."
    source venv/bin/activate
else
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 运行程序
echo "正在启动图片大小修改工具..."
python image_resizer_gui.py

# 退出虚拟环境
deactivate