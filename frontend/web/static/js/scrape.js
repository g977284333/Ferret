/**
 * 数据采集页面JavaScript
 */

let keywords = [];
let currentTaskId = null;
let statusInterval = null;

// 等待jQuery加载
function initScrapePage() {
    // 检查URL参数
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get('task_id');
    const keywordsParam = urlParams.get('keywords');
    
    // 如果有关键词参数，添加到关键词列表
    if (keywordsParam) {
        const keywordList = keywordsParam.split(',').map(k => decodeURIComponent(k)).filter(k => k);
        keywords = [...new Set([...keywords, ...keywordList])]; // 去重
        renderKeywords();
    }
    
    // 如果有task_id，开始监控
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
    
    // 新采集按钮
    $('#newScrapeBtn').on('click', function() {
        // 重置表单
        keywords = [];
        renderKeywords();
        $('#progressCard').hide();
        $('#resultsCard').hide();
        $('#scrapeForm').show();
        currentTaskId = null;
        if (statusInterval) {
            clearInterval(statusInterval);
            statusInterval = null;
        }
        // 清除URL参数
        window.history.pushState({}, '', '/scrape');
    });
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
    
    // 记录开始时间
    window.scrapeStartTime = Date.now();
    
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
            
            // 更新URL，添加task_id和关键词参数
            const keywordsParam = keywords.map(k => encodeURIComponent(k)).join(',');
            const newUrl = `/scrape?task_id=${currentTaskId}&keywords=${keywordsParam}`;
            window.history.pushState({}, '', newUrl);
            
            showMessage('采集任务已启动', 'success');
            
            // 开始监控（会自动显示进度卡片）
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
    
    // 记录开始时间
    window.scrapeStartTime = Date.now();
    
    // 显示进度卡片，隐藏表单
    $('#progressCard').show();
    $('#scrapeForm').hide();
    updateStatusDisplay('running', '正在采集数据...');
    
    statusInterval = setInterval(function() {
        checkStatus(taskId);
    }, 2000); // 每2秒查询一次
    
    // 立即查询一次
    checkStatus(taskId);
}

function updateStatusDisplay(status, text) {
    const statusText = $('#statusText');
    const statusIndicator = $('#statusIndicator');
    
    if (statusText) statusText.text(text || '运行中...');
    
    if (statusIndicator) {
        statusIndicator.removeClass('bg-blue-500 bg-green-500 bg-red-500 bg-yellow-500 animate-pulse');
        if (status === 'running') {
            statusIndicator.addClass('bg-blue-500 animate-pulse');
        } else if (status === 'completed') {
            statusIndicator.addClass('bg-green-500');
        } else if (status === 'error') {
            statusIndicator.addClass('bg-red-500');
        } else {
            statusIndicator.addClass('bg-yellow-500');
        }
    }
}

function checkStatus(taskId) {
    $.get(`/api/v1/scrape/status/${taskId}`)
        .done(function(response) {
            console.log('Status response:', response); // 调试日志
            
            if (response.status === 'success' && response.data) {
                const data = response.data;
                const taskStatus = data.status; // pending, running, completed, error, stopped
                
                console.log('Task status:', taskStatus, 'Progress:', data.progress); // 调试日志
                
                // 更新状态显示
                if (taskStatus === 'running') {
                    updateStatusDisplay('running', '正在采集数据...');
                    updateProgress(data);
                } else if (taskStatus === 'completed') {
                    clearInterval(statusInterval);
                    statusInterval = null;
                    updateStatusDisplay('completed', '采集完成！');
                    updateProgress(data);
                    
                    // 显示结果卡片
                    const results = data.results || {};
                    $('#appsCollectedResult').text(results.apps_collected || 0);
                    $('#opportunitiesFoundResult').text(results.opportunities_found || 0);
                    $('#resultsCard').show();
                    
                    showMessage(`采集完成！已采集 ${results.apps_collected || 0} 个App，发现 ${results.opportunities_found || 0} 个机会`, 'success');
                } else if (taskStatus === 'error') {
                    clearInterval(statusInterval);
                    statusInterval = null;
                    updateStatusDisplay('error', '采集失败');
                    showMessage('采集任务出错: ' + (data.error || '未知错误'), 'error');
                } else if (taskStatus === 'stopped') {
                    clearInterval(statusInterval);
                    statusInterval = null;
                    updateStatusDisplay('stopped', '已停止');
                    showMessage('采集任务已停止', 'warning');
                } else if (taskStatus === 'pending') {
                    // 任务还在等待启动
                    updateStatusDisplay('running', '等待启动...');
                }
            } else if (response.status === 'error') {
                // API调用失败
                console.error('API error:', response);
                clearInterval(statusInterval);
                statusInterval = null;
                updateStatusDisplay('error', '获取状态失败');
                showMessage('获取任务状态失败: ' + (response.message || '未知错误'), 'error');
            } else {
                // 兼容旧格式（直接返回任务状态）
                console.log('Using legacy format:', response);
                const taskStatus = response.status;
                if (taskStatus === 'running' || taskStatus === 'pending') {
                    updateStatusDisplay('running', '正在采集数据...');
                    updateProgress(response);
                }
            }
        })
        .fail(function(xhr) {
            console.error('Failed to check status:', xhr);
            // 不要立即停止，可能是网络问题，继续尝试
            if (xhr.status === 404) {
                clearInterval(statusInterval);
                statusInterval = null;
                updateStatusDisplay('error', '任务不存在');
                showMessage('任务不存在，可能已被清除', 'error');
            }
        });
}

function updateProgress(data) {
    const progress = data.progress || {};
    const results = data.results || {};
    
    // 更新总体进度
    const total = progress.total || 0;
    const completed = progress.completed || 0;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    $('#overallProgress').text(`${completed}/${total}`);
    $('#overallProgressBar').css('width', percentage + '%');
    
    // 更新当前关键词进度
    $('#currentKeyword').text(progress.current_keyword || '等待开始...');
    $('#currentProgress').text(progress.current_progress || '0/0');
    
    const currentProgressMatch = (progress.current_progress || '0/0').match(/(\d+)\/(\d+)/);
    if (currentProgressMatch) {
        const currentCompleted = parseInt(currentProgressMatch[1]);
        const currentTotal = parseInt(currentProgressMatch[2]);
        const currentPercentage = currentTotal > 0 ? Math.round((currentCompleted / currentTotal) * 100) : 0;
        $('#currentProgressBar').css('width', currentPercentage + '%');
    }
    
    // 更新实时统计
    $('#appsCollected').text(completed || 0);
    $('#opportunitiesFound').text(results.opportunities_found || 0);
    
    // 更新预计剩余时间（基于实际速度）
    if (completed > 0 && total > completed && window.scrapeStartTime) {
        const elapsed = (Date.now() - window.scrapeStartTime) / 1000; // 秒
        const speed = completed / elapsed; // 每秒完成数
        const remaining = (total - completed) / speed;
        
        if (remaining > 0) {
            const minutes = Math.floor(remaining / 60);
            const seconds = Math.floor(remaining % 60);
            if (minutes > 0) {
                $('#estimatedTime').text(`${minutes}分${seconds}秒`);
            } else {
                $('#estimatedTime').text(`${seconds}秒`);
            }
        } else {
            $('#estimatedTime').text('即将完成');
        }
    } else if (completed >= total && total > 0) {
        $('#estimatedTime').text('已完成');
    } else {
        $('#estimatedTime').text('计算中...');
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
