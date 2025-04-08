@echo off
REM 图片大小修改工具启动脚本 (Windows)

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查虚拟环境是否存在
if exist venv (
    echo 正在激活虚拟环境...
    call venv\Scripts\activate
) else (
    echo 虚拟环境不存在，正在创建...
    python -m venv venv
    call venv\Scripts\activate
    
    echo 正在安装依赖...
    pip install -r requirements.txt
)

REM 运行程序
echo 正在启动图片大小修改工具...
python image_resizer_gui.py

REM 退出虚拟环境
call deactivate