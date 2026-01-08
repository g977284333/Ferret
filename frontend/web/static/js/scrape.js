/**
 * 数据采集页面JavaScript
 */

let keywords = [];
let currentTaskId = null;
let statusInterval = null;

// 等待jQuery加载
function initScrapePage() {
    // 检查URL参数中是否有task_id
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get('task_id');
    if (taskId) {
        currentTaskId = taskId;
        startMonitoring(taskId);
    }
    
    // 关键词输入
    $('#keywordInput').on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            addKeyword();
        }
    });
    
    // 添加关键词按钮
    $('#addKeywordBtn').on('click', addKeyword);
    
    // 表单提交
    $('#scrapeForm').on('submit', function(e) {
        e.preventDefault();
        startScrape();
    });
    
    // 暂停按钮
    $('#pauseBtn').on('click', pauseScrape);
    
    // 停止按钮
    $('#stopBtn').on('click', stopScrape);
}

// 如果jQuery已加载，立即执行；否则等待
if (typeof $ !== 'undefined') {
    $(document).ready(initScrapePage);
} else {
    // 等待jQuery加载
    if (!window.jQueryReadyCallbacks) {
        window.jQueryReadyCallbacks = [];
    }
    window.jQueryReadyCallbacks.push(function() {
        $(document).ready(initScrapePage);
    });
}

function addKeyword() {
    const keyword = $('#keywordInput').val().trim();
    if (keyword && !keywords.includes(keyword)) {
        keywords.push(keyword);
        renderKeywords();
        $('#keywordInput').val('');
    }
}

function removeKeyword(keyword) {
    keywords = keywords.filter(k => k !== keyword);
    renderKeywords();
}

function renderKeywords() {
    const container = $('#keywordsContainer');
    container.empty();
    
    if (keywords.length === 0) {
        container.html('<span class="text-gray-400 text-sm">暂无关键词，请添加</span>');
        return;
    }
    
    keywords.forEach(keyword => {
        const tag = $(`
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                ${keyword}
                <button type="button" class="ml-2 text-blue-600 hover:text-blue-800 font-bold" onclick="removeKeyword('${keyword}')">
                    ×
                </button>
            </span>
        `);
        container.append(tag);
    });
}

function startScrape() {
    if (keywords.length === 0) {
        showMessage('请至少添加一个关键词', 'warning');
        return;
    }
    
    const dataSource = $('#dataSource').val();
    const limitPerKeyword = parseInt($('#limitPerKeyword').val());
    
    $('#startBtn').prop('disabled', true).text('启动中...');
    
    $.ajax({
        url: '/api/v1/scrape/start',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            keywords: keywords,
            data_source: dataSource,
            limit_per_keyword: limitPerKeyword
        })
    })
    .done(function(response) {
        if (response.status === 'success') {
            currentTaskId = response.task_id;
            showMessage('采集任务已启动', 'success');
            
            // 显示进度卡片
            $('#progressCard').show();
            
            // 更新按钮状态
            $('#startBtn').prop('disabled', true);
            $('#pauseBtn').prop('disabled', false);
            $('#stopBtn').prop('disabled', false);
            
            // 开始监控
            startMonitoring(currentTaskId);
        }
    })
    .fail(function(xhr) {
        const error = xhr.responseJSON || {message: '启动采集失败'};
        showMessage(error.message || '启动采集失败', 'error');
        $('#startBtn').prop('disabled', false).text('▶ 开始采集');
    });
}

function startMonitoring(taskId) {
    if (statusInterval) {
        clearInterval(statusInterval);
    }
    
    statusInterval = setInterval(function() {
        checkStatus(taskId);
    }, 2000); // 每2秒查询一次
    
    // 立即查询一次
    checkStatus(taskId);
}

function checkStatus(taskId) {
    $.get(`/api/v1/scrape/status/${taskId}`)
        .done(function(response) {
            if (response.status === 'success' || response.status === 'running') {
                updateProgress(response);
            } else if (response.status === 'completed') {
                clearInterval(statusInterval);
                updateProgress(response);
                showMessage('采集任务已完成', 'success');
                $('#startBtn').prop('disabled', false).text('▶ 开始采集');
                $('#pauseBtn').prop('disabled', true);
                $('#stopBtn').prop('disabled', true);
            } else if (response.status === 'error') {
                clearInterval(statusInterval);
                showMessage('采集任务出错: ' + (response.error || '未知错误'), 'error');
                $('#startBtn').prop('disabled', false).text('▶ 开始采集');
                $('#pauseBtn').prop('disabled', true);
                $('#stopBtn').prop('disabled', true);
            } else if (response.status === 'stopped') {
                clearInterval(statusInterval);
                showMessage('采集任务已停止', 'warning');
                $('#startBtn').prop('disabled', false).text('▶ 开始采集');
                $('#pauseBtn').prop('disabled', true);
                $('#stopBtn').prop('disabled', true);
            }
        })
        .fail(function() {
            console.error('Failed to check status');
        });
}

function updateProgress(data) {
    const progress = data.progress || {};
    const results = data.results || {};
    
    // 更新总体进度
    const total = progress.total || 0;
    const completed = progress.completed || 0;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    $('#overallProgress').text(percentage + '%');
    $('#overallProgressBar').css('width', percentage + '%');
    
    // 更新当前关键词进度
    $('#currentKeyword').text(progress.current_keyword || '-');
    $('#currentProgress').text(progress.current_progress || '0/0');
    
    const currentProgressMatch = (progress.current_progress || '0/0').match(/(\d+)\/(\d+)/);
    if (currentProgressMatch) {
        const currentCompleted = parseInt(currentProgressMatch[1]);
        const currentTotal = parseInt(currentProgressMatch[2]);
        const currentPercentage = currentTotal > 0 ? Math.round((currentCompleted / currentTotal) * 100) : 0;
        $('#currentProgressBar').css('width', currentPercentage + '%');
    }
    
    // 更新结果统计
    $('#collectedCount').text(results.apps_collected || completed);
    $('#opportunitiesCount').text(results.opportunities_found || 0);
    
    // 更新预计剩余时间（简化计算）
    if (total > 0 && completed > 0) {
        const remaining = total - completed;
        const avgTimePerApp = 2; // 假设每个App需要2秒
        const estimatedSeconds = remaining * avgTimePerApp;
        const minutes = Math.floor(estimatedSeconds / 60);
        const seconds = estimatedSeconds % 60;
        $('#estimatedTime').text(`${minutes}分${seconds}秒`);
    }
}

function pauseScrape() {
    // TODO: 实现暂停功能
    showMessage('暂停功能待实现', 'info');
}

function stopScrape() {
    if (!currentTaskId) {
        return;
    }
    
    if (!confirm('确定要停止采集任务吗？')) {
        return;
    }
    
    $.ajax({
        url: `/api/v1/scrape/stop/${currentTaskId}`,
        method: 'POST'
    })
    .done(function(response) {
        if (response.status === 'success') {
            clearInterval(statusInterval);
            showMessage('采集任务已停止', 'warning');
            $('#startBtn').prop('disabled', false).text('▶ 开始采集');
            $('#pauseBtn').prop('disabled', true);
            $('#stopBtn').prop('disabled', true);
        }
    })
    .fail(function() {
        showMessage('停止任务失败', 'error');
    });
}
