from flask import Flask, render_template, request, redirect, make_response, session, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix  # myip
from markupsafe import escape                       # myip
from config import Config
from dotenv import load_dotenv
from auth import generate_code, save_user_code, send_code_smtp, send_code_file, \
    get_user_record, increment_attempts, delete_user_record

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
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


@app.route('/home/')
def home():
    email = session.get('email')
    if not email:
        return redirect('/login/')
    return render_template('home.html', email=email)


@app.route('/logout/')
def logout():
    session.pop('email', None)
    return redirect('/')


@app.route('/code/', methods=['GET', 'POST'])
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


# Довіряємо одному проксі (Nginx) попереду -- бере реальний IP з X-Forwarded-For
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

@app.route('/myip/')
def myip():
    fields = [
        ('REMOTE_ADDR', request.remote_addr),
        ('REMOTE_PORT', request.environ.get('REMOTE_PORT', '')),
        ('X_FORWARDED_FOR', request.headers.get('X-Forwarded-For', '')),
        ('X_REAL_IP', request.headers.get('X-Real-IP', '')),
        ('USER_AGENT', request.headers.get('User-Agent', '')),
        ('ACCEPT', request.headers.get('Accept', '')),
        ('ACCEPT_LANGUAGE', request.headers.get('Accept-Language', '')),
        ('ACCEPT_ENCODING', request.headers.get('Accept-Encoding', '')),
        ('CACHE_CONTROL', request.headers.get('Cache-Control', '')),
        ('REFERER', request.headers.get('Referer', '')),
        ('SEC_CH_UA', request.headers.get('Sec-CH-UA', '')),
        ('SEC_CH_UA_MOBILE', request.headers.get('Sec-CH-UA-Mobile', '')),
        ('SEC_CH_UA_PLATFORM', request.headers.get('Sec-CH-UA-Platform', '')),
    ]
    rows = ''.join(
        f'<tr class="{"gr" if i % 2 else ""}"><td>{escape(k)}</td><td>&gt;</td><td>{escape(v)}</td></tr>'
        for i, (k, v) in enumerate(fields)
    )
    return f'<table>{rows}</table>'

if __name__ == '__main__':
    app.run()
