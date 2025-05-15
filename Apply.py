import os
import argparse
from DNGConverter import convert_raw_to_dng
from CameraMatching import modify_camera_info

def process_file(raw_file_path, output_directory=None):
    """
    处理单个RAW文件：转换为DNG并修改相机信息

    :param raw_file_path: RAW文件路径
    :param output_directory: 输出目录（可选）
    """
    # 获取输出DNG文件的预期路径
    raw_filename_stem = os.path.splitext(os.path.basename(raw_file_path))[0]
    dng_filename = f"{raw_filename_stem}.dng"
    
    if output_directory:
        dng_file_path = os.path.join(output_directory, dng_filename)
    else:
        source_dir = os.path.dirname(raw_file_path)
        dng_file_path = os.path.join(source_dir if source_dir else '.', dng_filename)

    # 第一步：转换RAW到DNG
    print(f"\n开始处理文件: {raw_file_path}")
    print("步骤1: 转换RAW到DNG格式")
    convert_raw_to_dng(raw_file_path, output_directory)

    # 检查DNG文件是否成功生成
    if os.path.exists(dng_file_path):
        # 第二步：修改相机信息
        print("\n步骤2: 修改相机型号信息")
        if modify_camera_info(dng_file_path):
            print(f"\n✓ 文件处理完成: {dng_file_path}")
            return True
    else:
        print(f"\n✗ 错误：DNG文件未生成，跳过相机信息修改步骤")
        return False

def process_directory(directory_path, output_directory=None):
    """
    处理目录中的所有RAW文件

    :param directory_path: 包含RAW文件的目录路径
    :param output_directory: 输出目录（可选）
    """
    if not os.path.isdir(directory_path):
        print(f"错误：目录不存在：{directory_path}")
        return

    # 支持常见的RAW文件扩展名
    raw_extensions = ('.raw', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.rw2', '.raf')
    raw_files = [f for f in os.listdir(directory_path) 
                if os.path.splitext(f)[1].lower() in raw_extensions]

    if not raw_files:
        print(f"在目录 {directory_path} 中未找到RAW文件。")
        return

    success_count = 0
    total_files = len(raw_files)
    print(f"\n找到 {total_files} 个RAW文件待处理")

    for index, raw_file in enumerate(raw_files, 1):
        print(f"\n处理文件 {index}/{total_files}")
        full_path = os.path.join(directory_path, raw_file)
        if process_file(full_path, output_directory):
            success_count += 1

    print(f"\n批处理完成！成功处理 {success_count} 个文件，共 {total_files} 个文件。")

def main():
    parser = argparse.ArgumentParser(description="将RAW文件转换为DNG并修改相机信息为富士X-T5。")
    parser.add_argument("input_path", help="RAW文件的路径或包含RAW文件的目录路径")
    parser.add_argument("-o", "--output", help="输出目录路径（可选）。如果未指定，则输出到源文件所在目录。", default=None)

    args = parser.parse_args()

    # 如果指定了输出目录，确保它存在
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    # 根据输入路径类型选择处理方式
    if os.path.isfile(args.input_path):
        process_file(args.input_path, args.output)
    else:
        process_directory(args.input_path, args.output)

    print("\n所有处理已完成！")
    print(f"\n使用方法示例:")
    print(f"处理单个文件: python3 {os.path.basename(__file__)} /path/to/your/image.raw")
    print(f"处理整个目录: python3 {os.path.basename(__file__)} /path/to/your/raw_folder")
    print(f"指定输出目录: python3 {os.path.basename(__file__)} /path/to/your/image.raw -o /path/to/output_folder")

if __name__ == "__main__":
    main()