// API base URL
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const loginForm = document.getElementById('loginForm');
const errorModal = new bootstrap.Modal(document.getElementById('errorModal'), {
    backdrop: false
});
const errorMessage = document.getElementById('errorMessage');

// Handle form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(loginForm);
    const data = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${data.username}&password=${data.password}`
        });

        if (response.ok) {
            const result = await response.json();
            localStorage.setItem('token', result.access_token);
            
            // Handle "Remember me" functionality
            if (document.getElementById('rememberMe').checked) {
                localStorage.setItem('rememberedUsername', data.username);
            } else {
                localStorage.removeItem('rememberedUsername');
            }
            
            // Redirect to home page
            window.location.href = 'index.html';
        } else {
            const error = await response.json();
            errorMessage.textContent = error.detail || 'Invalid username or password. Please try again.';
            errorModal.show();
        }
    } catch (error) {
        console.log(error);
        console.error('Login error:', error);
        errorMessage.textContent = 'An error occurred during login. Please try again.';
        errorModal.show();
    }
});

// Check for remembered username
document.addEventListener('DOMContentLoaded', () => {
    const rememberedUsername = localStorage.getItem('rememberedUsername');
    if (rememberedUsername) {
        document.getElementById('username').value = rememberedUsername;
        document.getElementById('rememberMe').checked = true;
    }
}); 