// API base URL
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');

// WebSocket connection
function connectWebSocket(userId) {
    try {
        if (window.socket && window.socket.readyState !== WebSocket.CLOSED) {
            window.socket.close();
        }
        
        window.socket = new WebSocket(`ws://localhost:8000/ws/${userId}`);
        
        window.socket.onopen = () => {
            console.log('WebSocket connection established');
        };
        
        window.socket.onmessage = (event) => {
            try {
                console.log(event)
                const notification = JSON.parse(JSON.parse(event.data)).payload;

                console.log(notification);
                console.log(notification.type);
                if (notification.type === 'hold_updated') {
                    console.log('In hold updated');
                    showToast(notification.message, 'info');
                    // If we're on the holds page, refresh the holds list
                    if (window.location.pathname.includes('account.html')) {
                        loadHolds();
                    }
                }
            } catch (error) {
                console.error('Error processing notification:', error);
            }
        };
        
        window.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        window.socket.onclose = () => {
            console.log('WebSocket connection closed');
            // Try to reconnect after 5 seconds
            setTimeout(() => connectWebSocket(userId), 5000);
        };
    } catch (error) {
        console.error('Error connecting to WebSocket:', error);
    }
}

// Update authentication state
function updateAuthState() {
    const token = localStorage.getItem('token');
    const authContainer = document.querySelector('.d-flex');
    
    if (token) {
        // User is logged in
        authContainer.innerHTML = `
            <button id="logoutBtn" class="btn btn-outline-light">Logout</button>
        `;
        
        // Add logout functionality
        document.getElementById('logoutBtn').addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        });
    } else {
        // User is not logged in
        authContainer.innerHTML = `
            <a href="login.html" class="btn btn-outline-light me-2">Login</a>
            <a href="register.html" class="btn btn-warm">Register</a>
        `;
    }
}

// Toast notification function
function showToast(message, type = 'info') {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toastContainer.remove();
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateAuthState();
}); 