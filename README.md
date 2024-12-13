# Django Project Setup

Этот проект является приложением на Django, который включает в себя API для работы с меню, корзинами и товарами в корзине. Этот файл описывает, как настроить и запустить проект в IDE.

## Требования

Для успешного запуска проекта вам нужно установить следующие инструменты:

- Python 3.8 или выше
- Django 4.x
- Django REST Framework
- SQLite или другая база данных (для разработки и тестирования можно использовать SQLite)

## Установка и настройка

1. **Клонирование репозитория**

   Клонируйте репозиторий проекта на ваш локальный компьютер:

   ```bash
   git clone https://github.com/ThreeToads/DASS_NewFastPizza.git
   cd NewFastPizza
2. **Создание виртуального окружения**
   ```bash
   python -m venv venv

3. **Активирование виртуального окружения**
   ```bash
   venv\Scripts\activate
4. **Установка зависимостей**
   ```bash
   pip install -r requirements.txt
5. **Настройка базы данных**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
6. **Создание суперюзера**
   ```bash
   python manage.py createsuperuser

7. **Запуск сервера разработки**
   ```bash
   python manage.py runserver
8. Для тестирования работы функционала испольщуйте переход по адресу: http://127.0.0.1:8000/swagger и http://127.0.0.1:8000/admin

 

   
