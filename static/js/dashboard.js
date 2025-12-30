// Global variables
let historicalChart = null;
let forecastChart = null;
let productChart = null;
let csrfToken = '';

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    
    // Set default dates (last 90 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 90);
    
    document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
    document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
    
    // Initialize charts
    initializeCharts();
    
    // Load initial data
    loadHistoricalData();
    loadProductPerformance();
    
    // Setup upload form
    setupUploadForm();
});

// Initialize Chart.js charts
function initializeCharts() {
    // Historical Sales Chart
    const historicalCtx = document.getElementById('historicalChart').getContext('2d');
    historicalChart = new Chart(historicalCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Revenue',
                data: [],
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Quantity',
                data: [],
                borderColor: 'rgb(118, 75, 162)',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                tension: 0.4,
                yAxisID: 'y1',
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
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
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Revenue ($)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Quantity'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
    
    // Forecast Chart
    const forecastCtx = document.getElementById('forecastChart').getContext('2d');
    forecastChart = new Chart(forecastCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Historical',
                data: [],
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4
            }, {
                label: 'Forecast',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4,
                borderDash: [5, 5]
            }, {
                label: 'Confidence Upper',
                data: [],
                borderColor: 'rgba(255, 99, 132, 0.3)',
                backgroundColor: 'rgba(255, 99, 132, 0.05)',
                tension: 0.4,
                borderDash: [2, 2],
                fill: '+1'
            }, {
                label: 'Confidence Lower',
                data: [],
                borderColor: 'rgba(255, 99, 132, 0.3)',
                backgroundColor: 'rgba(255, 99, 132, 0.05)',
                tension: 0.4,
                borderDash: [2, 2]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
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
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Revenue ($)'
                    }
                }
            }
        }
    });
    
    // Product Performance Chart
    const productCtx = document.getElementById('productChart').getContext('2d');
    productChart = new Chart(productCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Total Revenue',
                data: [],
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgb(102, 126, 234)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Revenue ($)'
                    }
                }
            }
        }
    });
}

// Load historical data
async function loadHistoricalData() {
    showLoading();
    try {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const product = document.getElementById('productFilter').value;
        const groupBy = document.getElementById('groupBy').value;
        
        const params = new URLSearchParams({
            start_date: startDate || '',
            end_date: endDate || '',
            product: product || '',
            group_by: groupBy
        });
        
        const response = await fetch(`/api/historical-data/?${params}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update historical chart
        historicalChart.data.labels = data.dates;
        historicalChart.data.datasets[0].data = data.revenue;
        historicalChart.data.datasets[1].data = data.quantity;
        historicalChart.update();
        
        // Update stats
        const totalRevenue = data.revenue.reduce((a, b) => a + b, 0);
        const totalQuantity = data.quantity.reduce((a, b) => a + b, 0);
        
        document.getElementById('totalRevenue').textContent = formatCurrency(totalRevenue);
        document.getElementById('totalQuantity').textContent = formatNumber(totalQuantity);
        document.getElementById('totalProducts').textContent = data.products.length;
        
        if (data.dates.length > 0) {
            document.getElementById('dateRange').textContent = 
                `${data.dates[0]} to ${data.dates[data.dates.length - 1]}`;
        }
        
        // Update product filter dropdown
        updateProductFilter(data.products);
        
    } catch (error) {
        console.error('Error loading historical data:', error);
        showNotification('Error loading historical data: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Load product performance
async function loadProductPerformance() {
    try {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        const params = new URLSearchParams({
            start_date: startDate || '',
            end_date: endDate || ''
        });
        
        const response = await fetch(`/api/product-performance/?${params}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update product chart
        const products = data.products.slice(0, 10); // Top 10 products
        productChart.data.labels = products.map(p => p.product);
        productChart.data.datasets[0].data = products.map(p => p.total_revenue);
        productChart.update();
        
        // Update product table
        updateProductTable(data.products);
        
    } catch (error) {
        console.error('Error loading product performance:', error);
    }
}

// Update product filter dropdown
function updateProductFilter(products) {
    const select = document.getElementById('productFilter');
    const currentValue = select.value;
    
    // Clear existing options except "All Products"
    select.innerHTML = '<option value="">All Products</option>';
    
    // Add product options
    products.forEach(product => {
        const option = document.createElement('option');
        option.value = product;
        option.textContent = product;
        select.appendChild(option);
    });
    
    // Restore previous selection if still valid
    if (currentValue && products.includes(currentValue)) {
        select.value = currentValue;
    }
}

// Update product performance table
function updateProductTable(products) {
    const tbody = document.getElementById('productTableBody');
    
    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No data available.</td></tr>';
        return;
    }
    
    tbody.innerHTML = products.map(product => `
        <tr>
            <td><strong>${escapeHtml(product.product)}</strong></td>
            <td>${formatCurrency(product.total_revenue)}</td>
            <td>${formatCurrency(product.avg_revenue)}</td>
            <td>${formatNumber(product.total_quantity)}</td>
            <td>${formatNumber(product.avg_quantity)}</td>
            <td>${formatNumber(product.transactions)}</td>
        </tr>
    `).join('');
}

