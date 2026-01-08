/**
 * Budget App Frontend JavaScript
 * 
 * Security: Using .textContent for XSS protection (OWASP A03)
 * All API requests include JWT bearer token
 */

const API_BASE = '';
let authToken = null;
let currentUser = null;

// Category mappings
const INCOME_CATEGORIES = {
    'salary': 'Salary',
    'freelance': 'Freelance',
    'investment': 'Investment',
    'other_income': 'Other Income'
};

const EXPENSE_CATEGORIES = {
    'housing': 'Housing',
    'transportation': 'Transportation',
    'food': 'Food',
    'utilities': 'Utilities',
    'healthcare': 'Healthcare',
    'entertainment': 'Entertainment',
    'shopping': 'Shopping',
    'other_expense': 'Other Expense'
};

// Security: Using .textContent to prevent XSS attacks
function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.classList.add('active');
    setTimeout(() => errorEl.classList.remove('active'), 5000);
}

function hideError(elementId) {
    const errorEl = document.getElementById(elementId);
    errorEl.classList.remove('active');
}

// Security: Store token in memory only (not localStorage for security)
function setAuthToken(token) {
    authToken = token;
}

function getAuthHeaders() {
    return {
        'Content-Type': 'application/json',
        ...(authToken && { 'Authorization': `Bearer ${authToken}` })
    };
}

// Auth Functions
async function login(email, password) {
    try {
        // Security: Send credentials in request body, not URL (OWASP A02)
        const formData = new URLSearchParams();
        formData.append('email', email);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            // Log the error for debugging (remove in production)
            console.error('Login error:', error);
            throw new Error(error.detail || 'Login failed');
        }
        
        const data = await response.json();
        setAuthToken(data.access_token);
        await loadDashboard();
    } catch (error) {
        console.error('Login exception:', error);
        showError('login-error', error.message);
    }
}

async function register(name, email, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                full_name: name,
                email: email,
                password: password
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            // Handle Pydantic validation errors (422) and regular errors
            if (error.detail) {
                // Check if detail is an array (Pydantic validation errors)
                if (Array.isArray(error.detail)) {
                    const errorMsg = error.detail.map(err => err.msg).join(', ');
                    throw new Error(errorMsg);
                } else if (typeof error.detail === 'string') {
                    throw new Error(error.detail);
                } else {
                    throw new Error(JSON.stringify(error.detail));
                }
            }
            throw new Error('Registration failed');
        }
        
        // Auto-login after successful registration
        await login(email, password);
    } catch (error) {
        showError('register-error', error.message);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    
    // Clear form inputs to prevent issues with cached values
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';
    document.getElementById('register-name').value = '';
    document.getElementById('register-email').value = '';
    document.getElementById('register-password').value = '';
    
    // Clear any error messages
    hideError('login-error');
    hideError('register-error');
    
    showAuthPage();
}

// Dashboard Functions
async function loadDashboard() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('dashboard-container').style.display = 'block';
    
    await Promise.all([
        loadBalance(),
        loadTransactions()
    ]);
}

