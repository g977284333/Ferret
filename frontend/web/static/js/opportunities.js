/**
 * 机会列表页面JavaScript
 */

let currentPage = 1;
let perPage = 20;
let totalPages = 1;
let filters = {
    search: '',
    category: '',
    min_score: null,
    max_score: null,
    sort_by: 'opportunity_score',
    order: 'desc'
};

// 等待jQuery加载
function initOpportunitiesPage() {
    // 检查URL参数，看是否从采集页面跳转过来
    const urlParams = new URLSearchParams(window.location.search);
    const fromScrape = urlParams.get('from_scrape');
    
    // 加载数据
    loadOpportunities();
    
    // 如果从采集页面跳转过来，显示提示
    if (fromScrape === 'true') {
        showMessage('采集完成！以下是新发现的机会', 'success');
        // 清除URL参数
        window.history.replaceState({}, '', '/opportunities');
    }
    
    // 搜索
    $('#searchInput').on('keypress', function(e) {
        if (e.which === 13) {
            applyFilters();
        }
    });
    
    // 应用筛选
    $('#applyFiltersBtn').on('click', applyFilters);
    
    // 重置筛选
    $('#resetFiltersBtn').on('click', resetFilters);
    
    // 排序
    $('#sortBy').on('change', function() {
        filters.sort_by = $(this).val();
        currentPage = 1;
        loadOpportunities();
    });
    
    // 导出
    $('#exportBtn').on('click', exportCSV);
    
    // 全选
    $('#selectAll').on('change', function() {
        const checked = $(this).prop('checked');
        $('.row-checkbox').prop('checked', checked);
    });
}

// 如果jQuery已加载，立即执行；否则等待
if (typeof $ !== 'undefined') {
    $(document).ready(initOpportunitiesPage);
} else {
    // 等待jQuery加载
    if (!window.jQueryReadyCallbacks) {
        window.jQueryReadyCallbacks = [];
    }
    window.jQueryReadyCallbacks.push(function() {
        $(document).ready(initOpportunitiesPage);
    });
    
    // 备用方案：使用原生JavaScript先加载数据
    window.addEventListener('load', function() {
        // 如果jQuery还没加载，使用原生JavaScript加载数据
        setTimeout(function() {
            if (typeof $ === 'undefined') {
                loadOpportunitiesNative();
            }
        }, 1000);
    });
}

// 原生JavaScript版本的数据加载（备用）
function loadOpportunitiesNative() {
    const params = new URLSearchParams({
        page: currentPage,
        per_page: perPage,
        sort_by: filters.sort_by,
        order: filters.order
    });
    
    fetch('/api/v1/opportunities?' + params.toString())
        .then(response => response.json())
        .then(function(response) {
            if (response.status === 'success') {
                const data = response.data;
                renderOpportunitiesNative(data.opportunities);
                updatePaginationNative(data.pagination);
            }
        })
        .catch(function(error) {
            console.error('加载失败:', error);
            const tbody = document.getElementById('opportunitiesTableBody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-red-500">加载失败，请刷新页面</td></tr>';
            }
        });
}

