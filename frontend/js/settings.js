// EcoWatt AI - Settings JavaScript

import { settingsAPI, authAPI } from './api.js';

// DOM Elements
const loadingOverlay = document.getElementById('loadingOverlay');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const profileForm = document.getElementById('profileForm');
const energyForm = document.getElementById('energyForm');
const appearanceForm = document.getElementById('appearanceForm');
const notificationForm = document.getElementById('notificationForm');
const clearDataBtn = document.getElementById('clearDataBtn');
const deleteAccountBtn = document.getElementById('deleteAccountBtn');
const logoutBtn = document.getElementById('logoutBtn');

// Show/hide loading
function setLoading(isLoading) {
    if (isLoading) {
        loadingOverlay.classList.add('active');
    } else {
        loadingOverlay.classList.remove('active');
    }
}

// Load user profile
async function loadUserProfile() {
    try {
        const user = await authAPI.getCurrentUser();
        
        document.getElementById('username').value = user.username;
        document.getElementById('email').value = user.email;
        document.getElementById('fullName').value = user.full_name || '';
        document.getElementById('phone').value = user.phone || '';
        document.getElementById('address').value = user.address || '';
        
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

// Load settings
async function loadSettings() {
    try {
        const settings = await settingsAPI.getSettings();
        
        document.getElementById('electricityRate').value = settings.electricity_rate;
        document.getElementById('currency').value = settings.currency;
        document.getElementById('carbonFactor').value = settings.carbon_factor;
        document.getElementById('theme').value = settings.theme;
        document.getElementById('notificationsEnabled').checked = settings.notifications_enabled;
        document.getElementById('emailAlerts').checked = settings.email_alerts;
        document.getElementById('smsAlerts').checked = settings.sms_alerts;
        
        // Apply theme
        applyTheme(settings.theme);
        
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Apply theme
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else if (theme === 'light') {
        document.body.classList.remove('dark-theme');
    } else if (theme === 'auto') {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }
    }
}

// Save profile settings
async function saveProfile() {
    const formData = new FormData(profileForm);
    const data = {
        full_name: formData.get('fullName'),
        phone: formData.get('phone'),
        address: formData.get('address')
    };
    
    try {
        await authAPI.updateCurrentUser(data);
        return true;
    } catch (error) {
        console.error('Error saving profile:', error);
        return false;
    }
}

// Save energy settings
async function saveEnergySettings() {
    const formData = new FormData(energyForm);
    const data = {
        electricity_rate: parseFloat(formData.get('electricityRate')),
        currency: formData.get('currency'),
        carbon_factor: parseFloat(formData.get('carbonFactor'))
    };
    
    try {
        await settingsAPI.updateSettings(data);
        return true;
    } catch (error) {
        console.error('Error saving energy settings:', error);
        return false;
    }
}

// Save appearance settings
async function saveAppearanceSettings() {
    const formData = new FormData(appearanceForm);
    const theme = formData.get('theme');
    
    try {
        await settingsAPI.updateSettings({ theme });
        applyTheme(theme);
        return true;
    } catch (error) {
        console.error('Error saving appearance settings:', error);
        return false;
    }
}

// Save notification settings
async function saveNotificationSettings() {
    const formData = new FormData(notificationForm);
    const data = {
        notifications_enabled: document.getElementById('notificationsEnabled').checked,
        email_alerts: document.getElementById('emailAlerts').checked,
        sms_alerts: document.getElementById('smsAlerts').checked
    };
    
    try {
        await settingsAPI.updateSettings(data);
        return true;
    } catch (error) {
        console.error('Error saving notification settings:', error);
        return false;
    }
}

// Save all settings
async function saveAllSettings() {
    setLoading(true);
    
    try {
        const results = await Promise.all([
            saveProfile(),
            saveEnergySettings(),
            saveAppearanceSettings(),
            saveNotificationSettings()
        ]);
        
        if (results.every(r => r === true)) {
            alert('Settings saved successfully!');
        } else {
            alert('Some settings failed to save. Please try again.');
        }
        
    } catch (error) {
        console.error('Error saving settings:', error);
        alert('Failed to save settings. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Clear all data
async function clearAllData() {
    if (!confirm('Are you sure you want to clear all your data? This action cannot be undone.')) {
        return;
    }
    
    if (!confirm('This will delete all your energy data, appliances, alerts, and recommendations. Are you absolutely sure?')) {
        return;
    }
    
    setLoading(true);
    
    try {
        // Note: This would need a backend endpoint to clear user data
        // For now, we'll just show a message
        alert('Data clear feature requires backend implementation. Please contact support.');
        
    } catch (error) {
        console.error('Error clearing data:', error);
        alert('Failed to clear data. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Delete account
async function deleteAccount() {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        return;
    }
    
    if (!confirm('All your data will be permanently deleted. This action is irreversible. Are you absolutely sure?')) {
        return;
    }
    
    const confirmation = prompt('Type "DELETE" to confirm account deletion:');
    if (confirmation !== 'DELETE') {
        alert('Account deletion cancelled.');
        return;
    }
    
    setLoading(true);
    
    try {
        // Note: This would need a backend endpoint to delete user account
        // For now, we'll just show a message
        alert('Account deletion feature requires backend implementation. Please contact support.');
        
    } catch (error) {
        console.error('Error deleting account:', error);
        alert('Failed to delete account. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Event listeners
saveSettingsBtn.addEventListener('click', saveAllSettings);
clearDataBtn.addEventListener('click', clearAllData);
deleteAccountBtn.addEventListener('click', deleteAccount);
logoutBtn.addEventListener('click', authAPI.logout);

// Theme change listener
document.getElementById('theme').addEventListener('change', (e) => {
    applyTheme(e.target.value);
});

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
}

// Initialize
async function initSettings() {
    setLoading(true);
    try {
        await Promise.all([
            loadUserProfile(),
            loadSettings()
        ]);
    } catch (error) {
        console.error('Error initializing settings:', error);
    } finally {
        setLoading(false);
    }
}

initSettings();
