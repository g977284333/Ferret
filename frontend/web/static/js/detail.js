/**
 * 机会详情页面JavaScript
 */

// 从data属性获取app_id，更可靠
function getAppId() {
    // 优先从data属性获取
    const appIdEl = document.querySelector('[data-app-id]');
    if (appIdEl) {
        return appIdEl.getAttribute('data-app-id');
    }
    // 备用：从模板变量获取
    return "{{ app_id }}";
}

// 等待jQuery加载
function initDetailPage() {
    const appId = getAppId();
    if (!appId) {
        showError('无法获取App ID');
        return;
    }
    
    loadOpportunityDetail(appId);
    
    $('#exportBtn').on('click', function() {
        exportData(appId);
    });
    
    // 翻译按钮
    $('#translateBtn').on('click', translateDescription);
    $('#showOriginalBtn').on('click', showOriginalDescription);
}

// 如果jQuery已加载，立即执行；否则等待
if (typeof $ !== 'undefined') {
    $(document).ready(initDetailPage);
} else {
    // 等待jQuery加载
    if (!window.jQueryReadyCallbacks) {
        window.jQueryReadyCallbacks = [];
    }
    window.jQueryReadyCallbacks.push(function() {
        $(document).ready(initDetailPage);
    });
    
    // 备用方案：使用原生JavaScript先加载数据
    window.addEventListener('load', function() {
        setTimeout(function() {
            if (typeof $ === 'undefined') {
                loadOpportunityDetailNative();
            }
        }, 1000);
    });
}

// 原生JavaScript版本的备用函数
function loadOpportunityDetailNative() {
    const appId = getAppId();
    if (!appId) {
        console.error('无法获取App ID');
        const loadingEl = document.getElementById('loadingIndicator');
        if (loadingEl) {
            loadingEl.innerHTML = `
                <div class="text-center py-12">
                    <div class="text-red-500 text-xl mb-4">❌</div>
                    <p class="text-gray-900 font-medium mb-2">无法获取App ID</p>
                    <a href="/opportunities" class="text-blue-600 hover:text-blue-700">返回列表</a>
                </div>
            `;
        }
        return;
    }
    
    console.log('Loading opportunity (native) with app_id:', appId);
    
    fetch(`/api/v1/opportunities/${appId}`)
        .then(response => response.json())
        .then(function(response) {
            if (response.status === 'success') {
                const data = response.data;
                renderDetailNative(data);
                const loadingEl = document.getElementById('loadingIndicator');
                const contentEl = document.getElementById('contentContainer');
                if (loadingEl) loadingEl.style.display = 'none';
                if (contentEl) contentEl.style.display = 'block';
            }
        })
        .catch(function(error) {
            console.error('加载失败:', error);
            const loadingEl = document.getElementById('loadingIndicator');
            if (loadingEl) {
                loadingEl.innerHTML = `
                    <div class="text-center py-12">
                        <div class="text-red-500 text-xl mb-4">❌</div>
                        <p class="text-gray-900 font-medium mb-2">加载失败，请刷新页面重试</p>
                        <a href="/opportunities" class="text-blue-600 hover:text-blue-700">返回列表</a>
                    </div>
                `;
            }
        });
}

