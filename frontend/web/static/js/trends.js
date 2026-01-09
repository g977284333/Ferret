/**
 * 搜索趋势页面JavaScript
 */

let keywords = [];
let currentTaskId = null;
let statusInterval = null;
let trendChart = null; // Chart.js实例

// 等待jQuery加载
function initTrendsPage() {
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
    
    // 获取建议按钮
    $('#getSuggestionsBtn').on('click', getSuggestions);
    
    // 表单提交
    $('#trendForm').on('submit', function(e) {
        e.preventDefault();
        startTrendCollection();
    });
    
    // 停止按钮（进度卡片中的）
    $('#stopBtnInProgress').on('click', stopTrendCollection);
    
    // 开始新的采集按钮（结果卡片中的）
    $('#newCollectionBtnInResults').on('click', startNewCollection);
    
    // 查看已采集关键词按钮
    $('#viewKeywordsBtn').on('click', function() {
        console.log('viewKeywordsBtn clicked');
        
        // 先刷新关键词列表
        loadCollectedKeywords();
        
        // 滚动到已采集关键词区域
        setTimeout(function() {
            const targetElement = $('#collectedKeywordsList').closest('.bg-white');
            if (targetElement.length) {
                $('html, body').animate({
                    scrollTop: targetElement.offset().top - 20
                }, 500);
                showMessage('已滚动到已采集关键词列表', 'info');
            } else {
                showMessage('未找到已采集关键词区域', 'warning');
            }
        }, 300);
    });
    
    // 当任务开始时，启用停止按钮
    // 当任务结束时，禁用停止按钮
    
    // 刷新热门关键词
    $('#refreshHotBtn').on('click', loadHotKeywords);
    
    // 刷新已采集关键词
    $('#refreshCollectedBtn').on('click', loadCollectedKeywords);
    
    // 加载图表
    $('#loadChartBtn').on('click', loadTrendChart);
    
    // 对比关键词
    $('#compareBtn').on('click', compareKeywords);
    
    // 初始化加载
    loadCollectedKeywords();
    loadHotKeywords();
    
    // 初始化Tooltip（使用Flowbite的tooltip功能）
    initTooltips();
}

function initTooltips() {
    // 使用Flowbite的tooltip功能
    // 如果Flowbite已加载，初始化tooltip
    if (typeof Flowbite !== 'undefined' && Flowbite.initTooltips) {
        Flowbite.initTooltips();
    } else {
        // 如果Flowbite未加载，使用简单的点击显示/隐藏
        $('[data-tooltip-target]').on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const targetId = $(this).attr('data-tooltip-target');
            const tooltip = $('#' + targetId);
            
            // 关闭其他tooltip
            $('.tooltip').removeClass('visible opacity-100').addClass('invisible opacity-0');
            
            // 切换当前tooltip
            if (tooltip.hasClass('invisible')) {
                tooltip.removeClass('invisible opacity-0').addClass('visible opacity-100');
                
                // 点击外部关闭
                $(document).one('click', function() {
                    tooltip.removeClass('visible opacity-100').addClass('invisible opacity-0');
                });
            } else {
                tooltip.removeClass('visible opacity-100').addClass('invisible opacity-0');
            }
        });
    }
}

