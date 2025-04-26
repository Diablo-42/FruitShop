import React, {useState} from 'react';
import {Form, Input, Button, Alert, message} from 'antd';
import {UserOutlined, LockOutlined, MailOutlined, HomeOutlined, PhoneOutlined} from '@ant-design/icons';

import {useAuth} from '../hooks/useAuth';

const SignupForm = ({onSwitchToLogin}) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const {register} = useAuth();
    const [form] = Form.useForm();

    const onFinish = async (values) => {
        setLoading(true);
        setError('');
        try {
            const {confirm, ...userData} = values;
            await register(...userData); // Отправляем payload
            message.success('Регистрация успешна! Теперь вы можете войти.');
            form.resetFields();
            onSwitchToLogin();
        } catch (err) {
            const errorMsg = err.response?.data?.detail || 'Ошибка регистрации.';
            setError(errorMsg);
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Form
            form={form}
            name="register"
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
                label="Email"
                name="email"
                rules={[
                    {required: true, message: 'Пожалуйста, введите email!'},
                    {type: 'email', message: 'Некорректный формат email!'}
                ]}
            >
                <Input prefix={<MailOutlined/>} placeholder="Email"/>
            </Form.Item>

            <Form.Item
                label="ФИО (необязательно)"
                name="full_name"
            >
                <Input prefix={<UserOutlined/>} placeholder="Фамилия Имя Отчество"/>
            </Form.Item>

            <Form.Item
                label="Адрес (необязательно)"
                name="address"
            >
                <Input prefix={<HomeOutlined/>} placeholder="Город, улица, дом, квартира"/>
            </Form.Item>

            <Form.Item
                label="Телефон (необязательно)"
                name="phone"
                rules={[
                    {
                        pattern: /^\+?[78]?[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{2}[- ]?\d{3}$/,
                        message: 'Некорректный формат телефона!'
                    }
                ]}
            >
                <Input prefix={<PhoneOutlined/>} placeholder="+7 (XXX) XXX-XX-XX"/>
            </Form.Item>

            <Form.Item
                label="Пароль"
                name="password"
                rules={[{required: true, message: 'Пожалуйста, введите пароль!'}]}
                hasFeedback
            >
                <Input.Password prefix={<LockOutlined/>} placeholder="Пароль"/>
            </Form.Item>

            <Form.Item
                name="confirm"
                label="Подтвердите пароль"
                dependencies={['password']}
                hasFeedback
                rules={[
                    {required: true, message: 'Пожалуйста, подтвердите пароль!'},
                    ({getFieldValue}) => ({
                        validator(_, value) {
                            if (!value || getFieldValue('password') === value) {
                                return Promise.resolve();
                            }
                            return Promise.reject(new Error('Пароли не совпадают!'));
                        },
                    }),
                ]}
            >
                <Input.Password prefix={<LockOutlined/>} placeholder="Подтвердите пароль"/>
            </Form.Item>

            <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} block>
                    Зарегистрироваться
                </Button>
            </Form.Item>
        </Form>
    );
};

export default SignupForm;