function renderDetailNative(data) {
    // 基本信息
    const nameEl = document.getElementById('appName');
    if (nameEl) nameEl.textContent = data.name || '-';
    
    const categoryEl = document.getElementById('category');
    if (categoryEl) categoryEl.textContent = data.category || '-';
    
    const ratingEl = document.getElementById('rating');
    if (ratingEl) ratingEl.textContent = data.rating ? data.rating.toFixed(2) : '-';
    
    const reviewCountEl = document.getElementById('reviewCount');
    if (reviewCountEl) reviewCountEl.textContent = `(${formatNumber(data.review_count || 0)} 条评论)`;
    
    const priceEl = document.getElementById('price');
    if (priceEl) priceEl.textContent = data.price === 0 || !data.price ? '免费' : `$${data.price.toFixed(2)}`;
    
    const scoreEl = document.getElementById('opportunityScore');
    if (scoreEl) scoreEl.textContent = data.opportunity_score ? (data.opportunity_score * 100).toFixed(1) + '%' : '-';
    
    const linkEl = document.getElementById('appStoreLink');
    if (linkEl && data.url) {
        linkEl.href = data.url;
    }
    
    // App图标
    if (data.artwork_url) {
        const iconEl = document.getElementById('appIcon');
        if (iconEl) {
            iconEl.src = data.artwork_url;
            iconEl.style.display = 'block';
        }
        const iconContainer = document.getElementById('appIconContainer');
        if (iconContainer) iconContainer.style.display = 'block';
    }
    
    // 开发者
    const sellerEl = document.getElementById('sellerName');
    if (sellerEl) sellerEl.textContent = data.seller_name || '-';
    
    // 发布日期
    if (data.release_date) {
        const releaseEl = document.getElementById('releaseDate');
        if (releaseEl) {
            const releaseDate = new Date(data.release_date);
            releaseEl.textContent = releaseDate.toLocaleDateString('zh-CN');
        }
    }
    
    // 当前版本
    const versionEl = document.getElementById('currentVersion');
    if (versionEl) versionEl.textContent = data.current_version || '-';
    
    if (data.current_version_date) {
        const versionDateEl = document.getElementById('versionDate');
        if (versionDateEl) {
            const versionDate = new Date(data.current_version_date);
            versionDateEl.textContent = '更新于 ' + versionDate.toLocaleDateString('zh-CN');
        }
    }
    
    // 版本评分
    if (data.current_version_rating) {
        const versionRatingEl = document.getElementById('currentVersionRating');
        if (versionRatingEl) versionRatingEl.textContent = data.current_version_rating.toFixed(2);
        
        const versionReviewsEl = document.getElementById('currentVersionReviews');
        if (versionReviewsEl) versionReviewsEl.textContent = `(${formatNumber(data.current_version_reviews || 0)} 条评论)`;
    }
    
    // 文件大小
    if (data.file_size) {
        const sizeEl = document.getElementById('fileSize');
        if (sizeEl) {
            const sizeMB = (data.file_size / 1024 / 1024).toFixed(2);
            sizeEl.textContent = sizeMB + ' MB';
        }
    }
    
    // 最低系统版本
    const osEl = document.getElementById('minimumOS');
    if (osEl) osEl.textContent = data.minimum_os_version || '-';
    
    // 内容评级
    const ratingEl2 = document.getElementById('contentRating');
    if (ratingEl2) ratingEl2.textContent = data.content_advisory_rating || '-';
    
    // 描述
    const descEl = document.getElementById('description');
    if (descEl) {
        if (data.description) {
            // 处理HTML格式的描述
            let description = data.description;
            descEl.innerHTML = description.replace(/\n/g, '<br>');
        } else {
            descEl.textContent = '暂无描述';
        }
    }
    
    // 截图
    if (data.screenshot_urls && Array.isArray(data.screenshot_urls) && data.screenshot_urls.length > 0) {
        const screenshotsEl = document.getElementById('screenshots');
        if (screenshotsEl) {
            screenshotsEl.innerHTML = '';
            data.screenshot_urls.forEach(function(url) {
                if (url) {
                    const img = document.createElement('img');
                    img.src = url;
                    img.className = 'w-full rounded-lg shadow-md cursor-pointer hover:opacity-80';
                    img.onclick = function() { window.open(url, '_blank'); };
                    const div = document.createElement('div');
                    div.appendChild(img);
                    screenshotsEl.appendChild(div);
                }
            });
        }
        const screenshotsContainer = document.getElementById('screenshotsContainer');
        if (screenshotsContainer) screenshotsContainer.style.display = 'block';
    } else {
        const screenshotsContainer = document.getElementById('screenshotsContainer');
        if (screenshotsContainer) screenshotsContainer.style.display = 'none';
    }
    
    // 数据来源时间
    if (data.created_at) {
        const timeEl = document.getElementById('dataSourceTime');
        if (timeEl) {
            const createdDate = new Date(data.created_at);
            timeEl.textContent = createdDate.toLocaleString('zh-CN');
        }
    }
}

