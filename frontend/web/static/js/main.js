/**
 * 主JavaScript文件
 * 通用功能和工具函数
 */

// API基础URL
const API_BASE = '/api/v1';

// 通用AJAX请求函数
function apiRequest(url, method = 'GET', data = null) {
    return $.ajax({
        url: API_BASE + url,
        method: method,
        contentType: 'application/json',
        data: data ? JSON.stringify(data) : null,
        dataType: 'json'
    });
}

// 显示提示消息
function showMessage(message, type = 'info') {
    const colors = {
        success: 'green',
        error: 'red',
        warning: 'yellow',
        info: 'blue'
    };
    
    const color = colors[type] || 'blue';
    
    // 使用Flowbite的toast组件
    const toast = $(`
        <div id="toast-${type}" class="fixed top-4 right-4 flex items-center p-4 mb-4 text-sm text-${color}-800 rounded-lg bg-${color}-50" role="alert">
            <svg class="flex-shrink-0 inline w-4 h-4 mr-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z"/>
            </svg>
            <span class="sr-only">Info</span>
            <div>${message}</div>
            <button type="button" class="ml-auto -mx-1.5 -my-1.5 text-${color}-500 rounded-lg focus:ring-2 focus:ring-${color}-400 p-1.5 inline-flex h-8 w-8" onclick="$(this).parent().remove()">
                <span class="sr-only">Close</span>
                <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                </svg>
            </button>
        </div>
    `);
    
    $('body').append(toast);
    
    // 3秒后自动消失
    setTimeout(() => {
        toast.fadeOut(() => toast.remove());
    }, 3000);
}

// 格式化数字
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// 格式化评分
function formatScore(score) {
    return (score * 100).toFixed(1) + '%';
}

// 页面加载完成
$(document).ready(function() {
    console.log('Ferret Web App loaded');
});
