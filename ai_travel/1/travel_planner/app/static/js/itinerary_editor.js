/**
 * AI Travel Planner - Itinerary Editor JavaScript
 * 
 * Implements:
 * - Drag-and-drop sorting with Sortable.js
 * - Dynamic day panel addition
 * - Activity card add/remove
 * - Real-time cost calculation
 * - Form data serialization
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initSortable();
    initCostCalculation();
});

// Initialize Sortable.js for activity lists
function initSortable() {
    const activityLists = document.querySelectorAll('.activity-list');
    activityLists.forEach(list => {
        new Sortable(list, {
            animation: 150,
            handle: '.grip-handle',
            ghostClass: 'sortable-ghost',
            onEnd: function(evt) {
                // Update cost when order changes
                updateCostDisplay();
            }
        });
    });
}

// Add new activity card to a specific day
function addActivity(dayIndex) {
    const dayPanel = document.querySelector(`[data-day-index="${dayIndex}"]`).closest('.accordion-item');
    const activityList = dayPanel.querySelector('.activity-list');
    
    const newActivity = document.createElement('div');
    newActivity.className = 'activity-card mb-3';
    newActivity.setAttribute('data-activity-id', 'new_' + Date.now());
    newActivity.innerHTML = `
        <div class="card">
            <div class="card-body">
                <div class="row">
                    <div class="col-1 d-flex align-items-center">
                        <i class="fas fa-grip grip-handle text-muted"></i>
                    </div>
                    <div class="col-2">
                        <select class="form-select activity-type">
                            <option value="景点">景点</option>
                            <option value="美食">美食</option>
                            <option value="住宿">住宿</option>
                            <option value="交通">交通</option>
                            <option value="购物">购物</option>
                        </select>
                    </div>
                    <div class="col-4">
                        <input type="text" class="form-control activity-name" placeholder="活动名称">
                    </div>
                    <div class="col-2">
                        <input type="text" class="form-control activity-duration" placeholder="时长">
                    </div>
                    <div class="col-2">
                        <input type="number" class="form-control activity-cost" placeholder="费用" onchange="updateCostDisplay()">
                    </div>
                    <div class="col-1 d-flex align-items-center">
                        <button class="btn btn-sm btn-outline-danger" onclick="removeActivity(this)">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-11 offset-1">
                        <input type="text" class="form-control form-control-sm activity-tips"
                               placeholder="小贴士（可选）">
                    </div>
                </div>
            </div>
        </div>
    `;
    
    activityList.appendChild(newActivity);
    
    // Make the new activity sortable
    new Sortable(activityList, {
        animation: 150,
        handle: '.grip-handle',
        ghostClass: 'sortable-ghost'
    });
    
    // Focus on the new activity name input
    const nameInput = newActivity.querySelector('.activity-name');
    nameInput.focus();
}

// Remove activity card
function removeActivity(button) {
    const card = button.closest('.activity-card');
    const activityList = card.closest('.activity-list');
    
    // Only remove if there are more than 1 activity
    if (activityList.querySelectorAll('.activity-card').length > 1) {
        card.remove();
        updateCostDisplay();
    } else {
        alert('每天至少需要一个活动');
    }
}

// Add new day panel
function addDay() {
    const accordion = document.getElementById('daysAccordion');
    const dayCount = accordion.querySelectorAll('.accordion-item').length + 1;
    
    const newDay = document.createElement('div');
    newDay.className = 'accordion-item';
    newDay.setAttribute('data-day-id', 'new_' + Date.now());
    newDay.innerHTML = `
        <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" 
                    data-bs-toggle="collapse" data-bs-target="#day${dayCount}">
                <i class="fas fa-calendar-day me-2 text-primary"></i>
                第 ${dayCount} 天
                <span class="badge bg-secondary ms-2">待设置</span>
            </button>
        </h2>
        <div id="day${dayCount}" class="accordion-collapse collapse" data-bs-parent="#daysAccordion">
            <div class="accordion-body">
                <div class="mb-3">
                    <label class="form-label">当天主题</label>
                    <input type="text" class="form-control day-theme" placeholder="例如：历史文化探索日">
                </div>
                
                <div class="activity-list" data-day-index="${dayCount - 1}">
                    <div class="activity-card mb-3" data-activity-id="new">
                        <div class="card">
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-1 d-flex align-items-center">
                                        <i class="fas fa-grip grip-handle text-muted"></i>
                                    </div>
                                    <div class="col-2">
                                        <select class="form-select activity-type">
                                            <option value="景点">景点</option>
                                            <option value="美食">美食</option>
                                            <option value="住宿">住宿</option>
                                            <option value="交通">交通</option>
                                            <option value="购物">购物</option>
                                        </select>
                                    </div>
                                    <div class="col-4">
                                        <input type="text" class="form-control activity-name" placeholder="活动名称">
                                    </div>
                                    <div class="col-2">
                                        <input type="text" class="form-control activity-duration" placeholder="时长">
                                    </div>
                                    <div class="col-2">
                                        <input type="number" class="form-control activity-cost" placeholder="费用">
                                    </div>
                                    <div class="col-1 d-flex align-items-center">
                                        <button class="btn btn-sm btn-outline-danger" onclick="removeActivity(this)">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="row mt-2">
                                    <div class="col-11 offset-1">
                                        <input type="text" class="form-control form-control-sm activity-tips"
                                               placeholder="小贴士（可选）">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <button class="btn btn-outline-primary btn-sm" onclick="addActivity(${dayCount - 1})">
                    <i class="fas fa-plus me-1"></i>添加活动
                </button>
            </div>
        </div>
    `;
    
    accordion.appendChild(newDay);
    
    // Initialize Sortable for the new activity list
    const newActivityList = newDay.querySelector('.activity-list');
    new Sortable(newActivityList, {
        animation: 150,
        handle: '.grip-handle',
        ghostClass: 'sortable-ghost'
    });
    
    // Open the new accordion
    const collapseButton = new Bootstrap.Collapse(newDay.querySelector('.accordion-collapse'), {
        toggle: true
    });
    
    // Update the "Add Day" button text
    updateAddDayButton();
}

// Update the "Add Day" button text
function updateAddDayButton() {
    const dayCount = document.querySelectorAll('.accordion-item').length;
    const addDayBtn = document.querySelector('button[onclick="addDay()"]');
    if (addDayBtn) {
        addDayBtn.innerHTML = `<i class="fas fa-plus me-1"></i>添加第 ${dayCount + 1} 天`;
    }
}

// Initialize cost calculation
function initCostCalculation() {
    // Add event listeners to all cost inputs
    document.querySelectorAll('.activity-cost').forEach(input => {
        input.addEventListener('change', updateCostDisplay);
    });
    
    // Initial calculation
    updateCostDisplay();
}

// Update cost display and pie chart
function updateCostDisplay() {
    const costs = {
        '景点': 0,
        '美食': 0,
        '住宿': 0,
        '交通': 0,
        '购物': 0
    };
    
    let total = 0;
    
    // Calculate costs from all activity cards
    document.querySelectorAll('.activity-card').forEach(card => {
        const type = card.querySelector('.activity-type').value;
        const costInput = card.querySelector('.activity-cost');
        const cost = parseFloat(costInput.value) || 0;
        
        if (costs.hasOwnProperty(type)) {
            costs[type] += cost;
        }
        total += cost;
    });
    
    // Update cost display
    document.getElementById('costAttractions').textContent = '¥' + costs['景点'].toFixed(0);
    document.getElementById('costFood').textContent = '¥' + costs['美食'].toFixed(0);
    document.getElementById('costAccommodation').textContent = '¥' + costs['住宿'].toFixed(0);
    document.getElementById('costTransport').textContent = '¥' + costs['交通'].toFixed(0);
    document.getElementById('costShopping').textContent = '¥' + costs['购物'].toFixed(0);
    document.getElementById('costTotal').textContent = '¥' + total.toFixed(0);
    
    // Update pie chart if Chart.js is available
    updateCostChart(costs);
}

// Update the cost pie chart
function updateCostChart(costs) {
    const ctx = document.getElementById('costChart');
    if (!ctx) return;
    
    if (window.costChartInstance) {
        window.costChartInstance.data.datasets[0].data = [
            costs['景点'],
            costs['美食'],
            costs['住宿'],
            costs['交通'],
            costs['购物']
        ];
        window.costChartInstance.update();
    } else {
        // Initialize chart if not exists
        window.costChartInstance = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['景点', '美食', '住宿', '交通', '购物'],
                datasets: [{
                    data: [
                        costs['景点'],
                        costs['美食'],
                        costs['住宿'],
                        costs['交通'],
                        costs['购物']
                    ],
                    backgroundColor: [
                        '#0d6efd',
                        '#ffc107',
                        '#6c757d',
                        '#198754',
                        '#dc3545'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Serialize form data to JSON
function serializeFormData() {
    const data = {
        title: document.getElementById('itineraryTitle').value,
        days: []
    };
    
    document.querySelectorAll('.accordion-item').forEach((dayPanel, dayIndex) => {
        const day = {
            id: dayPanel.getAttribute('data-day-id'),
            theme: dayPanel.querySelector('.day-theme')?.value || '',
            activities: []
        };
        
        dayPanel.querySelectorAll('.activity-card').forEach(activityCard => {
            const activity = {
                id: activityCard.getAttribute('data-activity-id'),
                type: activityCard.querySelector('.activity-type').value,
                name: activityCard.querySelector('.activity-name').value,
                duration: activityCard.querySelector('.activity-duration').value,
                cost: parseFloat(activityCard.querySelector('.activity-cost').value) || 0,
                tips: activityCard.querySelector('.activity-tips').value || ''
            };
            day.activities.push(activity);
        });
        
        data.days.push(day);
    });
    
    return data;
}

// Save itinerary
function saveItinerary() {
    const formData = serializeFormData();
    const itineraryId = document.getElementById('itineraryId').value;
    
    fetch('/itineraries/save?id=' + itineraryId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('行程保存成功！');
            window.location.href = '/itineraries/my';
        } else {
            alert(data.message || '保存失败');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('保存失败，请重试');
    });
}

// Preview itinerary
function previewItinerary() {
    const formData = serializeFormData();
    
    // Open preview in new window
    const previewWindow = window.open('', '_blank');
    previewWindow.document.write(`
        <html>
        <head>
            <title>行程预览</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>${formData.title}</h1>
                <pre>${JSON.stringify(formData, null, 2)}</pre>
            </div>
        </body>
        </html>
    `);
}

// Export PDF
function exportPDF() {
    window.location.href = '/itineraries/export-pdf';
}

// Share itinerary
function shareItinerary() {
    const itineraryId = document.getElementById('itineraryId').value;
    
    fetch('/itineraries/share?id=' + itineraryId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('行程已公开分享到社区！');
        } else {
            alert(data.message || '分享失败');
        }
    });
}

// Delete itinerary
function deleteItinerary() {
    if (confirm('确定要删除这个行程吗？此操作不可恢复。')) {
        const itineraryId = document.getElementById('itineraryId').value;
        
        fetch('/itineraries/' + itineraryId + '/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            }
        })
        .then(response => {
            if (response.redirected) {
                alert('行程已删除');
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            if (data && data.success === false) {
                alert(data.message || '删除失败');
            }
        });
    }
}

// AI Chat sidebar functions
function toggleAIChat() {
    const sidebar = document.getElementById('aiChatSidebar');
    const toggle = document.getElementById('aiChatToggle');
    
    if (sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        toggle.style.display = 'block';
    } else {
        sidebar.classList.add('open');
        toggle.style.display = 'none';
    }
}

// Make these functions globally available
window.addActivity = addActivity;
window.removeActivity = removeActivity;
window.addDay = addDay;
window.saveItinerary = saveItinerary;
window.previewItinerary = previewItinerary;
window.exportPDF = exportPDF;
window.shareItinerary = shareItinerary;
window.deleteItinerary = deleteItinerary;
window.toggleAIChat = toggleAIChat;
window.serializeFormData = serializeFormData;
