# RAW to DNG 转换工具

这是一个基于Web界面的RAW格式图片转换工具，可以将各种相机RAW格式（包括CR2、CR3、NEF、ARW等）转换为Adobe DNG格式。该工具提供了简单的Web界面，支持批量上传和转换，并具有文件预览功能。

## 最新更新
- 修复了Git远程仓库地址问题
- 优化了项目名称
- 完善了安装步骤说明

## 功能特点

- 支持多种RAW格式转换：CR2、CR3、NEF、ARW、ORF、RW2、RAF
- Web界面操作，简单易用
- 支持批量上传和转换
- 文件预览功能
- 自动清理临时文件
- 文件去重功能
- 安全的文件访问控制

## 系统要求

- macOS系统（其他系统需要修改DNG转换器路径）
- Python 3.6+
- Adobe DNG Converter
- ExifTool

## 安装步骤

1. 安装必要的系统工具：
```bash
# 安装ExifTool
brew install exiftool

# 安装Adobe DNG Converter
# 请从Adobe官网下载并安装到默认位置：/Applications/Adobe DNG Converter.app
```

2. 克隆项目并安装Python依赖：
```bash
# 克隆项目
git clone https://github.com/Yacode/WebRAWtoDNG.git
cd WebRAWtoDNG

# 安装Python依赖
pip3 install -r requirements.txt
```

## 使用方法

1. 启动Web服务器：
```bash
python3 run_server.py
```

2. 在浏览器中访问：`http://localhost:5221`
![todng d amstro asia_54404_(Pixel 7)](https://github.com/user-attachments/assets/7cfb4ef6-ff81-49e0-b18f-9efc057501e2)

3. 通过Web界面上传RAW文件，支持以下格式：
   - Canon: CR2, CR3
   - Nikon: NEF
   - Sony: ARW
   - Olympus: ORF
   - Panasonic: RW2
   - Fujifilm: RAF

4. 等待转换完成后，可以预览和下载转换后的DNG文件

## 注意事项

1. 确保Adobe DNG Converter已正确安装在默认位置
2. 确保有足够的磁盘空间用于文件转换
3. 建议在处理大量文件时使用输出目录参数
4. Web界面默认限制上传文件大小，可通过配置调整

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

本项目采用MIT许可证。详见LICENSE文件。
