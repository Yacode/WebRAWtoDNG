// 文件选择器交互
document.getElementById('file-upload').addEventListener('change', function() {
    const fileSelected = document.getElementById('file-selected');
    if (this.files.length > 0) {
        if (this.files.length === 1) {
            fileSelected.textContent = this.files[0].name;
        } else {
            fileSelected.textContent = `已选择 ${this.files.length} 个文件`;
        }
        fileSelected.style.color = '#2c3e50';
    } else {
        fileSelected.textContent = '未选择文件';
        fileSelected.style.color = '#7f8c8d';
    }
});

// 全局变量，用于存储选中的文件
let selectedFiles = [];

// 批量选择功能
function toggleSelectFile(element, filename) {
    const fileItem = element.closest('.file-item');
    if (fileItem.classList.contains('selected')) {
        fileItem.classList.remove('selected');
        selectedFiles = selectedFiles.filter(file => file !== filename);
    } else {
        fileItem.classList.add('selected');
        selectedFiles.push(filename);
    }
    
    // 更新批量下载按钮状态
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    if (selectedFiles.length > 0) {
        batchDownloadBtn.classList.add('active');
        batchDownloadBtn.textContent = `下载选中的 ${selectedFiles.length} 个文件`;
    } else {
        batchDownloadBtn.classList.remove('active');
        batchDownloadBtn.textContent = '批量下载';
    }
}

// 下载单个文件的函数
function downloadFile(url, token, buttonElement, originalButtonText) {
    fetch(`${url}?token=${token}`)
        .then(response => {
            if (response.ok) {
                // 创建下载链接并模拟点击
                response.blob().then(blob => {
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = downloadUrl;
                    a.download = url.split('/').pop();
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(downloadUrl);
                    
                    // 恢复按钮状态
                    if (buttonElement) {
                        buttonElement.innerHTML = originalButtonText;
                        buttonElement.style.pointerEvents = 'auto';
                    }
                });
            } else {
                // 恢复按钮状态
                if (buttonElement) {
                    buttonElement.innerHTML = originalButtonText;
                    buttonElement.style.pointerEvents = 'auto';
                }
                
                // 显示错误消息
                const statusMessage = document.getElementById('status-message');
                statusMessage.textContent = '下载失败，请重试';
                statusMessage.className = 'error';
                statusMessage.style.display = 'block';
            }
        })
        .catch(error => {
            // 恢复按钮状态
            if (buttonElement) {
                buttonElement.innerHTML = originalButtonText;
                buttonElement.style.pointerEvents = 'auto';
            }
            
            // 显示错误消息
            const statusMessage = document.getElementById('status-message');
            statusMessage.textContent = '下载失败，请重试';
            statusMessage.className = 'error';
            statusMessage.style.display = 'block';
        });
}

// 批量下载文件的函数
function batchDownloadFiles(files) {
    if (files.length === 0) return;
    
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    const originalText = batchDownloadBtn.textContent;
    batchDownloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 下载中...';
    batchDownloadBtn.disabled = true;
    
    let downloadedCount = 0;
    const statusMessage = document.getElementById('status-message');
    
    files.forEach(filename => {
        // 查找对应的下载按钮以获取token
        const downloadBtn = Array.from(document.querySelectorAll('.download-btn')).find(
            btn => btn.href.includes(`/download/${filename}`)
        );
        
        if (downloadBtn && downloadBtn.dataset.token) {
            const token = downloadBtn.dataset.token;
            const url = `/download/${filename}`;
            
            // 延迟下载，避免浏览器阻止多个下载
            setTimeout(() => {
                downloadFile(url, token);
                downloadedCount++;
                
                // 所有文件都已开始下载
                if (downloadedCount === files.length) {
                    // 恢复按钮状态
                    batchDownloadBtn.innerHTML = originalText;
                    batchDownloadBtn.disabled = false;
                    
                    // 清除选择
                    document.querySelectorAll('.file-item.selected').forEach(item => {
                        item.classList.remove('selected');
                    });
                    selectedFiles = [];
                    batchDownloadBtn.classList.remove('active');
                    batchDownloadBtn.textContent = '批量下载';
                    
                    // 显示成功消息
                    statusMessage.textContent = `已开始下载 ${files.length} 个文件`;
                    statusMessage.className = 'success';
                    statusMessage.style.display = 'block';
                }
            }, downloadedCount * 500); // 每个下载间隔500毫秒
        }
    });
}

