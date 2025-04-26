// src/contexts/CartContext.jsx
import React, {createContext, useState, useEffect, useCallback} from 'react';
import {useAuth} from '../hooks/useAuth';
import {
    getCart,
    addItemToCart,
    updateItemQuantity,
    removeItemFromCart,
    clearCartApi
} from '../services/api';
import {message} from 'antd';

export const CartContext = createContext(null);

export const CartProvider = ({children}) => {
    const {isAuthenticated} = useAuth();
    const [cartItems, setCartItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Функция для загрузки корзины с сервера
    const fetchCart = useCallback(async () => {
        if (!isAuthenticated) {
            setCartItems([]);
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const response = await getCart();
            setCartItems(response.data || []);
        } catch (err) {
            console.error("Ошибка загрузки корзины:", err);
            setError("Не удалось загрузить корзину.");
            message.error("Не удалось загрузить корзину.");
            setCartItems([]);
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated]);

    useEffect(() => {
        fetchCart();
    }, [fetchCart]);

    const addToCart = async (product, quantity = 1) => {
        if (!isAuthenticated) {
            message.warning('Пожалуйста, войдите, чтобы добавить товар в корзину.');
            return;
        }
        setLoading(true);
        try {
            await addItemToCart(product.id_product, quantity);
            message.success(`${product.name} добавлен в корзину!`);
            await fetchCart();
        } catch (err) {
            console.error("Ошибка добавления в корзину:", err);
            message.error(`Не удалось добавить ${product.name} в корзину.`);
        } finally {
            setLoading(false);
        }
    };

    const setCartItemQuantity = async (productId, newQuantity) => {
        const quantityToSend = Math.max(1, newQuantity);
        setLoading(true);
        try {
            await updateItemQuantity(productId, quantityToSend);
            await fetchCart();
        } catch (err) {
            console.error("Ошибка обновления количества:", err);
            message.error("Не удалось обновить количество товара.");
        } finally {
            setLoading(false);
        }
    };


    const removeFromCart = async (productId) => {
        setLoading(true);
        try {
            await removeItemFromCart(productId);
            message.success(`Товар удален из корзины.`);
            await fetchCart(); // Перезагружаем
        } catch (err) {
            console.error("Ошибка удаления из корзины:", err);
            message.error("Не удалось удалить товар из корзины.");
        } finally {
            setLoading(false);
        }
    };

    const clearCart = async () => {
        setLoading(true);
        try {
            await clearCartApi();
            message.success('Корзина очищена.');
            setCartItems([]);
        } catch (err) {
            console.error("Ошибка очистки корзины:", err);
            message.error("Не удалось очистить корзину.");
        } finally {
            setLoading(false);
        }
    };

    const getTotalItems = () => {
        return cartItems.reduce((total, item) => total + item.quantity, 0);
    };

    const getTotalPrice = () => {
        return cartItems.reduce((total, item) => {
            const price = item.product?.price_per_unit ?? 0;
            return total + price * item.quantity;
        }, 0);
    };

    const value = {
        cartItems,
        loading,
        error,
        fetchCart,
        addToCart,
        setCartItemQuantity,
        removeFromCart,
        clearCart,
        getTotalItems,
        getTotalPrice,
    };

    return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
