/**
 * 首页JavaScript
 */

let keywords = [];

// 等待jQuery加载
function initIndexPage() {
    // 加载统计信息
    loadStats();
    
    // 加载最近机会
    loadRecentOpportunities();
    
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
    $('#quickStartForm').on('submit', function(e) {
        e.preventDefault();
        startScrape();
    });
}

// 如果jQuery已加载，立即执行；否则等待
if (typeof $ !== 'undefined') {
    $(document).ready(initIndexPage);
} else {
    // 等待jQuery加载
    if (!window.jQueryReadyCallbacks) {
        window.jQueryReadyCallbacks = [];
    }
    window.jQueryReadyCallbacks.push(function() {
        $(document).ready(initIndexPage);
    });
    
    // 备用方案：使用原生JavaScript先加载数据
    window.addEventListener('load', function() {
        setTimeout(function() {
            if (typeof $ === 'undefined') {
                loadStatsNative();
                loadRecentOpportunitiesNative();
            }
        }, 1000);
    });
}

// 原生JavaScript版本的备用函数
function loadStatsNative() {
    fetch('/api/v1/stats')
        .then(response => response.json())
        .then(function(response) {
            if (response.status === 'success') {
                const data = response.data;
                const totalEl = document.getElementById('totalOpportunities');
                const todayEl = document.getElementById('todayCollected');
                const activeEl = document.getElementById('activeTasks');
                if (totalEl) totalEl.textContent = data.total_opportunities || 0;
                if (todayEl) todayEl.textContent = data.today_collected || 0;
                if (activeEl) activeEl.textContent = data.active_tasks || 0;
            }
        })
        .catch(function(error) {
            console.error('加载统计信息失败:', error);
        });
}

function loadRecentOpportunitiesNative() {
    fetch('/api/v1/opportunities?per_page=5&sort_by=opportunity_score&order=desc')
        .then(response => response.json())
        .then(function(response) {
            if (response.status === 'success') {
                const opportunities = response.data.opportunities;
                renderRecentOpportunitiesNative(opportunities);
            }
        })
        .catch(function(error) {
            console.error('加载最近机会失败:', error);
            const container = document.getElementById('recentOpportunities');
            if (container) {
                container.innerHTML = '<p class="text-gray-500 text-center py-8">加载失败</p>';
            }
        });
}

function renderRecentOpportunitiesNative(opportunities) {
    const container = document.getElementById('recentOpportunities');
    if (!container) return;
    
    if (opportunities.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-8">暂无机会，开始采集吧！</p>';
        return;
    }
    
    container.innerHTML = '';
    
    opportunities.forEach(function(opp) {
        const item = document.createElement('div');
        item.className = 'flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50';
        item.innerHTML = `
            <div class="flex-1">
                <h3 class="font-semibold text-gray-900">${opp.name}</h3>
                <div class="flex items-center gap-4 mt-2 text-sm text-gray-600">
                    <span>评分: ${opp.rating ? opp.rating.toFixed(2) : '-'}</span>
                    <span>评论: ${formatNumber(opp.review_count || 0)}</span>
                    <span>分类: ${opp.category || '-'}</span>
                </div>
            </div>
            <div class="ml-4 text-right">
                <div class="text-2xl font-bold text-blue-600">${(opp.opportunity_score * 100).toFixed(1)}%</div>
                <div class="text-xs text-gray-500">机会分数</div>
            </div>
            <a href="/opportunities/${opp.app_id}" class="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                查看
            </a>
        `;
        container.appendChild(item);
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
    
    keywords.forEach(keyword => {
        const tag = $(`
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                ${keyword}
                <button type="button" class="ml-2 text-blue-600 hover:text-blue-800" onclick="removeKeyword('${keyword}')">
                    ×
                </button>
            </span>
        `);
        container.append(tag);
    });
}

function loadStats() {
    $.get('/api/v1/stats')
        .done(function(response) {
            if (response.status === 'success') {
                const data = response.data;
                $('#totalOpportunities').text(data.total_opportunities || 0);
                $('#todayCollected').text(data.today_collected || 0);
                $('#activeTasks').text(data.active_tasks || 0);
            }
        })
        .fail(function() {
            console.error('Failed to load stats');
        });
}

function loadRecentOpportunities() {
    $.get('/api/v1/opportunities?per_page=5&sort_by=opportunity_score&order=desc')
        .done(function(response) {
            if (response.status === 'success') {
                const opportunities = response.data.opportunities;
                renderRecentOpportunities(opportunities);
            }
        })
        .fail(function() {
            $('#recentOpportunities').html('<p class="text-gray-500 text-center py-8">加载失败</p>');
        });
}

function renderRecentOpportunities(opportunities) {
    const container = $('#recentOpportunities');
    
    if (opportunities.length === 0) {
        container.html('<p class="text-gray-500 text-center py-8">暂无机会，开始采集吧！</p>');
        return;
    }
    
    container.empty();
    
    opportunities.forEach(opp => {
        const item = $(`
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div class="flex-1">
                    <h3 class="font-semibold text-gray-900">${opp.name}</h3>
                    <div class="flex items-center gap-4 mt-2 text-sm text-gray-600">
                        <span>评分: ${opp.rating?.toFixed(2) || '-'}</span>
                        <span>评论: ${formatNumber(opp.review_count || 0)}</span>
                        <span>分类: ${opp.category || '-'}</span>
                    </div>
                </div>
                <div class="ml-4 text-right">
                    <div class="text-2xl font-bold text-blue-600">${(opp.opportunity_score * 100).toFixed(1)}%</div>
                    <div class="text-xs text-gray-500">机会分数</div>
                </div>
                <a href="/opportunities/${opp.app_id}" class="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                    查看
                </a>
            </div>
        `);
        container.append(item);
    });
}

function startScrape() {
    if (keywords.length === 0) {
        showMessage('请至少添加一个关键词', 'warning');
        return;
    }
    
    const dataSource = $('#dataSource').val();
    const limitPerKeyword = parseInt($('#limitPerKeyword').val());
    
    $('#startScrapeBtn').prop('disabled', true).text('启动中...');
    
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
            showMessage('采集任务已启动', 'success');
            // 跳转到采集页面，传递关键词
            const keywordsParam = keywords.map(k => encodeURIComponent(k)).join(',');
            window.location.href = `/scrape?task_id=${response.task_id}&keywords=${keywordsParam}`;
        }
    })
    .fail(function() {
        showMessage('启动采集失败', 'error');
        $('#startScrapeBtn').prop('disabled', false).text('开始采集');
    });
}