// 原生JavaScript版本的图片查看模态框
function showImageModalNative(imageUrl) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.id = 'imageModal';
    modal.className = 'fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4';
    modal.style.display = 'flex';
    
    modal.innerHTML = `
        <div class="relative max-w-7xl max-h-full">
            <button id="closeImageModal" class="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-75 z-10">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
            <img src="${imageUrl}" alt="App Screenshot" class="max-w-full max-h-screen rounded-lg shadow-2xl">
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 点击背景关闭
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    // 点击关闭按钮
    const closeBtn = document.getElementById('closeImageModal');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.remove();
        });
    }
    
    // ESC键关闭
    function handleEscape(e) {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', handleEscape);
        }
    }
    document.addEventListener('keydown', handleEscape);
}

function loadOpportunityDetail(appId) {
    if (!appId) {
        appId = getAppId();
    }
    
    if (!appId) {
        showError('无法获取App ID');
        return;
    }
    
    console.log('Loading opportunity with app_id:', appId);
    
    $.get(`/api/v1/opportunities/${appId}`)
        .done(function(response) {
            if (response.status === 'success') {
                const data = response.data;
                renderDetail(data);
                $('#loadingIndicator').hide();
                $('#contentContainer').show();
            } else {
                showError('加载失败: ' + (response.message || '未知错误'));
            }
        })
        .fail(function(xhr) {
            console.error('API请求失败:', xhr);
            if (xhr.status === 404) {
                showError('机会不存在 (App ID: ' + appId + ')');
            } else {
                showError('加载失败，请刷新页面重试 (状态码: ' + xhr.status + ')');
            }
        });
}

function renderDetail(data) {
    // 基本信息
    $('#appName').text(data.name || '-');
    $('#category').text(data.category || '-');
    $('#rating').text(data.rating ? data.rating.toFixed(2) : '-');
    $('#reviewCount').text(`(${formatNumber(data.review_count || 0)} 条评论)`);
    $('#price').text(data.price === 0 || !data.price ? '免费' : `$${data.price.toFixed(2)}`);
    $('#opportunityScore').text(data.opportunity_score ? (data.opportunity_score * 100).toFixed(1) + '%' : '-');
    
    if (data.url) {
        $('#appStoreLink').attr('href', data.url);
    }
    
    // App图标
    if (data.artwork_url) {
        $('#appIcon').attr('src', data.artwork_url).show();
        $('#appIconContainer').show();
    }
    
    // 开发者
    $('#sellerName').text(data.seller_name || '-');
    
    // 发布日期
    if (data.release_date) {
        const releaseDate = new Date(data.release_date);
        $('#releaseDate').text(releaseDate.toLocaleDateString('zh-CN'));
    }
    
    // 当前版本
    $('#currentVersion').text(data.current_version || '-');
    if (data.current_version_date) {
        const versionDate = new Date(data.current_version_date);
        $('#versionDate').text('更新于 ' + versionDate.toLocaleDateString('zh-CN'));
    }
    
    // 版本评分
    if (data.current_version_rating) {
        $('#currentVersionRating').text(data.current_version_rating.toFixed(2));
        $('#currentVersionReviews').text(`(${formatNumber(data.current_version_reviews || 0)} 条评论)`);
    }
    
    // 文件大小
    if (data.file_size) {
        const sizeMB = (data.file_size / 1024 / 1024).toFixed(2);
        $('#fileSize').text(sizeMB + ' MB');
    }
    
    // 最低系统版本
    $('#minimumOS').text(data.minimum_os_version || '-');
    
    // 内容评级
    $('#contentRating').text(data.content_advisory_rating || '-');
    
    // 描述
    if (data.description) {
        let description = String(data.description);
        // 保存原始描述（用于翻译）
        originalDescription = description;
        // 处理换行符
        $('#description').html(description.replace(/\n/g, '<br>'));
    } else {
        $('#description').text('暂无描述');
        originalDescription = '';
    }
    
    // 截图
    const screenshotUrls = data.screenshot_urls;
    if (screenshotUrls && Array.isArray(screenshotUrls) && screenshotUrls.length > 0) {
        const screenshotsContainer = $('#screenshots');
        screenshotsContainer.empty();
        screenshotUrls.forEach(function(url) {
            if (url && typeof url === 'string') {
                const img = $('<img>')
                    .attr('src', url)
                    .attr('alt', 'App Screenshot')
                    .addClass('w-full rounded-lg shadow-lg cursor-pointer hover:shadow-xl transition-all duration-300 hover:scale-105')
                    .css('max-height', '400px')
                    .css('object-fit', 'contain');
                img.on('click', function() {
                    // 点击查看大图
                    showImageModal(url);
                });
                const div = $('<div>').addClass('relative group');
                div.append(img);
                screenshotsContainer.append(div);
            }
        });
        if (screenshotsContainer.children().length > 0) {
            $('#screenshotsContainer').show();
        } else {
            $('#screenshotsContainer').hide();
        }
    } else {
        $('#screenshotsContainer').hide();
    }
    
    
    // 数据来源时间
    if (data.created_at) {
        const createdDate = new Date(data.created_at);
        $('#dataSourceTime').text(createdDate.toLocaleString('zh-CN'));
    }
    
    // 总分
    const totalScore = data.opportunity_score || 0;
    $('#totalScore').text((totalScore * 100).toFixed(1) + '%');
    $('#totalScoreBar').css('width', (totalScore * 100) + '%');
    
    // 评分详情
    const scoringDetails = data.scoring_details || {};
    const weights = {
        market_size: { name: '市场规模', weight: 0.3 },
        competition: { name: '竞争程度', weight: 0.25 },
        user_satisfaction: { name: '用户满意度', weight: 0.2 },
        growth_trend: { name: '增长趋势', weight: 0.15 },
        monetization: { name: '变现潜力', weight: 0.1 }
    };
    
    const detailsContainer = $('#scoringDetails');
    detailsContainer.empty();
    
    Object.keys(weights).forEach(key => {
        const score = scoringDetails[key] || 0;
        const weight = weights[key].weight;
        const weightedScore = score * weight;
        
        const detailItem = $(`
            <div>
                <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-medium text-gray-700">
                        ${weights[key].name} (${(weight * 100).toFixed(0)}%)
                    </span>
                    <span class="text-sm font-semibold text-gray-900">${(score * 100).toFixed(1)}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                    <div class="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-300" 
                         style="width: ${score * 100}%"></div>
                </div>
                <div class="text-xs text-gray-500 mt-1">
                    加权贡献: ${(weightedScore * 100).toFixed(1)}%
                </div>
            </div>
        `);
        detailsContainer.append(detailItem);
    });
}

function exportData(appId) {
    if (!appId) {
        appId = getAppId();
    }
    if (!appId) {
        showMessage('无法获取App ID', 'error');
        return;
    }
    
    // 导出当前机会的数据
    const url = `/api/v1/opportunities/export?app_id=${appId}&format=json`;
    window.open(url, '_blank');
    showMessage('正在导出数据...', 'info');
}

function showError(message) {
    $('#loadingIndicator').html(`
        <div class="text-center py-12">
            <div class="text-red-500 text-xl mb-4">❌</div>
            <p class="text-gray-900 font-medium mb-2">${message}</p>
            <a href="/opportunities" class="text-blue-600 hover:text-blue-700">返回列表</a>
        </div>
    `);
}

// 翻译描述
let originalDescription = '';
let translatedDescription = '';

function translateDescription() {
    const descriptionEl = $('#description');
    let descriptionText = descriptionEl.text().trim();
    
    // 如果没有文本，尝试从HTML获取
    if (!descriptionText || descriptionText === '暂无描述' || descriptionText === '-') {
        descriptionText = descriptionEl.html().replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '').trim();
    }
    
    if (!descriptionText || descriptionText === '暂无描述' || descriptionText === '-') {
        showMessage('没有可翻译的内容', 'warning');
        return;
    }
    
    // 保存原文
    originalDescription = descriptionText;
    
    // 显示加载状态
    const btn = $('#translateBtn');
    const originalText = btn.text();
    btn.prop('disabled', true).text('翻译中...');
    
    // 调用翻译API
    $.ajax({
        url: '/api/v1/translate/text',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            text: descriptionText,
            target_lang: 'zh-CN'
        }),
        success: function(response) {
            if (response.status === 'success') {
                translatedDescription = response.data.translated_text;
                $('#translatedText').html(translatedDescription.replace(/\n/g, '<br>'));
                $('#translatedDescription').show();
                $('#description').hide();
                showMessage('翻译完成', 'success');
            } else {
                showMessage('翻译失败: ' + (response.message || '未知错误'), 'error');
            }
        },
        error: function(xhr) {
            console.error('翻译失败:', xhr);
            if (xhr.status === 503) {
                showMessage('翻译功能未安装，请联系管理员', 'error');
            } else {
                showMessage('翻译失败，请稍后重试', 'error');
            }
        },
        complete: function() {
            btn.prop('disabled', false).text(originalText);
        }
    });
}

function showOriginalDescription() {
    $('#translatedDescription').hide();
    $('#description').show();
}

// 图片查看模态框
function showImageModal(imageUrl) {
    // 创建模态框
    const modal = $(`
        <div id="imageModal" class="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4" style="display: flex;">
            <div class="relative max-w-7xl max-h-full">
                <button id="closeImageModal" class="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-75 z-10">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
                <img src="${imageUrl}" alt="App Screenshot" class="max-w-full max-h-screen rounded-lg shadow-2xl">
            </div>
        </div>
    `);
    
    $('body').append(modal);
    
    // 点击背景关闭
    modal.on('click', function(e) {
        if (e.target === modal[0]) {
            modal.remove();
        }
    });
    
    // 点击关闭按钮
    $('#closeImageModal').on('click', function() {
        modal.remove();
    });
    
    // ESC键关闭
    $(document).on('keydown.imageModal', function(e) {
        if (e.key === 'Escape') {
            modal.remove();
            $(document).off('keydown.imageModal');
        }
    });
}
