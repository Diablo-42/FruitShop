import React, {useState, useEffect} from 'react';
import {Layout, Menu, Spin, Row, Col, Alert} from 'antd';
import {AppstoreOutlined} from '@ant-design/icons';
import Header from '../components/Header';
import ProductCard from '../components/ProductCard';
import {getCategories, getProductsByCategory} from '../services/api';

const {Sider, Content} = Layout;

const HomePage = () => {
    const [categories, setCategories] = useState([]);
    const [products, setProducts] = useState([]);
    const [selectedCategoryId, setSelectedCategoryId] = useState(null);
    const [loadingCategories, setLoadingCategories] = useState(true);
    const [loadingProducts, setLoadingProducts] = useState(false);
    const [errorCategories, setErrorCategories] = useState('');
    const [errorProducts, setErrorProducts] = useState('');
    const [collapsed, setCollapsed] = useState(false);

    // Загрузка категорий
    useEffect(() => {
        const fetchCategories = async () => {
            setLoadingCategories(true);
            setErrorCategories('');
            try {
                const response = await getCategories();
                setCategories(response.data);
            } catch (error) {
                console.error("Failed to fetch categories", error);
                setErrorCategories('Не удалось загрузить категории.');
            } finally {
                setLoadingCategories(false);
            }
        };
        fetchCategories();
    }, []);

    // Загрузка продуктов при изменении категории
    useEffect(() => {
        const fetchProducts = async () => {
            setLoadingProducts(true);
            setErrorProducts('');
            try {
                const response = await getProductsByCategory(selectedCategoryId);
                setProducts(response.data);
            } catch (error) {
                console.error(`Failed to fetch products for category ${selectedCategoryId}`, error);
                setErrorProducts('Не удалось загрузить товары.');
            } finally {
                setLoadingProducts(false);
            }
        };
        fetchProducts();
    }, [selectedCategoryId]);

    const handleMenuClick = (e) => {
        setSelectedCategoryId(e.key === 'all' ? null : parseInt(e.key, 10));
    };

    // Формируем элементы меню
    const menuItems = [
        {key: 'all', label: 'Все категории', icon: <AppstoreOutlined/>},
        ...categories.map(cat => ({
            key: cat.id_category.toString(),
            label: cat.name_category,
        }))
    ];

    return (
        <Layout style={{minHeight: '100vh'}}>
            <Header/>
            <Layout>
                <Sider
                    className="bg-white shadow hidden md:block"
                    theme="light"
                    width={250}
                >
                    <div className="p-4 text-lg font-semibold text-center">Категории</div>
                    {loadingCategories ? (
                        <div className="flex justify-center mt-10"><Spin/></div>
                    ) : errorCategories ? (
                        <Alert message={errorCategories} type="error" className="m-4"/>
                    ) : (
                        <Menu
                            mode="inline"
                            selectedKeys={[selectedCategoryId === null ? 'all' : selectedCategoryId.toString()]}
                            onClick={handleMenuClick}
                            items={menuItems}
                            style={{borderRight: 0}}
                        />
                    )}
                </Sider>
                <Layout style={{padding: '24px'}}>
                    <div className="max-w-screen-xl mx-auto w-full">
                        <Content
                            style={{
                                margin: 0,
                                minHeight: 280,
                            }}
                        >
                            {loadingProducts ? (
                                <div className="flex justify-center mt-10"><Spin size="large"/></div>
                            ) : errorProducts ? (
                                <Alert message={errorProducts} type="error"/>
                            ) : products.length === 0 ? (
                                <p className="text-center text-gray-500">Нет товаров в этой категории.</p>
                            ) : (
                                <Row gutter={[16, 20]}>
                                    {products.map((product) => (
                                        <Col key={product.id_product} xs={12} sm={12} md={12} lg={8} xl={6}>
                                            <ProductCard product={product}/>
                                        </Col>
                                    ))}
                                </Row>
                            )}
                        </Content>
                    </div>
                </Layout>
            </Layout>
        </Layout>
    );
};

export default HomePage;
