from flask import Blueprint, render_template, redirect, session

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

