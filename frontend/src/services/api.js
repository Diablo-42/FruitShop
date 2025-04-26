import axios from 'axios';

const API_URL = 'http://127.0.0.1:5001';

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// --- Функции API ---
export const loginUser = (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return apiClient.post('/users/token', formData, {
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    });
};

export const registerUser = (userData) => {
    return apiClient.post('/users/register', userData);
};

export const getCurrentUser = () => {
    return apiClient.get('/users/me');
}

export const getCategories = () => {
    return apiClient.get('/category/all');
};

export const getAllProducts = () => {
    return apiClient.get('/product/all');
};

export const getProductsByCategory = (categoryId) => {
    if (!categoryId) return getAllProducts();
    return apiClient.get(`/category/${categoryId}/products`);
};

export const getCart = () => {
    return apiClient.get('/cart');
};

export const addItemToCart = (productId, quantity = 1) => {
    return apiClient.post('/cart/items', {product_id: productId, quantity});
};

export const updateItemQuantity = (productId, quantity) => {
    const validQuantity = Math.max(1, quantity);
    return apiClient.put(`/cart/items/${productId}`, {quantity: validQuantity});
};

export const removeItemFromCart = (productId) => {
    return apiClient.delete(`/cart/items/${productId}`);
};

export const clearCartApi = () => {
    return apiClient.delete('/cart');
};

export default apiClient;