from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from dotenv import load_dotenv

from auth import auth_bp
from main import main_bp

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Довіряємо одному проксі (Nginx) попереду -- бере реальний IP з X-Forwarded-For
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)


if __name__ == '__main__':
    app.run()
