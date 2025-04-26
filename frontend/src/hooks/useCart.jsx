import {useContext} from 'react';
import {CartContext} from '../contexts/CartContext';

export const useCart = () => {
    const context = useContext(CartContext);
    if (context === null) {
        throw new Error('useCart должен использоваться внутри CartProvider');
    }
    return context;
};