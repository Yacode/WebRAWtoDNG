// 用户鉴权相关函数
function getUserInfo() {
    let userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
    
    // 如果没有用户ID，则生成一个
    if (!userInfo.userId) {
        userInfo = generateUserInfo();
        setUserInfo(userInfo);
    }
    
    return userInfo;
}

function generateUserInfo() {
    // 生成唯一的用户ID
    const timestamp = new Date().getTime();
    const randomPart = Math.random().toString(36).substring(2, 10);
    const userId = `user_${timestamp}_${randomPart}`;
    
    return {
        userId: userId,
        createdAt: new Date().toISOString(),
        lastActive: new Date().toISOString()
    };
}

function setUserInfo(userInfo) {
    // 更新最后活动时间
    userInfo.lastActive = new Date().toISOString();
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
}

function clearUserInfo() {
    localStorage.removeItem('userInfo');
}

function isAuthenticated() {
    const userInfo = getUserInfo();
    return userInfo && userInfo.userId;
}

// 更新用户活动状态
function updateUserActivity() {
    const userInfo = getUserInfo();
    setUserInfo(userInfo);
}

// 获取用户文件列表
function loadUserFiles() {
    const userInfo = getUserInfo();
    const userId = userInfo.userId;
    
    // 显示加载状态
    const fileList = document.getElementById('fileList');
    const emptyList = document.querySelector('.empty-list');
    
    // 清空文件列表
    fileList.innerHTML = '';
    
    fetch(`/api/files?user_id=${userId}`)
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
            
            // 更新文件列表
            if (data.files && data.files.length > 0) {
                // 隐藏空列表提示
                if (emptyList) {
                    emptyList.style.display = 'none';
                }
                
                // 更新文件计数
                const fileCount = document.getElementById('file-count');
                if (fileCount) {
                    fileCount.textContent = data.files.length;
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
                
                // 添加文件到列表
                data.files.forEach(file => {
                    addFileToList(file.filename, file.unique_filename, file.token);
                });
            } else {
                // 显示空列表提示
                if (emptyList) {
                    emptyList.style.display = 'block';
                }
                
                // 更新文件计数
                const fileCount = document.getElementById('file-count');
                if (fileCount) {
                    fileCount.textContent = '0';
                }
            }
        })
        .catch(error => {
            console.error('Error loading files:', error);
            // 显示错误消息
            const statusMessage = document.getElementById('status-message');
            statusMessage.textContent = '加载文件列表失败，请刷新页面重试';
            statusMessage.className = 'error';
            statusMessage.style.display = 'block';
        });
}

// 添加文件到列表
function addFileToList(filename, uniqueFilename, token) {
    const fileList = document.getElementById('fileList');
    const userInfo = getUserInfo();
    const userId = userInfo.userId;
    
    // 确保显示的文件名有正确的扩展名
    const displayFilename = filename.toLowerCase().endsWith('.dng') ? 
        filename : filename.split('.')[0] + '.dng';
    
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
    fileSpan.textContent = displayFilename;
    fileInfo.appendChild(fileSpan);
    
    // 创建图片预览容器
    const previewContainer = document.createElement('div');
    previewContainer.className = 'preview-container';
    
    // 创建图片预览
    const previewImg = document.createElement('img');
    previewImg.className = 'preview-img';
    
    // 对于DNG文件，使用jpg预览
    let previewUrl;
    if (uniqueFilename.toLowerCase().endsWith('.dng')) {
        const jpgFilename = uniqueFilename.replace('.dng', '.jpg');
        previewUrl = `/preview/${jpgFilename}?token=${token}&user_id=${userId}`;
    } else {
        previewUrl = `/preview/${uniqueFilename}?token=${token}&user_id=${userId}`;
    }
    
    previewImg.src = previewUrl;
    previewImg.alt = displayFilename;
    previewImg.loading = 'lazy'; // 延迟加载图片
    
    // 添加图片加载错误处理
    previewImg.onerror = function() {
        this.onerror = null; // 防止循环调用
        console.error('预览图加载失败:', previewUrl);
        
        // 如果是JPG预览加载失败，尝试直接使用DNG预览
        if (uniqueFilename.toLowerCase().endsWith('.dng') && previewUrl.includes('.jpg')) {
            this.src = `/preview/${uniqueFilename}?token=${token}&user_id=${userId}`;
        } else {
            this.src = '/static/img/error.png'; // 可以添加一个默认的错误图片
            this.alt = '预览加载失败';
        }
    };
    
    previewContainer.appendChild(previewImg);
    
    // 创建选择框
    const selectBox = document.createElement('div');
    selectBox.className = 'select-box';
    selectBox.innerHTML = '<i class="fas fa-check"></i>';
    selectBox.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleSelectFile(this, uniqueFilename);
    });
    
    // 创建下载按钮
    const downloadBtn = document.createElement('a');
    downloadBtn.href = `/download/${uniqueFilename}`;
    downloadBtn.className = 'download-btn';
    downloadBtn.innerHTML = '<i class="fas fa-download"></i> 下载';
    downloadBtn.dataset.token = token;
    downloadBtn.dataset.filename = displayFilename; // 使用显示文件名作为下载文件名
    
    // 添加点击事件处理
    downloadBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        const token = this.dataset.token;
        if (token) {
            // 下载文件
            downloadFile(this.href, token, this, this.innerHTML);
        }
    });
    
    // 点击整个文件项也可以选择
    li.addEventListener('click', function(e) {
        if (!e.target.closest('.download-btn')) {
            const selectBoxElem = this.querySelector('.select-box');
            toggleSelectFile(selectBoxElem, uniqueFilename);
        }
    });
    
    // 按正确的顺序添加元素
    li.appendChild(selectBox);
    li.appendChild(fileInfo);
    li.appendChild(previewContainer);
    li.appendChild(downloadBtn);
    fileList.appendChild(li);
}

