/**
 * 搜索趋势页面JavaScript
 */

let keywords = [];
let currentTaskId = null;
let statusInterval = null;

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
    
    // 停止按钮
    $('#stopBtn').on('click', stopTrendCollection);
    
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
                    
                    showMessage('趋势采集完成！', 'success');
                    loadCollectedKeywords();
                    loadHotKeywords();
                } else if (taskStatus === 'error') {
                    clearInterval(statusInterval);
                    statusInterval = null;
                    updateStatusDisplay('error', '采集失败');
                    showMessage('采集任务出错: ' + (data.error || '未知错误'), 'error');
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
        statusIndicator.removeClass('bg-blue-500 bg-green-500 bg-red-500 bg-yellow-500 animate-pulse');
        if (status === 'running') {
            statusIndicator.addClass('bg-blue-500 animate-pulse');
        } else if (status === 'completed') {
            statusIndicator.addClass('bg-green-500');
        } else if (status === 'error') {
            statusIndicator.addClass('bg-red-500');
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

function stopTrendCollection() {
    if (!currentTaskId) {
        return;
    }
    
    if (!confirm('确定要停止采集任务吗？')) {
        return;
    }
    
    // TODO: 实现停止API
    showMessage('停止功能待实现', 'info');
}

function loadHotKeywords() {
    // 降低阈值，显示更多关键词（从20%降到5%）
    $.get('/api/v1/trends/hot?min_growth_rate=5')
        .done(function(response) {
            console.log('Hot keywords response:', response);
            const container = $('#hotKeywordsList');
            container.empty();
            
            if (response.status === 'success' && response.data) {
                const hotKeywords = response.data.hot_keywords || [];
                
                if (hotKeywords.length === 0) {
                    container.html('<p class="text-gray-400 text-sm">暂无热门关键词<br><span class="text-xs">（需要更多数据或降低增长率阈值）</span></p>');
                    return;
                }
                
                hotKeywords.slice(0, 10).forEach(item => {
                    const trend = item.trend || 'stable';
                    const growthRate = item.growth_rate || 0;
                    const trendIcon = trend === 'rising' ? '📈' : trend === 'declining' ? '📉' : '➡️';
                    const html = $(`
                        <div class="flex items-center justify-between p-2 bg-gray-50 rounded mb-2">
                            <div>
                                <span class="font-medium">${item.keyword || '未知'}</span>
                                <span class="text-xs text-gray-500 ml-2">${item.platform || 'google_trends'}</span>
                            </div>
                            <div class="text-right">
                                <div class="text-sm font-semibold ${growthRate > 0 ? 'text-green-600' : growthRate < 0 ? 'text-red-600' : 'text-gray-600'}">
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

function loadCollectedKeywords() {
    $.get('/api/v1/trends/keywords')
        .done(function(response) {
            if (response.status === 'success' && response.data.keywords) {
                const keywords = response.data.keywords;
                const container = $('#collectedKeywordsList');
                container.empty();
                
                if (keywords.length === 0) {
                    container.html('<p class="text-gray-400 text-sm">暂无已采集的关键词</p>');
                    return;
                }
                
                // 更新图表关键词选择
                const chartKeyword = $('#chartKeyword');
                chartKeyword.empty().append('<option value="">选择关键词...</option>');
                keywords.forEach(kw => {
                    chartKeyword.append(`<option value="${kw}">${kw}</option>`);
                });
                
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
            }
        })
        .fail(function() {
            $('#collectedKeywordsList').html('<p class="text-red-400 text-sm">加载失败</p>');
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
    
    $.get(`/api/v1/trends?keyword=${encodeURIComponent(keyword)}&platform=${platform}`)
        .done(function(response) {
            if (response.status === 'success' && response.data.trends) {
                const trends = response.data.trends;
                if (trends.length === 0) {
                    $('#chartContainer').html('<p class="text-gray-400 text-center mt-20">暂无数据</p>');
                    return;
                }
                
                // 使用简单的图表库或Canvas绘制
                renderSimpleChart(trends, keyword);
            }
        })
        .fail(function() {
            showMessage('加载图表数据失败', 'error');
        });
}

function renderSimpleChart(trends, keyword) {
    // 简单的图表渲染（可以使用Chart.js等库）
    const container = $('#chartContainer');
    container.empty();
    
    // 提取数据
    const dates = trends.map(t => t.date).sort();
    const values = trends.map(t => parseFloat(t.value) || 0);
    
    // 创建简单的SVG图表
    const width = container.width() - 40;
    const height = 360;
    const padding = 40;
    
    const maxValue = Math.max(...values, 1);
    const minValue = Math.min(...values, 0);
    const range = maxValue - minValue || 1;
    
    let svg = `<svg width="${width}" height="${height}" class="w-full">`;
    
    // 绘制坐标轴
    svg += `<line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="#ccc" stroke-width="2"/>`;
    svg += `<line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}" stroke="#ccc" stroke-width="2"/>`;
    
    // 绘制数据点
    const points = [];
    values.forEach((value, index) => {
        const x = padding + (index / (values.length - 1 || 1)) * (width - 2 * padding);
        const y = height - padding - ((value - minValue) / range) * (height - 2 * padding);
        points.push(`${x},${y}`);
    });
    
    // 绘制折线
    if (points.length > 1) {
        svg += `<polyline points="${points.join(' ')}" fill="none" stroke="#3b82f6" stroke-width="2"/>`;
    }
    
    // 绘制数据点
    points.forEach((point, index) => {
        const [x, y] = point.split(',').map(Number);
        svg += `<circle cx="${x}" cy="${y}" r="3" fill="#3b82f6"/>`;
    });
    
    svg += `</svg>`;
    
    container.html(`
        <div class="mb-4">
            <h3 class="text-lg font-bold">${keyword} - 搜索趋势</h3>
        </div>
        ${svg}
        <div class="mt-4 text-sm text-gray-600">
            <p>数据点数: ${trends.length}</p>
            <p>最大值: ${maxValue.toFixed(2)}</p>
            <p>最小值: ${minValue.toFixed(2)}</p>
        </div>
    `);
}

function compareKeywords() {
    const selectedKeywords = keywords.length > 0 ? keywords : [];
    
    if (selectedKeywords.length < 2) {
        showMessage('请至少选择2个关键词进行对比', 'warning');
        return;
    }
    
    $.ajax({
        url: '/api/v1/trends/compare',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            keywords: selectedKeywords,
            platform: 'google_trends'
        })
    })
    .done(function(response) {
        if (response.status === 'success' && response.data.comparison) {
            const comparison = response.data.comparison;
            
            let html = `
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
            `;
            
            $('#analysisContent').html(html);
            $('#analysisCard').show();
        }
    })
    .fail(function() {
        showMessage('对比失败', 'error');
    });
}
