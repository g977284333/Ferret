/**
 * 配置页面JavaScript
 */

let originalConfig = null;

// 等待jQuery加载
function initConfigPage() {
    loadConfig();
    
    $('#saveBtn').on('click', saveConfig);
    $('#resetBtn').on('click', resetConfig);
    $('#testBtn').on('click', testConfig);
}

// 如果jQuery已加载，立即执行；否则等待
if (typeof $ !== 'undefined') {
    $(document).ready(initConfigPage);
} else {
    // 等待jQuery加载
    if (!window.jQueryReadyCallbacks) {
        window.jQueryReadyCallbacks = [];
    }
    window.jQueryReadyCallbacks.push(function() {
        $(document).ready(initConfigPage);
    });
}

function loadConfig() {
    $.get('/api/v1/config')
        .done(function(response) {
            if (response.status === 'success') {
                originalConfig = response.data;
                renderConfig(response.data);
            }
        })
        .fail(function() {
            showMessage('加载配置失败', 'error');
        });
}

function renderConfig(config) {
    // 渲染评分权重
    renderWeights(config.scoring?.weights || {});
    
    // 渲染筛选阈值
    renderThresholds(config.scoring?.thresholds || {});
    
    // 渲染数据源配置
    renderDataSources(config.data_sources || {});
}

function renderWeights(weights) {
    const container = $('#weightsContainer');
    container.empty();
    
    const weightConfigs = [
        { key: 'market_size', name: '市场规模', default: 0.3 },
        { key: 'competition', name: '竞争程度', default: 0.25 },
        { key: 'user_satisfaction', name: '用户满意度', default: 0.2 },
        { key: 'growth_trend', name: '增长趋势', default: 0.15 },
        { key: 'monetization', name: '变现潜力', default: 0.1 }
    ];
    
    weightConfigs.forEach(wc => {
        const value = weights[wc.key] || wc.default;
        const item = $(`
            <div>
                <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-medium text-gray-700">${wc.name}</span>
                    <span class="text-sm font-semibold text-gray-900 weight-value" data-key="${wc.key}">${(value * 100).toFixed(0)}%</span>
                </div>
                <input type="range" 
                       class="weight-slider w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" 
                       data-key="${wc.key}"
                       min="0" 
                       max="100" 
                       step="5"
                       value="${value * 100}">
            </div>
        `);
        container.append(item);
    });
    
    // 绑定滑块事件
    $('.weight-slider').on('input', function() {
        const value = parseInt($(this).val());
        const key = $(this).data('key');
        $(`.weight-value[data-key="${key}"]`).text(value + '%');
        updateTotalWeight();
    });
    
    updateTotalWeight();
}

function updateTotalWeight() {
    let total = 0;
    $('.weight-slider').each(function() {
        total += parseInt($(this).val());
    });
    
    const totalPercent = total;
    $('#totalWeight').text(totalPercent + '%');
    
    const statusDiv = $('#weightStatus');
    if (totalPercent === 100) {
        statusDiv.html('<span class="text-green-600">✓ 权重总和正确</span>');
    } else if (totalPercent < 100) {
        statusDiv.html(`<span class="text-yellow-600">⚠ 权重总和不足，还差 ${100 - totalPercent}%</span>`);
    } else {
        statusDiv.html(`<span class="text-red-600">✗ 权重总和超出，超出 ${totalPercent - 100}%</span>`);
    }
}

function renderThresholds(thresholds) {
    $('#minScore').val(thresholds.min_score || 0.6);
    $('#minReviews').val(thresholds.min_reviews || 10);
    $('#maxCompetitors').val(thresholds.max_competitors || 20);
}

function renderDataSources(dataSources) {
    const container = $('#dataSourcesContainer');
    container.empty();
    
    Object.keys(dataSources).forEach(key => {
        const source = dataSources[key];
        const enabled = source.enabled || false;
        
        const item = $(`
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                    <h3 class="font-medium text-gray-900">${key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}</h3>
                    <p class="text-sm text-gray-600 mt-1">${getDataSourceDescription(key)}</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" class="sr-only peer" data-source="${key}" ${enabled ? 'checked' : ''}>
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
            </div>
        `);
        container.append(item);
    });
}

function getDataSourceDescription(key) {
    const descriptions = {
        'app_store': 'App Store数据源，支持搜索和分类浏览',
        'product_hunt': 'Product Hunt数据源，发现新产品',
        'google_play': 'Google Play数据源（待实现）'
    };
    return descriptions[key] || '数据源配置';
}

function saveConfig() {
    // 收集权重配置
    const weights = {};
    $('.weight-slider').each(function() {
        const key = $(this).data('key');
        const value = parseInt($(this).val()) / 100;
        weights[key] = value;
    });
    
    // 检查权重总和
    const total = Object.values(weights).reduce((sum, val) => sum + val, 0);
    if (Math.abs(total - 1.0) > 0.01) {
        showMessage('权重总和必须等于100%，当前为' + (total * 100).toFixed(0) + '%', 'warning');
        return;
    }
    
    // 收集阈值配置
    const thresholds = {
        min_score: parseFloat($('#minScore').val()) || 0.6,
        min_reviews: parseInt($('#minReviews').val()) || 10,
        max_competitors: parseInt($('#maxCompetitors').val()) || 20
    };
    
    // 收集数据源配置
    const dataSources = {};
    $('input[data-source]').each(function() {
        const key = $(this).data('source');
        dataSources[key] = {
            enabled: $(this).prop('checked')
        };
    });
    
    // 构建配置对象
    const config = {
        scoring: {
            weights: weights,
            thresholds: thresholds
        },
        data_sources: dataSources
    };
    
    // 保存配置
    $.ajax({
        url: '/api/v1/config',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(config)
    })
    .done(function(response) {
        if (response.status === 'success') {
            showMessage('配置已保存', 'success');
            originalConfig = config;
        }
    })
    .fail(function() {
        showMessage('保存配置失败', 'error');
    });
}

function resetConfig() {
    if (!confirm('确定要重置配置吗？将恢复到上次保存的状态。')) {
        return;
    }
    
    if (originalConfig) {
        renderConfig(originalConfig);
        showMessage('配置已重置', 'info');
    } else {
        loadConfig();
    }
}

function testConfig() {
    showMessage('测试配置功能待实现', 'info');
    // TODO: 实现配置测试功能
}
