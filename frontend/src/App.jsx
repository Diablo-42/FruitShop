import React from 'react';
import {Routes, Route, Navigate} from 'react-router-dom';
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
import ProtectedRoute from './components/ProtectedRoute';
import {useAuth} from './hooks/useAuth';
import {Spin} from "antd";

import '@ant-design/v5-patch-for-react-19';

function App() {
    const {isAuthenticated, loading} = useAuth();

    if (loading) {
        return <div className="flex justify-center items-center h-screen"><Spin size="large"/></div>;
    }

    return (
        <Routes>
            <Route
                path="/"
                element={
                    <ProtectedRoute>
                        <HomePage/>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/auth"
                element={isAuthenticated ? <Navigate to="/" replace/> :
                    <AuthPage/>}
            />
            <Route path="*" element={<Navigate to="/" replace/>}/>
        </Routes>
    );
}

export default App;
