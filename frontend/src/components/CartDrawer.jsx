import React from 'react';
import {Drawer, List, Button, Avatar, Typography, Empty, Popconfirm, Spin} from 'antd';
import {DeleteOutlined, PlusOutlined, MinusOutlined} from '@ant-design/icons';
import {useCart} from '../hooks/useCart';

const {Text, Title} = Typography;

const CartDrawer = ({visible, onClose}) => {
    const {
        cartItems,
        removeFromCart,
        setCartItemQuantity,
        clearCart,
        getTotalItems,
        getTotalPrice,
        loading
    } = useCart();

    const handleClearCart = () => {
        clearCart();
    };

    const getImageUrl = (product) => `/images/${product.id_product}.jpg`;

    return (
        <Drawer
            title={`Корзина (${getTotalItems()} шт.)`}
            placement="right"
            onClose={onClose}
            open={visible}
            width={400}
            footer={
                cartItems.length > 0 ? (
                    <div className="flex flex-col gap-3">
                        <div className="flex justify-between items-baseline">
                            <Title level={5}
                                   style={{marginBottom: 0}}>Итого:</Title>
                            <Title level={4} style={{marginBottom: 0}} className="text-green-700">
                                {getTotalPrice().toFixed(2)} ₽
                            </Title>
                        </div>

                        <Button
                            type="primary"
                            size="large"
                            block
                            disabled
                        >
                            Оформить заказ
                        </Button>

                        <Popconfirm
                            title="Вы уверены, что хотите очистить корзину?"
                            onConfirm={handleClearCart}
                            okText="Да, очистить"
                            cancelText="Отмена"
                            disabled={loading}
                        >
                            <Button
                                size="large"
                                block
                                danger
                                loading={loading}
                            >
                                Очистить корзину
                            </Button>
                        </Popconfirm>
                    </div>
                ) : null
            }
        >
            {loading && cartItems.length === 0 && (
                <div className="flex justify-center items-center h-full">
                    <Spin size="large"/>
                </div>
            )}

            {!loading && cartItems.length === 0 ? (
                <Empty description="Ваша корзина пуста"/>
            ) : (
                <List
                    itemLayout="horizontal"
                    dataSource={cartItems}
                    renderItem={(item) => (
                        <List.Item
                            actions={[
                                <Popconfirm
                                    title="Удалить товар?"
                                    onConfirm={() => removeFromCart(item.product.id_product)}
                                    okText="Да"
                                    cancelText="Нет"
                                    disabled={loading}
                                >
                                    <Button
                                        type="text"
                                        danger
                                        icon={<DeleteOutlined/>}
                                        disabled={loading}
                                    />
                                </Popconfirm>
                            ]}
                        >
                            <List.Item.Meta
                                avatar={
                                    <Avatar
                                        shape="square"
                                        size={64}
                                        src={getImageUrl(item.product)}
                                        alt={item.product.name}
                                        onError={(e) => {
                                            e.target.onerror = null;
                                            e.target.src = `https://via.placeholder.com/64x64.png?text=${encodeURIComponent(item.product.name[0])}`;
                                        }}
                                    />
                                }
                                title={
                                    <Text strong>
                                        {item.product.name}
                                    </Text>
                                }
                                description={
                                    <div className="flex flex-col">
                                        <Text type="secondary">
                                            {item.product.price_per_unit.toFixed(2)} ₽ / {item.product.unit_type}
                                        </Text>
                                        <div className="flex items-center mt-2">
                                            <Button
                                                size="small"
                                                icon={<MinusOutlined/>}
                                                onClick={() => setCartItemQuantity(item.product.id_product, item.quantity - 1)}
                                                disabled={item.quantity <= 1 || loading}
                                            />

                                            <Text className="mx-2 w-8 text-center">
                                                {item.quantity}
                                            </Text>

                                            <Button
                                                size="small"
                                                icon={<PlusOutlined/>}
                                                onClick={() => setCartItemQuantity(item.product.id_product, item.quantity + 1)}
                                                disabled={loading}
                                            />

                                            <Text strong className="ml-auto">
                                                {(item.product.price_per_unit * item.quantity).toFixed(2)} ₽
                                            </Text>
                                        </div>
                                    </div>
                                }
                            />
                        </List.Item>
                    )}
                />
            )}
        </Drawer>
    );
};

export default CartDrawer;
