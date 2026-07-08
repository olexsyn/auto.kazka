from flask import Blueprint, render_template, request, redirect, session
from markupsafe import escape

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/home/')
def home():
    email = session.get('email')
    if not email:
        return redirect('/login/')
    return render_template('home.html', email=email)


@main_bp.route('/ip/')
def ip():
    return f'<pre>{request.remote_addr}</pre>'


@main_bp.route('/about/')
def about():
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
    # rows = ''.join(
    #     f'<tr class="{"gr" if i % 2 else ""}"><td>{escape(k)}</td><td>&gt;</td><td>{escape(v)}</td></tr>'
    #     for i, (k, v) in enumerate(fields)
    # )
    # return f'<table>{rows}</table>'

    rows = ''.join(
        f'{escape(k)}: {escape(v)}\n'
        for i, (k, v) in enumerate(fields)
    )
    return f'<pre>{rows}</pre>'
