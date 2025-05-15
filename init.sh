#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${YELLOW}开始检查并安装依赖...${NC}"

# 检查是否安装了 Homebrew
if ! command -v brew &> /dev/null; then
    echo "${RED}未检测到 Homebrew，请先安装 Homebrew：${NC}"
    echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# 检查并安装 exiftool
if ! command -v exiftool &> /dev/null; then
    echo "${YELLOW}正在安装 exiftool...${NC}"
    brew install exiftool
    if [ $? -eq 0 ]; then
        echo "${GREEN}exiftool 安装成功！${NC}"
    else
        echo "${RED}exiftool 安装失败，请手动安装${NC}"
        exit 1
    fi
else
    echo "${GREEN}exiftool 已安装${NC}"
fi

# 检查 Adobe DNG Converter 是否已安装
DNG_CONVERTER_PATH="/Applications/Adobe DNG Converter.app"
if [ ! -d "$DNG_CONVERTER_PATH" ]; then
    echo "${YELLOW}请安装 Adobe DNG Converter：${NC}"
    echo "1. 访问 Adobe 官方网站下载 DNG Converter："
    echo "   https://helpx.adobe.com/photoshop/using/adobe-dng-converter.html"
    echo "2. 下载后将应用程序移动到 Applications 文件夹"
    exit 1
else
    echo "${GREEN}Adobe DNG Converter 已安装${NC}"
fi

# 检查 Python 是否已安装
if ! command -v python3 &> /dev/null; then
    echo "${YELLOW}正在安装 Python3...${NC}"
    brew install python3
    if [ $? -eq 0 ]; then
        echo "${GREEN}Python3 安装成功！${NC}"
    else
        echo "${RED}Python3 安装失败，请手动安装${NC}"
        exit 1
    fi
else
    echo "${GREEN}Python3 已安装${NC}"
fi

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "${YELLOW}正在创建虚拟环境...${NC}"
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        echo "${GREEN}虚拟环境创建成功！${NC}"
    else
        echo "${RED}虚拟环境创建失败${NC}"
        exit 1
    fi
else
    echo "${GREEN}虚拟环境已存在${NC}"
fi

# 激活虚拟环境并安装依赖
echo "${YELLOW}正在安装 Python 依赖...${NC}"
source .venv/bin/activate
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "${GREEN}Python 依赖安装成功！${NC}"
    else
        echo "${RED}Python 依赖安装失败${NC}"
        exit 1
    fi
else
    echo "${RED}未找到 requirements.txt 文件${NC}"
    exit 1
fi

echo "${GREEN}所有依赖检查完成！${NC}"

# 修改 run_server.py 中的端口号
echo "${YELLOW}正在配置服务器端口...${NC}"
sed -i '' 's/port=5001/port=5221/g' run_server.py
if [ $? -eq 0 ]; then
    echo "${GREEN}服务器端口配置成功！${NC}"
else
    echo "${RED}服务器端口配置失败${NC}"
    exit 1
fi

echo "${YELLOW}正在启动服务器...${NC}"
echo "${GREEN}服务器将在 http://localhost:5221 上运行${NC}"
echo "${YELLOW}按 Ctrl+C 可以停止服务器${NC}"
python run_server.py