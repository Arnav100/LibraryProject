// Dummy data for books
const dummyBooks = [
    {
        id: 1,
        name: "The Great Gatsby",
        author: "F. Scott Fitzgerald",
        isbn: "9780743273565",
        total_copies: 5,
        available_copies: 3,
        created_at: "2023-01-15T10:30:00Z",
        cover_url: "https://covers.openlibrary.org/b/isbn/9780743273565-L.jpg",
        description: "A novel about the American Dream"
    },
    {
        id: 2,
        name: "To Kill a Mockingbird",
        author: "Harper Lee",
        isbn: "9780446310789",
        total_copies: 4,
        available_copies: 2,
        created_at: "2023-02-20T14:45:00Z",
        cover_url: "https://covers.openlibrary.org/b/isbn/9780446310789-L.jpg",
        description: "A novel about the American Dream"
    },
    {
        id: 3,
        name: "1984",
        author: "George Orwell",
        isbn: "9780451524935",
        total_copies: 6,
        available_copies: 4,
        created_at: "2023-03-10T09:15:00Z",
        cover_url: "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg"
    },
    {
        id: 4,
        name: "Pride and Prejudice",
        author: "Jane Austen",
        isbn: "9780141439518",
        total_copies: 3,
        available_copies: 1,
        created_at: "2023-04-05T11:20:00Z",
        cover_url: "https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg"
    },
    {
        id: 5,
        name: "The Catcher in the Rye",
        author: "J.D. Salinger",
        isbn: "9780316769488",
        total_copies: 4,
        available_copies: 2,
        created_at: "2023-05-12T16:30:00Z",
        cover_url: "https://covers.openlibrary.org/b/isbn/9780316769488-L.jpg"
    },
    {
        id: 6,
        name: "Brave New World",
        author: "Aldous Huxley",
        isbn: "9780060850524",
        total_copies: 5,
        available_copies: 3,
        created_at: "2023-06-18T13:45:00Z",
        cover_url: "https://covers.openlibrary.org/b/isbn/9780060850524-L.jpg"
    }
];

// DOM Elements
const booksGrid = document.getElementById('booksGrid');
const searchInput = document.getElementById('searchInput');
const sortDropdown = document.getElementById('sortDropdown');

const API_BASE_URL = 'http://localhost:8000';
// Create book card
function createBookCard(book) {
    const card = document.createElement('div');
    card.className = 'col-md-4 col-sm-6';
    card.innerHTML = `
        <div class="book-card">
            <div class="book-cover">
                <img src="${book.cover_url || 'https://via.placeholder.com/200x300'}" 
                     class="img-fluid rounded" 
                     alt="${book.name}">
            </div>
            <div class="book-info mt-3">
                <h3 class="h5 text-warm">${book.name}</h3>
                <p class="text-muted"><i class="fas fa-user me-2"></i>${book.author}</p>
                <p class="text-muted"><i class="fas fa-barcode me-2"></i>${book.isbn}</p>
                <div class="d-flex justify-content-between align-items-center mt-2">
                    <span class="badge bg-${book.available_copies > 0 ? 'success' : 'danger'}">
                        ${book.available_copies} Available
                    </span>
                    <button class="btn btn-sm btn-warm view-details" data-book-id="${book.id}">
                        View Details
                    </button>
                </div>
            </div>
        </div>
    `;
    return card;
}

// Display books
function displayBooks(books) {
    booksGrid.innerHTML = '';
    books.forEach(book => {
        booksGrid.appendChild(createBookCard(book));
    });
    addViewDetailsListeners(books);
}

// Show book details in modal
function showBookDetails(book) {
    const modal = new bootstrap.Modal(document.getElementById('bookDetailModal'), {
        backdrop: false
    });
    
    // Update modal content
    document.getElementById('modalBookTitle').textContent = book.name;
    document.getElementById('modalBookAuthor').textContent = `by ${book.author}`;
    document.getElementById('modalBookISBN').textContent = book.isbn;
    document.getElementById('modalBookAvailable').textContent = book.available_copies;
    
    // Update book cover
    const modalImage = document.querySelector('#bookDetailModal .modal-body img');
    modalImage.src = book.cover_url || 'https://via.placeholder.com/300x400';
    modalImage.alt = book.name;
    // modalImage.onerror = function() {
    //     this.src = 'https://via.placeholder.com/300x400?text=No+Cover';
    // };
    
    // Add description
    document.getElementById('modalBookDescription').textContent = 
        `${book.description}. The book was added to our library on ${new Date(book.created_at).toLocaleDateString()}.`;
    
    // Add checkout button functionality
    const checkoutBtn = document.querySelector('#bookDetailModal .checkout-btn');
    checkoutBtn.onclick = function() {
        if (book.available_copies > 0) {
            // Add checkout logic here
            alert(`Checking out ${book.name}`);
            modal.hide();
        } else {
            alert('Sorry, this book is currently not available.');
        }
    };
    
    // Show the modal
    modal.show();
}

// Add event listeners for view details buttons
function addViewDetailsListeners(books) {
    document.querySelectorAll('.view-details').forEach(button => {
        button.addEventListener('click', (e) => {
            const bookId = parseInt(e.target.dataset.bookId);
            const book = books.find(b => b.id === bookId);
            if (book) {
                console.log(book);
                showBookDetails(book);
            }
        });
    });
}


// Initialize
document.addEventListener('DOMContentLoaded', () => {

    fetch(`${API_BASE_URL}/books`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem("token")}`,
            'Accept': 'application/json'
        },
        credentials: 'include',
    })
        .then(response => response.json())
        .then(books => {
            displayBooks(books);
                // Search functionality
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const searchTerm = e.target.value.toLowerCase();
                
                searchTimeout = setTimeout(() => {
                    const filteredBooks = books.filter(book => 
                        book.name.toLowerCase().includes(searchTerm) ||
                        book.author.toLowerCase().includes(searchTerm) ||
                        book.isbn.includes(searchTerm)
                    );
                    displayBooks(filteredBooks);
                }, 300);
            });

            // Sort functionality
            document.querySelectorAll('.dropdown-item[data-sort]').forEach(item => {
                item.addEventListener('click', (e) => {
                    const sortBy = e.target.dataset.sort;
                    let sortedBooks = [...books];
                    
                    switch(sortBy) {
                        case 'title':
                            sortedBooks.sort((a, b) => a.name.localeCompare(b.name));
                            break;
                        case 'author':
                            sortedBooks.sort((a, b) => a.author.localeCompare(b.author));
                            break;
                        case 'available':
                            sortedBooks.sort((a, b) => b.available_copies - a.available_copies);
                            break;
                    }
                    
                    displayBooks(sortedBooks);
                });
            });
        })
        .catch(error => {
            console.error('Error fetching books:', error);
        });

}); 