async function loadBalance() {
    try {
        const response = await fetch(`${API_BASE}/transactions/balance/current`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to load balance');
        
        const data = await response.json();
        
        // Security: Using .textContent to prevent XSS
        document.getElementById('current-balance').textContent = formatCurrency(data.current_balance);
        document.getElementById('total-income').textContent = formatCurrency(data.total_income);
        document.getElementById('total-expenses').textContent = formatCurrency(data.total_expenses);
    } catch (error) {
        console.error('Failed to load balance:', error);
    }
}

async function loadTransactions() {
    try {
        const response = await fetch(`${API_BASE}/transactions`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to load transactions');
        
        const transactions = await response.json();
        renderTransactions(transactions);
    } catch (error) {
        console.error('Failed to load transactions:', error);
    }
}

function renderTransactions(transactions) {
    const listEl = document.getElementById('transactions-list');
    
    if (transactions.length === 0) {
        // Security: Using .textContent
        listEl.textContent = 'No transactions yet. Add your first transaction above!';
        listEl.style.color = 'var(--color-text-secondary)';
        listEl.style.textAlign = 'center';
        listEl.style.padding = 'var(--space-lg)';
        return;
    }
    
    listEl.innerHTML = '';
    listEl.style = '';
    
    transactions.forEach(transaction => {
        const item = document.createElement('div');
        item.className = 'transaction-item';
        
        // Icon
        const icon = document.createElement('div');
        icon.className = `transaction-icon ${transaction.type}`;
        // Security: Using .textContent
        icon.textContent = transaction.type === 'income' ? '+' : '-';
        
        // Details
        const details = document.createElement('div');
        details.className = 'transaction-details';
        
        const category = document.createElement('div');
        category.className = 'transaction-category';
        // Security: Using .textContent to prevent XSS
        category.textContent = formatCategory(transaction.category);
        
        const description = document.createElement('div');
        description.className = 'transaction-description';
        // Security: Using .textContent to prevent XSS
        description.textContent = transaction.description || 'No description';
        
        details.appendChild(category);
        details.appendChild(description);
        
        // Date
        const date = document.createElement('div');
        date.className = 'transaction-date';
        date.textContent = formatDate(transaction.date);
        
        // Amount
        const amount = document.createElement('div');
        amount.className = `transaction-amount ${transaction.type}`;
        const sign = transaction.type === 'income' ? '+' : '-';
        amount.textContent = `${sign}${formatCurrency(transaction.amount)}`;
        
        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'transaction-delete';
        deleteBtn.textContent = 'Delete';
        deleteBtn.onclick = () => deleteTransaction(transaction.public_id);
        
        item.appendChild(icon);
        item.appendChild(details);
        item.appendChild(date);
        item.appendChild(amount);
        item.appendChild(deleteBtn);
        
        listEl.appendChild(item);
    });
}

async function createTransaction(type, category, amount, description) {
    try {
        const response = await fetch(`${API_BASE}/transactions`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                type,
                category,
                amount: parseFloat(amount),
                description: description || ''
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create transaction');
        }
        
        // Reload data
        await Promise.all([
            loadBalance(),
            loadTransactions()
        ]);
        
        // Clear form
        document.getElementById('transaction-form').reset();
        hideError('transaction-error');
    } catch (error) {
        showError('transaction-error', error.message);
    }
}

async function deleteTransaction(transactionId) {
    if (!confirm('Are you sure you want to delete this transaction?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/transactions/${transactionId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to delete transaction');
        
        // Reload data
        await Promise.all([
            loadBalance(),
            loadTransactions()
        ]);
    } catch (error) {
        console.error('Failed to delete transaction:', error);
        alert('Failed to delete transaction. Please try again.');
    }
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    }).format(date);
}

function formatCategory(category) {
    return category.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function updateCategoryOptions(type) {
    const categorySelect = document.getElementById('transaction-category');
    categorySelect.innerHTML = '';
    
    const categories = type === 'income' ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;
    
    Object.entries(categories).forEach(([value, label]) => {
        const option = document.createElement('option');
        option.value = value;
        // Security: Using .textContent
        option.textContent = label;
        categorySelect.appendChild(option);
    });
}

function showAuthPage() {
    document.getElementById('auth-container').style.display = 'flex';
    document.getElementById('dashboard-container').style.display = 'none';
    document.getElementById('login-page').classList.add('active');
    document.getElementById('register-page').classList.remove('active');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError('login-error');
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        await login(email, password);
    });
    
    // Register form
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError('register-error');
        
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        
        await register(name, email, password);
    });
    
    // Toggle between login and register
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('login-page').classList.remove('active');
        document.getElementById('register-page').classList.add('active');
    });
    
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('register-page').classList.remove('active');
        document.getElementById('login-page').classList.add('active');
    });
    
    // Logout
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Transaction form
    document.getElementById('transaction-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError('transaction-error');
        
        const type = document.getElementById('transaction-type').value;
        const category = document.getElementById('transaction-category').value;
        const amount = document.getElementById('transaction-amount').value;
        const description = document.getElementById('transaction-description').value;
        
        await createTransaction(type, category, amount, description);
    });
    
    // Update categories when type changes
    document.getElementById('transaction-type').addEventListener('change', (e) => {
        updateCategoryOptions(e.target.value);
    });
    
    // Initialize category options
    updateCategoryOptions('income');
    
    // Check if user is logged in
    if (authToken) {
        loadDashboard();
    }
});