// 如果jQuery已加载，立即执行；否则等待
if (typeof $ !== 'undefined') {
    $(document).ready(initTrendsPage);
} else {
    if (!window.jQueryReadyCallbacks) {
        window.jQueryReadyCallbacks = [];
    }
    window.jQueryReadyCallbacks.push(function() {
        $(document).ready(initTrendsPage);
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

function getSuggestions() {
    const keyword = $('#keywordInput').val().trim();
    if (!keyword) {
        showMessage('请先输入关键词', 'warning');
        return;
    }
    
    $.get(`/api/v1/trends/suggestions?keyword=${encodeURIComponent(keyword)}`)
        .done(function(response) {
            if (response.status === 'success' && response.data.suggestions) {
                const suggestions = response.data.suggestions;
                if (suggestions.length === 0) {
                    showMessage('未找到相关建议', 'info');
                    return;
                }
                
                // 显示建议列表
                let suggestionsHtml = '<div class="mt-2 p-3 bg-blue-50 rounded-lg"><p class="text-sm font-medium mb-2">建议关键词：</p><div class="flex flex-wrap gap-2">';
                suggestions.slice(0, 10).forEach(s => {
                    const title = s.title || s.mid || '';
                    if (title) {
                        suggestionsHtml += `<button type="button" class="px-2 py-1 bg-white text-blue-700 rounded text-sm hover:bg-blue-100" onclick="addSuggestion('${title.replace(/'/g, "\\'")}')">${title}</button>`;
                    }
                });
                suggestionsHtml += '</div></div>';
                
                $('#keywordInput').after(suggestionsHtml);
            }
        })
        .fail(function() {
            showMessage('获取建议失败', 'error');
        });
}

function addSuggestion(keyword) {
    if (keyword && !keywords.includes(keyword)) {
        keywords.push(keyword);
        renderKeywords();
        $('#keywordInput').val('');
        $('.bg-blue-50').remove(); // 移除建议框
    }
}

function startTrendCollection() {
    if (keywords.length === 0) {
        showMessage('请至少添加一个关键词', 'warning');
        return;
    }
    
    const platforms = [];
    $('input[name="platform"]:checked').each(function() {
        platforms.push($(this).val());
    });
    
    if (platforms.length === 0) {
        showMessage('请至少选择一个平台', 'warning');
        return;
    }
    
    const timeframe = $('#timeframe').val();
    
    $('#startBtn').prop('disabled', true).text('启动中...');
    
    $.ajax({
        url: '/api/v1/trends/start',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            keywords: keywords,
            platforms: platforms,
            timeframe: timeframe
        })
    })
    .done(function(response) {
        if (response.status === 'success') {
            currentTaskId = response.task_id;
            
            const keywordsParam = keywords.map(k => encodeURIComponent(k)).join(',');
            const newUrl = `/trends?task_id=${currentTaskId}&keywords=${keywordsParam}`;
            window.history.pushState({}, '', newUrl);
            
            showMessage('趋势采集任务已启动', 'success');
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
    
    $('#progressCard').show();
    $('#trendForm').hide();
    updateStatusDisplay('running', '正在采集趋势数据...');
    
    // 启用停止按钮（进度卡片中的）
    $('#stopBtnInProgress').prop('disabled', false).show();
    
    // 初始化任务状态存储
    if (!window.trendTasks) {
        window.trendTasks = {};
    }
    
    statusInterval = setInterval(function() {
        checkStatus(taskId);
    }, 2000);
    
    checkStatus(taskId);
}

function checkStatus(taskId) {
    $.get(`/api/v1/trends/status/${taskId}`)
        .done(function(response) {
            if (response.status === 'success' && response.data) {
                const data = response.data;
                const taskStatus = data.status;
                
                if (taskStatus === 'running') {
                    updateStatusDisplay('running', '正在采集趋势数据...');
                    updateProgress(data);
                } else if (taskStatus === 'completed') {
                    clearInterval(statusInterval);
                    statusInterval = null;
                    updateStatusDisplay('completed', '采集完成！');
                    updateProgress(data);
                    
                    // 禁用停止按钮
                    $('#stopBtnInProgress').prop('disabled', true);
                    
                    showMessage('趋势采集完成！', 'success');
                    
                    // 保存采集的关键词（用于后续自动加载图表）
                    const collectedKeywords = keywords.length > 0 ? [...keywords] : [];
                    
                    // 刷新关键词列表，完成后自动选择并加载图表
                    loadCollectedKeywords(function() {
                        // 如果采集了关键词，自动选择第一个并加载图表
                        if (collectedKeywords.length > 0) {
                            const firstKeyword = collectedKeywords[0];
                            // 等待关键词列表更新完成
                            setTimeout(function() {
                                // 设置图表关键词选择
                                const chartKeywordSelect = $('#chartKeyword');
                                if (chartKeywordSelect.find(`option[value="${firstKeyword}"]`).length > 0) {
                                    chartKeywordSelect.val(firstKeyword);
                                    // 自动加载图表
                                    loadTrendChart();
                                    showMessage(`已自动加载关键词 "${firstKeyword}" 的趋势图表`, 'info');
                                }
                            }, 800);
                        }
                    });
                    loadHotKeywords();
                } else if (taskStatus === 'error') {
                    clearInterval(statusInterval);
                    statusInterval = null;
                    updateStatusDisplay('error', '采集失败');
                    
                    // 禁用停止按钮
                    $('#stopBtnInProgress').prop('disabled', true);
                    
                    showMessage('采集任务出错: ' + (data.error || '未知错误'), 'error');
                } else if (taskStatus === 'stopped') {
                    clearInterval(statusInterval);
                    statusInterval = null;
                    updateStatusDisplay('stopped', '已停止');
                    
                    // 禁用停止按钮
                    $('#stopBtn').prop('disabled', true);
                    $('#stopBtnInProgress').prop('disabled', true);
                    
                    // 隐藏进度卡片，显示结果卡片
                    $('#progressCard').hide();
                    
                    // 更新结果卡片数据并显示
                    if ($('#resultsCard').length) {
                        const results = data.results || {};
                        $('#keywordsCollectedResult').text(results.keywords_collected || 0);
                        $('#trendsSavedResult').text(results.trends_saved || 0);
                        $('#resultsCard').show();
                    }
                    
                    showMessage('采集任务已停止', 'info');
                }
            }
        })
        .fail(function(xhr) {
            if (xhr.status === 404) {
                clearInterval(statusInterval);
                statusInterval = null;
                updateStatusDisplay('error', '任务不存在');
                showMessage('任务不存在，可能已被清除', 'error');
            }
        });
}

function updateStatusDisplay(status, text) {
    const statusText = $('#statusText');
    const statusIndicator = $('#statusIndicator');
    
    if (statusText) statusText.text(text || '运行中...');
    
    if (statusIndicator) {
        statusIndicator.removeClass('bg-blue-500 bg-green-500 bg-red-500 bg-yellow-500 bg-gray-500 animate-pulse');
        if (status === 'running') {
            statusIndicator.addClass('bg-blue-500 animate-pulse');
        } else if (status === 'completed') {
            statusIndicator.addClass('bg-green-500');
        } else if (status === 'error') {
            statusIndicator.addClass('bg-red-500');
        } else if (status === 'stopped') {
            statusIndicator.addClass('bg-gray-500');
        } else {
            statusIndicator.addClass('bg-yellow-500');
        }
    }
}

function updateProgress(data) {
    const progress = data.progress || {};
    const total = progress.total || 0;
    const completed = progress.completed || 0;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    $('#overallProgress').text(`${completed}/${total}`);
    $('#overallProgressBar').css('width', percentage + '%');
    $('#currentKeyword').text(progress.current_keyword || '-');
    $('#currentPlatform').text(progress.current_platform || '-');
}

function startNewCollection() {
    console.log('startNewCollection called');
    
    // 重置所有状态
    currentTaskId = null;
    
    // 停止监控
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }
    
    // 隐藏进度卡片和结果卡片
    $('#progressCard').hide();
    $('#resultsCard').hide();
    
    // 显示采集表单
    $('#trendForm').show();
    
    // 重置表单
    $('#keywordInput').val('');
    keywords = [];
    renderKeywords();
    
    // 重置按钮状态
    $('#startBtn').prop('disabled', false).text('▶ 开始采集');
    $('#stopBtnInProgress').prop('disabled', true);
    
    // 滚动到表单顶部
    setTimeout(function() {
        const formElement = $('#trendForm').closest('.bg-white');
        if (formElement.length) {
            $('html, body').animate({
                scrollTop: formElement.offset().top - 20
            }, 500);
        }
    }, 100);
    
    showMessage('已重置，可以开始新的采集', 'info');
}

function stopTrendCollection() {
    if (!currentTaskId) {
        showMessage('没有正在运行的任务', 'warning');
        return;
    }
    
    // 确认停止
    if (!confirm('确定要停止当前采集任务吗？')) {
        return;
    }
    
    // 发送停止请求
    $.ajax({
        url: `/api/v1/trends/stop/${currentTaskId}`,
        method: 'POST',
        contentType: 'application/json'
    })
    .done(function(response) {
        if (response.status === 'success') {
            showMessage('采集任务已停止', 'success');
            
            // 更新任务状态为stopped
            if (!window.trendTasks) {
                window.trendTasks = {};
            }
            if (window.trendTasks[currentTaskId]) {
                window.trendTasks[currentTaskId].status = 'stopped';
            }
            
            // 停止监控
            if (statusInterval) {
                clearInterval(statusInterval);
                statusInterval = null;
            }
            
            // 更新UI显示
            updateStatusDisplay('stopped', '已停止');
            
            // 禁用停止按钮
            $('#stopBtnInProgress').prop('disabled', true);
            
            // 隐藏进度卡片，显示结果卡片
            $('#progressCard').hide();
            
            // 更新结果卡片数据并显示
            if ($('#resultsCard').length) {
                const task = window.trendTasks && window.trendTasks[currentTaskId];
                if (task && task.results) {
                    $('#keywordsCollectedResult').text(task.results.keywords_collected || 0);
                    $('#trendsSavedResult').text(task.results.trends_saved || 0);
                } else {
                    $('#keywordsCollectedResult').text('0');
                    $('#trendsSavedResult').text('0');
                }
                $('#resultsCard').show();
            }
        } else {
            showMessage(response.message || '停止失败', 'error');
        }
    })
    .fail(function(xhr) {
        console.error('Stop trend collection failed:', xhr);
        showMessage('停止失败: ' + (xhr.responseJSON?.message || '网络错误'), 'error');
    });
}

function loadHotKeywords() {
    // 降低阈值，显示更多关键词（从20%降到5%）
    $.get('/api/v1/trends/hot?min_growth_rate=5')
        .done(function(response) {
            console.log('Hot keywords response:', response);
            const container = $('#hotKeywordsList');
            const thresholdLabel = $('#hotKeywordsThreshold');
            container.empty();
            
            if (response.status === 'success' && response.data) {
                const hotKeywords = response.data.hot_keywords || [];
                
                if (hotKeywords.length === 0) {
                    container.html('<p class="text-gray-400 text-sm">暂无热门关键词<br><span class="text-xs">（需要更多数据或降低增长率阈值）</span></p>');
                    if (thresholdLabel) thresholdLabel.text('增长率 ≥ 5%');
                    return;
                }
                
                // 检查是否所有关键词都符合阈值（如果不符合，说明返回了所有关键词）
                const allMeetThreshold = hotKeywords.every(item => (item.growth_rate || 0) >= 5);
                if (!allMeetThreshold && thresholdLabel) {
                    thresholdLabel.text('所有关键词（按增长率排序）');
                } else if (thresholdLabel) {
                    thresholdLabel.text('增长率 ≥ 5%');
                }
                
                hotKeywords.slice(0, 10).forEach(item => {
                    const trend = item.trend || 'stable';
                    const growthRate = item.growth_rate || 0;
                    const trendIcon = trend === 'rising' ? '📈' : trend === 'declining' ? '📉' : '➡️';
                    // 根据增长率显示不同颜色
                    let colorClass = 'text-gray-600';
                    if (growthRate >= 5) {
                        colorClass = 'text-green-600';
                    } else if (growthRate < 0) {
                        colorClass = 'text-red-600';
                    }
                    
                    const html = $(`
                        <div class="flex items-center justify-between p-2 bg-gray-50 rounded mb-2">
                            <div>
                                <span class="font-medium">${item.keyword || '未知'}</span>
                                <span class="text-xs text-gray-500 ml-2">${item.platform || 'google_trends'}</span>
                            </div>
                            <div class="text-right">
                                <div class="text-sm font-semibold ${colorClass}">
                                    ${trendIcon} ${growthRate > 0 ? '+' : ''}${growthRate.toFixed(1)}%
                                </div>
                            </div>
                        </div>
                    `);
                    container.append(html);
                });
            } else {
                container.html('<p class="text-gray-400 text-sm">暂无热门关键词</p>');
            }
        })
        .fail(function(xhr) {
            console.error('Load hot keywords failed:', xhr);
            $('#hotKeywordsList').html('<p class="text-red-400 text-sm">加载失败</p>');
        });
}

function loadCollectedKeywords(callback) {
    $.get('/api/v1/trends/keywords')
        .done(function(response) {
            if (response.status === 'success' && response.data.keywords) {
                const keywords = response.data.keywords;
                const container = $('#collectedKeywordsList');
                container.empty();
                
                if (keywords.length === 0) {
                    container.html('<p class="text-gray-400 text-sm">暂无已采集的关键词</p>');
                    // 清空图表选择
                    $('#chartKeyword').empty().append('<option value="">选择关键词...</option>');
                    if (callback) callback();
                    return;
                }
                
                // 更新图表关键词选择
                const chartKeyword = $('#chartKeyword');
                const currentValue = chartKeyword.val(); // 保存当前选择
                chartKeyword.empty().append('<option value="">选择关键词...</option>');
                keywords.forEach(kw => {
                    chartKeyword.append(`<option value="${kw}">${kw}</option>`);
                });
                // 恢复之前的选择（如果存在且有效）
                if (currentValue && keywords.includes(currentValue)) {
                    chartKeyword.val(currentValue);
                }
                
                keywords.slice(0, 20).forEach(keyword => {
                    // 转义单引号，避免onclick中的JavaScript错误
                    const safeKeyword = keyword.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                    const html = $(`
                        <div class="flex items-center justify-between p-2 bg-gray-50 rounded mb-2">
                            <span class="font-medium">${keyword}</span>
                            <button class="text-blue-600 hover:text-blue-800 text-sm font-medium px-2 py-1 rounded hover:bg-blue-50" 
                                    onclick="window.analyzeKeyword('${safeKeyword}')">
                                分析
                            </button>
                        </div>
                    `);
                    container.append(html);
                });
                
                // 执行回调
                if (callback) callback();
            } else {
                container.html('<p class="text-gray-400 text-sm">暂无已采集的关键词</p>');
                if (callback) callback();
            }
        })
        .fail(function() {
            $('#collectedKeywordsList').html('<p class="text-red-400 text-sm">加载失败</p>');
            if (callback) callback();
        });
}

// 将analyzeKeyword暴露为全局函数，以便onclick可以调用
window.analyzeKeyword = function(keyword) {
    console.log('Analyzing keyword:', keyword);
    
    // 显示加载状态
    $('#analysisCard').show();
    $('#analysisContent').html('<div class="text-center py-8"><div class="loading-spinner mx-auto mb-4"></div><p class="text-gray-600">分析中...</p></div>');
    
    $.get(`/api/v1/trends/analyze/${encodeURIComponent(keyword)}?platform=google_trends`)
        .done(function(response) {
            console.log('Analysis response:', response);
            if (response.status === 'success' && response.data) {
                const analysis = response.data.analysis;
                const summary = response.data.summary;
                
                let html = `
                    <div class="space-y-4">
                        <div class="mb-4">
                            <h3 class="text-lg font-bold text-gray-900">关键词：${keyword}</h3>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div class="p-4 bg-blue-50 rounded-lg">
                                <p class="text-sm text-gray-600">增长率</p>
                                <p class="text-2xl font-bold ${analysis.growth_rate > 0 ? 'text-green-600' : 'text-red-600'}">
                                    ${analysis.growth_rate > 0 ? '+' : ''}${analysis.growth_rate.toFixed(1)}%
                                </p>
                            </div>
                            <div class="p-4 bg-green-50 rounded-lg">
                                <p class="text-sm text-gray-600">趋势分数</p>
                                <p class="text-2xl font-bold text-green-600">${(summary.trend_score || 0).toFixed(3)}</p>
                            </div>
                        </div>
                        <div class="p-4 bg-gray-50 rounded-lg">
                            <p class="text-sm font-medium mb-2">趋势分析</p>
                            <p class="text-sm">趋势：<span class="font-semibold">${getTrendText(analysis.trend || 'stable')}</span></p>
                            <p class="text-sm">平均热度：${(analysis.avg_value || 0).toFixed(2)}</p>
                            <p class="text-sm">最高热度：${(analysis.max_value || 0).toFixed(2)}</p>
                            <p class="text-sm">最低热度：${(analysis.min_value || 0).toFixed(2)}</p>
                            <p class="text-sm">波动性：${(analysis.volatility || 0).toFixed(2)}</p>
                            <p class="text-sm">数据点数：${response.data.data_points || 0}</p>
                        </div>
                    </div>
                `;
                
                $('#analysisContent').html(html);
                showMessage('分析完成', 'success');
            } else {
                $('#analysisContent').html(`<div class="text-center py-8"><p class="text-red-600">分析失败：${response.message || '未知错误'}</p></div>`);
                showMessage('分析失败：' + (response.message || '未知错误'), 'error');
            }
        })
        .fail(function(xhr) {
            console.error('Analysis failed:', xhr);
            let errorMsg = '分析失败';
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMsg = xhr.responseJSON.message;
            }
            $('#analysisContent').html(`<div class="text-center py-8"><p class="text-red-600">${errorMsg}</p></div>`);
            showMessage(errorMsg, 'error');
        });
};

// 也保留原来的函数定义（兼容性）
function analyzeKeyword(keyword) {
    window.analyzeKeyword(keyword);
}

function getTrendText(trend) {
    const trendMap = {
        'rising': '上升',
        'slightly_rising': '小幅上升',
        'stable': '稳定',
        'slightly_declining': '小幅下降',
        'declining': '下降'
    };
    return trendMap[trend] || trend;
}

function loadTrendChart() {
    const keyword = $('#chartKeyword').val();
    const platform = $('#chartPlatform').val();
    
    if (!keyword) {
        showMessage('请选择关键词', 'warning');
        return;
    }
    
    // 显示加载状态
    $('#chartContainer').html('<div class="text-center py-20"><div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div><p class="mt-4 text-gray-600">加载中...</p></div>');
    
    $.get(`/api/v1/trends?keyword=${encodeURIComponent(keyword)}&platform=${platform}`)
        .done(function(response) {
            if (response.status === 'success' && response.data.trends) {
                const trends = response.data.trends;
                if (trends.length === 0) {
                    $('#chartContainer').html('<p class="text-gray-400 text-center mt-20">暂无数据</p>');
                    return;
                }
                
                // 使用Chart.js渲染图表
                renderChartWithChartJS(trends, keyword, platform);
            } else {
                $('#chartContainer').html('<p class="text-gray-400 text-center mt-20">加载失败</p>');
            }
        })
        .fail(function(xhr) {
            console.error('Load chart failed:', xhr);
            $('#chartContainer').html('<p class="text-red-400 text-center mt-20">加载图表数据失败</p>');
            showMessage('加载图表数据失败', 'error');
        });
}

function renderChartWithChartJS(trends, keyword, platform) {
    // 使用Chart.js渲染图表
    const container = $('#chartContainer');
    container.empty();
    
    // 准备数据：按日期排序
    const sortedTrends = trends.sort((a, b) => new Date(a.date) - new Date(b.date));
    const dates = sortedTrends.map(t => {
        const date = new Date(t.date);
        // 格式化日期显示
        return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    });
    const values = sortedTrends.map(t => parseFloat(t.value) || 0);
    
    // 创建canvas元素
    const canvas = $('<canvas id="trendChart"></canvas>');
    container.append(canvas);
    
    // 销毁旧图表
    if (trendChart) {
        trendChart.destroy();
    }
    
    // 创建Chart.js图表
    const ctx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: keyword,
                data: values,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 5,
                pointBackgroundColor: 'rgb(59, 130, 246)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${keyword} - ${platform === 'google_trends' ? 'Google Trends' : platform} 搜索趋势`,
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: '搜索热度'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '日期'
                    },
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
    
    // 添加统计信息
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);
    const avgValue = values.reduce((a, b) => a + b, 0) / values.length;
    
    container.append(`
        <div class="mt-4 grid grid-cols-3 gap-4 text-sm">
            <div class="text-center p-3 bg-blue-50 rounded-lg">
                <p class="text-gray-600">最大值</p>
                <p class="text-lg font-bold text-blue-600">${maxValue.toFixed(2)}</p>
            </div>
            <div class="text-center p-3 bg-green-50 rounded-lg">
                <p class="text-gray-600">平均值</p>
                <p class="text-lg font-bold text-green-600">${avgValue.toFixed(2)}</p>
            </div>
            <div class="text-center p-3 bg-gray-50 rounded-lg">
                <p class="text-gray-600">最小值</p>
                <p class="text-lg font-bold text-gray-600">${minValue.toFixed(2)}</p>
            </div>
        </div>
    `);
}

