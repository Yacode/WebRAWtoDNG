import os
import uuid
import hashlib
import shutil
import time
from flask import Flask, request, send_file, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from Apply import process_file
from DNGToJPG import convert_dng_to_jpg

app = Flask(__name__)

# 配置上传和输出目录
UPLOAD_FOLDER = 'upload'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'.raw', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.rw2', '.raf'}

# 存储文件访问令牌的字典，格式为 {user_id: {filename: token}}
file_tokens = {}

# 存储已处理文件的哈希值，格式为 {user_id: {file_hash}}
processed_files_hash = {}

# 存储用户文件映射，格式为 {user_id: {original_filename: unique_filename}}
user_files = {}

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
    user_files.clear()
    
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

def is_file_processed(user_id, file_hash):
    """检查文件是否已经处理过"""
    if user_id not in processed_files_hash:
        processed_files_hash[user_id] = set()
        return False
    return file_hash in processed_files_hash[user_id]

def generate_unique_filename(user_id, original_filename):
    """生成唯一的文件名"""
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(original_filename)[1]
    return f"{user_id}_{timestamp}_{unique_id}{ext}"

# 检查文件扩展名是否允许
def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # 获取已处理的文件列表
    # 注意：这里不再直接返回所有文件，而是在前端通过API获取
    return render_template('index.html', processed_files=[])

