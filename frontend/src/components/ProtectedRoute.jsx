import React from 'react';
import {Navigate, useLocation} from 'react-router-dom';
import {useAuth} from '../hooks/useAuth';
import {Spin} from 'antd';

const ProtectedRoute = ({children}) => {
    const {isAuthenticated, loading} = useAuth();
    const location = useLocation();

    if (loading) {
        return <div className="flex justify-center items-center h-screen"><Spin size="large"/></div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/auth" state={{from: location}} replace/>;
    }

    return children;
};

export default ProtectedRoute;