function compareKeywords() {
    // 从已采集关键词列表获取关键词，或者使用当前关键词列表
    const selectedKeywords = [];
    
    // 尝试从已采集关键词中获取
    $('#collectedKeywordsList .font-medium').each(function() {
        const keyword = $(this).text().trim();
        if (keyword && !selectedKeywords.includes(keyword)) {
            selectedKeywords.push(keyword);
        }
    });
    
    // 如果不够，使用当前关键词列表
    if (selectedKeywords.length < 2 && keywords.length >= 2) {
        selectedKeywords.push(...keywords.slice(0, 5)); // 最多5个
    }
    
    if (selectedKeywords.length < 2) {
        showMessage('请至少采集2个关键词才能进行对比', 'warning');
        return;
    }
    
    const platform = $('#chartPlatform').val() || 'google_trends';
    
    // 显示加载状态
    $('#chartContainer').html('<div class="text-center py-20"><div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div><p class="mt-4 text-gray-600">加载对比数据中...</p></div>');
    
    // 获取所有关键词的数据
    const promises = selectedKeywords.map(kw => {
        return $.get(`/api/v1/trends?keyword=${encodeURIComponent(kw)}&platform=${platform}`);
    });
    
    $.when.apply($, promises)
        .done(function() {
            // 处理所有响应
            const datasets = [];
            const colors = [
                'rgb(59, 130, 246)',   // blue
                'rgb(16, 185, 129)',   // green
                'rgb(245, 101, 101)',  // red
                'rgb(251, 191, 36)',   // yellow
                'rgb(139, 92, 246)'    // purple
            ];
            
            let allDates = new Set();
            const trendsData = {};
            
            // 收集所有数据
            Array.from(arguments).forEach((response, index) => {
                if (response.status === 'success' && response.data.trends) {
                    const trends = response.data.trends.sort((a, b) => new Date(a.date) - new Date(b.date));
                    const keyword = selectedKeywords[index];
                    trendsData[keyword] = trends;
                    trends.forEach(t => allDates.add(t.date));
                }
            });
            
            // 排序日期
            const sortedDates = Array.from(allDates).sort((a, b) => new Date(a) - new Date(b));
            const dateLabels = sortedDates.map(date => {
                const d = new Date(date);
                return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
            });
            
            // 为每个关键词创建数据集
            selectedKeywords.forEach((keyword, index) => {
                if (trendsData[keyword]) {
                    const values = sortedDates.map(date => {
                        const trend = trendsData[keyword].find(t => t.date === date);
                        return trend ? parseFloat(trend.value) || 0 : null;
                    });
                    
                    datasets.push({
                        label: keyword,
                        data: values,
                        borderColor: colors[index % colors.length],
                        backgroundColor: colors[index % colors.length].replace('rgb', 'rgba').replace(')', ', 0.1)'),
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    });
                }
            });
            
            if (datasets.length === 0) {
                $('#chartContainer').html('<p class="text-gray-400 text-center mt-20">暂无数据</p>');
                return;
            }
            
            // 渲染对比图表
            renderCompareChart(dateLabels, datasets, platform);
            
            // 同时显示对比表格
            $.ajax({
                url: '/api/v1/trends/compare',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    keywords: selectedKeywords,
                    platform: platform
                })
            })
            .done(function(response) {
                if (response.status === 'success' && response.data.comparison) {
                    const comparison = response.data.comparison;
                    
                    let html = `
                        <div class="mt-6">
                            <h3 class="text-lg font-bold mb-4">对比统计</h3>
                            <div class="overflow-x-auto">
                                <table class="min-w-full divide-y divide-gray-200">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">关键词</th>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">增长率</th>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">趋势</th>
                                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">平均热度</th>
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white divide-y divide-gray-200">
                    `;
                    
                    comparison.forEach(item => {
                        html += `
                            <tr>
                                <td class="px-4 py-3 text-sm font-medium">${item.keyword}</td>
                                <td class="px-4 py-3 text-sm ${item.growth_rate > 0 ? 'text-green-600' : 'text-red-600'}">
                                    ${item.growth_rate > 0 ? '+' : ''}${item.growth_rate.toFixed(1)}%
                                </td>
                                <td class="px-4 py-3 text-sm">${getTrendText(item.trend)}</td>
                                <td class="px-4 py-3 text-sm">${item.avg_value.toFixed(2)}</td>
                            </tr>
                        `;
                    });
                    
                    html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                    
                    $('#chartContainer').append(html);
                }
            })
            .fail(function() {
                console.error('Failed to load comparison data');
            });
        })
        .fail(function() {
            $('#chartContainer').html('<p class="text-red-400 text-center mt-20">加载对比数据失败</p>');
            showMessage('加载对比数据失败', 'error');
        });
}

function renderCompareChart(labels, datasets, platform) {
    // 检查Chart.js是否已加载
    if (typeof Chart === 'undefined') {
        $('#chartContainer').html('<p class="text-red-400 text-center mt-20">Chart.js未加载，请刷新页面重试</p>');
        console.error('Chart.js is not loaded');
        return;
    }
    
    const container = $('#chartContainer');
    // 只清空图表部分，保留统计表格
    const existingTable = container.find('table').parent().parent();
    container.empty();
    
    // 创建canvas元素
    const canvas = $('<canvas id="trendChart"></canvas>');
    container.append(canvas);
    
    // 如果之前有表格，重新添加
    if (existingTable.length > 0) {
        container.append(existingTable);
    }
    
    // 销毁旧图表
    if (trendChart) {
        trendChart.destroy();
    }
    
    // 创建Chart.js对比图表
    const ctx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `关键词对比 - ${platform === 'google_trends' ? 'Google Trends' : platform}`,
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: '搜索热度'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '日期'
                    },
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}
