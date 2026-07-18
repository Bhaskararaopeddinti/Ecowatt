// EcoWatt AI - Analysis JavaScript

import { energyAPI, appliancesAPI, alertsAPI, authAPI } from './api.js';

// DOM Elements
const loadingOverlay = document.getElementById('loadingOverlay');
const analyzeBtn = document.getElementById('analyzeBtn');
const exportBtn = document.getElementById('exportBtn');
const csvFileInput = document.getElementById('csvFileInput');
const detectAppliancesBtn = document.getElementById('detectAppliancesBtn');
const detectLeaksBtn = document.getElementById('detectLeaksBtn');
const loadMoreBtn = document.getElementById('loadMoreBtn');
const logoutBtn = document.getElementById('logoutBtn');

// Chart instances
let hourlyChart = null;
let dailyChart = null;
let powerEnergyChart = null;

// Current data
let currentEnergyData = [];
let currentOffset = 0;
const DATA_LIMIT = 50;

// Show/hide loading
function setLoading(isLoading) {
    if (isLoading) {
        loadingOverlay.classList.add('active');
    } else {
        loadingOverlay.classList.remove('active');
    }
}

// Format numbers
function formatNumber(num, decimals = 2) {
    return num.toFixed(decimals);
}

// Format currency
function formatCurrency(amount) {
    return `₹${formatNumber(amount)}`;
}

// Format datetime
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Load energy data
async function loadEnergyData(hours = 24 * 7) {
    try {
        const data = await energyAPI.getRecentEnergyData(hours);
        currentEnergyData = data;
        return data;
    } catch (error) {
        console.error('Error loading energy data:', error);
        return [];
    }
}

// Calculate statistics
function calculateStatistics(data) {
    if (!data || data.length === 0) {
        return {
            avgDailyUsage: 0,
            peakUsageTime: '--',
            totalCost: 0,
            totalCarbon: 0
        };
    }
    
    const totalEnergy = data.reduce((sum, d) => sum + (d.energy || 0), 0);
    const avgDailyUsage = totalEnergy / 7; // Assuming 7 days
    const totalCost = totalEnergy * 6.0; // ₹6 per kWh
    const totalCarbon = totalEnergy * 0.85; // 0.85 kg CO2 per kWh
    
    // Find peak usage time
    let maxPower = 0;
    let peakTime = '--';
    
    data.forEach(d => {
        if (d.power && d.power > maxPower) {
            maxPower = d.power;
            const date = new Date(d.timestamp);
            peakTime = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        }
    });
    
    return {
        avgDailyUsage,
        peakUsageTime: peakTime,
        totalCost,
        totalCarbon
    };
}

// Update statistics display
function updateStatistics(stats) {
    document.getElementById('avgDailyUsage').textContent = `${formatNumber(stats.avgDailyUsage)} kWh`;
    document.getElementById('peakUsageTime').textContent = stats.peakUsageTime;
    document.getElementById('totalCost').textContent = formatCurrency(stats.totalCost);
    document.getElementById('totalCarbon').textContent = `${formatNumber(stats.totalCarbon)} kg`;
}

// Load hourly chart
function loadHourlyChart(data) {
    const hourlyData = {};
    
    data.forEach(d => {
        const hour = new Date(d.timestamp).getHours();
        if (!hourlyData[hour]) {
            hourlyData[hour] = { power: 0, energy: 0, count: 0 };
        }
        hourlyData[hour].power += d.power || 0;
        hourlyData[hour].energy += d.energy || 0;
        hourlyData[hour].count += 1;
    });
    
    const labels = Object.keys(hourlyData).sort().map(h => `${h}:00`);
    const powerData = Object.keys(hourlyData).sort().map(h => hourlyData[h].power / hourlyData[h].count);
    const energyData = Object.keys(hourlyData).sort().map(h => hourlyData[h].energy);
    
    const ctx = document.getElementById('hourlyChart').getContext('2d');
    
    if (hourlyChart) {
        hourlyChart.destroy();
    }
    
    hourlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Average Power (W)',
                    data: powerData,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    yAxisID: 'y'
                },
                {
                    label: 'Total Energy (kWh)',
                    data: energyData,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Power (W)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Energy (kWh)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

// Load daily chart
function loadDailyChart(data) {
    const dailyData = {};
    
    data.forEach(d => {
        const date = new Date(d.timestamp).toDateString();
        if (!dailyData[date]) {
            dailyData[date] = 0;
        }
        dailyData[date] += d.energy || 0;
    });
    
    const labels = Object.keys(dailyData).map(d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    const energyData = Object.values(dailyData);
    
    const ctx = document.getElementById('dailyChart').getContext('2d');
    
    if (dailyChart) {
        dailyChart.destroy();
    }
    
    dailyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Energy (kWh)',
                data: energyData,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Energy (kWh)'
                    }
                }
            }
        }
    });
}

// Load power vs energy chart
function loadPowerEnergyChart(data) {
    const powerData = data.map(d => d.power);
    const energyData = data.map(d => d.energy);
    
    const ctx = document.getElementById('powerEnergyChart').getContext('2d');
    
    if (powerEnergyChart) {
        powerEnergyChart.destroy();
    }
    
    powerEnergyChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Power vs Energy',
                data: data.map(d => ({ x: d.power, y: d.energy })),
                backgroundColor: 'rgba(16, 185, 129, 0.6)',
                borderColor: '#10b981'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Power (W)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Energy (kWh)'
                    }
                }
            }
        }
    });
}