@app.route('/api/files', methods=['GET'])
def get_user_files():
    """获取用户的文件列表"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': '缺少用户标识'}), 400
    
    if user_id not in user_files:
        return jsonify({'files': []})
    
    # 返回用户的文件列表和对应的访问令牌
    user_file_list = []
    for original_file, unique_file in user_files[user_id].items():
        if unique_file.endswith('.dng') and os.path.exists(os.path.join(OUTPUT_FOLDER, unique_file)):
            # 为每个文件生成新的访问令牌
            if user_id not in file_tokens:
                file_tokens[user_id] = {}
            
            access_token = str(uuid.uuid4())
            file_tokens[user_id][unique_file] = access_token
            
            user_file_list.append({
                'filename': original_file,
                'unique_filename': unique_file,
                'token': access_token
            })
    
    return jsonify({'files': user_file_list})

@app.route('/upload', methods=['POST'])
def upload_file():
    # 获取用户标识
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'error': '缺少用户标识'}), 400
    
    if 'files' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    # 初始化用户的数据结构
    if user_id not in processed_files_hash:
        processed_files_hash[user_id] = set()
    
    if user_id not in user_files:
        user_files[user_id] = {}
    
    if user_id not in file_tokens:
        file_tokens[user_id] = {}
    
    files = request.files.getlist('files')
    processed_files = []
    file_tokens_list = []
    skipped_files = []
    original_to_unique = {}
    
    for file in files:
        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            # 确保原始文件名有.dng扩展名
            original_dng_filename = original_filename
            if not original_dng_filename.lower().endswith('.dng'):
                original_dng_filename = os.path.splitext(original_filename)[0] + '.dng'
            
            # 生成唯一的文件名
            unique_filename = generate_unique_filename(user_id, original_filename)
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # 计算文件哈希值
            file_hash = calculate_file_hash(file_path)
            
            # 检查文件是否已处理
            if is_file_processed(user_id, file_hash):
                output_filename = os.path.splitext(unique_filename)[0] + '.dng'
                skipped_files.append(original_dng_filename)
                # 为已处理的文件生成新的访问令牌
                access_token = str(uuid.uuid4())
                file_tokens[user_id][output_filename] = access_token
                processed_files.append(original_dng_filename)
                file_tokens_list.append(access_token)
                # 记录原始文件名到唯一文件名的映射
                original_to_unique[original_dng_filename] = output_filename
            else:
                # 处理新文件
                if process_file(file_path, OUTPUT_FOLDER):
                    output_filename = os.path.splitext(unique_filename)[0] + '.dng'
                    # 为每个文件生成唯一的访问令牌
                    access_token = str(uuid.uuid4())
                    file_tokens[user_id][output_filename] = access_token
                    processed_files.append(original_dng_filename)
                    file_tokens_list.append(access_token)
                    # 记录已处理的文件哈希值
                    processed_files_hash[user_id].add(file_hash)
                    # 记录原始文件名到唯一文件名的映射
                    original_to_unique[original_dng_filename] = output_filename
            
            # 删除上传的原始文件
            os.remove(file_path)
    
    # 更新用户文件映射
    for original, unique in original_to_unique.items():
        user_files[user_id][original] = unique
    
    message = f'成功处理 {len(processed_files)} 个文件'
    if skipped_files:
        message += f'，跳过 {len(skipped_files)} 个已处理的文件'
    
    # 返回原始文件名和对应的令牌
    return jsonify({
        'message': message,
        'processed_files': list(original_to_unique.keys()),
        'file_tokens': file_tokens_list,
        'skipped_files': skipped_files,
        'file_mapping': original_to_unique
    })

@app.route('/download/<filename>')
def download_file(filename):
    # 获取用户标识
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': '缺少用户标识'}), 400
    
    # 获取访问令牌
    access_token = request.args.get('token')
    if not access_token:
        return jsonify({'error': '缺少访问令牌'}), 400
    
    # 检查用户是否存在
    if user_id not in file_tokens:
        return jsonify({'error': '无效的用户标识'}), 403
    
    # 验证访问令牌
    if filename not in file_tokens[user_id] or file_tokens[user_id][filename] != access_token:
        return jsonify({'error': '无效的访问令牌'}), 403
    
    file_path = os.path.join(os.path.abspath(OUTPUT_FOLDER), filename)
    if not os.path.exists(file_path):
        return jsonify({'error': f'文件不存在: {file_path}'}), 404
    
    try:
        # 获取原始文件名
        original_filename = None
        for orig, unique in user_files[user_id].items():
            if unique == filename:
                original_filename = orig
                break
        
        # 如果找不到原始文件名，使用唯一文件名
        if original_filename:
            # 确保原始文件名有正确的扩展名
            if not original_filename.lower().endswith('.dng'):
                original_filename = os.path.splitext(original_filename)[0] + '.dng'
        else:
            original_filename = filename
        
        # 使用send_file发送文件，确保as_attachment=True以强制下载
        response = send_file(
            file_path, 
            as_attachment=True,
            download_name=original_filename,
            mimetype='application/octet-stream'  # 强制以二进制流下载
        )
        
        # 添加额外的头信息，确保文件被下载而不是在浏览器中打开
        response.headers["Content-Disposition"] = f"attachment; filename={original_filename}"
        
        # 下载后删除文件和令牌
        os.remove(file_path)
        # 删除对应的JPG文件（如果存在）
        jpg_path = os.path.splitext(file_path)[0] + '.jpg'
        if os.path.exists(jpg_path):
            os.remove(jpg_path)
        
        # 从用户文件映射和令牌中删除
        if user_id in file_tokens and filename in file_tokens[user_id]:
            del file_tokens[user_id][filename]
        
        # 从用户文件映射中删除
        for orig, unique in list(user_files[user_id].items()):
            if unique == filename:
                del user_files[user_id][orig]
                break
        
        return response
    except Exception as e:
        print(f"下载文件时出错: {str(e)}")
        return jsonify({'error': f'文件下载错误: {str(e)}'}), 500

@app.route('/preview/<filename>')
def preview_file(filename):
    # 获取用户标识
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': '缺少用户标识'}), 400
    
    # 检查用户是否存在
    if user_id not in file_tokens:
        return jsonify({'error': '无效的用户标识'}), 403
    
    # 获取原始DNG文件名（如果是JPG预览）
    original_filename = filename
    if filename.lower().endswith('.jpg'):
        original_filename = filename.replace('.jpg', '.dng')
    
    # 验证访问令牌
    token = request.args.get('token')
    if not token or token != file_tokens[user_id].get(original_filename):
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
            # 检查JPG文件是否存在，如果不存在，尝试从DNG生成
            jpg_path = os.path.join(OUTPUT_FOLDER, filename)
            if not os.path.exists(jpg_path):
                dng_path = os.path.join(OUTPUT_FOLDER, original_filename)
                if os.path.exists(dng_path):
                    if not convert_dng_to_jpg(dng_path, jpg_path):
                        return jsonify({'error': '预览图生成失败'}), 500
                else:
                    return jsonify({'error': '找不到对应的DNG文件'}), 404
            
            # 使用原始DNG文件名对应的token
            if token != file_tokens[user_id].get(original_filename):
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