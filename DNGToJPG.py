import subprocess
import os
from PIL import Image
import io

def convert_dng_to_jpg(dng_path, jpg_path=None):
    """
    将DNG文件转换为JPG格式

    :param dng_path: DNG文件路径
    :param jpg_path: JPG输出路径（可选，默认与DNG同目录）
    :return: 成功返回JPG路径，失败返回None
    """
    if not os.path.exists(dng_path):
        print(f"错误：DNG文件不存在：{dng_path}")
        return None

    if jpg_path is None:
        jpg_path = os.path.splitext(dng_path)[0] + '.jpg'

    try:
        # 使用exiftool提取DNG的预览图
        command = [
            'exiftool',
            '-b',  # 二进制输出
            '-PreviewImage',  # 提取预览图
            dng_path
        ]
        
        process = subprocess.run(command, capture_output=True, check=True)
        
        if process.stdout:
            # 将二进制数据转换为图片
            image = Image.open(io.BytesIO(process.stdout))
            # 保存为JPG
            image.save(jpg_path, 'JPEG', quality=95)
            print(f"成功将DNG转换为JPG：{jpg_path}")
            return jpg_path
        else:
            print(f"警告：无法从DNG文件中提取预览图：{dng_path}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"转换失败。错误码: {e.returncode}")
        if e.stderr:
            print(f"错误信息:\n{e.stderr}")
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="将DNG文件转换为JPG格式。")
    parser.add_argument("dng_file", help="要转换的DNG文件的路径。")
    parser.add_argument("-o", "--output", help="JPG文件的输出路径。如果未指定，则输出到DNG文件所在的目录。", default=None)

    args = parser.parse_args()
    convert_dng_to_jpg(args.dng_file, args.output) 