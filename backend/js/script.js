// API endpoints
const API_URL = 'http://localhost:8000';

// DOM Elements
const loginForm = document.querySelector('.login-form form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const loginButton = document.querySelector('.login-button');

// Error handling
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    loginForm.insertBefore(errorDiv, loginButton);
    setTimeout(() => errorDiv.remove(), 5000);
}

// Token management
function setToken(token) {
    localStorage.setItem('access_token', token);
}

function getToken() {
    return localStorage.getItem('access_token');
}

function removeToken() {
    localStorage.removeItem('access_token');
}

// API calls
async function login(email, password) {
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        setToken(data.access_token);
        window.location.href = '/dashboard.html'; // Redirect to dashboard
    } catch (error) {
        showError(error.message);
    }
}

async function register(email, password, fullName) {
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, full_name: fullName }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
        }

        setToken(data.access_token);
        window.location.href = '/dashboard.html'; // Redirect to dashboard
    } catch (error) {
        showError(error.message);
    }
}

// Form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
        showError('Please fill in all fields');
        return;
    }

    loginButton.disabled = true;
    loginButton.textContent = 'Entrando...';

    try {
        await login(email, password);
    } finally {
        loginButton.disabled = false;
        loginButton.textContent = 'Entrar';
    }
});

// Check authentication status
function checkAuth() {
    const token = getToken();
    if (token) {
        // If user is already logged in, redirect to dashboard
        window.location.href = '/dashboard.html';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
}); 