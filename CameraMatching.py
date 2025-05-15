import subprocess
import os
import argparse

def modify_camera_info(dng_file_path):
    """
    修改DNG文件的相机信息为富士X-T5

    :param dng_file_path: DNG文件的路径
    """
    if not os.path.isfile(dng_file_path):
        print(f"错误：文件不存在：{dng_file_path}")
        return False

    # 构建exiftool命令
    command = [
        'exiftool',
        '-Make=FUJIFILM',
        '-Model=Fujifilm X-T5',
        '-UniqueCameraModel=Fujifilm X-T5'
    ]
    # 覆盖原文件
    command.append('-overwrite_original')
    
    # 添加文件路径
    command.append(dng_file_path)

    try:
        # 执行exiftool命令
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print("EXIF信息修改成功！")
        if process.stdout:
            print(f"输出信息:\n{process.stdout}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"修改失败。错误码: {e.returncode}")
        if e.stdout:
            print(f"输出:\n{e.stdout}")
        if e.stderr:
            print(f"错误信息:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print("错误：未找到exiftool工具。请确保已安装exiftool。")
        print("可以使用以下命令安装exiftool：")
        print("macOS: brew install exiftool")
        print("Ubuntu/Debian: sudo apt-get install libimage-exiftool-perl")
        return False
    except Exception as e:
        print(f"发生未知错误: {e}")
        return False

def process_directory(directory_path):
    """
    处理目录中的所有DNG文件

    :param directory_path: 包含DNG文件的目录路径
    """
    if not os.path.isdir(directory_path):
        print(f"错误：目录不存在：{directory_path}")
        return

    dng_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.dng')]
    
    if not dng_files:
        print(f"在目录 {directory_path} 中未找到DNG文件。")
        return

    success_count = 0
    for dng_file in dng_files:
        full_path = os.path.join(directory_path, dng_file)
        print(f"\n处理文件: {dng_file}")
        if modify_camera_info(full_path):
            success_count += 1

    print(f"\n处理完成！成功修改 {success_count} 个文件，共 {len(dng_files)} 个文件。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="修改DNG文件的相机信息为富士X-T5。")
    parser.add_argument("path", help="DNG文件的路径或包含DNG文件的目录路径")

    args = parser.parse_args()

    if os.path.isfile(args.path):
        modify_camera_info(args.path)
    else:
        process_directory(args.path)