// Generate forecast
async function generateForecast() {
    showLoading();
    try {
        const method = document.getElementById('forecastMethod').value;
        const periods = parseInt(document.getElementById('forecastPeriods').value);
        const product = document.getElementById('productFilter').value || null;
        const startDate = document.getElementById('startDate').value || null;
        const endDate = document.getElementById('endDate').value || null;
        
        const response = await fetch('/api/forecast/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                method: method,
                periods: periods,
                product: product,
                start_date: startDate,
                end_date: endDate
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Load historical data to combine with forecast
        await loadHistoricalData();
        
        // Update forecast chart
        const historicalData = historicalChart.data;
        const forecastDates = data.forecasts.map(f => f.date);
        const forecastValues = data.forecasts.map(f => f.forecast);
        const forecastUpper = data.forecasts.map(f => f.upper);
        const forecastLower = data.forecasts.map(f => f.lower);
        
        // Combine historical and forecast dates
        const allDates = [...historicalData.labels, ...forecastDates];
        const historicalValues = [...historicalData.datasets[0].data];
        const forecastValuesExtended = [...new Array(historicalValues.length).fill(null), ...forecastValues];
        const forecastUpperExtended = [...new Array(historicalValues.length).fill(null), ...forecastUpper];
        const forecastLowerExtended = [...new Array(historicalValues.length).fill(null), ...forecastLower];
        
        forecastChart.data.labels = allDates;
        forecastChart.data.datasets[0].data = historicalValues;
        forecastChart.data.datasets[1].data = forecastValuesExtended;
        forecastChart.data.datasets[2].data = forecastUpperExtended;
        forecastChart.data.datasets[3].data = forecastLowerExtended;
        forecastChart.update();
        
        showNotification(`Forecast generated successfully using ${method.toUpperCase()} method!`, 'success');
        
    } catch (error) {
        console.error('Error generating forecast:', error);
        showNotification('Error generating forecast: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Apply filters
function applyFilters() {
    loadHistoricalData();
    loadProductPerformance();
}

// Reset filters
function resetFilters() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 90);
    
    document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
    document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
    document.getElementById('productFilter').value = '';
    document.getElementById('groupBy').value = 'day';
    
    applyFilters();
}

// Setup upload form
function setupUploadForm() {
    const form = document.getElementById('uploadForm');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('csvFile');
        const file = fileInput.files[0];
        
        if (!file) {
            showNotification('Please select a file', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        showLoading();
        
        try {
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            showNotification(`Successfully imported ${data.records_count} records!`, 'success');
            closeUploadModal();
            
            // Reload data
            setTimeout(() => {
                loadHistoricalData();
                loadProductPerformance();
            }, 1000);
            
        } catch (error) {
            console.error('Upload error:', error);
            showNotification('Upload failed: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    });
}

// Modal functions
function showUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    document.getElementById('uploadForm').reset();
    document.getElementById('uploadStatus').innerHTML = '';
    document.getElementById('uploadStatus').className = 'status-message';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('uploadModal');
    if (event.target == modal) {
        closeUploadModal();
    }
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    
    // Also show as alert for non-modal notifications
    if (type === 'success') {
        setTimeout(() => {
            statusDiv.className = 'status-message';
            statusDiv.textContent = '';
        }, 5000);
    }
}

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

