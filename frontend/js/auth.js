// Authentication utility functions for managing JWT tokens and user authentication

const API_BASE = '';
const TOKEN_KEY = 'gallery_auth_token';
const USER_KEY = 'gallery_user_data';

/**
 * Save authentication token to localStorage
 * @param {string} token - JWT access token
 */
export function saveToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Get authentication token from localStorage
 * @returns {string|null} JWT access token or null if not found
 */
export function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Clear authentication token from localStorage (logout)
 */
export function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has a valid token
 */
export function isAuthenticated() {
    const token = getToken();
    return token !== null && token !== '';
}

/**
 * Save user data to localStorage
 * @param {object} userData - User information
 */
export function saveUserData(userData) {
    localStorage.setItem(USER_KEY, JSON.stringify(userData));
}

/**
 * Get user data from localStorage
 * @returns {object|null} User data or null if not found
 */
export function getUserData() {
    const data = localStorage.getItem(USER_KEY);
    return data ? JSON.parse(data) : null;
}

/**
 * Register a new user
 * @param {string} username - Username
 * @param {string} email - Email address
 * @param {string} password - Password
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function register(username, email, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        const data = await response.json();

        if (response.ok) {
            return { success: true, data };
        } else {
            return { 
                success: false, 
                error: data.detail || 'Registration failed' 
            };
        }
    } catch (error) {
        console.error('Registration error:', error);
        return { 
            success: false, 
            error: 'Network error. Please try again.' 
        };
    }
}

/**
 * Login user and save token
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function login(username, password) {
    try {
        // OAuth2 requires form data
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Save token
            saveToken(data.access_token);
            
            // Fetch and save user data
            const userResult = await getCurrentUser();
            if (userResult.success) {
                saveUserData(userResult.data);
            }
            
            return { success: true, data };
        } else {
            return { 
                success: false, 
                error: data.detail || 'Login failed' 
            };
        }
    } catch (error) {
        console.error('Login error:', error);
        return { 
            success: false, 
            error: 'Network error. Please try again.' 
        };
    }
}

/**
 * Get current authenticated user information
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function getCurrentUser() {
    const token = getToken();
    
    if (!token) {
        return { 
            success: false, 
            error: 'Not authenticated' 
        };
    }

    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            }
        });

        const data = await response.json();

        if (response.ok) {
            return { success: true, data };
        } else {
            // If token is invalid, clear it
            if (response.status === 401) {
                clearToken();
            }
            return { 
                success: false, 
                error: data.detail || 'Failed to get user info' 
            };
        }
    } catch (error) {
        console.error('Get current user error:', error);
        return { 
            success: false, 
            error: 'Network error. Please try again.' 
        };
    }
}

/**
 * Logout user (clear token and user data)
 */
export function logout() {
    clearToken();
    // Redirect to home page
    window.location.href = '/index.html';
}

/**
 * Check authentication and redirect to login if not authenticated
 * @param {boolean} requireAuth - Whether authentication is required
 */
export function checkAuthAndRedirect(requireAuth = false) {
    if (requireAuth && !isAuthenticated()) {
        // Store the current URL to redirect back after login
        const returnUrl = window.location.pathname + window.location.search;
        if (returnUrl !== '/login.html') {
            localStorage.setItem('return_url', returnUrl);
        }
        window.location.href = '/login.html';
    }
}

/**
 * Get and clear the return URL after login
 * @returns {string} The return URL or default to index
 */
export function getReturnUrl() {
    const returnUrl = localStorage.getItem('return_url');
    localStorage.removeItem('return_url');
    return returnUrl || '/index.html';
}
