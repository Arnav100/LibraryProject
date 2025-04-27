// API base URL
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const addBookForm = document.getElementById('addBookForm');
const logoutBtn = document.getElementById('logoutBtn');
const successModal = new bootstrap.Modal(document.getElementById('successModal'), {
    backdrop: false
});

const adminTokenField = "token";    

// Check admin authentication
function checkAdminAuth() {
    const token = localStorage.getItem(adminTokenField);
    if (!token) {
        window.location.href = 'index.html';
    }
}

// Handle form submission
addBookForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const bookData = {
        name: document.getElementById('bookName').value,
        author: document.getElementById('bookAuthor').value,
        isbn: document.getElementById('bookISBN').value,
        total_copies: parseInt(document.getElementById('totalCopies').value),
        cover_url: document.getElementById('bookCover').value || null,
        description: document.getElementById('bookDescription').value || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/books`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem(adminTokenField)}`,
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(bookData)
        });

        if (response.ok) {
            // Show success modal
            successModal.show();
            // Reset form
            addBookForm.reset();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to add book');
        }
    } catch (error) {
        console.error('Error adding book:', error);
        alert('Failed to add book. Please try again.');
    }
});

// Handle logout
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem(adminTokenField);
    window.location.href = 'index.html';
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAdminAuth();
}); 