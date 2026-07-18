// EcoWatt AI - Reports JavaScript

import { reportsAPI, authAPI } from './api.js';

// DOM Elements
const loadingOverlay = document.getElementById('loadingOverlay');
const generateReportBtn = document.getElementById('generateReportBtn');
const reportForm = document.getElementById('reportForm');
const reportsList = document.getElementById('reportsList');
const reportPreviewCard = document.getElementById('reportPreviewCard');
const reportPreview = document.getElementById('reportPreview');
const closePreviewBtn = document.getElementById('closePreviewBtn');
const downloadReportBtn = document.getElementById('downloadReportBtn');
const logoutBtn = document.getElementById('logoutBtn');

// Current report data
let currentReport = null;

// Show/hide loading
function setLoading(isLoading) {
    if (isLoading) {
        loadingOverlay.classList.add('active');
    } else {
        loadingOverlay.classList.remove('active');
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric',
        month: 'short', 
        day: 'numeric'
    });
}

// Format datetime
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
        year: 'numeric',
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format currency
function formatCurrency(amount) {
    return `₹${amount.toFixed(2)}`;
}

// Load reports list
async function loadReports() {
    try {
        const reports = await reportsAPI.getReports();
        
        if (reports.length === 0) {
            reportsList.innerHTML = '<p class="empty-state">No reports generated yet</p>';
            return;
        }
        
        reportsList.innerHTML = `
            <div class="reports-grid">
                ${reports.map(report => `
                    <div class="report-item" data-report-id="${report.id}">
                        <div class="report-icon">📄</div>
                        <div class="report-info">
                            <h4>${report.report_type.charAt(0).toUpperCase() + report.report_type.slice(1)} Report</h4>
                            <p>${formatDateTime(report.created_at)}</p>
                            <div class="report-stats">
                                <span>Energy: ${report.total_energy?.toFixed(2) || 0} kWh</span>
                                <span>Cost: ${formatCurrency(report.total_cost || 0)}</span>
                                <span>Carbon: ${report.carbon_footprint?.toFixed(2) || 0} kg</span>
                            </div>
                        </div>
                        <div class="report-actions">
                            <button class="btn btn-sm btn-outline view-report-btn" data-id="${report.id}">View</button>
                            <button class="btn btn-sm btn-primary download-report-btn" data-id="${report.id}">Download</button>
                            <button class="btn btn-sm btn-outline delete-report-btn" data-id="${report.id}">Delete</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Add event listeners to buttons
        document.querySelectorAll('.view-report-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                viewReport(parseInt(btn.dataset.id));
            });
        });
        
        document.querySelectorAll('.download-report-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                downloadReport(parseInt(btn.dataset.id));
            });
        });
        
        document.querySelectorAll('.delete-report-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteReport(parseInt(btn.dataset.id));
            });
        });
        
    } catch (error) {
        console.error('Error loading reports:', error);
        reportsList.innerHTML = '<p class="empty-state">Error loading reports</p>';
    }
}

// Generate report
async function generateReport(e) {
    e.preventDefault();
    
    const formData = new FormData(reportForm);
    const reportType = formData.get('reportType');
    const startDate = formData.get('startDate');
    const endDate = formData.get('endDate');
    
    setLoading(true);
    
    try {
        const result = await reportsAPI.generateReport(reportType, startDate, endDate);
        
        alert('Report generated successfully!');
        reportForm.reset();
        loadReports();
        
        // Show preview
        showReportPreview(result);
        
    } catch (error) {
        console.error('Error generating report:', error);
        alert('Failed to generate report. Please try again.');
    } finally {
        setLoading(false);
    }
}

// View report
async function viewReport(reportId) {
    setLoading(true);
    
    try {
        const report = await reportsAPI.getReport(reportId);
        currentReport = report;
        showReportPreview(report);
        
    } catch (error) {
        console.error('Error viewing report:', error);
        alert('Failed to load report. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Show report preview
function showReportPreview(report) {
    reportPreview.innerHTML = `
        <div class="report-summary">
            <h4>Report Summary</h4>
            <div class="summary-grid">
                <div class="summary-item">
                    <span>Report Type:</span>
                    <span>${report.report_type.charAt(0).toUpperCase() + report.report_type.slice(1)}</span>
                </div>
                <div class="summary-item">
                    <span>Generated:</span>
                    <span>${formatDateTime(report.created_at)}</span>
                </div>
                <div class="summary-item">
                    <span>Period:</span>
                    <span>${report.start_date ? formatDate(report.start_date) : 'N/A'} - ${report.end_date ? formatDate(report.end_date) : 'N/A'}</span>
                </div>
                <div class="summary-item">
                    <span>Total Energy:</span>
                    <span>${report.total_energy?.toFixed(2) || 0} kWh</span>
                </div>
                <div class="summary-item">
                    <span>Total Cost:</span>
                    <span>${formatCurrency(report.total_cost || 0)}</span>
                </div>
                <div class="summary-item">
                    <span>Carbon Footprint:</span>
                    <span>${report.carbon_footprint?.toFixed(2) || 0} kg CO2</span>
                </div>
            </div>
        </div>
    `;
    
    reportPreviewCard.style.display = 'block';
    downloadReportBtn.onclick = () => downloadReport(report.id);
}

// Download report
function downloadReport(reportId) {
    try {
        reportsAPI.downloadReport(reportId);
    } catch (error) {
        console.error('Error downloading report:', error);
        alert('Failed to download report. Please try again.');
    }
}

// Delete report
async function deleteReport(reportId) {
    if (!confirm('Are you sure you want to delete this report?')) {
        return;
    }
    
    setLoading(true);
    
    try {
        await reportsAPI.deleteReport(reportId);
        alert('Report deleted successfully!');
        loadReports();
        
        if (currentReport && currentReport.id === reportId) {
            reportPreviewCard.style.display = 'none';
            currentReport = null;
        }
        
    } catch (error) {
        console.error('Error deleting report:', error);
        alert('Failed to delete report. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Close preview
closePreviewBtn.addEventListener('click', () => {
    reportPreviewCard.style.display = 'none';
    currentReport = null;
});

// Event listeners
generateReportBtn.addEventListener('click', () => {
    reportForm.scrollIntoView({ behavior: 'smooth' });
});

reportForm.addEventListener('submit', generateReport);
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

// Set default dates for custom report
const reportTypeSelect = document.getElementById('reportType');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');

reportTypeSelect.addEventListener('change', () => {
    if (reportTypeSelect.value === 'custom') {
        startDateInput.required = true;
        endDateInput.required = true;
    } else {
        startDateInput.required = false;
        endDateInput.required = false;
    }
});

// Initialize
loadReports();
