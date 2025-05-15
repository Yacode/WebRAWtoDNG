import os
import uuid
import hashlib
import shutil
from flask import Flask, request, send_file, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from Apply import process_file
from DNGToJPG import convert_dng_to_jpg

app = Flask(__name__)

# 配置上传和输出目录
UPLOAD_FOLDER = 'upload'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'.raw', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.rw2', '.raf'}

# 存储文件访问令牌的字典
file_tokens = {}

# 存储已处理文件的哈希值
processed_files_hash = set()

def clear_directories():
    """清空上传和输出目录"""
    # 清空上传目录
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # 清空输出目录
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # 清空文件令牌和哈希值
    file_tokens.clear()
    processed_files_hash.clear()
    
    print("已清空上传和输出目录")

# 确保上传和输出目录存在
clear_directories()

def calculate_file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_file_processed(file_hash):
    """检查文件是否已经处理过"""
    return file_hash in processed_files_hash

# 检查文件扩展名是否允许
def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # 获取已处理的文件列表
    processed_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.dng')]
    return render_template('index.html', processed_files=processed_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    files = request.files.getlist('files')
    processed_files = []
    file_tokens_list = []
    skipped_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # 计算文件哈希值
            file_hash = calculate_file_hash(file_path)
            
            # 检查文件是否已处理
            if is_file_processed(file_hash):
                output_filename = os.path.splitext(filename)[0] + '.dng'
                skipped_files.append(output_filename)
                # 为已处理的文件生成新的访问令牌
                access_token = str(uuid.uuid4())
                file_tokens[output_filename] = access_token
                processed_files.append(output_filename)
                file_tokens_list.append(access_token)
            else:
                # 处理新文件
                if process_file(file_path, OUTPUT_FOLDER):
                    output_filename = os.path.splitext(filename)[0] + '.dng'
                    # 为每个文件生成唯一的访问令牌
                    access_token = str(uuid.uuid4())
                    file_tokens[output_filename] = access_token
                    processed_files.append(output_filename)
                    file_tokens_list.append(access_token)
                    # 记录已处理的文件哈希值
                    processed_files_hash.add(file_hash)
            
            # 删除上传的原始文件
            os.remove(file_path)
    
    message = f'成功处理 {len(processed_files)} 个文件'
    if skipped_files:
        message += f'，跳过 {len(skipped_files)} 个已处理的文件'
    
    return jsonify({
        'message': message,
        'processed_files': processed_files,
        'file_tokens': file_tokens_list,
        'skipped_files': skipped_files
    })

@app.route('/download/<filename>')
def download_file(filename):
    # 获取访问令牌
    access_token = request.args.get('token')
    if not access_token:
        return jsonify({'error': '缺少访问令牌'}), 400
    
    # Secure filename and path handling
    filename = secure_filename(filename) 
    if not filename.endswith('.dng'):
        return jsonify({'error': '无效的文件类型'}), 400
    
    # 验证访问令牌
    if filename not in file_tokens or file_tokens[filename] != access_token:
        return jsonify({'error': '无效的访问令牌'}), 403
    
    file_path = os.path.join(os.path.abspath(OUTPUT_FOLDER), filename)
    if not os.path.exists(file_path):
        return jsonify({'error': f'文件不存在: {file_path}'}), 404
    
    try:
        response = send_file(file_path, as_attachment=True)
        # 下载后删除文件和令牌
        os.remove(file_path)
        # 删除对应的JPG文件（如果存在）
        jpg_path = os.path.splitext(file_path)[0] + '.jpg'
        if os.path.exists(jpg_path):
            os.remove(jpg_path)
        del file_tokens[filename]
        return response
    except Exception as e:
        return jsonify({'error': f'文件下载错误: {str(e)}'}), 500

@app.route('/preview/<filename>')
def preview_file(filename):
    # 获取原始DNG文件名（如果是JPG预览）
    original_filename = filename
    if filename.lower().endswith('.jpg'):
        original_filename = filename.replace('.jpg', '.dng')
    
    # 验证访问令牌
    token = request.args.get('token')
    if not token or token != file_tokens.get(original_filename):
        return jsonify({'error': '无效的访问令牌'}), 403
    
    # 如果是DNG文件，先转换为JPG
    if filename.lower().endswith('.dng'):
        dng_path = os.path.join(OUTPUT_FOLDER, filename)
        jpg_path = os.path.splitext(dng_path)[0] + '.jpg'
        
        # 如果JPG不存在，则转换
        if not os.path.exists(jpg_path):
            if not convert_dng_to_jpg(dng_path, jpg_path):
                return jsonify({'error': '预览图生成失败'}), 500
        
        # 返回JPG预览图
        try:
            return send_from_directory(OUTPUT_FOLDER, os.path.basename(jpg_path), as_attachment=False)
        except Exception as e:
            print(f"预览DNG文件时出错: {str(e)}")
            return jsonify({'error': str(e)}), 500
    elif filename.lower().endswith('.jpg'):
        # 直接返回JPG预览图
        try:
            # 使用原始DNG文件名对应的token
            if token != file_tokens.get(original_filename):
                return jsonify({'error': '无效的访问令牌'}), 403
            return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=False)
        except Exception as e:
            print(f"预览JPG文件时出错: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:
        # 其他文件直接返回
        try:
            return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=False)
        except Exception as e:
            print(f"预览其他文件时出错: {str(e)}")
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5221, debug=True)