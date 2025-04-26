import React, {useState} from 'react';
import {Card, Tabs} from 'antd';
import LoginForm from '../components/LoginFrom';
import SignupForm from '../components/SignupFrom';

const {TabPane} = Tabs;

const AuthPage = () => {
    const [activeTab, setActiveTab] = useState('login');

    const handleTabChange = (key) => {
        setActiveTab(key);
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
            <Card className="w-full max-w-md shadow-lg">
                <Tabs activeKey={activeTab} onChange={handleTabChange} centered>
                    <TabPane tab="Вход" key="login">
                        <LoginForm/>
                    </TabPane>
                    <TabPane tab="Регистрация" key="signup">
                        <SignupForm onSwitchToLogin={() => setActiveTab('login')}/>
                    </TabPane>
                </Tabs>
            </Card>
        </div>
    );
};

export default AuthPage;
