import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Badge } from 'antd';
import { ShoppingCartOutlined, LoginOutlined, LogoutOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import CartDrawer from './CartDrawer';

const Header = () => {
    const { isAuthenticated, user, logout } = useAuth();
    const { getTotalItems } = useCart();
    const navigate = useNavigate();

    const [isCartVisible, setCartVisible] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/auth');
    };

    const showCart = () => {
        setCartVisible(true);
    };

    const closeCart = () => {
        setCartVisible(false);
    };

    return (
        <>
            <header className="bg-white shadow-md p-4 flex justify-between items-center sticky top-0 z-10">
                <Link to="/" className="text-2xl font-bold text-green-600">
                    FruitShop
                </Link>
                <div className="flex items-center space-x-4">
                    <Button
                        type="text"
                        onClick={showCart}
                        icon={
                            <Badge count={getTotalItems()} size="default">
                                <ShoppingCartOutlined className="text-2xl text-gray-700 hover:text-green-600" />
                            </Badge>
                        }
                    />

                    {isAuthenticated ? (
                        <>
                            <span className="hidden md:inline">Привет, {user?.username}!</span>
                            <Button icon={<LogoutOutlined />} onClick={handleLogout}>
                                Выйти
                            </Button>
                        </>
                    ) : (
                        <Link to="/auth">
                            <Button type="primary" icon={<LoginOutlined />}>
                                Войти
                            </Button>
                        </Link>
                    )}
                </div>
            </header>

            <CartDrawer visible={isCartVisible} onClose={closeCart} />
        </>
    );
};

export default Header;
