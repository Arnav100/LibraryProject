// API base URL
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const searchInput = document.getElementById('searchInput');
const recentBooksContainer = document.getElementById('recentBooks');

// Event Listeners
loginBtn.addEventListener('click', () => loginModal.show());
registerBtn.addEventListener('click', () => registerModal.show());

// Login functionality
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
            loginModal.hide();
            updateAuthState();
            showToast('Login successful!', 'success');
        } else {
            showToast('Login failed. Please check your credentials.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('An error occurred during login.', 'error');
    }
});

// Registration functionality
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const data = {
        name: formData.get('name'),
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showToast('Registration successful! Please login.', 'success');
            registerModal.hide();
        } else {
            showToast('Registration failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('An error occurred during registration.', 'error');
    }
});

// Search functionality
let searchTimeout;
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const searchTerm = e.target.value;
    
    if (searchTerm.length > 2) {
        searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/search?title=${searchTerm}`);
                if (response.ok) {
                    const books = await response.json();
                    displayBooks(books);
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        }, 300);
    }
});

// Book display functions
function createBookCard(book) {
    const card = document.createElement('div');
    card.className = 'col-md-4 col-sm-6';
    card.innerHTML = `
        <div class="book-card">
            <h3>${book.name}</h3>
            <p><i class="fas fa-user me-2"></i>${book.author}</p>
            <p><i class="fas fa-barcode me-2"></i>${book.isbn}</p>
            <p><i class="fas fa-copy me-2"></i>Available Copies: ${book.total_copies}</p>
            <button class="btn btn-warm checkout-btn" data-book-id="${book.id}">
                <i class="fas fa-shopping-cart me-2"></i>Checkout
            </button>
        </div>
    `;
    return card;
}

function displayBooks(books) {
    recentBooksContainer.innerHTML = '';
    books.forEach(book => {
        recentBooksContainer.appendChild(createBookCard(book));
    });
}

// Load recent books on page load
async function loadRecentBooks() {
    try {
        const response = await fetch(`${API_BASE_URL}/books`);
        if (response.ok) {
            const books = await response.json();
            displayBooks(books);
        }
    } catch (error) {
        console.error('Error loading books:', error);
        showToast('Error loading books. Please try again later.', 'error');
    }
}

// Update authentication state
function updateAuthState() {
    const token = localStorage.getItem('token');
    if (token) {
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        // Add user profile button or other authenticated UI elements
    } else {
        loginBtn.style.display = 'block';
        registerBtn.style.display = 'block';
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
    loadRecentBooks();
    updateAuthState();
}); 