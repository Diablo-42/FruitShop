import React from 'react';
import {Card, Button} from 'antd';
import {ShoppingCartOutlined} from '@ant-design/icons';
import {useCart} from '../hooks/useCart';

const {Meta} = Card;

const ProductCard = ({product}) => {
    const {addToCart} = useCart();

    const handleAddToCart = () => {
        addToCart(product);
    };

    const formatDate = (dateString) => {
        try {
            if (!dateString || isNaN(new Date(dateString).getTime())) {
                return 'N/A';
            }
            return new Date(dateString).toLocaleDateString('ru-RU');
        } catch (e) {
            console.error("Ошибка форматирования даты:", e, "для значения:", dateString);
            return 'Ошибка даты';
        }
    };

    const imageUrl = `/images/${product.id_product}.jpg`;

    const handleImageError = (e) => {
        e.target.onerror = null;
        e.target.src = `https://via.placeholder.com/300x200.png?text=${encodeURIComponent(product.name)}`;
        console.warn(`Изображение не найдено по пути: ${imageUrl}`);
    };


    return (
        <Card
            hoverable
            className="w-full shadow-md rounded-lg overflow-hidden flex flex-col h-full"
            styles={{body: {padding: '0.75rem'}}}
            cover={
                <div className="aspect-[3.5/3] w-full overflow-hidden">
                    <img
                        alt={product.name}
                        src={imageUrl}
                        className="w-full h-full object-cover"
                        onError={handleImageError}
                    />
                </div>
            }
            actions={[
                <div className="px-3 pb-2 pt-1">
                    <Button
                        type="primary"
                        icon={<ShoppingCartOutlined/>}
                        onClick={handleAddToCart}
                        key="add"
                        block
                    >
                        В корзину
                    </Button>
                </div>
            ]}
        >
            <Meta
                title={<span className="font-semibold text-xl block truncate mb-1">{product.name}</span>}
                description={
                    <div className="text-sm text-gray-600">
                        <p><span className="font-medium">Категория:</span> {product.category?.name_category || 'N/A'}
                        </p>
                        <p><span className="font-medium">Страна:</span> {product.country?.name_country || 'N/A'}</p>
                        <p><span className="font-medium">Срок годности:</span> {formatDate(product.expiration_date)}</p>
                        <p className="text-lg font-bold text-green-700 mt-2">
                            {product.price_per_unit.toFixed(2)} ₽ / {product.unit_type}
                        </p>
                    </div>
                }
            />
        </Card>
    );
};

export default ProductCard;
