from flask import Blueprint, render_template, request
from markupsafe import escape

net_bp = Blueprint('net', __name__)


@net_bp.route('/ip/')
def ip():
    return render_template('net_ip.html', user_ip=request.remote_addr)


@net_bp.route('/ua/')
def ua():
    fields = {
        'REMOTE_ADDR':        request.remote_addr,
        'REMOTE_PORT':        request.environ.get('REMOTE_PORT', ''),
        'X_FORWARDED_FOR':    request.headers.get('X-Forwarded-For', ''),
        'X_REAL_IP':          request.headers.get('X-Real-IP', ''),
        'USER_AGENT':         request.headers.get('User-Agent', ''),
        'ACCEPT':             request.headers.get('Accept', ''),
        'ACCEPT_LANGUAGE':    request.headers.get('Accept-Language', ''),
        'ACCEPT_ENCODING':    request.headers.get('Accept-Encoding', ''),
        'CACHE_CONTROL':      request.headers.get('Cache-Control', ''),
        'REFERER':            request.headers.get('Referer', ''),
        'SEC_CH_UA':          request.headers.get('Sec-CH-UA', ''),
        'SEC_CH_UA_MOBILE':   request.headers.get('Sec-CH-UA-Mobile', ''),
        'SEC_CH_UA_PLATFORM': request.headers.get('Sec-CH-UA-Platform', ''),
    }

    return render_template('net_ua.html', fields=fields)