// 检查用户鉴权状态，如果未登录则显示登录表单
function checkAuthStatus() {
    if (!isAuthenticated()) {
        // 生成新用户信息
        const userInfo = generateUserInfo();
        setUserInfo(userInfo);
    }
    
    // 更新用户活动状态
    updateUserActivity();
    
    // 加载用户文件列表
    loadUserFiles();
}

// 更新UI以反映认证状态
function updateAuthUI() {
    const userInfo = getUserInfo();
    
    // 如果页面上没有用户信息栏，则创建一个
    if (!document.getElementById('user-info-bar')) {
        const userInfoBar = document.createElement('div');
        userInfoBar.id = 'user-info-bar';
        userInfoBar.className = 'user-info-bar';
        
        const container = document.querySelector('.container');
        container.insertBefore(userInfoBar, container.firstChild);
    }
    
    // 更新用户信息栏内容
    const userInfoBar = document.getElementById('user-info-bar');
    userInfoBar.innerHTML = `
        <span>用户ID: ${userInfo.userId.substring(0, 8)}...</span>
        <button id="refresh-btn" class="refresh-btn">
            <i class="fas fa-sync-alt"></i> 刷新文件列表
        </button>
    `;
    
    // 添加刷新按钮事件
    document.getElementById('refresh-btn').addEventListener('click', function() {
        loadUserFiles();
    });
}

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
    const userInfo = getUserInfo();
    const userId = userInfo.userId;
    
    // 显示下载中状态
    if (buttonElement) {
        buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 下载中...';
        buttonElement.style.pointerEvents = 'none';
    }
    
    // 获取原始文件名
    const filename = buttonElement ? buttonElement.dataset.filename : url.split('/').pop();
    // 确保文件名有.dng扩展名
    const downloadFilename = filename.toLowerCase().endsWith('.dng') ? 
        filename : filename.split('.')[0] + '.dng';
    
    // 使用XMLHttpRequest进行下载，以便更好地控制下载过程
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `${url}?token=${token}&user_id=${userId}`, true);
    xhr.responseType = 'blob';
    
    xhr.onload = function() {
        if (this.status === 200) {
            // 创建下载链接并模拟点击
            const blob = new Blob([this.response], { type: 'application/octet-stream' });
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            a.download = downloadFilename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            
            // 恢复按钮状态
            if (buttonElement) {
                buttonElement.innerHTML = originalButtonText;
                buttonElement.style.pointerEvents = 'auto';
            }
            
            // 下载成功后，从列表中移除该文件
            if (buttonElement) {
                const fileItem = buttonElement.closest('.file-item');
                if (fileItem) {
                    fileItem.remove();
                    
                    // 更新文件计数
                    const fileCount = document.getElementById('file-count');
                    if (fileCount) {
                        const currentCount = parseInt(fileCount.textContent || '0');
                        fileCount.textContent = Math.max(0, currentCount - 1);
                    }
                    
                    // 如果没有文件了，显示空列表提示
                    const fileList = document.getElementById('fileList');
                    if (fileList.children.length === 0) {
                        const emptyList = document.querySelector('.empty-list');
                        if (emptyList) {
                            emptyList.style.display = 'block';
                        }
                    }
                }
            }
        } else {
            console.error('Download error:', this.status);
            
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
    };
    
    xhr.onerror = function() {
        console.error('Download network error');
        
        // 恢复按钮状态
        if (buttonElement) {
            buttonElement.innerHTML = originalButtonText;
            buttonElement.style.pointerEvents = 'auto';
        }
        
        // 显示错误消息
        const statusMessage = document.getElementById('status-message');
        statusMessage.textContent = '下载失败，网络错误';
        statusMessage.className = 'error';
        statusMessage.style.display = 'block';
    };
    
    xhr.send();
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
    
    files.forEach((filename, index) => {
        // 查找对应的下载按钮以获取token
        const downloadBtn = Array.from(document.querySelectorAll('.download-btn')).find(
            btn => btn.href.includes(`/download/${filename}`)
        );
        
        if (downloadBtn && downloadBtn.dataset.token) {
            const token = downloadBtn.dataset.token;
            const url = `/download/${filename}`;
            
            // 延迟下载，避免浏览器阻止多个下载
            setTimeout(() => {
                // 使用我们修改后的下载函数
                downloadFile(url, token, downloadBtn, downloadBtn.innerHTML);
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
            }, index * 1000); // 每个下载间隔1秒，防止浏览器阻止多个下载
        }
    });
}

document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // 检查用户是否已登录
    if (!isAuthenticated()) {
        checkAuthStatus();
        return;
    }
    
    const submitBtn = document.getElementById('submitBtn');
    const statusMessage = document.getElementById('status-message');
    const formData = new FormData(this);
    
    // 添加用户ID到表单数据
    const userInfo = getUserInfo();
    formData.append('user_id', userInfo.userId);
    
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
            // 重新加载用户文件列表
            loadUserFiles();
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
        submitBtn.innerHTML = '<i class="fas fa-cog"></i> 上传并处理';
        document.getElementById('file-upload').value = '';
        document.getElementById('file-selected').textContent = '未选择文件';
        document.getElementById('file-selected').style.color = '#7f8c8d';
    });
});

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户鉴权状态
    checkAuthStatus();
    
    // 更新UI
    updateAuthUI();
});
