import React, { createContext, useState, useContext, useEffect } from 'react';

const CartContext = createContext(null);

// Загрузка корзины из localStorage
const initialCart = JSON.parse(localStorage.getItem('cart') || '[]');

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState(initialCart);

  // Сохранение корзины в localStorage при изменении
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cartItems));
  }, [cartItems]);

  const addToCart = (product, quantity = 1) => {
    setCartItems((prevItems) => {
      const existingItem = prevItems.find(item => item.product.id_product === product.id_product);
      if (existingItem) {
        // Увеличиваем количество, если товар уже в корзине
        return prevItems.map(item =>
          item.product.id_product === product.id_product
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        // Добавляем новый товар
        return [...prevItems, { product, quantity }];
      }
    });
  };

  const updateQuantity = (productId, amount) => {
     setCartItems((prevItems) =>
        prevItems.map(item =>
           item.product.id_product === productId
           ? { ...item, quantity: Math.max(1, item.quantity + amount) } // Не даем уйти в 0 или меньше
           : item
        )
     );
  };

  const removeFromCart = (productId) => {
    setCartItems((prevItems) =>
      prevItems.filter(item => item.product.id_product !== productId)
    );
  };

  const clearCart = () => {
    setCartItems([]);
  };

  const getTotalItems = () => {
    return cartItems.reduce((total, item) => total + item.quantity, 0);
  };

  const getTotalPrice = () => {
    return cartItems.reduce((total, item) => total + item.product.price_per_unit * item.quantity, 0);
  };


  const value = {
    cartItems,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    getTotalItems,
    getTotalPrice,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

export const useCart = () => {
  return useContext(CartContext);
};
