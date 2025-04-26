import React, { createContext, useState, useContext, useEffect } from 'react';
import { loginUser as apiLogin, registerUser as apiRegister, getCurrentUser } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // Для начальной загрузки пользователя

  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          // Запрос к /users/me для получения актуальных данных пользователя
          const response = await getCurrentUser();
          setUser(response.data);
        } catch (error) {
          console.error("Failed to fetch user or token expired", error);
          // Токен невалиден или истек, очищаем
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };
    loadUser();
  }, [token]); // Перезагружаем пользователя при изменении токена

  const login = async (username, password) => {
    try {
      const response = await apiLogin(username, password);
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token); // Это вызовет useEffect для загрузки пользователя
      // setUser можно установить сразу, если /token возвращает юзера, но лучше через /users/me
      return true; // Успешный вход
    } catch (error) {
      console.error("Login failed", error);
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      throw error; // Передаем ошибку дальше для отображения
    }
  };

  const register = async (userData) => {
     try {
        await apiRegister(userData);
        // Можно сразу логинить пользователя после регистрации или просить войти
        // await login(userData.username, userData.password);
        return true;
     } catch (error) {
        console.error("Registration failed", error);
        throw error;
     }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const value = {
    token,
    user,
    isAuthenticated: !!token && !!user, // Проверяем и токен и юзера
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  return useContext(AuthContext);
};
