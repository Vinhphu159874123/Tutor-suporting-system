const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3003;

// Middleware
app.use(cors());
app.use(express.json());

// Mock library resources
const mockBooks = [
  {
    id: 'LIB001',
    title: 'Introduction to Algorithms',
    author: 'Thomas H. Cormen, Charles E. Leiserson',
    isbn: '978-0262033848',
    category: 'Computer Science',
    publisher: 'MIT Press',
    year: 2009,
    edition: '3rd',
    available_copies: 5,
    total_copies: 10,
    location: 'CS-A-001',
    language: 'English'
  },
  {
    id: 'LIB002',
    title: 'Clean Code',
    author: 'Robert C. Martin',
    isbn: '978-0132350884',
    category: 'Software Engineering',
    publisher: 'Prentice Hall',
    year: 2008,
    edition: '1st',
    available_copies: 3,
    total_copies: 8,
    location: 'SE-B-045',
    language: 'English'
  },
  {
    id: 'LIB003',
    title: 'Design Patterns',
    author: 'Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides',
    isbn: '978-0201633610',
    category: 'Software Engineering',
    publisher: 'Addison-Wesley',
    year: 1994,
    edition: '1st',
    available_copies: 2,
    total_copies: 6,
    location: 'SE-B-123',
    language: 'English'
  },
  {
    id: 'LIB004',
    title: 'Database System Concepts',
    author: 'Abraham Silberschatz, Henry F. Korth',
    isbn: '978-0078022159',
    category: 'Database',
    publisher: 'McGraw-Hill',
    year: 2019,
    edition: '7th',
    available_copies: 4,
    total_copies: 7,
    location: 'DB-C-067',
    language: 'English'
  },
  {
    id: 'LIB005',
    title: 'Machine Learning Yearning',
    author: 'Andrew Ng',
    isbn: '978-0999820001',
    category: 'Artificial Intelligence',
    publisher: 'deeplearning.ai',
    year: 2018,
    edition: '1st',
    available_copies: 6,
    total_copies: 10,
    location: 'AI-D-089',
    language: 'English'
  }
];

// Mock borrowed books
const mockBorrowedBooks = {
  '2210001': [
    {
      book_id: 'LIB001',
      title: 'Introduction to Algorithms',
      borrow_date: '2024-01-15',
      due_date: '2024-02-15',
      status: 'borrowed'
    }
  ],
  '2210002': [
    {
      book_id: 'LIB002',
      title: 'Clean Code',
      borrow_date: '2024-01-20',
      due_date: '2024-02-20',
      status: 'borrowed'
    }
  ]
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'mock-hcmut-library' });
});

// Search books
app.get('/api/books/search', (req, res) => {
  const { query, category, author } = req.query;
  
  let results = [...mockBooks];
  
  if (query) {
    const searchTerm = query.toLowerCase();
    results = results.filter(book => 
      book.title.toLowerCase().includes(searchTerm) ||
      book.author.toLowerCase().includes(searchTerm) ||
      book.isbn.includes(searchTerm)
    );
  }
  
  if (category) {
    results = results.filter(book => 
      book.category.toLowerCase() === category.toLowerCase()
    );
  }
  
  if (author) {
    results = results.filter(book => 
      book.author.toLowerCase().includes(author.toLowerCase())
    );
  }
  
  res.json({
    success: true,
    data: {
      total: results.length,
      books: results
    }
  });
});

// Get book by ID
app.get('/api/books/:book_id', (req, res) => {
  const { book_id } = req.params;
  const book = mockBooks.find(b => b.id === book_id);
  
  if (!book) {
    return res.status(404).json({ 
      error: 'Book not found',
      book_id 
    });
  }
  
  res.json({
    success: true,
    data: book
  });
});

// Get all books
app.get('/api/books', (req, res) => {
  res.json({
    success: true,
    data: {
      total: mockBooks.length,
      books: mockBooks
    }
  });
});

// Get borrowed books for student
app.get('/api/students/:student_code/borrowed', (req, res) => {
  const { student_code } = req.params;
  const borrowed = mockBorrowedBooks[student_code] || [];
  
  res.json({
    success: true,
    data: {
      student_code,
      total: borrowed.length,
      borrowed_books: borrowed
    }
  });
});

// Get book categories
app.get('/api/categories', (req, res) => {
  const categories = [...new Set(mockBooks.map(book => book.category))];
  
  res.json({
    success: true,
    data: categories
  });
});

// Get new arrivals (last 3 books)
app.get('/api/books/new-arrivals', (req, res) => {
  const newBooks = mockBooks.slice(0, 3);
  
  res.json({
    success: true,
    data: {
      total: newBooks.length,
      books: newBooks
    }
  });
});

// Check book availability
app.get('/api/books/:book_id/availability', (req, res) => {
  const { book_id } = req.params;
  const book = mockBooks.find(b => b.id === book_id);
  
  if (!book) {
    return res.status(404).json({ 
      error: 'Book not found',
      book_id 
    });
  }
  
  res.json({
    success: true,
    data: {
      book_id,
      title: book.title,
      available_copies: book.available_copies,
      total_copies: book.total_copies,
      is_available: book.available_copies > 0
    }
  });
});

// Fallback for unknown routes
app.use((req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.path,
    available_endpoints: [
      'GET /health',
      'GET /api/books',
      'GET /api/books/search?query=<term>&category=<cat>&author=<name>',
      'GET /api/books/:book_id',
      'GET /api/books/:book_id/availability',
      'GET /api/books/new-arrivals',
      'GET /api/categories',
      'GET /api/students/:student_code/borrowed'
    ]
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Mock HCMUT Library service running on port ${PORT}`);
});