// Load appliance breakdown
async function loadApplianceBreakdown() {
    try {
        const appliances = await appliancesAPI.getAppliances();
        const container = document.getElementById('applianceBreakdown');
        
        if (appliances.length === 0) {
            container.innerHTML = '<p class="empty-state">No appliance data available. Click "Detect Appliances" to analyze.</p>';
            return;
        }
        
        container.innerHTML = `
            <div class="appliance-grid">
                ${appliances.map(app => `
                    <div class="appliance-item">
                        <div class="appliance-header">
                            <h4>${app.name}</h4>
                            <span class="appliance-status ${app.status}">${app.status}</span>
                        </div>
                        <div class="appliance-details">
                            <div class="appliance-detail">
                                <span>Type:</span>
                                <span>${app.type}</span>
                            </div>
                            <div class="appliance-detail">
                                <span>Power:</span>
                                <span>${app.power_rating}W</span>
                            </div>
                            <div class="appliance-detail">
                                <span>Monthly Cost:</span>
                                <span>₹${formatNumber(app.monthly_cost)}</span>
                            </div>
                            <div class="appliance-detail">
                                <span>Usage:</span>
                                <span>${app.percentage?.toFixed(1) || 0}%</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error loading appliance breakdown:', error);
    }
}

// Detect appliances
async function detectAppliances() {
    setLoading(true);
    try {
        await appliancesAPI.detectAppliances();
        await loadApplianceBreakdown();
        alert('Appliance detection completed!');
    } catch (error) {
        console.error('Error detecting appliances:', error);
        alert('Failed to detect appliances. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Detect leaks
async function detectLeaks() {
    setLoading(true);
    try {
        const leaks = await alertsAPI.detectLeaks();
        const container = document.getElementById('leakResults');
        
        if (leaks.length === 0) {
            container.innerHTML = '<p class="empty-state">No energy leaks detected. Great job!</p>';
            return;
        }
        
        container.innerHTML = `
            <div class="leak-list">
                ${leaks.map(leak => `
                    <div class="leak-item ${leak.severity}">
                        <h4>${leak.leak_type.replace(/_/g, ' ').toUpperCase()}</h4>
                        <p>${leak.message}</p>
                        <div class="leak-details">
                            <span>Severity: ${leak.severity}</span>
                            <span>Value: ${formatNumber(leak.value)}</span>
                            <span>Threshold: ${formatNumber(leak.threshold)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        alert(`Detected ${leaks.length} energy leak(s)!`);
    } catch (error) {
        console.error('Error detecting leaks:', error);
        alert('Failed to detect energy leaks. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Load consumption table
function loadConsumptionTable(data) {
    const tbody = document.querySelector('#consumptionTable tbody');
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No data available</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(d => `
        <tr>
            <td>${formatDateTime(d.timestamp)}</td>
            <td>${formatNumber(d.voltage)}</td>
            <td>${formatNumber(d.current)}</td>
            <td>${formatNumber(d.power)}</td>
            <td>${formatNumber(d.energy, 4)}</td>
            <td>${formatNumber(d.power_factor)}</td>
        </tr>
    `).join('');
}

// Load more data
async function loadMoreData() {
    currentOffset += DATA_LIMIT;
    try {
        const data = await energyAPI.getEnergyData(currentOffset, DATA_LIMIT);
        loadConsumptionTable(data);
        
        if (data.length < DATA_LIMIT) {
            loadMoreBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading more data:', error);
    }
}

// Export data
function exportData() {
    if (currentEnergyData.length === 0) {
        alert('No data to export. Please run analysis first.');
        return;
    }
    
    const headers = ['Timestamp', 'Voltage (V)', 'Current (A)', 'Power (W)', 'Energy (kWh)', 'Frequency (Hz)', 'Power Factor'];
    const rows = currentEnergyData.map(d => [
        d.timestamp,
        d.voltage,
        d.current,
        d.power,
        d.energy,
        d.frequency,
        d.power_factor
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `energy_data_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Upload CSV file
async function uploadCSVFile() {
    const file = csvFileInput.files?.[0];
    if (!file) {
        alert('Please choose a CSV file first.');
        return;
    }

    setLoading(true);
    try {
        const result = await energyAPI.uploadCSV(file);
        alert(`Uploaded ${result.count || 0} rows successfully.`);
        await runAnalysis();
    } catch (error) {
        console.error('CSV upload failed:', error);
        alert(error.message || 'Failed to upload CSV file.');
    } finally {
        setLoading(false);
    }
}

// Run analysis
async function runAnalysis() {
    setLoading(true);
    try {
        const hours = parseInt(document.querySelector('.time-range-btn.active').dataset.range) * 24;
        const data = await loadEnergyData(hours);
        
        const stats = calculateStatistics(data);
        updateStatistics(stats);
        
        loadHourlyChart(data);
        loadDailyChart(data);
        loadPowerEnergyChart(data);
        loadConsumptionTable(data.slice(0, DATA_LIMIT));
        
        currentOffset = 0;
        loadMoreBtn.style.display = 'block';
        
    } catch (error) {
        console.error('Error running analysis:', error);
        alert('Failed to run analysis. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Time range buttons
document.querySelectorAll('.time-range-btn').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.time-range-btn').forEach(b => b.classList.remove('active'));
        button.classList.add('active');
        runAnalysis();
    });
});

// Event listeners
analyzeBtn.addEventListener('click', runAnalysis);
exportBtn.addEventListener('click', exportData);
csvFileInput.addEventListener('change', uploadCSVFile);
detectAppliancesBtn.addEventListener('click', detectAppliances);
detectLeaksBtn.addEventListener('click', detectLeaks);
loadMoreBtn.addEventListener('click', loadMoreData);
logoutBtn.addEventListener('click', authAPI.logout);

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
}

// Initialize analysis
runAnalysis();
