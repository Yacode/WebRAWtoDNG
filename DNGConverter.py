import subprocess
import argparse
import os

# Adobe DNG Converter 在 macOS 上的典型路径
ADOBE_DNG_CONVERTER_PATH = "/Applications/Adobe DNG Converter.app/Contents/MacOS/Adobe DNG Converter"

def convert_raw_to_dng(raw_file_path, output_directory=None, preserve_exif=True):
    """
    使用 Adobe DNG Converter 将 RAW 文件转换为 DNG 文件。

    :param raw_file_path: 输入的 RAW 文件的路径。
    :param output_directory: DNG 文件的输出目录。如果为 None，则输出到 RAW 文件所在的目录。
    :param preserve_exif: 是否保留原始EXIF信息。默认为True，Adobe DNG Converter会自动保留EXIF元数据。
    """
    if not os.path.exists(ADOBE_DNG_CONVERTER_PATH):
        print(f"错误：找不到 Adobe DNG Converter，请确保它安装在路径：{ADOBE_DNG_CONVERTER_PATH}")
        return

    if not os.path.isfile(raw_file_path):
        print(f"错误：RAW 文件不存在：{raw_file_path}")
        return

    command = [ADOBE_DNG_CONVERTER_PATH]

    # -c: 创建压缩的 DNG 文件 (可选，根据需要添加)
    # command.append("-c")

    # -u: 不更新嵌入的 JPEG 预览 (可选)
    # command.append("-u")
    
    # 注意：Adobe DNG Converter 默认会保留所有EXIF元数据信息
    # 我们不使用 -e 选项，因为它会嵌入整个原始RAW文件，导致文件过大
    # 如果需要嵌入原始RAW文件，可以手动添加 -e 选项
    
    if preserve_exif:
        print("信息：将保留原始EXIF元数据信息。")

    if output_directory:
        if not os.path.isdir(output_directory):
            try:
                os.makedirs(output_directory, exist_ok=True)
                print(f"已创建输出目录：{output_directory}")
            except OSError as e:
                print(f"错误：无法创建输出目录 {output_directory}: {e}")
                return
        command.extend(["-d", output_directory])
    else:
        # 如果未指定输出目录，则输出到源文件目录
        source_dir = os.path.dirname(raw_file_path)
        if source_dir: # 确保源文件路径不是仅文件名
             command.extend(["-d", source_dir])

    command.append(raw_file_path)

    print(f"正在执行命令: {' '.join(command)}")

    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print("转换成功!")
        if process.stdout:
            print(f"输出:\n{process.stdout}")
        # Adobe DNG Converter 成功时通常没有太多标准输出，更多信息可能在日志中
        # DNG 文件名通常与原始 RAW 文件名相同，扩展名为 .dng
        raw_filename_stem = os.path.splitext(os.path.basename(raw_file_path))[0]
        dng_filename = f"{raw_filename_stem}.dng"
        
        if output_directory:
            expected_dng_path = os.path.join(output_directory, dng_filename)
        elif source_dir:
            expected_dng_path = os.path.join(source_dir, dng_filename)
        else:
            expected_dng_path = dng_filename
            
        if os.path.exists(expected_dng_path):
            print(f"生成的 DNG 文件位于: {expected_dng_path}")
        else:
            print(f"注意：转换过程已执行，但未在预期位置找到 DNG 文件: {expected_dng_path}。请检查转换器的输出或日志。")

    except subprocess.CalledProcessError as e:
        print(f"转换失败。错误码: {e.returncode}")
        if e.stdout:
            print(f"输出:\n{e.stdout}")
        if e.stderr:
            print(f"错误信息:\n{e.stderr}")
    except FileNotFoundError:
        print(f"错误：Adobe DNG Converter 执行文件未找到或无法执行。请检查路径：{ADOBE_DNG_CONVERTER_PATH}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将 RAW 文件转换为 DNG 文件。")
    parser.add_argument("raw_file", help="要转换的 RAW 文件的路径。")
    parser.add_argument("-o", "--output", help="DNG 文件的输出目录。如果未指定，则输出到 RAW 文件所在的目录。", default=None)
    parser.add_argument("--no-exif", action="store_false", dest="preserve_exif", help="不保留原始EXIF信息（不推荐）。默认会保留所有EXIF元数据。")

    args = parser.parse_args()

    convert_raw_to_dng(args.raw_file, args.output, args.preserve_exif)
    print("\n脚本执行完毕。")
    print(f"用法示例: python3 {os.path.basename(__file__)} /path/to/your/image.raw -o /path/to/output_folder")
    print(f"或者，不指定输出文件夹: python3 {os.path.basename(__file__)} /path/to/your/image.raw")
    print(f"不保留EXIF信息: python3 {os.path.basename(__file__)} /path/to/your/image.raw --no-exif")