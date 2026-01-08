/**
 * 主JavaScript文件 - 优化版本
 * 使用原生JavaScript，减少对jQuery的依赖
 */

// 等待DOM加载完成
(function() {
    'use strict';
    
    // 如果jQuery未加载，使用原生JavaScript
    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }
    
    // API基础URL
    const API_BASE = window.API_BASE || '/api/v1';
    
    // 通用AJAX请求函数（原生JavaScript版本）
    function apiRequest(url, method, data) {
        return new Promise(function(resolve, reject) {
            const xhr = new XMLHttpRequest();
            xhr.open(method || 'GET', API_BASE + url);
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onload = function() {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        resolve(JSON.parse(xhr.responseText));
                    } catch (e) {
                        resolve(xhr.responseText);
                    }
                } else {
                    reject(new Error('Request failed: ' + xhr.status));
                }
            };
            
            xhr.onerror = function() {
                reject(new Error('Network error'));
            };
            
            if (data) {
                xhr.send(JSON.stringify(data));
            } else {
                xhr.send();
            }
        });
    }
    
    // 如果jQuery可用，使用jQuery版本
    ready(function() {
        if (typeof $ !== 'undefined') {
            // jQuery版本（更强大）
            window.apiRequest = function(url, method, data) {
                return $.ajax({
                    url: API_BASE + url,
                    method: method || 'GET',
                    contentType: 'application/json',
                    data: data ? JSON.stringify(data) : null,
                    dataType: 'json'
                });
            };
        } else {
            // 原生JavaScript版本（备用）
            window.apiRequest = apiRequest;
        }
        
        console.log('Ferret Web App loaded');
    });
    
    // 格式化数字
    window.formatNumber = function(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    };
    
    // 格式化评分
    window.formatScore = function(score) {
        return (score * 100).toFixed(1) + '%';
    };
    
    // 显示提示消息（原生版本）
    window.showMessage = function(message, type) {
        type = type || 'info';
        const colors = {
            success: 'green',
            error: 'red',
            warning: 'yellow',
            info: 'blue'
        };
        
        const color = colors[type] || 'blue';
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 flex items-center p-4 mb-4 text-sm text-${color}-800 rounded-lg bg-${color}-50`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <svg class="flex-shrink-0 inline w-4 h-4 mr-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z"/>
            </svg>
            <div>${message}</div>
            <button type="button" class="ml-auto -mx-1.5 -my-1.5 text-${color}-500 rounded-lg focus:ring-2 focus:ring-${color}-400 p-1.5 inline-flex h-8 w-8" onclick="this.parentElement.remove()">
                <span class="sr-only">Close</span>
                <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                </svg>
            </button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(function() {
            toast.style.opacity = '0';
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 3000);
    };
})();
