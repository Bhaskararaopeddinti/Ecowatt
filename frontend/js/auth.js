// EcoWatt AI - Authentication JavaScript

const API_BASE = `${window.location.origin}/api`;

// DOM Elements
const authTabs = document.querySelectorAll('.auth-tab');
const authForms = document.querySelectorAll('.auth-form');
const switchTabs = document.querySelectorAll('.switch-tab');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const alertBox = document.getElementById('alert');
const loading = document.querySelector('.loading');

// Tab switching
authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;
        
        // Update tab styles
        authTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Show corresponding form
        authForms.forEach(form => {
            form.classList.remove('active');
            form.style.display = 'none';
            if (form.id === `${targetTab}Form`) {
                form.classList.add('active');
                form.style.display = 'block';
            }
        });
    });
});

// Switch tabs via links
switchTabs.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetTab = link.dataset.tab;
        
        // Find and click the corresponding tab
        authTabs.forEach(tab => {
            if (tab.dataset.tab === targetTab) {
                tab.click();
            }
        });
    });
});

// Show alert
function showAlert(message, type = 'error') {
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type} active`;
    
    setTimeout(() => {
        alertBox.classList.remove('active');
    }, 5000);
}

// Show/hide loading
function setLoading(isLoading) {
    if (isLoading) {
        loading.classList.add('active');
        authForms.forEach(form => form.style.display = 'none');
    } else {
        loading.classList.remove('active');
        authForms.forEach(form => {
            if (form.classList.contains('active')) {
                form.style.display = 'block';
            }
        });
    }
}

// Store token
function setToken(token) {
    localStorage.setItem('token', token);
}

// Get token
function getToken() {
    return localStorage.getItem('token');
}

// Remove token
function removeToken() {
    localStorage.removeItem('token');
}

// Check if user is logged in
function isLoggedIn() {
    return !!getToken();
}

// Redirect to dashboard if logged in
function checkAuth() {
    if (isLoggedIn()) {
        window.location.href = 'dashboard.html';
    }
}

// Form validation
function validateForm(form) {
    let isValid = true;
    const formGroups = form.querySelectorAll('.form-group');
    
    formGroups.forEach(group => {
        const input = group.querySelector('input');
        const error = group.querySelector('.error');
        
        if (input && input.hasAttribute('required') && !input.value.trim()) {
            group.classList.add('error');
            isValid = false;
        } else if (input && input.type === 'email' && input.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(input.value)) {
                group.classList.add('error');
                isValid = false;
            }
        } else if (input && input.type === 'password' && input.minLength > 0 && input.value.length < input.minLength) {
            group.classList.add('error');
            isValid = false;
        } else {
            group.classList.remove('error');
        }
    });
    
    // Check password confirmation for signup
    if (form.id === 'signupForm') {
        const password = form.querySelector('#signupPassword').value;
        const confirmPassword = form.querySelector('#signupConfirmPassword').value;
        
        if (password !== confirmPassword) {
            const confirmGroup = form.querySelector('#signupConfirmPassword').closest('.form-group');
            confirmGroup.classList.add('error');
            isValid = false;
        }
    }
    
    return isValid;
}

// Remove error on input
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', () => {
        const formGroup = input.closest('.form-group');
        if (formGroup) {
            formGroup.classList.remove('error');
        }
    });
});

// Login form submission
if (loginForm) {
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!validateForm(loginForm)) {
        return;
    }
    
    const formData = new FormData(loginForm);
    const data = new URLSearchParams();
    data.append('username', formData.get('username'));
    data.append('password', formData.get('password'));
    
    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: data
        });
        
        const text = await response.text();
        let result = {};
        try {
            result = text ? JSON.parse(text) : {};
        } catch (_) {
            result = { detail: text || 'Login failed.' };
        }
        
        if (response.ok) {
            setToken(result.access_token);
            showAlert('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showAlert(result.detail || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        showAlert('An error occurred. Please try again.');
        console.error('Login error:', error);
    } finally {
        setLoading(false);
    }
});
}

// Signup form submission
if (signupForm) {
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!validateForm(signupForm)) {
        return;
    }
    
    const formData = new FormData(signupForm);
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        full_name: formData.get('fullName') || null,
        phone: null,
        address: null
    };
    
    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const text = await response.text();
        let result = {};
        try {
            result = text ? JSON.parse(text) : {};
        } catch (_) {
            result = { detail: text || 'Signup failed.' };
        }
        
        if (response.ok) {
            showAlert('Account created successfully! Please login.', 'success');
            // Switch to login tab
            authTabs[0].click();
            // Pre-fill username
            document.getElementById('loginUsername').value = data.username;
            signupForm.reset();
        } else {
            showAlert(result.detail || 'Signup failed. Please try again.');
        }
    } catch (error) {
        showAlert('An error occurred. Please try again.');
        console.error('Signup error:', error);
    } finally {
        setLoading(false);
    }
});
}

// Check auth on page load
checkAuth();

// Handle URL hash for signup
if (window.location.hash === '#signup') {
    authTabs[1].click();
}
