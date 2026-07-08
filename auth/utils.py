import os
import random
from datetime import datetime

# Шляхи до файлів
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(BASE_DIR, 'data', 'users.txt')
SENT_DIR = os.path.join(BASE_DIR, 'data', 'sent')


def generate_code():
    """Генерує випадковий 5-значний код."""
    return str(random.randint(10000, 99999))


# --- Робота з users.txt ---

def read_users():
    """Читає users.txt і повертає словник {email: [code, attempts]}."""
    users = {}
    if not os.path.exists(USERS_FILE):
        return users
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(':')
            if len(parts) == 3:
                email, code, attempts = parts
                users[email] = [code, int(attempts)]
    return users


def write_users(users):
    """Записує словник users назад у users.txt."""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        for email, (code, attempts) in users.items():
            f.write(f'{email}:{code}:{attempts}\n')


def save_user_code(email, code):
    """Зберігає або оновлює запис користувача з новим кодом і обнуляє спроби."""
    users = read_users()
    users[email] = [code, 0]
    write_users(users)


def get_user_record(email):
    """Повертає [code, attempts] для email або None."""
    users = read_users()
    return users.get(email)


def increment_attempts(email):
    """Збільшує лічильник невдалих спроб на 1. Повертає нову кількість спроб."""
    users = read_users()
    if email in users:
        users[email][1] += 1
        write_users(users)
        return users[email][1]
    return None


def delete_user_record(email):
    """Видаляє запис користувача (після успішного входу або перевищення спроб)."""
    users = read_users()
    if email in users:
        del users[email]
        write_users(users)


# --- Відправка коду ---

def send_code_smtp(email, code):
    """
    Заглушка для майбутньої відправки коду через SMTP.
    Зараз нічого не робить.
    """
    pass


def send_code_file(email, code):
    """
    Зберігає інформацію про "відправлений" лист у файл у папці data/sent/.
    Ім'я файлу: email_YYMMDD-hhmmss.txt
    """
    os.makedirs(SENT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    filename = f'{email}_{timestamp}.txt'
    filepath = os.path.join(SENT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f'Кому: {email}\n')
        f.write(f'Час: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'Код: {code}\n')
