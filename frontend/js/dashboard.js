// EcoWatt AI - Dashboard JavaScript

import { dashboardAPI, energyAPI, alertsAPI, recommendationsAPI, appliancesAPI, authAPI } from './api.js';

// DOM Elements
const loadingOverlay = document.getElementById('loadingOverlay');
const simulateBtn = document.getElementById('simulateBtn');
const refreshBtn = document.getElementById('refreshBtn');
const detectAppliancesBtn = document.getElementById('detectAppliancesBtn');
const detectLeaksBtn = document.getElementById('detectLeaksBtn');
const generateRecommendationsBtn = document.getElementById('generateRecommendationsBtn');
const logoutBtn = document.getElementById('logoutBtn');

// Chart instances
let usageChart = null;
let applianceChart = null;

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

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
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

// Load dashboard summary
async function loadDashboardSummary() {
    try {
        const summary = await dashboardAPI.getSummary();
        
        document.getElementById('todayUsage').textContent = `${formatNumber(summary.today_usage)} kWh`;
        document.getElementById('monthlyUsage').textContent = `${formatNumber(summary.monthly_usage)} kWh`;
        document.getElementById('currentBill').textContent = formatCurrency(summary.current_bill);
        document.getElementById('predictedBill').textContent = formatCurrency(summary.predicted_bill);
        document.getElementById('carbonFootprint').textContent = `${formatNumber(summary.carbon_footprint)} kg`;
        document.getElementById('energyScore').textContent = summary.energy_score;
        
        // Update energy score color
        const scoreElement = document.getElementById('energyScore');
        if (summary.energy_score >= 80) {
            scoreElement.style.color = '#22c55e';
        } else if (summary.energy_score >= 60) {
            scoreElement.style.color = '#f59e0b';
        } else {
            scoreElement.style.color = '#ef4444';
        }
        
        // Update alert count
        document.getElementById('alertCount').textContent = summary.active_alerts;
        
    } catch (error) {
        console.error('Error loading dashboard summary:', error);
    }
}

// Load usage chart
async function loadUsageChart(days = 30) {
    try {
        const data = await dashboardAPI.getUsageChart(days);
        
        const labels = data.map(d => formatDate(d.date));
        const energyData = data.map(d => d.energy);
        const powerData = data.map(d => d.power);
        
        const ctx = document.getElementById('usageChart').getContext('2d');
        
        if (usageChart) {
            usageChart.destroy();
        }
        
        usageChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Energy (kWh)',
                        data: energyData,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Power (W)',
                        data: powerData,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4,
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
                            text: 'Energy (kWh)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Power (W)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading usage chart:', error);
    }
}

// Load appliance chart
async function loadApplianceChart() {
    try {
        const appliances = await appliancesAPI.getAppliances();
        
        if (appliances.length === 0) {
            document.getElementById('applianceChart').style.display = 'none';
            return;
        }
        
        const labels = appliances.map(a => a.name);
        const data = appliances.map(a => a.monthly_cost);
        
        const ctx = document.getElementById('applianceChart').getContext('2d');
        
        if (applianceChart) {
            applianceChart.destroy();
        }
        
        applianceChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#f59e0b',
                        '#ef4444',
                        '#8b5cf6',
                        '#ec4899',
                        '#06b6d4',
                        '#84cc16'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading appliance chart:', error);
    }
}

