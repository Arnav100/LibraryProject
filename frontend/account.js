// API base URL
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const logoutBtn = document.getElementById('logoutBtn');
const userName = document.getElementById('userName');
const userUsername = document.getElementById('userUsername');
const checkoutsTableBody = document.getElementById('checkoutsTableBody');
const holdsTableBody = document.getElementById('holdsTableBody');
const returnBookModal = new bootstrap.Modal(document.getElementById('returnBookModal'));
const cancelHoldModal = new bootstrap.Modal(document.getElementById('cancelHoldModal'));
const confirmReturn = document.getElementById('confirmReturn');
const confirmCancelHold = document.getElementById('confirmCancelHold');

// State
let currentUser = null;
let currentCheckoutId = null;
let currentHoldId = null;

// WebSocket connection
let socket = null;

function connectWebSocket(userId) {
    if (socket) {
        socket.close();
    }
    
    socket = new WebSocket(`ws://localhost:8000/ws/${userId}`);
    
    socket.onmessage = (event) => {
        const notification = JSON.parse(event.data);
        if (notification.type === 'hold_updated') {
            showToast(notification.message, 'info');
            loadHolds(); // Refresh the holds list
        }
    };
    
    socket.onclose = () => {
        console.log('WebSocket connection closed');
        // Try to reconnect after 5 seconds
        setTimeout(() => connectWebSocket(userId), 5000);
    };
}

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    loadUserProfile();
    loadCheckouts();
    loadHolds();
}

// Load user profile
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/user/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            currentUser = user;
            userName.textContent = user.name;
            userUsername.textContent = `@${user.username}`;
            
            // Connect WebSocket
            connectWebSocket(user.id);
        } else {
            throw new Error('Failed to load user profile');
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
        alert('Failed to load user profile. Please try again.');
    }
}

// Load checkouts
async function loadCheckouts() {
    try {
        const response = await fetch(`${API_BASE_URL}/checkouts/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const checkouts = await response.json();
            displayCheckouts(checkouts);
        } else {
            throw new Error('Failed to load checkouts');
        }
    } catch (error) {
        console.error('Error loading checkouts:', error);
        alert('Failed to load checkouts. Please try again.');
    }
}

// Display checkouts
function displayCheckouts(checkouts) {
    checkoutsTableBody.innerHTML = '';
    checkouts.forEach(checkout => {
        const row = document.createElement('tr');
        const dueDate = new Date(checkout.end_date);
        const isOverdue = dueDate < new Date() && !checkout.returned;
        
        row.innerHTML = `
            <td>${checkout.book.name}</td>
            <td>${checkout.book.author}</td>
            <td>${new Date(checkout.start_date).toLocaleDateString()}</td>
            <td>${dueDate.toLocaleDateString()}</td>
            <td>
                <span class="badge bg-${checkout.returned ? 'success' : isOverdue ? 'danger' : 'warning'}">
                    ${checkout.returned ? 'Returned' : isOverdue ? 'Overdue' : 'Checked Out'}
                </span>
            </td>
            <td>
                ${!checkout.returned ? `
                    <button class="btn btn-sm btn-warm return-btn" data-checkout-id="${checkout.id}">
                        <i class="fas fa-undo me-1"></i>Return
                    </button>
                ` : ''}
            </td>
        `;
        checkoutsTableBody.appendChild(row);
    });

    // Add event listeners to return buttons
    document.querySelectorAll('.return-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            currentCheckoutId = e.target.closest('.return-btn').dataset.checkoutId;
            returnBookModal.show();
        });
    });
}

// Load holds
async function loadHolds() {
    try {
        const response = await fetch(`${API_BASE_URL}/holds/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const holds = await response.json();
            displayHolds(holds);
        } else {
            throw new Error('Failed to load holds');
        }
    } catch (error) {
        console.error('Error loading holds:', error);
        alert('Failed to load holds. Please try again.');
    }
}

// Display holds
function displayHolds(holds) {
    holdsTableBody.innerHTML = '';
    holds.forEach(hold => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${hold.book.name}</td>
            <td>${hold.book.author}</td>
            <td>${new Date(hold.hold_date).toLocaleDateString()}</td>
            <td>${hold.position}</td>
            <td>
                <span class="badge bg-${hold.position === 1 ? 'success' : 'warning'}">
                    ${hold.position === 1 ? "You're next!" : 'Waiting'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-warm cancel-hold-btn" data-hold-id="${hold.id}">
                    <i class="fas fa-times me-1"></i>Cancel
                </button>
            </td>
        `;
        holdsTableBody.appendChild(row);
    });

    // Add event listeners to cancel buttons
    document.querySelectorAll('.cancel-hold-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            currentHoldId = e.target.closest('.cancel-hold-btn').dataset.holdId;
            cancelHoldModal.show();
        });
    });
}

// Handle return book
confirmReturn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/return`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                checkout_id: currentCheckoutId
            })
        });

        if (response.ok) {
            returnBookModal.hide();
            loadCheckouts();
            alert('Book returned successfully!');
        } else {
            throw new Error('Failed to return book');
        }
    } catch (error) {
        console.error('Error returning book:', error);
        alert('Failed to return book. Please try again.');
    }
});

// Handle cancel hold
confirmCancelHold.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/holds/${currentHoldId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            cancelHoldModal.hide();
            loadHolds();
            alert('Hold cancelled successfully!');
        } else {
            throw new Error('Failed to cancel hold');
        }
    } catch (error) {
        console.error('Error cancelling hold:', error);
        alert('Failed to cancel hold. Please try again.');
    }
});

// Handle logout
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
});

// Initialize
document.addEventListener('DOMContentLoaded', checkAuth); 