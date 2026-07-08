from flask import Blueprint, render_template, request, redirect, make_response, session, jsonify
from .utils import (
    generate_code,
    save_user_code,
    get_user_record,
    increment_attempts,
    delete_user_record,
    send_code_smtp,
    send_code_file,
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            return render_template('login.html', error='Введіть електронну адресу.', saved_email='')

        # Генеруємо код і зберігаємо у users.txt
        code = generate_code()
        save_user_code(email, code)

        # Відправка коду (SMTP -- заглушка, file -- зберігає у data/sent/)
        send_code_smtp(email, code)
        send_code_file(email, code)

        # Зберігаємо email у сесії для сторінки верифікації
        session['pending_email'] = email

        # Зберігаємо email у куці на 30 днів (для автопідстановки при наступному вході)
        response = make_response(redirect('/code/'))
        response.set_cookie('saved_email', email, max_age=30 * 24 * 3600, httponly=True)
        return response

    # GET: зчитуємо email з куки, якщо є
    saved_email = request.cookies.get('saved_email', '')
    return render_template('login.html', saved_email=saved_email)


@auth_bp.route('/logout/')
def logout():
    session.pop('email', None)
    return redirect('/')


@auth_bp.route('/code/', methods=['GET', 'POST'])
def code():
    email = session.get('pending_email')

    # Якщо немає pending_email у сесії -- нема чого верифікувати
    if not email:
        return redirect('/login/')

    if request.method == 'POST':
        data = request.get_json()
        entered_code = (data.get('code', '')).strip()

        record = get_user_record(email)

        # Запис зник (наприклад, хтось повторно запросив код)
        if not record:
            return jsonify({'error': 'expired'})

        saved_code, attempts = record

        if entered_code == saved_code:
            # Код вірний -- авторизуємо
            delete_user_record(email)
            session.pop('pending_email', None)
            session['email'] = email
            session.permanent = True
            return jsonify({'success': True})

        # Код невірний -- збільшуємо лічильник
        new_attempts = increment_attempts(email)
        attempts_left = 3 - new_attempts

        if attempts_left <= 0:
            delete_user_record(email)
            session.pop('pending_email', None)
            return jsonify({'error': 'limit'})

        return jsonify({'error': 'wrong', 'attempts_left': attempts_left})

    # GET
    return render_template('code.html', email=email)
