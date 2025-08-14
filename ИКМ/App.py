import sys
import re

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLineEdit, QTabWidget, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt
import psycopg2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Магазин электроники - Управление БД")
        self.setGeometry(100, 100, 800, 600)

        self.connection = self.connect_to_db()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_clients_tab(), "Клиенты")
        self.tabs.addTab(self.create_products_tab(), "Продукты")
        self.tabs.addTab(self.create_brands_tab(), "Бренды")
        self.tabs.addTab(self.create_categories_tab(), "Категории")
        self.tabs.addTab(self.create_payments_tab(), "Оплата")
        #self.tabs.addTab(self.create_orders_tab(), "Заказы")





        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.central_widget.setLayout(layout)

    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                dbname=" electronics_store",
                user="postgres",
                password="12345",
                host="localhost",
                port="5432"
            )
            return conn
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к базе данных: {e}")
            sys.exit(1)

    def create_clients_tab(self):
        """Вкладка для работы с таблицей Клиенты."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица для отображения данных
        self.clients_table = QTableWidget()
        layout.addWidget(self.clients_table)

        # Кнопки
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        edit_button = QPushButton("Редактировать")
        delete_button = QPushButton("Удалить")
        refresh_button = QPushButton("Обновить")
        filter_button = QPushButton("Фильтр")
        sort_button = QPushButton("Упорядочить")  # Новая кнопка

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(filter_button)
        button_layout.addWidget(sort_button)  # Добавление кнопки

        layout.addLayout(button_layout)

        # Подключение сигналов к методам
        refresh_button.clicked.connect(self.load_clients_data)
        add_button.clicked.connect(self.add_client)
        edit_button.clicked.connect(self.edit_client)
        delete_button.clicked.connect(self.delete_client)
        filter_button.clicked.connect(self.filter_by_city)
        sort_button.clicked.connect(self.sort_clients_by_id)  # Подключение кнопки сортировки

        tab.setLayout(layout)
        self.load_clients_data()
        return tab

    def load_clients_data(self):
        """Загрузка данных из таблицы Клиенты."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Clients;")
            rows = cursor.fetchall()
            columns = [
                "ID Клиента", "Имя", "Фамилия", "Адрес", "Город",
                "Область", "Почтовый индекс", "Страна", "Телефон", "Email"
            ]

            self.clients_table.setRowCount(len(rows))
            self.clients_table.setColumnCount(len(columns))
            self.clients_table.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.clients_table.setItem(i, j, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.connection.rollback()

    def add_client(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить клиента")
        form_layout = QFormLayout(dialog)

        # Поля ввода данных
        first_name_input = QLineEdit(dialog)
        last_name_input = QLineEdit(dialog)
        email_input = QLineEdit(dialog)
        phone_input = QLineEdit(dialog)
        address_input = QLineEdit(dialog)
        city_input = QLineEdit(dialog)
        region_input = QLineEdit(dialog)
        postal_code_input = QLineEdit(dialog)
        country_input = QLineEdit(dialog)

        form_layout.addRow("Имя:", first_name_input)
        form_layout.addRow("Фамилия:", last_name_input)
        form_layout.addRow("Email:", email_input)
        form_layout.addRow("Телефон:", phone_input)
        form_layout.addRow("Адрес:", address_input)
        form_layout.addRow("Город:", city_input)
        form_layout.addRow("Область:", region_input)
        form_layout.addRow("Почтовый индекс:", postal_code_input)
        form_layout.addRow("Страна:", country_input)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            first_name = first_name_input.text().strip()
            last_name = last_name_input.text().strip()
            email = email_input.text().strip()
            phone = phone_input.text().strip()
            address = address_input.text().strip()
            city = city_input.text().strip()
            region = region_input.text().strip()
            postal_code = postal_code_input.text().strip()
            country = country_input.text().strip()

            # Валидация данных
            if not first_name or not last_name or not email or not phone:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля (Имя, Фамилия, Email, Телефон).")
                return

            # Проверка на валидность email
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный Email.")
                return

            # Проверка на валидность телефона (только цифры, длина 10-11 символов)
            if not phone.isdigit() or len(phone) not in [10, 11]:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный номер телефона (10 или 11 цифр).")
                return

            cursor = self.connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO Clients (first_name, last_name, client_address, city, region, postal_code, country, email, phone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING client_id
                """, (first_name, last_name, address, city, region, postal_code, country, email, phone))
                client_id = cursor.fetchone()[0]
                self.connection.commit()

                QMessageBox.information(self, "Успех", "Клиент успешно добавлен!")
                self.load_clients_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления клиента: {e}")
                self.connection.rollback()

    def edit_client(self):
        """Редактирование выбранного клиента."""
        selected_row = self.clients_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента для редактирования.")
            return

        client_id = self.clients_table.item(selected_row, 0).text()
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать клиента")

        form_layout = QFormLayout(dialog)

        first_name_input = QLineEdit(dialog)
        last_name_input = QLineEdit(dialog)
        client_address_input = QLineEdit(dialog)
        city_input = QLineEdit(dialog)
        region_input = QLineEdit(dialog)
        postal_code_input = QLineEdit(dialog)
        country_input = QLineEdit(dialog)
        phone_input = QLineEdit(dialog)
        email_input = QLineEdit(dialog)

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Clients WHERE client_id = %s", (client_id,))
        client = cursor.fetchone()

        first_name_input.setText(client[1])
        last_name_input.setText(client[2])
        client_address_input.setText(client[3])
        city_input.setText(client[4])
        region_input.setText(client[5])
        postal_code_input.setText(client[6])
        country_input.setText(client[7])
        phone_input.setText(client[8])
        email_input.setText(client[9])

        form_layout.addRow("Имя:", first_name_input)
        form_layout.addRow("Фамилия:", last_name_input)
        form_layout.addRow("Адрес:", client_address_input)
        form_layout.addRow("Город:", city_input)
        form_layout.addRow("Область:", region_input)
        form_layout.addRow("Почтовый индекс:", postal_code_input)
        form_layout.addRow("Страна:", country_input)
        form_layout.addRow("Телефон:", phone_input)
        form_layout.addRow("Email:", email_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            first_name = first_name_input.text().strip()
            last_name = last_name_input.text().strip()
            email = email_input.text().strip()
            phone = phone_input.text().strip()

            # Валидация данных
            if not first_name or not last_name or not email or not phone:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля (Имя, Фамилия, Email, Телефон).")
                return

            # Проверка на валидность email
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный Email.")
                return

            # Проверка на валидность телефона (только цифры, длина 10-11 символов)
            if not phone.isdigit() or len(phone) not in [10, 11]:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный номер телефона (10 или 11 цифр).")
                return

            try:
                cursor.execute("""
                    UPDATE Clients SET first_name=%s, last_name=%s, client_address=%s, city=%s, region=%s, 
                    postal_code=%s, country=%s, phone=%s, email=%s
                    WHERE client_id=%s
                """, (first_name, last_name, client_address_input.text(), city_input.text(),
                    region_input.text(), postal_code_input.text(), country_input.text(), phone, email, client_id))
                self.connection.commit()
                QMessageBox.information(self, "Успех", "Данные клиента успешно обновлены!")
                self.load_clients_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка обновления клиента: {e}")
                self.connection.rollback()

    def delete_client(self):
        """Удаление выбранного клиента."""
        selected_row = self.clients_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента для удаления.")
            return

        client_id = self.clients_table.item(selected_row, 0).text()
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Clients WHERE client_id = %s", (client_id,))
            self.connection.commit()
            QMessageBox.information(self, "Успех", "Клиент успешно удален!")
            self.load_clients_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления клиента: {e}")
            self.connection.rollback()

    def filter_by_city(self):
        """Фильтрация записей по городам."""
        try:
            # Получение списка городов из базы данных
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT city FROM Clients;")
            cities = [row[0] for row in cursor.fetchall()]

            # Создание диалога для выбора городов
            dialog = QDialog(self)
            dialog.setWindowTitle("Фильтр по городам")
            dialog_layout = QVBoxLayout(dialog)

            city_checkboxes = []
            for city in cities:
                checkbox = QCheckBox(city, dialog)
                city_checkboxes.append(checkbox)
                dialog_layout.addWidget(checkbox)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            dialog_layout.addWidget(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)

            if dialog.exec_() == QDialog.Accepted:
                # Получение выбранных городов
                selected_cities = [checkbox.text() for checkbox in city_checkboxes if checkbox.isChecked()]

                if selected_cities:
                    # Формирование SQL-запроса с фильтром
                    placeholders = ', '.join(['%s'] * len(selected_cities))
                    query = f"SELECT * FROM Clients WHERE city IN ({placeholders})"
                    cursor.execute(query, selected_cities)
                else:
                    # Если города не выбраны, загружаем все записи
                    cursor.execute("SELECT * FROM Clients;")

                # Обновление таблицы
                rows = cursor.fetchall()
                columns = [
                    "ID Клиента", "Имя", "Фамилия", "Адрес", "Город",
                    "Область", "Почтовый индекс", "Страна", "Телефон", "Email"
                ]

                self.clients_table.setRowCount(len(rows))
                self.clients_table.setColumnCount(len(columns))
                self.clients_table.setHorizontalHeaderLabels(columns)

                for i, row in enumerate(rows):
                    for j, value in enumerate(row):
                        self.clients_table.setItem(i, j, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка фильтрации данных: {e}")
            self.connection.rollback()

    def sort_clients_by_id(self):
        """Сортировка клиентов по ID."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Clients ORDER BY client_id;")
            rows = cursor.fetchall()

            columns = [
                "ID Клиента", "Имя", "Фамилия", "Адрес", "Город",
                "Область", "Почтовый индекс", "Страна", "Телефон", "Email"
            ]

            self.clients_table.setRowCount(len(rows))
            self.clients_table.setColumnCount(len(columns))
            self.clients_table.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.clients_table.setItem(i, j, QTableWidgetItem(str(value)))

            QMessageBox.information(self, "Успех", "Данные упорядочены по ID Клиента.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сортировки данных: {e}")
            self.connection.rollback()





    def create_products_tab(self):
        """Создание вкладки Товар."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Фильтр по категории
        self.category_filter = QComboBox()
        self.category_filter.currentIndexChanged.connect(self.filter_products_by_category)
        layout.addWidget(self.category_filter)

        # Таблица для отображения данных
        self.products_table = QTableWidget()
        layout.addWidget(self.products_table)

        # Кнопки управления
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        edit_button = QPushButton("Редактировать")
        delete_button = QPushButton("Удалить")
        refresh_button = QPushButton("Обновить")

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        refresh_button.clicked.connect(self.load_products_data)
        add_button.clicked.connect(self.add_product)
        edit_button.clicked.connect(self.edit_product)
        delete_button.clicked.connect(self.delete_product)

        tab.setLayout(layout)
        self.load_categories_for_filter()
        self.load_products_data()
        return tab

    def load_products_data(self):
        """Загрузка данных из таблицы Товары."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT product_id, product_name, product_description, brand_name, price, stock_quantity, category_id
                FROM Products;
            """)
            rows = cursor.fetchall()
            columns = ['ID Товара', 'Название', 'Описание', 'Бренд', 'Цена', 'Кол-во на складе', 'ID Категории']

            self.products_table.setRowCount(len(rows))
            self.products_table.setColumnCount(len(columns))
            self.products_table.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.products_table.setItem(i, j, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.connection.rollback()

    def add_product(self):
        """Добавление нового продукта."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить продукт")
        form_layout = QFormLayout(dialog)

        # Поля ввода данных
        product_name_input = QLineEdit(dialog)
        description_input = QLineEdit(dialog)
        brand_input = QComboBox(dialog)  # Выпадающий список для брендов
        price_input = QLineEdit(dialog)
        stock_quantity_input = QLineEdit(dialog)
        category_input = QComboBox(dialog)  # Выпадающий список для категорий

        # Загрузка данных брендов в ComboBox
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT brand_name FROM Brands;")
            brands = cursor.fetchall()
            if not brands:
                QMessageBox.warning(self, "Ошибка", "Список брендов пуст. Добавьте хотя бы один бренд во вкладке 'Бренды'.")
                return
            for (brand_name,) in brands:
                brand_input.addItem(brand_name)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки брендов: {e}")
            return

        # Загрузка данных категорий в ComboBox
        try:
            cursor.execute("SELECT category_id, category_name FROM Categories;")
            categories = cursor.fetchall()
            if not categories:
                QMessageBox.warning(self, "Ошибка", "Список категорий пуст. Добавьте хотя бы одну категорию во вкладке 'Категории'.")
                return
            for category_id, category_name in categories:
                category_input.addItem(category_name, category_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки категорий: {e}")
            return

        form_layout.addRow("Название:", product_name_input)
        form_layout.addRow("Описание:", description_input)
        form_layout.addRow("Бренд:", brand_input)
        form_layout.addRow("Цена:", price_input)
        form_layout.addRow("Количество на складе:", stock_quantity_input)
        form_layout.addRow("Категория:", category_input)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            product_name = product_name_input.text().strip()
            description = description_input.text().strip()
            brand_name = brand_input.currentText()  # Получение названия бренда
            price = price_input.text().strip()
            stock_quantity = stock_quantity_input.text().strip()
            category_id = category_input.currentData()  # Получение ID категории

            # Валидация данных
            if not product_name or not brand_name or not price or not stock_quantity or not category_id:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля (Название, Бренд, Цена, Количество, Категория).")
                return

            # Проверка на валидность цены (должна быть числом)
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректную положительную цену.")
                return

            # Проверка на валидность количества (целое число)
            try:
                stock_quantity = int(stock_quantity)
                if stock_quantity < 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректное количество на складе (неотрицательное целое число).")
                return

            try:
                cursor.execute("""
                    INSERT INTO Products (product_name, product_description, brand_name, price, stock_quantity, category_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (product_name, description, brand_name, price, stock_quantity, category_id))
                self.connection.commit()
                QMessageBox.information(self, "Успех", "Продукт успешно добавлен!")
                self.load_products_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления продукта: {e}")
                self.connection.rollback()

    def edit_product(self):
        selected_row = self.products_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите продукт для редактирования.")
            return

        product_id = self.products_table.item(selected_row, 0).text()
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать продукт")

        form_layout = QFormLayout(dialog)

        name_input = QLineEdit(dialog)
        description_input = QLineEdit(dialog)
        brand_id_input = QLineEdit(dialog)
        price_input = QLineEdit(dialog)
        stock_quantity_input = QLineEdit(dialog)
        category_id_input = QLineEdit(dialog)

        cursor = self.connection.cursor()
        cursor.execute("SELECT product_name, product_description, brand_name, price, stock_quantity, category_id FROM Products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        name_input.setText(product[0])
        description_input.setText(product[1])
        brand_id_input.setText(str(product[2]))
        price_input.setText(str(product[3]))
        stock_quantity_input.setText(str(product[4]))
        category_id_input.setText(str(product[5]))

        form_layout.addRow("Название:", name_input)
        form_layout.addRow("Описание:", description_input)
        form_layout.addRow("Название Бренда:", brand_id_input)
        form_layout.addRow("Цена:", price_input)
        form_layout.addRow("Количество на складе:", stock_quantity_input)
        form_layout.addRow("ID Категории:", category_id_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            description = description_input.text().strip()
            brand_name = brand_id_input.text().strip()
            price = price_input.text().strip()
            stock_quantity = stock_quantity_input.text().strip()
            category_id = category_id_input.text().strip()

            # Валидация данных
            if not name or not brand_name or not price or not stock_quantity or not category_id:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля (Название, Бренд, Цена, Количество, Категория).")
                return

            # Проверка на валидность цены (должна быть числом)
            try:
                price = float(price)
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректную цену.")
                return

            # Проверка на валидность количества (целое число)
            try:
                stock_quantity = int(stock_quantity)
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректное количество на складе.")
                return

            # Проверка на валидность ID категории (целое число)
            try:
                category_id = int(category_id)
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный ID категории.")
                return

            try:
                cursor.execute("""
                    UPDATE Products SET product_name = %s, product_description = %s, brand_name = %s, price = %s, stock_quantity = %s, category_id = %s
                    WHERE product_id = %s
                """, (name, description, brand_name, price, stock_quantity, category_id, product_id))
                self.connection.commit()
                QMessageBox.information(self, "Успех", "Продукт успешно обновлен!")
                self.load_products_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка редактирования продукта: {e}")
                self.connection.rollback()

    def delete_product(self):
        selected_row = self.products_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите продукт для удаления.")
            return

        product_id = self.products_table.item(selected_row, 0).text()
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Products WHERE product_id = %s", (product_id,))
            self.connection.commit()
            QMessageBox.information(self, "Успех", "Продукт успешно удален!")
            self.load_products_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления продукта: {e}")
            self.connection.rollback()

    def filter_products_by_category(self):
        """Фильтрация товаров по выбранной категории."""
        selected_category_index = self.category_filter.currentIndex()

        try:
            cursor = self.connection.cursor()

            if selected_category_index == 0:  # Если выбрано "Все категории"
                cursor.execute("""
                    SELECT product_id, product_name, product_description, brand_name, price, stock_quantity, category_id
                    FROM Products;
                """)
            else:
                category_id = self.category_filter.itemData(selected_category_index)
                cursor.execute("""
                    SELECT p.product_id, p.product_name, p.product_description, p.brand_name, p.price, p.stock_quantity, p.category_id
                    FROM Products p
                    INNER JOIN Categories c ON p.category_id = c.category_id
                    WHERE c.category_id = %s;
                """, (category_id,))

            rows = cursor.fetchall()
            columns = ['ID Товара', 'Название', 'Описание', 'Бренд', 'Цена', 'Кол-во на складе', 'ID Категории']

            self.products_table.setRowCount(len(rows))
            self.products_table.setColumnCount(len(columns))
            self.products_table.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.products_table.setItem(i, j, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка фильтрации товаров: {e}")

    def load_categories_for_filter(self):
        """Загрузка списка категорий в фильтр."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT category_id, category_name FROM Categories;")
            categories = cursor.fetchall()

            self.category_filter.clear()
            self.category_filter.addItem("Все категории")  # Опция для отображения всех товаров

            for category_id, category_name in categories:
                self.category_filter.addItem(category_name, category_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки категорий: {e}")





    def create_brands_tab(self):
        """Вкладка для работы с таблицей Бренды."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица для отображения данных
        self.brands_table = QTableWidget()
        layout.addWidget(self.brands_table)

        # Кнопки
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        edit_button = QPushButton("Редактировать")
        delete_button = QPushButton("Удалить")
        refresh_button = QPushButton("Обновить")

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        # Сигналы
        refresh_button.clicked.connect(self.load_brands_data)
        add_button.clicked.connect(self.add_brand)
        edit_button.clicked.connect(self.edit_brand)
        delete_button.clicked.connect(self.delete_brand)

        tab.setLayout(layout)
        self.load_brands_data()  # Загрузка данных при инициализации
        return tab

    def load_brands_data(self):
        """Загрузка данных из таблицы Бренды."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Brands;")
            rows = cursor.fetchall()
            columns = ['Название', 'Страна', 'Описание']

            self.brands_table.setRowCount(len(rows))
            self.brands_table.setColumnCount(len(columns))
            self.brands_table.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.brands_table.setItem(i, j, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.connection.rollback()

    def add_brand(self):
        """Добавление нового бренда."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить бренд")

        form_layout = QFormLayout(dialog)

        name_input = QLineEdit(dialog)
        description_input = QLineEdit(dialog)
        country_input = QLineEdit(dialog)

        form_layout.addRow("Название:", name_input)
        form_layout.addRow("Описание:", description_input)
        form_layout.addRow("Страна производитель:", country_input)


        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO Brands (brand_name, country_of_origin, brand_description)
                    VALUES (%s, %s, %s)
                """, (name_input.text(), country_input.text() , description_input.text()))
                self.connection.commit()
                QMessageBox.information(self, "Успех", "Бренд успешно добавлен!")
                self.load_brands_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления бренда: {e}")
                self.connection.rollback()

    def edit_brand(self):
        """Редактирование выбранного бренда."""
        selected_row = self.brands_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите бренд для редактирования.")
            return

        brand_name = self.brands_table.item(selected_row, 0).text()
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать бренд")

        form_layout = QFormLayout(dialog)

        name_input = QLineEdit(dialog)
        country_input = QLineEdit(dialog)
        description_input = QLineEdit(dialog)

        cursor = self.connection.cursor()
        cursor.execute("SELECT brand_name, country_of_origin, brand_description FROM Brands WHERE brand_name = %s", (brand_name,))
        brand = cursor.fetchone()

        name_input.setText(brand[0])
        old_name = brand[0]
        country_input.setText(brand[1])
        description_input.setText(brand[2])

        form_layout.addRow("Название:", name_input)
        form_layout.addRow("Страна производитель:", country_input)
        form_layout.addRow("Описание:", description_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            try:
                cursor.execute("""
                    UPDATE Brands SET brand_name = %s,country_of_origin = %s,brand_description = %s
                    WHERE brand_name = %s
                """, (name_input.text(), country_input.text(), description_input.text(), old_name))
                self.connection.commit()
                QMessageBox.information(self, "Успех", "Бренд успешно обновлен!")
                self.load_brands_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка редактирования бренда: {e}")
                self.connection.rollback()

    def delete_brand(self):
        """Удаление выбранного бренда."""
        selected_row = self.brands_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите бренд для удаления.")
            return

        brand_name = self.brands_table.item(selected_row, 0).text()
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Brands WHERE brand_name = %s", (brand_name,))
            self.connection.commit()
            QMessageBox.information(self, "Успех", "Бренд успешно удален!")
            self.load_brands_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления бренда: {e}")
            self.connection.rollback()




    def create_categories_tab(self):
        """Вкладка для работы с таблицей Категории."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица для отображения данных
        self.categories_table = QTableWidget()
        layout.addWidget(self.categories_table)

        # Кнопки
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        edit_button = QPushButton("Редактировать")
        delete_button = QPushButton("Удалить")
        refresh_button = QPushButton("Обновить")

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        # Сигналы
        refresh_button.clicked.connect(self.load_categories_data)
        add_button.clicked.connect(self.add_category)
        edit_button.clicked.connect(self.edit_category)
        delete_button.clicked.connect(self.delete_category)

        tab.setLayout(layout)
        self.load_categories_data()  # Загрузка данных при инициализации
        return tab

    def load_categories_data(self):
        """Загрузка данных из таблицы Категории."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Categories;")
            rows = cursor.fetchall()
            columns = ["ID Категории", "Название", "Описание"]

            self.categories_table.setRowCount(len(rows))
            self.categories_table.setColumnCount(len(columns))
            self.categories_table.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.categories_table.setItem(i, j, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")

    def add_category(self):
        """Добавление новой категории."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить категорию")

        form_layout = QFormLayout(dialog)

        name_input = QLineEdit(dialog)
        description_input = QLineEdit(dialog)

        form_layout.addRow("Название категории:", name_input)
        form_layout.addRow("Описание категории:", description_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO Categories (category_name, category_description)
                    VALUES (%s, %s)
                """, (name_input.text(), description_input.text()))
                self.connection.commit()
                QMessageBox.information(self, "Успех", "Категория успешно добавлена!")
                self.load_categories_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления категории: {e}")
    
    def edit_category(self):
        """Редактирование выбранной категории."""
        selected_row = self.categories_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию для редактирования.")
            return

        category_id = self.categories_table.item(selected_row, 0).text()
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать категорию")

        form_layout = QFormLayout(dialog)

        name_input = QLineEdit(dialog)
        description_input = QLineEdit(dialog)

        cursor = self.connection.cursor()
        cursor.execute("SELECT category_name, category_description FROM Categories WHERE category_id = %s", (category_id,))
        category = cursor.fetchone()

        name_input.setText(category[0])
        description_input.setText(category[1])

        form_layout.addRow("Название категории:", name_input)
        form_layout.addRow("Описание категории:", description_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            try:
                cursor.execute("""
                    UPDATE Categories SET category_name = %s, category_description = %s
                    WHERE category_id = %s
                """, (name_input.text(), description_input.text(), category_id))
                self.connection.commit()
                QMessageBox.information(self, "Успех", "Категория успешно обновлена!")
                self.load_categories_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка редактирования категории: {e}")

    def delete_category(self):
        """Удаление выбранной категории."""
        selected_row = self.categories_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию для удаления.")
            return

        category_id = self.categories_table.item(selected_row, 0).text()
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Categories WHERE category_id = %s", (category_id,))
            self.connection.commit()
            QMessageBox.information(self, "Успех", "Категория успешно удалена!")
            self.load_categories_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления категории: {e}")




    def create_orders_tab(self):
        """Создание вкладки для отображения таблицы Заказы."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица для отображения данных
        self.orders_table = QTableWidget()
        layout.addWidget(self.orders_table)

        # Установка макета и загрузка данных
        tab.setLayout(layout)
        #self.load_orders_data()

        return tab

    def create_payments_tab(self):
        """Создание вкладки для работы с таблицей Оплата."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица для отображения данных
        self.payments_table = QTableWidget()
        layout.addWidget(self.payments_table)

        # Кнопки управления
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        edit_button = QPushButton("Редактировать")
        delete_button = QPushButton("Удалить")
        refresh_button = QPushButton("Обновить")

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        # Привязка сигналов
        refresh_button.clicked.connect(self.load_payments_data)
        add_button.clicked.connect(self.add_payment)
        edit_button.clicked.connect(self.edit_payment)
        delete_button.clicked.connect(self.delete_payment)

        # Установка макета и загрузка данных
        tab.setLayout(layout)
        self.load_payments_data()

        return tab
    
    def load_payments_data(self):
        """Загрузка данных из таблицы Оплата."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Payments;")
            rows = cursor.fetchall()
            columns = ["Номер карты", "Тип карты", "Дата истечения"]

            self.payments_table.setRowCount(len(rows))
            self.payments_table.setColumnCount(len(columns))
            self.payments_table.setHorizontalHeaderLabels(columns)

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.payments_table.setItem(i, j, QTableWidgetItem(str(value)))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")

    def add_payment(self):
        """Добавление новой записи в таблицу Оплата."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить оплату")

        form_layout = QFormLayout(dialog)

        # Поля ввода
        card_number_input = QLineEdit(dialog)
        card_type_input = QLineEdit(dialog)
        expiration_date_input = QLineEdit(dialog)

        form_layout.addRow("Номер карты (16 цифр):", card_number_input)
        form_layout.addRow("Тип карты:", card_type_input)
        form_layout.addRow("Дата истечения (ГГГГ-ММ-ДД):", expiration_date_input)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            card_number = card_number_input.text().strip()
            card_type = card_type_input.text().strip()
            expiration_date = expiration_date_input.text().strip()

            # Валидация данных
            # Проверка номера карты (16 цифр)
            if not re.match(r'^\d{16}$', card_number):
                QMessageBox.warning(self, "Ошибка", "Номер карты должен содержать 16 цифр.")
                return

            # Проверка типа карты (не пустое значение)
            if not card_type:
                QMessageBox.warning(self, "Ошибка", "Тип карты не может быть пустым.")
                return

            # Проверка даты истечения (формат ГГГГ-ММ-ДД)
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', expiration_date):
                QMessageBox.warning(self, "Ошибка", "Дата истечения должна быть в формате ГГГГ-ММ-ДД.")
                return

            # Проверка на корректность даты истечения
            try:
                #expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d')
                pass
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Некорректная дата истечения. Пожалуйста, используйте формат ГГГГ-ММ-ДД.")
                return

            # Вставка данных в базу
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO Payments (card_number, card_type, expiration_date)
                    VALUES (%s, %s, %s)
                """, (card_number, card_type, expiration_date))
                self.connection.commit()
                self.load_payments_data()
                QMessageBox.information(self, "Успех", "Оплата успешно добавлена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления оплаты: {e}")
                self.connection.rollback()

    def edit_payment(self):
        """Редактирование выбранной записи в таблице Оплата."""
        selected_row = self.payments_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования.")
            return

        card_number = self.payments_table.item(selected_row, 0).text()
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать оплату")

        form_layout = QFormLayout(dialog)

        # Поля ввода
        card_type_input = QLineEdit(dialog)
        expiration_date_input = QLineEdit(dialog)

        # Заполнение текущими данными
        card_type_input.setText(self.payments_table.item(selected_row, 1).text())
        expiration_date_input.setText(self.payments_table.item(selected_row, 2).text())

        form_layout.addRow("Тип карты:", card_type_input)
        form_layout.addRow("Дата истечения (ГГГГ-ММ-ДД):", expiration_date_input)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            card_type = card_type_input.text().strip()
            expiration_date = expiration_date_input.text().strip()

            if not card_type:
                QMessageBox.warning(self, "Ошибка", "Тип карты не может быть пустым.")
                return

            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE Payments
                    SET card_type = %s, expiration_date = %s
                    WHERE card_number = %s
                """, (card_type, expiration_date, card_number))
                self.connection.commit()
                self.load_payments_data()
                QMessageBox.information(self, "Успех", "Оплата успешно обновлена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка обновления оплаты: {e}")
                self.connection.rollback()
    
    def delete_payment(self):
        """Удаление выбранной записи из таблицы Оплата."""
        selected_row = self.payments_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления.")
            return

        card_number = self.payments_table.item(selected_row, 0).text()
        confirm = QMessageBox.question(
            self, "Подтверждение", f"Вы уверены, что хотите удалить оплату с номером карты {card_number}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Payments WHERE card_number = %s", (card_number,))
                self.connection.commit()
                self.load_payments_data()
                QMessageBox.information(self, "Успех", "Оплата успешно удалена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления оплаты: {e}")
                self.connection.rollback()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    print(123)
    sys.exit(app.exec())