document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const statusMessage = document.getElementById('status-message');
    const formData = new FormData(this);
    
    // 禁用提交按钮
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
    
    // 清除之前的状态消息
    statusMessage.style.display = 'none';
    statusMessage.className = '';
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        // 显示成功消息
        statusMessage.textContent = data.message;
        statusMessage.classList.add('success');
        statusMessage.style.display = 'block';
        
        // 更新文件列表
        if (data.processed_files && data.processed_files.length > 0) {
            const fileList = document.getElementById('fileList');
            const emptyList = document.querySelector('.empty-list');
            
            // 隐藏空列表提示
            if (emptyList) {
                emptyList.style.display = 'none';
            }
            
            data.processed_files.forEach((file, index) => {
                const li = document.createElement('li');
                li.className = 'file-item';
                
                // 创建文件信息容器
                const fileInfo = document.createElement('div');
                fileInfo.className = 'file-info';
                
                // 添加文件图标
                const fileIcon = document.createElement('i');
                fileIcon.className = 'fas fa-file-image';
                fileInfo.appendChild(fileIcon);
                
                // 添加文件名
                const fileSpan = document.createElement('span');
                fileSpan.className = 'file-name';
                fileSpan.textContent = file;
                if (data.skipped_files && data.skipped_files.includes(file)) {
                    fileSpan.textContent += ' (已处理)';
                    fileSpan.style.color = '#666';
                }
                fileInfo.appendChild(fileSpan);
                
                // 创建图片预览容器
                const previewContainer = document.createElement('div');
                previewContainer.className = 'preview-container';
                
                // 创建图片预览
                const previewImg = document.createElement('img');
                previewImg.className = 'preview-img';
                // 对于DNG文件，使用jpg预览
                const previewUrl = file.toLowerCase().endsWith('.dng') 
                    ? `/preview/${file.replace('.dng', '.jpg')}?token=${data.file_tokens[index]}`
                    : `/preview/${file}?token=${data.file_tokens[index]}`;
                previewImg.src = previewUrl;
                previewImg.alt = file;
                previewImg.loading = 'lazy'; // 延迟加载图片
                
                // 添加图片加载错误处理
                previewImg.onerror = function() {
                    this.onerror = null; // 防止循环调用
                    this.src = '/static/img/error.png'; // 可以添加一个默认的错误图片
                    this.alt = '预览加载失败';
                };
                
                previewContainer.appendChild(previewImg);
                
                // 创建选择框
                const selectBox = document.createElement('div');
                selectBox.className = 'select-box';
                selectBox.innerHTML = '<i class="fas fa-check"></i>';
                selectBox.addEventListener('click', function(e) {
                    e.stopPropagation();
                    toggleSelectFile(this, file);
                });
                
                // 创建下载按钮
                const downloadBtn = document.createElement('a');
                downloadBtn.href = `/download/${file}`;
                downloadBtn.className = 'download-btn';
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> 下载';
                downloadBtn.dataset.token = data.file_tokens[index];
                
                // 添加点击事件处理
                downloadBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const token = this.dataset.token;
                    if (token) {
                        // 显示下载中状态
                        const originalText = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 下载中...';
                        this.style.pointerEvents = 'none';
                        
                        // 下载文件
                        downloadFile(this.href, token, this, originalText);
                    }
                });
                
                // 点击整个文件项也可以选择
                li.addEventListener('click', function(e) {
                    if (!e.target.closest('.download-btn')) {
                        const selectBoxElem = this.querySelector('.select-box');
                        toggleSelectFile(selectBoxElem, file);
                    }
                });
                
                // 按正确的顺序添加元素
                li.appendChild(selectBox);
                li.appendChild(fileInfo);
                li.appendChild(previewContainer);
                li.appendChild(downloadBtn);
                fileList.appendChild(li);
            });
            
            // 更新文件计数
            const fileCount = document.getElementById('file-count');
            if (fileCount) {
                const currentCount = parseInt(fileCount.textContent || '0');
                fileCount.textContent = currentCount + data.processed_files.length;
            }
            
            // 添加批量下载按钮（如果不存在）
            if (!document.getElementById('batch-download-btn')) {
                const batchDownloadContainer = document.createElement('div');
                batchDownloadContainer.className = 'batch-download-container';
                
                const batchDownloadBtn = document.createElement('button');
                batchDownloadBtn.id = 'batch-download-btn';
                batchDownloadBtn.className = 'batch-download-btn';
                batchDownloadBtn.textContent = '批量下载';
                batchDownloadBtn.addEventListener('click', function() {
                    if (selectedFiles.length > 0) {
                        batchDownloadFiles(selectedFiles);
                    }
                });
                
                batchDownloadContainer.appendChild(batchDownloadBtn);
                document.querySelector('.processed-files').insertBefore(batchDownloadContainer, document.getElementById('fileList'));
            }
        }
    })
    .catch(error => {
        // 显示错误消息
        let errorMessage = '上传处理失败，请重试';
        if (error.message) {
            errorMessage = error.message;
        }
        statusMessage.textContent = errorMessage;
        statusMessage.classList.add('error');
        statusMessage.style.display = 'block';
        console.error('Error:', error);
    })
    .finally(() => {
        // 重置表单和按钮状态
        submitBtn.disabled = false;
        submitBtn.innerHTML = '上传并处理';
        document.getElementById('file-upload').value = '';
        document.getElementById('file-selected').textContent = '未选择文件';
        document.getElementById('file-selected').style.color = '#7f8c8d';
    });
});