function renderOpportunitiesNative(opportunities) {
    const tbody = document.getElementById('opportunitiesTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (opportunities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-500">暂无机会数据</td></tr>';
        return;
    }
    
    opportunities.forEach(function(opp) {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <input type="checkbox" class="row-checkbox rounded" value="${opp.app_id}">
            </td>
            <td class="px-6 py-4">
                <div class="font-medium text-gray-900">${opp.name || '-'}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="text-lg font-bold text-blue-600">${(opp.opportunity_score * 100).toFixed(1)}%</div>
                    <div class="ml-2 w-24 bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-600 h-2 rounded-full" style="width: ${opp.opportunity_score * 100}%"></div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <span class="text-gray-900 font-medium">${opp.rating ? opp.rating.toFixed(2) : '-'}</span>
                    ${opp.rating ? '<span class="ml-1 text-yellow-500">⭐</span>' : ''}
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-gray-600">
                ${formatNumber(opp.review_count || 0)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                    ${opp.category || '-'}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <a href="/opportunities/${opp.app_id}" class="text-blue-600 hover:text-blue-900">查看详情</a>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updatePaginationNative(pagination) {
    totalPages = pagination.pages;
    const total = pagination.total;
    
    const totalCountEl = document.getElementById('totalCount');
    if (totalCountEl) {
        totalCountEl.textContent = `共 ${total} 个机会`;
    }
    
    const pageInfoEl = document.getElementById('pageInfo');
    if (pageInfoEl) {
        pageInfoEl.textContent = `第 ${pagination.page} 页，共 ${totalPages} 页`;
    }
}

function applyFilters() {
    filters.search = $('#searchInput').val();
    filters.category = $('#categoryFilter').val();
    filters.min_score = $('#minScore').val() ? parseFloat($('#minScore').val()) : null;
    filters.max_score = $('#maxScore').val() ? parseFloat($('#maxScore').val()) : null;
    currentPage = 1;
    loadOpportunities();
}

function resetFilters() {
    $('#searchInput').val('');
    $('#categoryFilter').val('');
    $('#minScore').val('');
    $('#maxScore').val('');
    $('#sortBy').val('opportunity_score');
    filters = {
        search: '',
        category: '',
        min_score: null,
        max_score: null,
        sort_by: 'opportunity_score',
        order: 'desc'
    };
    currentPage = 1;
    loadOpportunities();
}

function loadOpportunities() {
    // 构建查询参数
    const params = new URLSearchParams({
        page: currentPage,
        per_page: perPage,
        sort_by: filters.sort_by,
        order: filters.order
    });
    
    if (filters.search) params.append('search', filters.search);
    if (filters.category) params.append('category', filters.category);
    if (filters.min_score !== null) params.append('min_score', filters.min_score);
    if (filters.max_score !== null) params.append('max_score', filters.max_score);
    
    $.get(`/api/v1/opportunities?${params.toString()}`)
        .done(function(response) {
            if (response.status === 'success') {
                const data = response.data;
                renderOpportunities(data.opportunities);
                updatePagination(data.pagination);
                updateCategories(data.opportunities);
            }
        })
        .fail(function() {
            $('#opportunitiesTableBody').html(`
                <tr>
                    <td colspan="7" class="px-6 py-8 text-center text-red-500">
                        加载失败，请刷新页面重试
                    </td>
                </tr>
            `);
        });
}

function renderOpportunities(opportunities) {
    const tbody = $('#opportunitiesTableBody');
    tbody.empty();
    
    if (opportunities.length === 0) {
        tbody.html(`
            <tr>
                <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                    暂无机会数据
                </td>
            </tr>
        `);
        return;
    }
    
    opportunities.forEach(opp => {
        const row = $(`
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <input type="checkbox" class="row-checkbox rounded" value="${opp.app_id}">
                </td>
                <td class="px-6 py-4">
                    <div class="font-medium text-gray-900">${opp.name || '-'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="text-lg font-bold text-blue-600">${(opp.opportunity_score * 100).toFixed(1)}%</div>
                        <div class="ml-2 w-24 bg-gray-200 rounded-full h-2">
                            <div class="bg-blue-600 h-2 rounded-full" style="width: ${opp.opportunity_score * 100}%"></div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <span class="text-gray-900 font-medium">${opp.rating ? opp.rating.toFixed(2) : '-'}</span>
                        ${opp.rating ? `<span class="ml-1 text-yellow-500">⭐</span>` : ''}
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-600">
                    ${formatNumber(opp.review_count || 0)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                        ${opp.category || '-'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <a href="/opportunities/${opp.app_id}" class="text-blue-600 hover:text-blue-900">查看详情</a>
                </td>
            </tr>
        `);
        tbody.append(row);
    });
}

function updatePagination(pagination) {
    totalPages = pagination.pages;
    const total = pagination.total;
    
    $('#totalCount').text(`共 ${total} 个机会`);
    $('#pageInfo').text(`第 ${pagination.page} 页，共 ${totalPages} 页`);
    
    const paginationDiv = $('#pagination');
    paginationDiv.empty();
    
    // 上一页
    paginationDiv.append(`
        <button ${currentPage <= 1 ? 'disabled' : ''} 
                class="px-3 py-2 border border-gray-300 rounded-lg ${currentPage <= 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'}"
                onclick="goToPage(${currentPage - 1})">
            上一页
        </button>
    `);
    
    // 页码
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        paginationDiv.append(`<button class="px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 hover:bg-gray-50" onclick="goToPage(1)">1</button>`);
        if (startPage > 2) {
            paginationDiv.append(`<span class="px-3 py-2 text-gray-500">...</span>`);
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationDiv.append(`
            <button class="px-3 py-2 border rounded-lg ${i === currentPage ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'}"
                    onclick="goToPage(${i})">
                ${i}
            </button>
        `);
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationDiv.append(`<span class="px-3 py-2 text-gray-500">...</span>`);
        }
        paginationDiv.append(`<button class="px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 hover:bg-gray-50" onclick="goToPage(${totalPages})">${totalPages}</button>`);
    }
    
    // 下一页
    paginationDiv.append(`
        <button ${currentPage >= totalPages ? 'disabled' : ''} 
                class="px-3 py-2 border border-gray-300 rounded-lg ${currentPage >= totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'}"
                onclick="goToPage(${currentPage + 1})">
            下一页
        </button>
    `);
}

function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadOpportunities();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateCategories(opportunities) {
    // 提取所有分类
    const categories = [...new Set(opportunities.map(opp => opp.category).filter(Boolean))];
    const categorySelect = $('#categoryFilter');
    
    // 如果当前没有分类选项，添加它们
    if (categorySelect.find('option').length <= 1) {
        categories.forEach(cat => {
            if (!categorySelect.find(`option[value="${cat}"]`).length) {
                categorySelect.append(`<option value="${cat}">${cat}</option>`);
            }
        });
    }
}

function exportCSV() {
    // 构建查询参数（获取所有数据）
    const params = new URLSearchParams({
        per_page: 10000, // 获取所有数据
        sort_by: filters.sort_by,
        order: filters.order
    });
    
    if (filters.search) params.append('search', filters.search);
    if (filters.category) params.append('category', filters.category);
    if (filters.min_score !== null) params.append('min_score', filters.min_score);
    if (filters.max_score !== null) params.append('max_score', filters.max_score);
    
    // 创建下载链接
    const url = `/api/v1/opportunities/export?${params.toString()}&format=csv`;
    window.open(url, '_blank');
    showMessage('正在导出CSV文件...', 'info');
}
