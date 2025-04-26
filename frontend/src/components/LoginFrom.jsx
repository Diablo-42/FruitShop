import React, {useState} from 'react';
import {Form, Input, Button, Alert} from 'antd';
import {UserOutlined, LockOutlined} from '@ant-design/icons';
import {useAuth} from '../hooks/useAuth';
import {useNavigate} from 'react-router-dom';

const LoginForm = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const {login} = useAuth();
    const navigate = useNavigate();

    const onFinish = async (values) => {
        setLoading(true);
        setError('');
        try {
            await login(values.username, values.password);
            navigate('/');
        } catch (err) {
            setError('Ошибка входа. Проверьте имя пользователя или пароль.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Form
            name="login"
            onFinish={onFinish}
            autoComplete="off"
            layout="vertical"
        >
            {error && <Alert message={error} type="error" showIcon closable className="mb-4"/>}

            <Form.Item
                label="Имя пользователя"
                name="username"
                rules={[{required: true, message: 'Пожалуйста, введите имя пользователя!'}]}
            >
                <Input prefix={<UserOutlined/>} placeholder="Имя пользователя"/>
            </Form.Item>

            <Form.Item
                label="Пароль"
                name="password"
                rules={[{required: true, message: 'Пожалуйста, введите пароль!'}]}
            >
                <Input.Password prefix={<LockOutlined/>} placeholder="Пароль"/>
            </Form.Item>

            <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} block>
                    Войти
                </Button>
            </Form.Item>
        </Form>
    );
};

export default LoginForm;
