Drop Table if Exists owners;
Drop Table if Exists models;
Drop Table if Exists brands;



-- Таблица брендов
CREATE TABLE brands (
    brand_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Таблица моделей
CREATE TABLE models (
    model_id SERIAL PRIMARY KEY,
    brand_id INT REFERENCES brands(brand_id),
    model_name VARCHAR(50) NOT NULL,
    year INT NOT NULL
);

-- Таблица владельцев
CREATE TABLE owners (
    owner_id SERIAL PRIMARY KEY,
    model_id INT REFERENCES models(model_id),
    owner_name VARCHAR(50) NOT NULL,
    purchase_date DATE NOT NULL
);
INSERT INTO brands (name) VALUES 
('Volkswagen'),
('Audi'),
('Porsche'),
('Skoda'),
('SEAT'),
('Bentley'),
('Bugatti');
INSERT INTO models (brand_id, model_name, year) VALUES 
(1, 'Golf', 2020),
(1, 'Passat', 2021),
(1, 'Tiguan', 2022),
(1, 'Jetta', 2019),
(1, 'Arteon', 2020),
(1, 'Polo', 2021),
(2, 'A4', 2021),
(2, 'A6', 2020),
(2, 'Q5', 2022),
(2, 'Q7', 2019),
(3, '911', 2020),
(3, 'Cayenne', 2021),
(3, 'Macan', 2022),
(4, 'Octavia', 2021),
(4, 'Fabia', 2020),
(4, 'Kodiaq', 2022),
(5, 'Leon', 2021),
(5, 'Ibiza', 2020),
(6, 'Continental GT', 2021),
(6, 'Bentayga', 2020),
(7, 'Chiron', 2022),
(7, 'Veyron', 2019);
INSERT INTO owners (model_id, owner_name, purchase_date) VALUES 
(1, 'Иван Иванов', '2020-05-15'),
(2, 'Петр Петров', '2021-06-20'),
(3, 'Сергей Сергеев', '2022-07-30'),
(4, 'Алексей Алексеев', '2019-08-01'),
(5, 'Дмитрий Дмитриев', '2020-09-10'),
(6, 'Мария Смирнова', '2021-10-05'),
(7, 'Анна Кузнецова', '2021-11-15'),
(8, 'Олег Сидоров', '2020-12-01'),
(9, 'Наталья Васильева', '2019-01-20'),
(10, 'Виктория Лебедева', '2022-02-10'),
(11, 'Андрей Федоров', '2020-03-15'),
(12, 'Екатерина Иванова', '2021-04-20'),
(13, 'Денис Павлов', '2022-05-25'),
(14, 'Валентина Романова', '2019-06-30'),
(15, 'Станислав Ковалев', '2020-07-10'),
(16, 'Кирилл Громов', '2021-08-15'),
(17, 'Галина Михайлова', '2019-09-20'),
(18, 'Роман Орлов', '2020-10-25'),
(19, 'Татьяна Зайцева', '2021-11-30'),
(20, 'Евгений Соловьев', '2019-12-05');

SELECT * from "brands"
   

