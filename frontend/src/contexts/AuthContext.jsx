import React, {createContext, useState, useEffect} from 'react'; // Убрали useContext
import {loginUser as apiLogin, registerUser as apiRegister, getCurrentUser} from '../services/api';

export const AuthContext = createContext(null);

export const AuthProvider = ({children}) => {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadUser = async () => {
            if (token) {
                try {
                    const response = await getCurrentUser();
                    setUser(response.data);
                } catch (error) {
                    console.error("Failed to fetch user or token expired", error);
                    localStorage.removeItem('token');
                    setToken(null);
                    setUser(null);
                }
            }
            setLoading(false);
        };
        loadUser();
    }, [token]);

    const login = async (username, password) => {
        try {
            const response = await apiLogin(username, password); // Вызываем API
            const {access_token} = response.data;
            localStorage.setItem('token', access_token); // Сохраняем токен
            setToken(access_token);
            return true;
        } catch (error) {
            console.error("Ошибка входа:", error);
            localStorage.removeItem('token');
            setToken(null);
            setUser(null);
            throw error;
        }
    };

    const register = async (userData) => {
        try {
            const response = await apiRegister(userData);
            await login(userData.username, userData.password);
            return response.data;
        } catch (error) {
            console.error("Ошибка регистрации:", error);
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        navigate('/auth');
    };

    const value = {
        token,
        user,
        isAuthenticated: !!token && !!user,
        loading,
        login,
        register,
        logout,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};