// Load alerts
async function loadAlerts() {
    try {
        const alerts = await alertsAPI.getAlerts(true);
        const alertsList = document.getElementById('alertsList');
        
        if (alerts.length === 0) {
            alertsList.innerHTML = '<p class="empty-state">No active alerts</p>';
            return;
        }
        
        alertsList.innerHTML = alerts.map(alert => `
            <div class="alert-item ${alert.severity}">
                <h4>${alert.type.replace(/_/g, ' ').toUpperCase()}</h4>
                <p>${alert.message}</p>
                <small>${formatDateTime(alert.created_at)}</small>
            </div>
        `).join('');
        
        document.getElementById('alertCount').textContent = alerts.length;
        
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// Load recommendations
async function loadRecommendations() {
    try {
        const recommendations = await recommendationsAPI.getRecommendations(true);
        const recommendationsList = document.getElementById('recommendationsList');
        
        if (recommendations.length === 0) {
            recommendationsList.innerHTML = '<p class="empty-state">No recommendations available</p>';
            return;
        }
        
        recommendationsList.innerHTML = recommendations.slice(0, 5).map(rec => `
            <div class="recommendation-item">
                <h4>${rec.title}</h4>
                <p>${rec.description}</p>
                <span class="recommendation-savings">Save ₹${formatNumber(rec.estimated_savings)}/month</span>
            </div>
        `).join('');
        
        document.getElementById('recommendationCount').textContent = recommendations.length;
        
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const activities = await dashboardAPI.getRecentActivity(10);
        const activityList = document.getElementById('activityList');
        
        if (activities.length === 0) {
            activityList.innerHTML = '<p class="empty-state">No recent activity</p>';
            return;
        }
        
        const icons = {
            energy_reading: '⚡',
            alert: '🚨',
            recommendation: '💡'
        };
        
        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">${icons[activity.type] || '📋'}</div>
                <div class="activity-content">
                    <p>${activity.message}</p>
                    <span class="activity-time">${formatDateTime(activity.timestamp)}</span>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

// Simulate data
async function simulateData() {
    setLoading(true);
    try {
        await energyAPI.simulateData(20);
        await loadDashboardSummary();
        await loadUsageChart(30);
        await loadRecentActivity();
    } catch (error) {
        console.error('Error simulating data:', error);
        alert('Failed to simulate data. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Detect appliances
async function detectAppliances() {
    setLoading(true);
    try {
        await appliancesAPI.detectAppliances();
        await loadApplianceChart();
        alert('Appliance detection completed!');
    } catch (error) {
        console.error('Error detecting appliances:', error);
        alert('Failed to detect appliances. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Detect energy leaks
async function detectLeaks() {
    setLoading(true);
    try {
        await alertsAPI.detectLeaks();
        await loadAlerts();
        alert('Energy leak detection completed!');
    } catch (error) {
        console.error('Error detecting leaks:', error);
        alert('Failed to detect energy leaks. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Generate recommendations
async function generateRecommendations() {
    setLoading(true);
    try {
        await recommendationsAPI.generateRecommendations();
        await loadRecommendations();
        alert('Recommendations generated successfully!');
    } catch (error) {
        console.error('Error generating recommendations:', error);
        alert('Failed to generate recommendations. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Refresh dashboard
async function refreshDashboard() {
    setLoading(true);
    try {
        await loadDashboardSummary();
        await loadUsageChart(30);
        await loadAlerts();
        await loadRecommendations();
        await loadRecentActivity();
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
    } finally {
        setLoading(false);
    }
}

// Chart period buttons
document.querySelectorAll('.chart-period').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.chart-period').forEach(b => b.classList.remove('active'));
        button.classList.add('active');
        const days = parseInt(button.dataset.days);
        loadUsageChart(days);
    });
});

// Event listeners
simulateBtn.addEventListener('click', simulateData);
refreshBtn.addEventListener('click', refreshDashboard);
detectAppliancesBtn.addEventListener('click', detectAppliances);
detectLeaksBtn.addEventListener('click', detectLeaks);
generateRecommendationsBtn.addEventListener('click', generateRecommendations);
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

// Initialize dashboard
async function initDashboard() {
    setLoading(true);
    try {
        await Promise.all([
            loadDashboardSummary(),
            loadUsageChart(30),
            loadApplianceChart(),
            loadAlerts(),
            loadRecommendations(),
            loadRecentActivity()
        ]);
    } catch (error) {
        console.error('Error initializing dashboard:', error);
    } finally {
        setLoading(false);
    }
}

// Load on page ready
initDashboard();
