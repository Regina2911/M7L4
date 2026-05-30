import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь добавлен в базу данных."

def test_add_new_existing_name_user(setup_database, connection):
    # Тест добавления пользователя с существующим именем.
    add_user('testuser', 'testuser@example.com', 'password123')
    assert not add_user('testuser', 'testuser2@example.com', 'password456') == "Пользователь с таким именем уже существует.", "Должно возвращаться сообщение об ошибке при добавлении пользователя с существующим логином."

def test_successful_authentication(setup_database, connection):
    """Тест успешной аутентификации пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    assert authenticate_user('testuser', 'password123') == True, "Пользователь успешно аутентифицирован."

def test_nonexisting_user(setup_database, connection):
    #Тест аутентификации несуществующего пользователя.
    add_user('testuser', 'testuser@example.com', 'password123')
    assert authenticate_user('nonexistinguser', 'password123') == False, "Аутентификация несуществующего пользователя."

def test_wrong_password(setup_database, connection):
    #Тест аутентификации пользователя с неправильным паролем.
    assert authenticate_user('testuser', 'wrong_password') == False, "Неправильный пароль"

def test_display_users(setup_database, connection):
    """Тест отображения списка пользователей."""
    users = display_users()
    assert len(users) > 0, "Должно отображаться хотя бы один пользователь."
