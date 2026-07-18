// EcoWatt AI - API Utility Functions

const API_BASE = `${window.location.origin}/api`;

// Get token from localStorage
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

// Redirect to login if not authenticated
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
    }
}

// Generic API call function
async function apiCall(endpoint, options = {}) {
    const token = getToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers
    };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        
        if (response.status === 401) {
            // Unauthorized - redirect to login
            removeToken();
            window.location.href = 'login.html';
            return null;
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// GET request
async function get(endpoint) {
    return apiCall(endpoint, { method: 'GET' });
}

// POST request
async function post(endpoint, data) {
    return apiCall(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// PUT request
async function put(endpoint, data) {
    return apiCall(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// DELETE request
async function del(endpoint) {
    return apiCall(endpoint, { method: 'DELETE' });
}

// Auth API
export const authAPI = {
    async login(username, password) {
        const formData = new URLSearchParams({ username, password });
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        return await response.json();
    },
    
    async signup(userData) {
        return post('/auth/signup', userData);
    },
    
    async getCurrentUser() {
        return get('/auth/me');
    },
    
    async logout() {
        removeToken();
        window.location.href = 'login.html';
    }
};

// Dashboard API
export const dashboardAPI = {
    async getSummary() {
        return get('/dashboard/summary');
    },
    
    async getUsageChart(days = 30) {
        return get(`/dashboard/usage-chart?days=${days}`);
    },
    
    async getRecentActivity(limit = 10) {
        return get(`/dashboard/recent-activity?limit=${limit}`);
    }
};

// Energy API
export const energyAPI = {
    async createEnergyData(data) {
        return post('/energy/data', data);
    },
    
    async getEnergyData(skip = 0, limit = 100) {
        return get(`/energy/data?skip=${skip}&limit=${limit}`);
    },
    
    async getRecentEnergyData(hours = 24) {
        return get(`/energy/data/recent?hours=${hours}`);
    },
    
    async simulateData(count = 10) {
        return post(`/energy/simulate?count=${count}`);
    },

    async uploadCSV(file) {
        const formData = new FormData();
        formData.append('file', file);

        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/energy/upload-csv`, {
            method: 'POST',
            headers: {
                ...(token ? { Authorization: `Bearer ${token}` } : {})
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'CSV upload failed' }));
            throw new Error(error.detail || 'CSV upload failed');
        }

        return await response.json();
    }
};

// Appliances API
export const appliancesAPI = {
    async createAppliance(data) {
        return post('/appliances/', data);
    },
    
    async getAppliances() {
        return get('/appliances/');
    },
    
    async getAppliance(id) {
        return get(`/appliances/${id}`);
    },
    
    async updateAppliance(id, data) {
        return put(`/appliances/${id}`, data);
    },
    
    async deleteAppliance(id) {
        return del(`/appliances/${id}`);
    },
    
    async detectAppliances() {
        return post('/appliances/detect');
    }
};

// Alerts API
export const alertsAPI = {
    async createAlert(data) {
        return post('/alerts/', data);
    },
    
    async getAlerts(unresolvedOnly = false) {
        return get(`/alerts/?unresolved_only=${unresolvedOnly}`);
    },
    
    async getAlert(id) {
        return get(`/alerts/${id}`);
    },
    
    async resolveAlert(id) {
        return put(`/alerts/${id}/resolve`);
    },
    
    async deleteAlert(id) {
        return del(`/alerts/${id}`);
    },
    
    async detectLeaks() {
        return post('/alerts/detect');
    }
};

// Predictions API
export const predictionsAPI = {
    async createPrediction(data) {
        return post('/predictions/', data);
    },
    
    async getPredictions(type = null) {
        const endpoint = type ? `/predictions/?prediction_type=${type}` : '/predictions/';
        return get(endpoint);
    },
    
    async generateDailyPrediction() {
        return post('/predictions/generate/daily');
    },
    
    async generateWeeklyPrediction() {
        return post('/predictions/generate/weekly');
    },
    
    async generateMonthlyPrediction() {
        return post('/predictions/generate/monthly');
    }
};

// Recommendations API
export const recommendationsAPI = {
    async createRecommendation(data) {
        return post('/recommendations/', data);
    },
    
    async getRecommendations(unimplementedOnly = false) {
        return get(`/recommendations/?unimplemented_only=${unimplementedOnly}`);
    },
    
    async getRecommendation(id) {
        return get(`/recommendations/${id}`);
    },
    
    async implementRecommendation(id) {
        return put(`/recommendations/${id}/implement`);
    },
    
    async deleteRecommendation(id) {
        return del(`/recommendations/${id}`);
    },
    
    async generateRecommendations() {
        return post('/recommendations/generate');
    }
};

// Chatbot API
export const chatbotAPI = {
    async ask(question) {
        const response = await fetch(`${API_BASE}/chatbot/ask?question=${encodeURIComponent(question)}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Chatbot request failed');
        }
        
        return await response.json();
    },
    
    async getChatHistory() {
        return get('/chatbot/history');
    },
    
    async clearChatHistory() {
        return del('/chatbot/history');
    }
};

// Reports API
export const reportsAPI = {
    async createReport(data) {
        return post('/reports/', data);
    },
    
    async getReports() {
        return get('/reports/');
    },
    
    async getReport(id) {
        return get(`/reports/${id}`);
    },
    
    async generateReport(reportType, startDate = null, endDate = null) {
        let url = `/reports/generate/${reportType}`;
        const params = [];
        
        if (startDate) params.push(`start_date=${startDate}`);
        if (endDate) params.push(`end_date=${endDate}`);
        
        if (params.length > 0) {
            url += `?${params.join('&')}`;
        }
        
        return post(url);
    },
    
    async downloadReport(id) {
        const token = getToken();
        window.location.href = `${API_BASE}/reports/download/${id}?token=${token}`;
    },
    
    async deleteReport(id) {
        return del(`/reports/${id}`);
    }
};

// Settings API
export const settingsAPI = {
    async createSettings(data) {
        return post('/settings/', data);
    },
    
    async getSettings() {
        return get('/settings/');
    },
    
    async updateSettings(data) {
        return put('/settings/', data);
    }
};

// Check auth on page load
requireAuth();
