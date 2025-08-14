-- Таблица клиентов
CREATE TABLE Clients (
    client_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    client_address VARCHAR(255),
    city VARCHAR(100),
    region VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE
);

-- Таблица товаров
CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    product_description TEXT,
    brand_name INT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    category_id INT NOT NULL,
    FOREIGN KEY (brand_name) REFERENCES Brands (brand_name),
    FOREIGN KEY (category_id) REFERENCES Categories (category_id)
);

-- Таблица оплаты
CREATE TABLE Payments (
    card_number VARCHAR(16) UNIQUE NOT NULL,
    card_type VARCHAR(50) NOT NULL,
    expiration_date DATE NOT NULL
);

-- Таблица отзывов
CREATE TABLE Reviews (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    client_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    FOREIGN KEY (order_id) REFERENCES Orders (order_id),
    FOREIGN KEY (product_id) REFERENCES Products (product_id),
    FOREIGN KEY (client_id) REFERENCES Clients (client_id)
);

-- Таблица категорий
CREATE TABLE Categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_description TEXT
);

-- Таблица доставки
CREATE TABLE Deliveries (
    order_id SERIAL PRIMARY KEY,
    payment_status BOOLEAN NOT NULL,
    delivery_status VARCHAR(50) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица количества товара в заказе
CREATE TABLE OrderDetails (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES Orders (order_id),
    FOREIGN KEY (product_id) REFERENCES Products (product_id)
);

-- Таблица брендов
CREATE TABLE Brands (
    brand_name VARCHAR(100) NOT NULL,
    country_of_origin VARCHAR(100),
    brand_description TEXT
);

-- Общая таблица заказов
CREATE TABLE Orders (
    order_id PRIMARY KEY,
    client_id INT NOT NULL,
    card_number INT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES Clients (client_id),
    FOREIGN KEY (card_number) REFERENCES Payments (card_number)
);

-- Пример хранимой процедуры
CREATE OR REPLACE FUNCTION update_stock(product_id INT, quantity INT) RETURNS VOID AS $$
BEGIN
    UPDATE Products
    SET stock_quantity = stock_quantity - quantity
    WHERE product_id = product_id;

    IF (SELECT stock_quantity FROM Products WHERE product_id = product_id) < 0 THEN
        RAISE EXCEPTION 'Stock cannot be negative';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Пример триггера для автоматической проверки наличия товара на складе при создании записи в OrderDetails
CREATE OR REPLACE FUNCTION check_stock() RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT stock_quantity FROM Products WHERE product_id = NEW.product_id) < NEW.quantity THEN
        RAISE EXCEPTION 'Not enough stock for product ID %', NEW.product_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_stock
BEFORE INSERT ON OrderDetails
FOR EACH ROW
EXECUTE FUNCTION check_stock();